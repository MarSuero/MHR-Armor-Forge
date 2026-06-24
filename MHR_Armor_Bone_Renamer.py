#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
怪物猎人崛起 外观mod骨骼/模型一键替换工具
PCL2 风格 UI - 稳定版
"""

import json
import ctypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
import importlib.util
import tkinter as tk
from tkinter import ttk, font, filedialog, messagebox

# 检查当前 Python 是否能正常加载 py7zr
def check_current_python():
    """检查当前 Python 是否能加载 py7zr"""
    try:
        import py7zr
        return True
    except Exception:
        return False

# 如果当前 Python 不能加载 py7zr，尝试切换到 D:\python.exe
if not check_current_python():
    print("[检测] 当前 Python 3.14 与 py7zr 不兼容")
    print("[检测] 尝试切换到 D:\\python.exe...")

    d_python_paths = [
        r"D:\python.exe",
        r"D:\Python\python.exe",
        r"D:\Python314\python.exe",
        r"D:\Python312\python.exe",
        r"D:\Python311\python.exe",
    ]

    for d_python in d_python_paths:
        if os.path.exists(d_python):
            # 检查这个 Python 是否能加载 py7zr
            try:
                result = subprocess.run(
                    [d_python, "-c", "import py7zr; print('OK')"],
                    capture_output=True, text=True, timeout=5
                )
                if "OK" in result.stdout:
                    print(f"[切换] 找到兼容的 Python: {d_python}")
                    # 重新启动这个 Python
                    script_path = os.path.abspath(__file__)
                    subprocess.Popen([d_python, script_path])
                    sys.exit(0)
            except Exception as e:
                continue

# 尝试添加各种可能的 site-packages 到路径
def setup_extra_paths():
    """扫描常见位置添加 site-packages"""
    candidates = [
        r"D:\lib\site-packages",
        r"D:\Python\Lib\site-packages",
        r"D:\Python314\Lib\site-packages",
        r"D:\python\Lib\site-packages",
        r"D:\Python313\Lib\site-packages",
        r"D:\Python312\Lib\site-packages",
        r"D:\Python311\Lib\site-packages",
        r"D:\Programs\Python\Python314\Lib\site-packages",
        r"D:\Programs\Python\Python313\Lib\site-packages",
    ]

    for path in candidates:
        if os.path.isdir(path) and path not in sys.path:
            sys.path.insert(0, path)
            print(f"[路径] 添加: {path}")

    # 自动扫描 D 盘下所有 site-packages
    for drive in ["D:", "E:", "F:"]:
        if not os.path.exists(drive):
            continue
        try:
            for root, dirs, files in os.walk(drive):
                # 限制深度，避免太慢
                depth = root[len(drive):].count(os.sep)
                if depth > 3:
                    dirs[:] = []
                    continue
                if root.endswith("site-packages"):
                    if root not in sys.path:
                        sys.path.insert(0, root)
                        print(f"[路径] 自动发现: {root}")
        except (PermissionError, OSError):
            pass

setup_extra_paths()


def find_package_path(pkg_name):
    """查找包的实际路径"""
    for path in sys.path:
        if not path or not os.path.isdir(path):
            continue
        candidate = os.path.join(path, pkg_name)
        if os.path.isdir(candidate):
            return candidate
        # 也检查 .py 文件
        candidate_py = os.path.join(path, pkg_name + ".py")
        if os.path.isfile(candidate_py):
            return candidate_py
    return None


def load_package_dynamically(pkg_name):
    """动态加载包"""
    try:
        spec = importlib.util.find_spec(pkg_name)
        if spec is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[pkg_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"[动态加载] {pkg_name} 失败: {e}")
        return None

# 自动复制缺失的库到当前 Python
def auto_copy_missing_libs():
    """自动从已知的 site-packages 复制缺失的库"""
    target = os.path.dirname(os.__file__)
    target_site = os.path.join(target, "site-packages")

    # 确保目标目录存在
    os.makedirs(target_site, exist_ok=True)

    needed = {
        "py7zr": ["py7zr", "py7zr-*"],
        "rarfile": ["rarfile", "rarfile-*"],
        "tkinterdnd2": ["tkinterdnd2", "tkinterdnd2-*"],
    }

    for pkg, patterns in needed.items():
        # 检查当前 Python 是否已经有这个库
        target_pkg = os.path.join(target_site, pkg)
        if os.path.exists(target_pkg):
            continue

        # 在已知的 site-packages 中查找
        for search_path in sys.path:
            if not search_path or not os.path.isdir(search_path):
                continue
            if "site-packages" not in search_path:
                continue
            try:
                for item in os.listdir(search_path):
                    if item.lower() == pkg.lower() or item.lower().startswith(pkg.lower() + "-"):
                        src_path = os.path.join(search_path, item)
                        dst_path = os.path.join(target_site, item)
                        try:
                            if os.path.exists(dst_path):
                                continue
                            if os.path.isdir(src_path):
                                shutil.copytree(src_path, dst_path)
                                print(f"[复制] {item}: {src_path} -> {dst_path}")
                            else:
                                shutil.copy2(src_path, dst_path)
                                print(f"[复制] {item}: {src_path} -> {dst_path}")
                        except Exception as e:
                            print(f"[复制失败] {item}: {e}")
            except (PermissionError, OSError):
                pass

# 在导入前先尝试自动复制
try:
    auto_copy_missing_libs()
except Exception as e:
    print(f"[自动复制错误] {e}")

# 复制完成后，把目标 site-packages 添加到 sys.path
_target_site = os.path.join(os.path.dirname(os.__file__), "site-packages")
if os.path.isdir(_target_site) and _target_site not in sys.path:
    sys.path.insert(0, _target_site)
    print(f"[路径] 目标 site-packages: {_target_site}")

# 强制重新检测（清除已缓存的失败导入）
import importlib
for mod_name in list(sys.modules.keys()):
    if mod_name in ['py7zr', 'rarfile', 'tkinterdnd2']:
        del sys.modules[mod_name]

# Windows DPI 缩放支持
def enable_dpi_awareness():
    """启用 Windows DPI 缩放感知"""
    try:
        # Windows 10 1703+ (Per Monitor V2)
        ctypes.windll.shcore.SetProcessDpiAwarenessContext(
            ctypes.c_void_p(-4))  # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
    except (AttributeError, OSError):
        try:
            # Windows 8.1+ (Per Monitor)
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError, OSError):
            try:
                # Windows Vista+ (System DPI)
                ctypes.windll.user32.SetProcessDPIAware()
            except (AttributeError, OSError):
                pass

# 在创建窗口前启用 DPI 感知
if sys.platform == 'win32':
    enable_dpi_awareness()

# 尝试引入拖放支持
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAVE_DND = True
except ImportError:
    HAVE_DND = False

# 压缩包支持
try:
    import zipfile
    HAVE_ZIP = True
except ImportError:
    HAVE_ZIP = False

# py7zr - 兼容 Python 3.14
HAVE_7Z = False
try:
    import py7zr
    HAVE_7Z = True
    print("[成功] 加载 py7zr")
except Exception as e:
    print(f"[提示] py7zr 加载失败: {e}")
    HAVE_7Z = False

# rarfile
HAVE_RAR = False
try:
    import rarfile
    HAVE_RAR = True
    print("[成功] 加载 rarfile")
except Exception as e:
    print(f"[提示] rarfile 加载失败: {e}")
    HAVE_RAR = False

# tkinterdnd2
HAVE_DND = False
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAVE_DND = True
    print("[成功] 加载 tkinterdnd2")
except Exception as e:
    print(f"[提示] tkinterdnd2 加载失败: {e}")
    HAVE_DND = False


PART_PATTERNS = {
    "头": ["head", "helm", "hat", "头", "帽", "盔"],
    "胸": ["body", "chest", "torso", "胸", "身", "铠"],
    "手": ["arm", "hand", "glove", "手", "臂"],
    "腰": ["waist", "wst", "belt", "腰"],
    "腿": ["leg", "feet", "boot", "腿", "脚"],
}

# ============================================================
# 内置装备对照表
# ============================================================
EQUIPMENT_TABLE = {
    "200": ["炎火装束", "炎火装束・霸", "炎火装束・继"],
    "001": ["皮制", "皮制S", "皮制X"],
    "014": ["锁甲", "锁甲S", "锁甲X"],
    "002": ["猎人", "猎人S", "猎人X"],
    "044": ["杜宾", "杜宾X"],
    "004": ["合金", "合金S", "合金X"],
    "031": ["铸铁", "铸铁S", "铸铁X"],
    "043": ["花纹钢", "花纹钢X"],
    "238": ["花瓣", "花瓣S", "花瓣X"],
    "239": ["鱼鳞", "鱼鳞S", "鱼鳞X"],
    "026": ["死神", "死神S", "死神X"],
    "240": ["南瓜", "南瓜S", "南瓜X"],
    "241": ["锹形", "锹形S", "凤蝶", "凤蝶S", "锹形X", "凤蝶X"],
    "242": ["海境", "海境S", "海境X"],
    "243": ["混沌", "混沌・霸", "混沌・真"],
    "244": ["雪绒花", "雪绒花S", "雪绒花X"],
    "245": ["毒蝎", "毒蝎S", "毒蛛", "毒蛛S", "毒蝎X", "毒蛛X"],
    "246": ["倪泰表", "倪泰表・霸", "依巫", "依巫・祈", "倪泰表・真", "依巫・燿"],
    "259": ["神凪", "神凪・愿", "倪泰里", "倪泰里・霸", "神凪・洸", "倪泰里・真"],
    "248": ["贝壳", "贝壳S", "贝壳X"],
    "249": ["哥特", "哥特S", "哥特X"],
    "202": ["天狗兽", "天狗兽S", "天狗兽X", "天狗兽Z"],
    "203": ["伞鸟", "伞鸟S", "伞鸟X"],
    "204": ["河童蛙", "河童蛙S", "河童蛙X"],
    "205": ["人鱼龙", "人鱼龙S", "人鱼龙X", "人鱼龙Z"],
    "206": ["妃蜘蛛", "妃蜘蛛X", "妃蜘蛛Z"],
    "207": ["雪鬼兽", "雪鬼兽S", "雪鬼兽X"],
    "208": ["泥翁龙", "泥翁龙S", "泥翁龙X", "泥翁龙Ｚ"],
    "209": ["风卷", "风卷・真"],
    "210": ["鸣神", "鸣神・真"],
    "211": ["镰鼬龙", "镰鼬龙S", "镰鼬龙X"],
    "047": ["钢龙", "钢龙X", "脉动钢龙"],
    "212": ["水行", "水行・真", "水行・醒"],
    "046": ["帝王", "帝王X", "脉动帝王"],
    "213": ["丸鸟伪装", "丸鸟S伪装", "丸鸟X伪装"],
    "214": ["垂皮龙", "垂皮龙S", "垂皮龙X"],
    "215": ["硬甲龙", "硬甲龙S", "硬甲龙X"],
    "216": ["狗龙皮", "狗龙皮S", "狗龙皮X"],
    "217": ["飞甲虫", "飞甲虫S", "飞甲虫X"],
    "218": ["野猪伪装", "野猪S伪装"],
    "219": ["翼蛇龙", "翼蛇龙S", "翼蛇龙X"],
    "220": ["水生兽", "水生兽S", "水生兽X"],
    "221": ["熔岩兽", "熔岩兽S", "熔岩兽X"],
    "222": ["毒狗龙", "毒狗龙S", "毒狗龙X"],
    "223": ["眠狗龙", "眠狗龙S", "眠狗龙X"],
    "224": ["青熊兽", "青熊兽S", "青熊兽X"],
    "225": ["白兔兽", "白兔兽S", "白兔兽X"],
    "226": ["赤甲兽", "赤甲兽S", "赤甲兽X"],
    "227": ["水兽", "水兽S", "水兽X"],
    "012": ["土砂龙", "土砂龙S", "土砂龙X"],
    "229": ["奇怪龙", "奇怪龙S", "奇怪龙X"],
    "080": ["迅龙", "迅龙S", "迅龙X"],
    "079": ["冰牙龙", "冰牙龙S", "冰牙龙X"],
    "021": ["雌火龙", "雌火龙S", "雌火龙X"],
    "033": ["火龙", "火龙S", "火龙X"],
    "083": ["轰龙", "轰龙S", "轰龙X"],
    "034": ["角龙", "角龙S", "角龙X"],
    "233": ["岩龙", "岩龙S", "岩龙X"],
    "234": ["雷狼龙", "雷狼龙S", "雷狼龙X"],
    "235": ["金色", "齐天・真", "怒天"],
    "237": ["赫耀", "赫耀・真", "赫耀・历"],
    "009": ["搔鸟", "搔鸟S", "搔鸟X"],
    "010": ["毒妖鸟", "毒妖鸟S", "毒妖鸟X"],
    "011": ["泥鱼龙", "泥鱼龙X"],
    "013": ["飞雷龙", "飞雷龙S", "飞雷龙X"],
    "020": ["蛮颚龙", "蛮颚龙S", "蛮颚龙X"],
    "042": ["爆鳞龙", "爆鳞龙X"],
    "252": ["铬合金", "铬合金X"],
    "054": ["骷髅", "骷髅S", "骷髅X"],
    "061": ["炎之封眼"],
    "255": ["黑色皮制"],
    "062": ["墨镜"],
    "257": ["狗龙伪装", "狗龙S伪装", "狗龙X伪装"],
    "060": ["知略眼镜"],
    "037": ["强弓羽饰", "名手羽饰"],
    "201": ["祸铠", "祸铠・霸", "祸铠・真", "祸铠・怨"],
    "003": ["骨制", "骨制S", "骨制X"],
    "228": ["泡狐龙", "泡狐龙S", "泡狐龙X"],
    "036": ["旅团", "旅团S", "旅团X"],
    "272": ["炎火武士"],
    "250": ["祸铠封具"],
    "263": ["龙人耳饰"],
    "264": ["狐狸面具"],
    "262": ["名角假发"],
    "266": ["飞燕"],
    "261": ["艾露猫尾巴", "艾露猫耳朵"],
    "260": ["牙猎犬伪装", "牙猎犬尾巴"],
    "254": ["骑士"],
    "265": ["染花"],
    "276": ["豪鬼"],
    "251": ["亚瑟"],
    "279": ["公会十字"],
    "268": ["狸兽伪装"],
    "277": ["潜水员"],
    "282": ["华丽耳饰"],
    "283": ["鬼火鸟耳饰"],
    "284": ["犬猫耳饰"],
    "267": ["兔团子耳饰"],
    "281": ["苦无耳饰"],
    "289": ["猎户星"],
    "269": ["敬爱围巾"],
    "285": ["蝴蝶结项链"],
    "286": ["皮制项圈"],
    "288": ["博爱绷带"],
    "287": ["褶边项圈"],
    "278": ["原型"],
    "270": ["艾露猫忍头巾"],
    "290": ["盛装"],
    "291": ["盛开"],
    "280": ["黑带", "黑带S"],
    "271": ["炎火外套"],
    "292": ["索尼克服装"],
    "293": ["苍世武士"],
    "358": ["蓝速龙"],
    "360": ["巨甲虫"],
    "359": ["巨蜂"],
    "310": ["镰鼬龙X"],
    "302": ["伞鸟X"],
    "315": ["水兽X"],
    "316": ["土砂龙X"],
    "337": ["大名盾蟹"],
    "303": ["河童蛙X"],
    "314": ["花纹钢X"],
    "311": ["钢龙X"],
    "312": ["水行・真"],
    "313": ["帝王X"],
    "317": ["奇怪龙X"],
    "301": ["天狗兽X"],
    "347": ["天狗兽Z"],
    "329": ["毒妖鸟X"],
    "330": ["泥鱼龙X"],
    "324": ["岩龙X"],
    "304": ["人鱼龙X"],
    "348": ["人鱼龙Z"],
    "320": ["雌火龙X"],
    "331": ["飞雷龙X"],
    "332": ["蛮颚龙X"],
    "319": ["冰牙龙X"],
    "300": ["祸铠・真"],
    "318": ["迅龙X"],
    "306": ["雪鬼兽X"],
    "354": ["刚缠兽"],
    "338": ["将军镰蟹"],
    "307": ["泥翁龙X"],
    "350": ["泥翁龙Ｚ"],
    "305": ["妃蜘蛛X"],
    "349": ["妃蜘蛛Z"],
    "308": ["风卷・真"],
    "309": ["鸣神・真"],
    "327": ["赫耀・真"],
    "339": ["怒天"],
    "346": ["祸铠・怨"],
    "381": ["王国据点司令"],
    "507": ["翔驱羽饰", "祝福羽饰"],
    "387": ["公会宫殿"],
    "382": ["掠夺者王冠"],
    "361": ["蔚蓝"],
    "391": ["幻想宝冠"],
    "392": ["雷尔尼亚"],
    "394": ["灭龙猎装"],
    "375": ["龙公礼服"],
    "433": ["黑带S"],
    "508": ["埃尔迦德"],
    "351": ["矜持"],
    "335": ["金黄澄月"],
    "336": ["银白耀日"],
    "340": ["月光"],
    "395": ["夏日"],
    "363": ["情谊"],
    "407": ["菲奥莱娜"],
    "408": ["倪泰"],
    "400": ["啮生虫王冠"],
    "345": ["阴阳师"],
    "357": ["棘龙Z"],
    "416": ["水行・醒"],
    "396": ["秋风"],
    "409": ["阿尔洛"],
    "424": ["蒸汽贵族"],
    "406": ["探明的单片眼镜"],
    "401": ["海豚王冠"],
    "421": ["混茫", "堕天"],
    "415": ["脉动钢龙"],
    "417": ["脉动帝王"],
    "397": ["蓬松毛皮"],
    "410": ["火芽"],
    "425": ["机械"],
    "402": ["黑翼耳饰"],
    "405": ["牙猎面具"],
    "362": ["朱伟"],
    "367": ["薄暮"],
    "422": ["雪崩"],
    "418": ["赫耀・历"],
    "403": ["白色福木兔耳套"],
    "393": ["蒙面围巾"],
    "366": ["海洋"],
    "365": ["漾光"],
    "364": ["雷尼根"],
    "398": ["怪悟猎仁", "百龙夜子"],
    "411": ["水芸"],
    "370": ["艾丽西亚"],
    "428": ["狂野"],
    "423": ["风雨"],
    "419": ["美德", "久爱"],
    "435": ["健美"],
    "368": ["碧空"],
    "420": ["原初"],
    "372": ["王国轻装骑士"],
    "385": ["五行"],
    "388": ["结云"],
    "389": ["福木兔伪装"],
    "373": ["王国炮术队"],
    "376": ["公会诗人", "学士"],
    "386": ["守护者"],
    "390": ["海蛞蝓帽子"],
    "378": ["猎鹰", "求知"],
    "369": ["尊严"],
    "383": ["巴尔巴尼亚"],
    "384": ["恩宠"],
    "326": ["齐天・真"],
    "333": ["爆鳞龙X"],
    "341": ["黑蚀龙"],
    "343": ["千刃龙"],
    "344": ["电龙"],
    "353": ["冰狼龙"],
    "356": ["棘龙"],
    "371": ["王国重装骑士"],
    "342": ["方舟", "友爱"],
    "352": ["爵银龙"],
    "374": ["教授", "博爱"],
    "379": ["贤者"],
    "380": ["追踪者"],
    "377": ["水手"],
    "355": ["冥渊缠铠"]
}


class PCL2ModTool:
    """PCL2 风格的Mod工具"""

    def __init__(self, root):
        self.root = root

        # 计算 DPI 缩放比例
        self.scale = self.get_dpi_scale()
        # 根据缩放比例调整窗口大小
        base_width = 1100
        base_height = 720
        scaled_width = int(base_width * self.scale)
        scaled_height = int(base_height * self.scale)

        self.root.title("MHR 外观mod替换工具")
        self.root.geometry(f"{scaled_width}x{scaled_height}")
        self.root.configure(bg="#FFFFFF")

        # 状态变量
        self.mod_path = None
        self.work_path = None
        self.is_archive = False
        self.original_archive = None
        self.equipment_map = EQUIPMENT_TABLE
        self.unique_ids = []
        self.detected_id = None
        self.detected_part_files = {}
        self.save_path = None
        self.current_page = None

        # 主题配置
        self.themes = self._get_theme_definitions()
        self.config_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "config.json"
        )
        self.current_theme = self._load_theme()

        # PCL2 颜色（应用当前主题）
        self.colors = self.themes.get(self.current_theme, self.themes["默认蓝"]).copy()
        self.root.configure(bg=self.colors['bg'])

        self.setup_ui()
        self.load_builtin_equipment()

    def setup_ui(self):
        """设置 PCL2 风格 UI"""
        # 应用 DPI 缩放
        self.apply_dpi_scale()
        self.setup_ttk_style()

        # 左侧导航栏
        self.sidebar = tk.Frame(self.root, bg=self.colors['sidebar'],
                                width=int(200 * self.scale))
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        # Logo 区域
        logo_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
        logo_frame.pack(fill='x', pady=(20, 10), padx=15)

        # Logo 文字
        tk.Label(logo_frame, text="MHR",
                font=('Microsoft YaHei', 22, 'bold'),
                bg=self.colors['sidebar'],
                fg=self.colors['accent']).pack(anchor='w')

        tk.Label(logo_frame, text="外观mod工具",
                font=('Microsoft YaHei', 10),
                bg=self.colors['sidebar'],
                fg=self.colors['text_secondary']).pack(anchor='w')

        # 分隔线
        sep = tk.Frame(self.sidebar, bg=self.colors['border'], height=1)
        sep.pack(fill='x', padx=15, pady=15)

        # 导航按钮
        self.nav_buttons = []
        nav_items = [
            ("📦  MOD修改", self.show_import_page),
            ("💾  存档备份", self.show_save_backup_page),
            ("⚙️  设置", self.show_settings_page),
            ("📋  日志", self.show_log_page),
        ]

        nav_container = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
        nav_container.pack(fill='x', padx=10)

        for text, command in nav_items:
            btn = self.create_nav_button(nav_container, text, command)
            btn.pack(fill='x', pady=2)
            self.nav_buttons.append(btn)

        # 高亮第一个
        self.nav_buttons[0].config(bg=self.colors['sidebar_active'])

        # 底部信息
        bottom_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
        bottom_frame.pack(side='bottom', fill='x', padx=15, pady=15)

        tk.Label(bottom_frame, text="作者@鸠十六",
                font=('Microsoft YaHei', 10, 'bold'),
                bg=self.colors['sidebar'],
                fg=self.colors['accent']).pack(anchor='w')

        tk.Label(bottom_frame, text="v1.4",
                font=('Microsoft YaHei', 9),
                bg=self.colors['sidebar'],
                fg=self.colors['text_secondary']).pack(anchor='w', pady=(2, 0))

        # 主内容区
        self.main_content = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_content.pack(side='left', fill='both', expand=True)

        # 创建四个页面
        self.import_page = self.create_import_page()
        self.save_backup_page = self.create_save_backup_page()
        self.settings_page = self.create_settings_page()
        self.log_page = self.create_log_page()

        self.show_import_page()

    # ============================================================
    # 主题管理
    # ============================================================
    def _get_theme_definitions(self):
        """定义所有主题配色方案"""
        return {
            "默认蓝": {
                'bg': '#FFFFFF',
                'sidebar': '#F0F0F0',
                'sidebar_hover': '#E5F1FB',
                'sidebar_active': '#D4E8F7',
                'accent': '#1E88E5',
                'accent_dark': '#1565C0',
                'accent_light': '#64B5F6',
                'text': '#212121',
                'text_secondary': '#616161',
                'text_disabled': '#9E9E9E',
                'border': '#E0E0E0',
                'border_light': '#EEEEEE',
                'border_accent': '#BBDEFB',
                'card': '#FAFAFA',
                'card_hover': '#F5F5F5',
                'success': '#43A047',
                'warning': '#FB8C00',
                'error': '#E53935',
                'primary_btn': '#1E88E5',
                'primary_btn_hover': '#1976D2',
            },
            "深邃黑": {
                'bg': '#1E1E1E',
                'sidebar': '#252526',
                'sidebar_hover': '#2A2D2E',
                'sidebar_active': '#37373D',
                'accent': '#007ACC',
                'accent_dark': '#005F9E',
                'accent_light': '#4FC3F7',
                'text': '#E0E0E0',
                'text_secondary': '#A0A0A0',
                'text_disabled': '#6E6E6E',
                'border': '#3E3E42',
                'border_light': '#464649',
                'border_accent': '#007ACC',
                'card': '#252526',
                'card_hover': '#2A2D2E',
                'success': '#4CAF50',
                'warning': '#FF9800',
                'error': '#F44336',
                'primary_btn': '#007ACC',
                'primary_btn_hover': '#005F9E',
            },
            "护眼绿": {
                'bg': '#F5F5DC',
                'sidebar': '#E8E4C9',
                'sidebar_hover': '#D6D2B0',
                'sidebar_active': '#C8C49D',
                'accent': '#2E7D32',
                'accent_dark': '#1B5E20',
                'accent_light': '#66BB6A',
                'text': '#2C3E2C',
                'text_secondary': '#5C6B5C',
                'text_disabled': '#8C9B8C',
                'border': '#D0CDB0',
                'border_light': '#E0DDC5',
                'border_accent': '#81C784',
                'card': '#FBF8E8',
                'card_hover': '#F5F2DA',
                'success': '#388E3C',
                'warning': '#F57C00',
                'error': '#D32F2F',
                'primary_btn': '#2E7D32',
                'primary_btn_hover': '#1B5E20',
            },
            "樱花粉": {
                'bg': '#FFF0F5',
                'sidebar': '#FCE4EC',
                'sidebar_hover': '#F8BBD9',
                'sidebar_active': '#F48FB1',
                'accent': '#C2185B',
                'accent_dark': '#880E4F',
                'accent_light': '#F06292',
                'text': '#3E2723',
                'text_secondary': '#5D4037',
                'text_disabled': '#8D6E63',
                'border': '#F8BBD0',
                'border_light': '#FCE4EC',
                'border_accent': '#F48FB1',
                'card': '#FFF5F8',
                'card_hover': '#FFEBF0',
                'success': '#43A047',
                'warning': '#FF9800',
                'error': '#E53935',
                'primary_btn': '#C2185B',
                'primary_btn_hover': '#880E4F',
            },
            "日落橙": {
                'bg': '#FFF3E0',
                'sidebar': '#FFE0B2',
                'sidebar_hover': '#FFCC80',
                'sidebar_active': '#FFB74D',
                'accent': '#E65100',
                'accent_dark': '#BF360C',
                'accent_light': '#FF9800',
                'text': '#3E2723',
                'text_secondary': '#5D4037',
                'text_disabled': '#8D6E63',
                'border': '#FFCC80',
                'border_light': '#FFE0B2',
                'border_accent': '#FFB74D',
                'card': '#FFF8E1',
                'card_hover': '#FFF0CC',
                'success': '#43A047',
                'warning': '#F57C00',
                'error': '#E53935',
                'primary_btn': '#E65100',
                'primary_btn_hover': '#BF360C',
            },
            "暗夜紫": {
                'bg': '#1A1025',
                'sidebar': '#22142E',
                'sidebar_hover': '#2D1B3D',
                'sidebar_active': '#3D2549',
                'accent': '#7B1FA2',
                'accent_dark': '#4A148C',
                'accent_light': '#CE93D8',
                'text': '#E1E1E1',
                'text_secondary': '#B0B0B0',
                'text_disabled': '#808080',
                'border': '#3D2549',
                'border_light': '#4A2E5A',
                'border_accent': '#7B1FA2',
                'card': '#22142E',
                'card_hover': '#2D1B3D',
                'success': '#66BB6A',
                'warning': '#FFA726',
                'error': '#EF5350',
                'primary_btn': '#7B1FA2',
                'primary_btn_hover': '#4A148C',
            },
        }

    def _load_theme(self):
        """加载保存的主题配置"""
        default_theme = "默认蓝"
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    theme_name = config.get("theme", default_theme)
                    if theme_name in self.themes:
                        return theme_name
        except Exception:
            pass
        return default_theme

    def _save_theme(self, theme_name):
        """保存主题配置到文件"""
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
            config["theme"] = theme_name
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.log_msg(f"❌ 保存主题配置失败: {e}")
            return False

    def _apply_theme_colors(self):
        """应用当前主题颜色到 self.colors"""
        if self.current_theme in self.themes:
            self.colors = self.themes[self.current_theme].copy()
        else:
            self.colors = self.themes["默认蓝"].copy()

    def create_nav_button(self, parent, text, command):
        """创建 PCL2 风格导航按钮"""
        btn = tk.Button(parent, text=text,
                       font=('Microsoft YaHei', 11),
                       bg=self.colors['sidebar'],
                       fg=self.colors['text'],
                       activebackground=self.colors['sidebar_active'],
                       activeforeground=self.colors['text'],
                       bd=0, padx=15, pady=10,
                       anchor='w', cursor='hand2',
                       relief='flat',
                       command=command)
        return btn

    def show_import_page(self):
        """显示导入页面"""
        self._hide_all_pages()
        self.import_page.pack(fill='both', expand=True)
        self.update_nav_highlight(0)

    def show_settings_page(self):
        """显示设置页面"""
        self._hide_all_pages()
        self.settings_page.pack(fill='both', expand=True)
        self.update_nav_highlight(2)

    def show_log_page(self):
        """显示日志页面"""
        self._hide_all_pages()
        self.log_page.pack(fill='both', expand=True)
        self.update_nav_highlight(3)

    def show_save_backup_page(self):
        """显示存档备份页面"""
        self._hide_all_pages()
        self.save_backup_page.pack(fill='both', expand=True)
        self.update_nav_highlight(1)

    def _hide_all_pages(self):
        """隐藏所有页面"""
        self.import_page.pack_forget()
        self.save_backup_page.pack_forget()
        self.settings_page.pack_forget()
        self.log_page.pack_forget()

    def update_nav_highlight(self, index):
        """更新导航高亮"""
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.config(bg=self.colors['sidebar_active'],
                          activebackground=self.colors['sidebar_active'])
            else:
                btn.config(bg=self.colors['sidebar'],
                          activebackground=self.colors['sidebar_hover'])

    # ============================================================
    # 导入页面
    # ============================================================
    def create_import_page(self):
        """创建导入页面 - 左右分栏布局"""
        page = tk.Frame(self.main_content, bg=self.colors['bg'])
        page.pack_propagate(False)

        # 顶部标题
        header = tk.Frame(page, bg=self.colors['bg'])
        header.pack(fill='x', padx=30, pady=(25, 0))

        tk.Label(header, text="导入 Mod",
                font=('Microsoft YaHei', 24, 'bold'),
                bg=self.colors['bg'],
                fg=self.colors['text']).pack(anchor='w')

        tk.Label(header, text="拖放文件或浏览选择你的mod文件",
                font=('Microsoft YaHei', 12),
                bg=self.colors['bg'],
                fg=self.colors['text_secondary']).pack(anchor='w', pady=(4, 0))

        # 内容容器 - 上下分栏
        content = tk.Frame(page, bg=self.colors['bg'])
        content.pack(fill='both', expand=True, padx=30, pady=20)

        # 上部分 - 左右分栏
        upper = tk.Frame(content, bg=self.colors['bg'])
        upper.pack(fill='both', expand=True)

        # 左侧 - 文件导入
        left = tk.Frame(upper, bg=self.colors['card'],
                       highlightbackground=self.colors['border_light'],
                       highlightthickness=1)
        left.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # 左侧内容
        left_inner = tk.Frame(left, bg=self.colors['card'])
        left_inner.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(left_inner, text="文件导入",
                font=('Microsoft YaHei', 14, 'bold'),
                bg=self.colors['card'],
                fg=self.colors['text']).pack(anchor='w', pady=(0, 12))

        # 拖放区域
        self.drop_frame = tk.Frame(left_inner, bg='#F5F5F5',
                                   highlightbackground=self.colors['accent'],
                                   highlightthickness=2,
                                   height=int(150 * self.scale))
        self.drop_frame.pack(fill='x', pady=(0, 12))
        self.drop_frame.pack_propagate(False)

        drop_inner = tk.Frame(self.drop_frame, bg='#F5F5F5')
        drop_inner.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(drop_inner, text="📦",
                font=('Microsoft YaHei', 32),
                bg='#F5F5F5',
                fg=self.colors['accent']).pack()

        self.lbl_drop = tk.Label(drop_inner,
                                text="将 mod 文件夹或压缩包拖到这里\n支持 .zip .7z .rar",
                                font=('Microsoft YaHei', 11),
                                bg='#F5F5F5',
                                fg=self.colors['text_secondary'])
        self.lbl_drop.pack(pady=(6, 0))

        # 浏览按钮
        btn_browse = tk.Button(left_inner, text="📁  浏览文件",
                              font=('Microsoft YaHei', 11, 'bold'),
                              bg=self.colors['primary_btn'],
                              fg='white',
                              activebackground=self.colors['primary_btn_hover'],
                              activeforeground='white',
                              bd=0, padx=20, pady=8,
                              cursor='hand2',
                              command=self.browse_mod)
        btn_browse.pack(pady=(0, 16))

        # 文件信息
        info_frame = tk.Frame(left_inner, bg=self.colors['card'])
        info_frame.pack(fill='x')

        status_row = tk.Frame(info_frame, bg=self.colors['card'])
        status_row.pack(fill='x', pady=(0, 10))

        self.status_indicator = tk.Canvas(status_row, width=10, height=10,
                                         bg=self.colors['card'],
                                         highlightthickness=0)
        self.status_indicator.pack(side='left', padx=(0, 8))
        self.status_circle = self.status_indicator.create_oval(2, 2, 8, 8,
                                                               fill=self.colors['text_disabled'])

        self.lbl_path = tk.Label(status_row, text="未选择 mod 文件",
                                font=('Microsoft YaHei', 10),
                                bg=self.colors['card'],
                                fg=self.colors['text_secondary'])
        self.lbl_path.pack(side='left')

        # 装备名称
        self.lbl_equip_name = tk.Label(info_frame, text="",
                                      font=('Microsoft YaHei', 20, 'bold'),
                                      bg=self.colors['card'],
                                      fg=self.colors['accent'])
        self.lbl_equip_name.pack(anchor='w', pady=(0, 4))

        # 装备编号
        self.lbl_detected = tk.Label(info_frame, text="装备编号: --",
                                    font=('Microsoft YaHei', 12),
                                    bg=self.colors['card'],
                                    fg=self.colors['text'])
        self.lbl_detected.pack(anchor='w', pady=(0, 4))

        # 骨骼文件
        self.lbl_bones = tk.Label(info_frame, text="骨骼文件: --",
                                 font=('Microsoft YaHei', 10),
                                 bg=self.colors['card'],
                                 fg=self.colors['text_secondary'])
        self.lbl_bones.pack(anchor='w')

        # 右侧 - 操作面板
        right = tk.Frame(upper, bg=self.colors['card'],
                        highlightbackground=self.colors['border_light'],
                        highlightthickness=1, width=int(320 * self.scale))
        right.pack(side='right', fill='y', padx=(10, 0))
        right.pack_propagate(False)

        # 目标套装
        right_inner = tk.Frame(right, bg=self.colors['card'])
        right_inner.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(right_inner, text="目标套装",
                font=('Microsoft YaHei', 14, 'bold'),
                bg=self.colors['card'],
                fg=self.colors['text']).pack(anchor='w', pady=(0, 12))

        # 搜索框
        tk.Label(right_inner, text="搜索",
                font=('Microsoft YaHei', 10),
                bg=self.colors['card'],
                fg=self.colors['text_secondary']).pack(anchor='w')

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = tk.Entry(right_inner,
                               textvariable=self.search_var,
                               font=('Microsoft YaHei', 10),
                               bg='white',
                               fg=self.colors['text'],
                               insertbackground=self.colors['accent'],
                               bd=1, relief='solid',
                               highlightbackground=self.colors['border_light'],
                               highlightthickness=1,
                               highlightcolor=self.colors['accent'])
        search_entry.pack(fill='x', pady=(4, 10), ipady=3)

        # 下拉框
        tk.Label(right_inner, text="选择装备",
                font=('Microsoft YaHei', 10),
                bg=self.colors['card'],
                fg=self.colors['text_secondary']).pack(anchor='w')

        self.combo_target = ttk.Combobox(right_inner,
                                        state="readonly",
                                        font=('Microsoft YaHei', 10))
        self.combo_target.pack(fill='x', pady=(4, 12), ipady=2)

        # 分隔
        tk.Frame(right_inner, bg=self.colors['border'],
                height=1).pack(fill='x', pady=10)

        # 选项
        tk.Label(right_inner, text="选项",
                font=('Microsoft YaHei', 14, 'bold'),
                bg=self.colors['card'],
                fg=self.colors['text']).pack(anchor='w', pady=(0, 8))

        self.backup_var = tk.BooleanVar(value=True)
        self.create_pcl2_checkbox(right_inner, "修改前备份原文件", self.backup_var)

        self.repack_var = tk.BooleanVar(value=True)
        self.create_pcl2_checkbox(right_inner, "压缩包自动重新打包", self.repack_var)

        self.open_folder_var = tk.BooleanVar(value=True)
        self.create_pcl2_checkbox(right_inner, "应用后打开输出文件夹", self.open_folder_var)

        # 分隔
        tk.Frame(right_inner, bg=self.colors['border'],
                height=1).pack(fill='x', pady=10)

        # 操作按钮
        btn_preview = tk.Button(right_inner, text="👁  预览修改",
                               font=('Microsoft YaHei', 11),
                               bg='white',
                               fg=self.colors['text'],
                               activebackground=self.colors['card_hover'],
                               bd=1, relief='solid',
                               highlightbackground=self.colors['border_light'],
                               highlightthickness=1,
                               padx=20, pady=8,
                               cursor='hand2',
                               command=self.preview_changes)
        btn_preview.pack(fill='x', pady=(0, 8))

        btn_apply = tk.Button(right_inner, text="✓  应用修改",
                             font=('Microsoft YaHei', 11, 'bold'),
                             bg=self.colors['primary_btn'],
                             fg='white',
                             activebackground=self.colors['primary_btn_hover'],
                             activeforeground='white',
                             bd=0, padx=20, pady=8,
                             cursor='hand2',
                             command=self.apply_changes)
        btn_apply.pack(fill='x')

        # 配置拖放
        if HAVE_DND:
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)

        return page

    def create_rounded_frame(self, parent, bg_color, border_color=None,
                            radius=10, padding=0, **kwargs):
        """创建圆角框架（使用 Canvas 模拟）"""
        # 简化的圆角模拟：通过增加 padding 和柔和边框颜色
        container = tk.Frame(parent, bg=parent['bg'] if 'bg' in parent.keys() else self.colors['bg'],
                            **kwargs)

        # 内层框架
        inner = tk.Frame(container, bg=bg_color)
        if padding:
            inner.pack(fill='both', expand=True, padx=padding, pady=padding)

        return container, inner

    def create_rounded_widget(self, parent, widget_class, **kwargs):
        """创建一个伪圆角 widget（在内部用 Canvas 绘制圆角背景）"""
        bg = kwargs.pop('bg', self.colors['accent'])
        fg = kwargs.pop('fg', 'white')
        text = kwargs.pop('text', '')
        font = kwargs.pop('font', ('Microsoft YaHei', 11, 'bold'))
        command = kwargs.pop('command', None)
        padx = kwargs.pop('padx', 20)
        pady = kwargs.pop('pady', 10)
        width = kwargs.pop('width', None)
        height = kwargs.pop('height', None)

        # 计算尺寸
        if width is None:
            test_label = tk.Label(parent, text=text, font=font)
            width = test_label.winfo_reqwidth() + padx * 2
            test_label.destroy()
        if height is None:
            test_label = tk.Label(parent, text=text, font=font)
            height = test_label.winfo_reqheight() + pady * 2
            test_label.destroy()

        # 创建 Canvas 作为容器
        canvas = tk.Canvas(parent, width=width, height=height,
                          bg=parent['bg'] if 'bg' in parent.keys() else self.colors['bg'],
                          highlightthickness=0)

        # 绘制圆角矩形
        radius = 10
        self._draw_rounded_rect_on_canvas(canvas, 0, 0, width, height, radius, bg)

        # 文字
        canvas.create_text(width//2, height//2, text=text, font=font, fill=fg)

        # 绑定事件
        def on_enter(e):
            self._draw_rounded_rect_on_canvas(canvas, 0, 0, width, height, radius,
                                              self.colors.get('primary_hover', bg))
        def on_leave(e):
            self._draw_rounded_rect_on_canvas(canvas, 0, 0, width, height, radius, bg)
        def on_click(e):
            if command:
                command()

        canvas.bind('<Enter>', on_enter)
        canvas.bind('<Leave>', on_leave)
        canvas.bind('<Button-1>', on_click)
        canvas.config(cursor='hand2')

        return canvas

    def _draw_rounded_rect_on_canvas(self, canvas, x1, y1, x2, y2, radius, color, outline=None):
        """在 Canvas 上绘制圆角矩形"""
        canvas.delete("all")
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1,
        ]
        canvas.create_polygon(points, smooth=True, fill=color, outline=outline or "")

    def create_rounded_card_real(self, parent, bg_color=None, border_color=None,
                                  radius=12, min_height=100):
        """
        创建一个真正的圆角卡片（Canvas 绘制）
        返回 (canvas, content_frame) 元组
        """
        if bg_color is None:
            bg_color = self.colors['card']
        if border_color is None:
            border_color = '#E8E8E8'

        # 用 Canvas 绘制圆角背景
        canvas = tk.Canvas(parent,
                          bg=parent['bg'] if 'bg' in parent.keys() else self.colors['bg'],
                          highlightthickness=0,
                          height=min_height)
        canvas.pack(fill='x', pady=(0, 12))

        def redraw(event=None):
            canvas.delete("all")
            w = canvas.winfo_width()
            h = canvas.winfo_height()
            if w < 2 or h < 2:
                return
            # 外边框
            self._draw_rounded_rect_on_canvas(
                canvas, 0, 0, w, h, radius,
                border_color)
            # 内填充
            self._draw_rounded_rect_on_canvas(
                canvas, 1, 1, w-1, h-1, radius-1,
                bg_color)

        canvas.bind('<Configure>', redraw)

        # 内嵌 Frame
        content_frame = tk.Frame(canvas, bg=bg_color)
        canvas.create_window(15, 15, window=content_frame,
                           anchor='nw', width=canvas.winfo_reqwidth()-30)

        # 监听大小变化以调整 content_frame
        def resize_content(event=None):
            w = canvas.winfo_width()
            h = canvas.winfo_height()
            if w > 30 and h > 30:
                canvas.itemconfig(canvas.find_withtag('content_window')[0]
                                 if canvas.find_withtag('content_window')
                                 else 1, width=w-30)

        return canvas, content_frame

    def create_pcl2_checkbox(self, parent, text, variable):
        """创建 PCL2 风格复选框"""
        frame = tk.Frame(parent, bg=self.colors['card'])
        frame.pack(fill='x', pady=4)

        # 复选框画布 - 用更明显的样式
        canvas = tk.Canvas(frame, width=20, height=20,
                          bg=self.colors['card'],
                          highlightthickness=0)
        canvas.pack(side='left')

        def draw_checkbox():
            canvas.delete("all")
            if variable.get():
                # 选中状态：蓝色填充 + 白色勾
                canvas.create_rectangle(2, 2, 18, 18,
                                       fill=self.colors['accent'],
                                       outline=self.colors['accent'],
                                       width=0)
                canvas.create_line(6, 10, 9, 13, 14, 7,
                                  fill='white', width=2.5)
            else:
                # 未选中状态：白色填充 + 灰色边框
                canvas.create_rectangle(2, 2, 18, 18,
                                       fill='white',
                                       outline=self.colors['text_disabled'],
                                       width=2)
                # 内部画一个淡淡的斜杠或点表示空
                canvas.create_line(2, 2, 18, 18,
                                  fill='',
                                  width=0)

        draw_checkbox()

        def toggle(event=None):
            variable.set(not variable.get())
            draw_checkbox()

        canvas.bind('<Button-1>', toggle)

        label = tk.Label(frame, text=text,
                        font=('Microsoft YaHei', 11),
                        bg=self.colors['card'],
                        fg=self.colors['text'])
        label.pack(side='left', padx=(8, 0))
        label.bind('<Button-1>', toggle)
        frame.bind('<Button-1>', toggle)

    # ============================================================
    # 存档备份页面
    # ============================================================
    def get_steam_save_path(self):
        """获取 Steam 版怪猎崛起存档路径"""
        candidates = [
            r"C:\Program Files (x86)\Steam\userdata",
            r"D:\Program Files (x86)\Steam\userdata",
            r"E:\Program Files (x86)\Steam\userdata",
            r"C:\Steam\userdata",
            r"D:\Steam\userdata",
        ]

        for base in candidates:
            if not os.path.isdir(base):
                continue
            try:
                for user_id in os.listdir(base):
                    user_path = os.path.join(base, user_id)
                    if not os.path.isdir(user_path):
                        continue
                    save_path = os.path.join(user_path, "1446780")
                    if os.path.isdir(save_path):
                        return save_path
            except PermissionError:
                continue
        return None

    def create_rounded_card(self, parent, bg_color=None, border_color=None,
                        radius=12, height=None):
        """
        创建一个真正的圆角卡片（用 Canvas 绘制圆角背景）
        返回 (canvas, content_frame) 元组
        """
        if bg_color is None:
            bg_color = self.colors['card']
        if border_color is None:
            border_color = self.colors['border_light']

        # 创建容器
        container = tk.Frame(parent, bg=parent['bg'] if 'bg' in parent.keys() else self.colors['bg'])
        return container

    def create_save_backup_page(self):
        """创建存档备份页面"""
        page = tk.Frame(self.main_content, bg=self.colors['bg'])
        page.pack_propagate(False)

        # 标题
        header = tk.Frame(page, bg=self.colors['bg'])
        header.pack(fill='x', padx=30, pady=(25, 0))

        tk.Label(header, text="存档备份",
                font=('Microsoft YaHei', 28, 'bold'),
                bg=self.colors['bg'],
                fg=self.colors['text']).pack(anchor='w')

        tk.Label(header, text="备份和恢复 Steam 版怪物猎人崛起存档",
                font=('Microsoft YaHei', 13),
                bg=self.colors['bg'],
                fg=self.colors['text_secondary']).pack(anchor='w', pady=(6, 0))

        # 内容
        content = tk.Frame(page, bg=self.colors['bg'])
        content.pack(fill='both', expand=True, padx=30, pady=20)

        # 上部分 - 存档路径和备份
        upper = tk.Frame(content, bg=self.colors['bg'])
        upper.pack(fill='x')

        # 存档路径卡片（用 Canvas 绘制圆角）
        path_card = tk.Frame(upper, bg=self.colors['bg'],
                            height=int(120 * self.scale))
        path_card.pack(fill='x', pady=(0, 12))
        path_card.pack_propagate(False)

        path_canvas = tk.Canvas(path_card,
                               bg=self.colors['bg'],
                               highlightthickness=0,
                               height=int(120 * self.scale))
        path_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        def redraw_path(event=None):
            w = path_canvas.winfo_width()
            h = path_canvas.winfo_height()
            if w < 2 or h < 2:
                return
            # 外边框
            self._draw_rounded_rect_on_canvas(
                path_canvas, 0, 0, w, h, 12, '#E8E8E8')
            # 内填充
            self._draw_rounded_rect_on_canvas(
                path_canvas, 1, 1, w-1, h-1, 11, self.colors['card'])

        path_canvas.bind('<Configure>', redraw_path)
        path_inner = tk.Frame(path_card, bg=self.colors['card'])
        path_inner.place(x=15, y=15, relwidth=1, width=-30, relheight=1, height=-30)

        tk.Label(path_inner, text="存档路径",
                font=('Microsoft YaHei', 14, 'bold'),
                bg=self.colors['card'],
                fg=self.colors['text']).pack(anchor='w', pady=(0, 8))

        self.lbl_save_path = tk.Label(path_inner, text="正在检测...",
                                     font=('Microsoft YaHei', 11),
                                     bg=self.colors['card'],
                                     fg=self.colors['text_secondary'],
                                     wraplength=int(700 * self.scale), justify='left')
        self.lbl_save_path.pack(anchor='w', pady=(0, 8))

        # 检测存档按钮
        btn_detect = tk.Button(path_inner, text="🔍 重新检测存档路径",
                              font=('Microsoft YaHei', 10),
                              bg=self.colors['card'],
                              fg=self.colors['accent'],
                              activebackground=self.colors['sidebar_hover'],
                              bd=1, padx=15, pady=6,
                              cursor='hand2',
                              command=self.detect_save_path)
        btn_detect.pack(anchor='w')

        # 备份卡片（圆角）
        backup_card_container = tk.Frame(upper, bg=self.colors['bg'],
                                        height=int(180 * self.scale))
        backup_card_container.pack(fill='x', pady=(0, 12))
        backup_card_container.pack_propagate(False)

        backup_canvas = tk.Canvas(backup_card_container,
                                 bg=self.colors['bg'],
                                 highlightthickness=0,
                                 height=int(180 * self.scale))
        backup_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        def redraw_backup(event=None):
            w = backup_canvas.winfo_width()
            h = backup_canvas.winfo_height()
            if w < 2 or h < 2:
                return
            self._draw_rounded_rect_on_canvas(
                backup_canvas, 0, 0, w, h, 12, '#E8E8E8')
            self._draw_rounded_rect_on_canvas(
                backup_canvas, 1, 1, w-1, h-1, 11, self.colors['card'])

        backup_canvas.bind('<Configure>', redraw_backup)
        backup_inner = tk.Frame(backup_card_container, bg=self.colors['card'])
        backup_inner.place(x=15, y=15, relwidth=1, width=-30, relheight=1, height=-30)

        tk.Label(backup_inner, text="创建备份",
                font=('Microsoft YaHei', 14, 'bold'),
                bg=self.colors['card'],
                fg=self.colors['text']).pack(anchor='w', pady=(0, 8))

        # 备注输入
        tk.Label(backup_inner, text="备份备注（可选）",
                font=('Microsoft YaHei', 10),
                bg=self.colors['card'],
                fg=self.colors['text_secondary']).pack(anchor='w')

        self.backup_note_var = tk.StringVar()
        note_entry = tk.Entry(backup_inner,
                             textvariable=self.backup_note_var,
                             font=('Microsoft YaHei', 11),
                             bg='white',
                             fg=self.colors['text'],
                             insertbackground=self.colors['accent'],
                             bd=1, relief='solid',
                             highlightbackground=self.colors['border_light'],
                             highlightthickness=1,
                             highlightcolor=self.colors['accent'])
        note_entry.pack(fill='x', pady=(4, 10), ipady=4)

        # 备份按钮
        btn_backup = tk.Button(backup_inner, text="💾 立即备份",
                              font=('Microsoft YaHei', 12, 'bold'),
                              bg=self.colors['success'],
                              fg='white',
                              activebackground='#2DA14F',
                              activeforeground='white',
                              bd=0, padx=25, pady=10,
                              cursor='hand2',
                              command=self.backup_save)
        btn_backup.pack(anchor='w')

        # 下部分 - 备份列表
        list_card = tk.Frame(content,
                            bg=self.colors['card'],
                            bd=0)
        list_card.pack(fill='both', expand=True, padx=0, pady=0)

        list_header = tk.Frame(list_card, bg=self.colors['card'])
        list_header.pack(fill='x', padx=20, pady=(20, 5))

        tk.Label(list_header, text="备份列表",
                font=('Microsoft YaHei', 14, 'bold'),
                bg=self.colors['card'],
                fg=self.colors['text']).pack(side='left')

        btn_refresh = tk.Button(list_header, text="🔄 刷新",
                                font=('Microsoft YaHei', 10),
                                bg=self.colors['card'],
                                fg=self.colors['accent'],
                                activebackground=self.colors['sidebar_hover'],
                                bd=1, padx=15, pady=4,
                                cursor='hand2',
                                command=self.refresh_backup_list)
        btn_refresh.pack(side='right')

        # 列表和按钮容器
        list_body = tk.Frame(list_card, bg=self.colors['card'])
        list_body.pack(fill='both', expand=True, padx=20, pady=(5, 20))

        # 备份列表
        list_frame = tk.Frame(list_body, bg=self.colors['card'])
        list_frame.pack(fill='both', expand=True, padx=20, pady=(10, 20))

        self.backup_listbox = tk.Listbox(list_frame,
                                        font=('Microsoft YaHei', 10),
                                        bg='white',
                                        fg=self.colors['text'],
                                        selectbackground=self.colors['accent'],
                                        selectforeground='white',
                                        bd=1, relief='solid',
                                        highlightthickness=0,
                                        height=8)
        self.backup_listbox.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical',
                                 command=self.backup_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.backup_listbox.config(yscrollcommand=scrollbar.set)

        # 恢复和删除按钮
        btn_frame = tk.Frame(list_body, bg=self.colors['card'])
        btn_frame.pack(fill='x', padx=20, pady=(0, 15))

        btn_restore = tk.Button(btn_frame, text="🔙 恢复选中备份",
                               font=('Microsoft YaHei', 11, 'bold'),
                               bg=self.colors['accent'],
                               fg='white',
                               activebackground=self.colors['accent_dark'],
                               activeforeground='white',
                               bd=0, padx=20, pady=8,
                               cursor='hand2',
                               command=self.restore_save)
        btn_restore.pack(side='left', padx=(0, 10))

        btn_delete = tk.Button(btn_frame, text="🗑 删除选中备份",
                              font=('Microsoft YaHei', 11),
                              bg=self.colors['card'],
                              fg=self.colors['error'],
                              activebackground='#FFEBEE',
                              bd=0, padx=20, pady=8,
                              cursor='hand2',
                              command=self.delete_backup)
        btn_delete.pack(side='left', padx=(0, 10))

        btn_edit_note = tk.Button(btn_frame, text="✏️ 编辑备注",
                                 font=('Microsoft YaHei', 11),
                                 bg=self.colors['card'],
                                 fg=self.colors['accent'],
                                 activebackground=self.colors['sidebar_hover'],
                                 bd=1, padx=20, pady=8,
                                 cursor='hand2',
                                 command=self.edit_backup_note)
        btn_edit_note.pack(side='left', padx=(0, 10))

        btn_open_folder = tk.Button(btn_frame, text="📁 打开备份文件夹",
                                   font=('Microsoft YaHei', 11),
                                   bg=self.colors['card'],
                                   fg=self.colors['text_secondary'],
                                   activebackground=self.colors['sidebar_hover'],
                                   bd=1, padx=20, pady=8,
                                   cursor='hand2',
                                   command=self.open_backup_folder)
        btn_open_folder.pack(side='right')

        # 初始化时检测路径
        self.root.after(100, self.detect_save_path)
        self.root.after(200, self.refresh_backup_list)

        return page

    def detect_save_path(self):
        """检测存档路径"""
        path = self.get_steam_save_path()
        if path:
            self.save_path = path
            self.lbl_save_path.config(text=f"✓ 已找到: {path}",
                                    fg=self.colors['success'])
            self.log_msg(f"✓ 检测到存档路径: {path}")
        else:
            self.save_path = None
            self.lbl_save_path.config(
                text="✗ 未找到 Steam 版存档\n请确认游戏已通过 Steam 安装并运行过一次",
                fg=self.colors['error'])
            self.log_msg("✗ 未检测到 Steam 版存档路径")

    def get_backup_folder(self):
        """获取备份文件夹路径"""
        # 如果用户设置了自定义备份目录，使用自定义目录
        if hasattr(self, 'backup_dir_var') and self.backup_dir_var.get():
            backup_dir = self.backup_dir_var.get()
        else:
            # 默认使用项目目录下的 save_backups 文件夹
            script_dir = os.path.dirname(os.path.abspath(__file__))
            backup_dir = os.path.join(script_dir, "save_backups")

        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    def backup_save(self):
        """备份存档"""
        if not self.save_path:
            messagebox.showwarning("提示", "请先检测到存档路径")
            return
        if not os.path.exists(self.save_path):
            messagebox.showerror("错误", "存档路径不存在")
            return

        try:
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            note = self.backup_note_var.get().strip()
            if note:
                # 清理备注中的非法字符
                note = re.sub(r'[<>:"/\\|?*]', '_', note)
                backup_name = f"MHR_Save_{timestamp}_{note}"
            else:
                backup_name = f"MHR_Save_{timestamp}"

            backup_path = os.path.join(self.get_backup_folder(), backup_name)

            # 显示进度
            self.log_msg(f"📦 开始备份: {backup_name}")
            self.root.update()

            # 复制文件夹
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.copytree(self.save_path, backup_path)

            # 保存备份信息
            info_file = os.path.join(backup_path, "_backup_info.txt")
            with open(info_file, "w", encoding="utf-8") as f:
                f.write(f"备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"源路径: {self.save_path}\n")
                f.write(f"备注: {note if note else '(无)'}\n")

            self.log_msg(f"✓ 备份完成: {backup_name}")
            messagebox.showinfo("成功", f"备份完成！\n\n{backup_name}")

            # 刷新列表
            self.refresh_backup_list()
            self.backup_note_var.set("")

        except Exception as e:
            self.log_msg(f"❌ 备份失败: {e}")
            messagebox.showerror("错误", f"备份失败:\n{e}")

    def refresh_backup_list(self):
        """刷新备份列表"""
        self.backup_listbox.delete(0, tk.END)
        backup_dir = self.get_backup_folder()

        try:
            backups = []
            for item in os.listdir(backup_dir):
                item_path = os.path.join(backup_dir, item)
                if os.path.isdir(item_path) and item.startswith("MHR_Save_"):
                    # 读取备份信息
                    info_file = os.path.join(item_path, "_backup_info.txt")
                    note = ""
                    if os.path.exists(info_file):
                        try:
                            with open(info_file, "r", encoding="utf-8") as f:
                                for line in f:
                                    if line.startswith("备注:"):
                                        note = line.replace("备注:", "").strip()
                                        break
                        except Exception:
                            pass
                    display = item
                    if note and note != "(无)":
                        display = f"{item}  [{note}]"
                    backups.append((item, display))

            # 按时间排序（最新的在前面）
            backups.sort(reverse=True)

            for backup_name, display in backups:
                self.backup_listbox.insert(tk.END, display)
                # 存储原始名称到列表
                if not hasattr(self, '_backup_names'):
                    self._backup_names = []
                # 更新或追加
                idx = self.backup_listbox.size() - 1
                # 简化处理：直接存储
                if len(self._backup_names) <= idx:
                    self._backup_names.append(backup_name)
                else:
                    self._backup_names[idx] = backup_name

        except Exception as e:
            self.log_msg(f"❌ 刷新备份列表失败: {e}")

    def get_selected_backup(self):
        """获取选中的备份"""
        selection = self.backup_listbox.curselection()
        if not selection:
            return None
        idx = selection[0]
        if hasattr(self, '_backup_names') and idx < len(self._backup_names):
            return self._backup_names[idx]
        return None

    def restore_save(self):
        """恢复存档"""
        backup_name = self.get_selected_backup()
        if not backup_name:
            messagebox.showwarning("提示", "请先选择一个备份")
            return

        if not self.save_path:
            messagebox.showwarning("提示", "请先检测到存档路径")
            return

        backup_path = os.path.join(self.get_backup_folder(), backup_name)

        if not messagebox.askyesno("确认",
            f"确定要恢复备份 [{backup_name}] 吗？\n\n"
            f"当前存档将被覆盖！\n"
            f"建议先创建一个当前存档的备份。"):
            return

        try:
            # 先备份当前存档
            self.log_msg("📦 备份当前存档...")
            self.root.update()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup_name = f"MHR_Save_{timestamp}_恢复前自动备份"
            current_backup_path = os.path.join(
                self.get_backup_folder(), current_backup_name)
            if os.path.exists(self.save_path):
                shutil.copytree(self.save_path, current_backup_path)

            # 删除当前存档
            if os.path.exists(self.save_path):
                shutil.rmtree(self.save_path)

            # 恢复备份
            self.log_msg(f"🔙 恢复备份: {backup_name}")
            self.root.update()
            shutil.copytree(backup_path, self.save_path)

            # 删除恢复后自动备份的备份信息文件（避免混淆）
            auto_info = os.path.join(self.save_path, "_backup_info.txt")
            if os.path.exists(auto_info):
                # 但保留另一个备份的信息（如果存在）
                pass

            self.log_msg(f"✓ 恢复完成: {backup_name}")
            messagebox.showinfo("成功", f"恢复完成！\n\n{backup_name}\n\n"
                               f"当前存档已自动备份为:\n{current_backup_name}")

            self.refresh_backup_list()

        except Exception as e:
            self.log_msg(f"❌ 恢复失败: {e}")
            messagebox.showerror("错误", f"恢复失败:\n{e}")

    def edit_backup_note(self):
        """编辑备份备注"""
        backup_name = self.get_selected_backup()
        if not backup_name:
            messagebox.showwarning("提示", "请先选择一个备份")
            return

        backup_path = os.path.join(self.get_backup_folder(), backup_name)
        info_file = os.path.join(backup_path, "_backup_info.txt")

        # 读取当前备注
        current_note = ""
        if os.path.exists(info_file):
            try:
                with open(info_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("备注:"):
                            current_note = line.replace("备注:", "").strip()
                            if current_note == "(无)":
                                current_note = ""
                            break
            except Exception:
                pass

        # 弹出编辑对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑备注")
        dialog.geometry("500x320")
        dialog.configure(bg=self.colors['card'])
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        # 居中
        dialog.update_idletasks()
        w, h = 500, 320
        x = (dialog.winfo_screenwidth() - w) // 2
        y = (dialog.winfo_screenheight() - h) // 2
        dialog.geometry(f"{w}x{h}+{x}+{y}")

        # 标题
        tk.Label(dialog, text="编辑备份备注",
                font=('Microsoft YaHei', 14, 'bold'),
                bg=self.colors['card'],
                fg=self.colors['text']).pack(pady=(20, 8))

        # 备份名（可能很长，需要截断显示）
        display_name = backup_name
        if len(display_name) > 50:
            display_name = display_name[:47] + "..."
        tk.Label(dialog, text=display_name,
                font=('Microsoft YaHei', 10),
                bg=self.colors['card'],
                fg=self.colors['text_secondary'],
                wraplength=int(460 * self.scale)).pack(pady=(0, 15))

        # 输入框容器（用于圆角效果）
        entry_container = tk.Frame(dialog, bg='white',
                                   highlightbackground=self.colors['accent'],
                                   highlightthickness=2)
        entry_container.pack(fill='x', padx=40, pady=(0, 15))

        note_var = tk.StringVar(value=current_note)
        note_entry = tk.Entry(entry_container,
                             textvariable=note_var,
                             font=('Microsoft YaHei', 11),
                             bg='white',
                             fg=self.colors['text'],
                             insertbackground=self.colors['accent'],
                             bd=0,
                             highlightthickness=0)
        note_entry.pack(fill='x', padx=8, pady=10)
        note_entry.focus()
        note_entry.select_range(0, tk.END)

        btn_frame = tk.Frame(dialog, bg=self.colors['card'])
        btn_frame.pack(pady=(0, 20))

        def save_note():
            new_note = note_var.get().strip()
            try:
                # 重新写入备份信息文件
                backup_time = ""
                source_path = ""
                with open(info_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("备份时间:"):
                            backup_time = line.strip()
                        elif line.startswith("源路径:"):
                            source_path = line.strip()

                with open(info_file, "w", encoding="utf-8") as f:
                    f.write(backup_time + "\n")
                    f.write(source_path + "\n")
                    f.write(f"备注: {new_note if new_note else '(无)'}\n")

                self.log_msg(f"✓ 备注已更新: {backup_name}")
                self.refresh_backup_list()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"保存失败:\n{e}", parent=dialog)

        btn_save = tk.Button(btn_frame, text="保存",
                            font=('Microsoft YaHei', 11, 'bold'),
                            bg=self.colors['accent'],
                            fg='white',
                            activebackground=self.colors['accent_dark'],
                            activeforeground='white',
                            bd=0, padx=30, pady=10,
                            cursor='hand2',
                            command=save_note)
        btn_save.pack(side='left', padx=(0, 15))

        btn_cancel = tk.Button(btn_frame, text="取消",
                              font=('Microsoft YaHei', 11),
                              bg='white',
                              fg=self.colors['text_secondary'],
                              activebackground=self.colors['sidebar_hover'],
                              bd=1, highlightbackground=self.colors['border_light'],
                              highlightthickness=1,
                              padx=30, pady=10,
                              cursor='hand2',
                              command=dialog.destroy)
        btn_cancel.pack(side='left')

        # 回车保存
        note_entry.bind('<Return>', lambda e: save_note())

    def delete_backup(self):
        """删除备份"""
        backup_name = self.get_selected_backup()
        if not backup_name:
            messagebox.showwarning("提示", "请先选择一个备份")
            return

        if not messagebox.askyesno("确认",
            f"确定要删除备份 [{backup_name}] 吗？\n此操作不可恢复！"):
            return

        try:
            backup_path = os.path.join(self.get_backup_folder(), backup_name)
            shutil.rmtree(backup_path)
            self.log_msg(f"✓ 已删除备份: {backup_name}")
            self.refresh_backup_list()
        except Exception as e:
            self.log_msg(f"❌ 删除失败: {e}")
            messagebox.showerror("错误", f"删除失败:\n{e}")

    def open_backup_folder(self):
        """打开备份文件夹"""
        backup_dir = self.get_backup_folder()
        try:
            if sys.platform == 'win32':
                os.startfile(backup_dir)
            elif sys.platform == 'darwin':
                os.system(f'open "{backup_dir}"')
            else:
                os.system(f'xdg-open "{backup_dir}"')
            self.log_msg(f"✓ 已打开备份文件夹: {backup_dir}")
        except Exception as e:
            self.log_msg(f"⚠️ 打开文件夹失败: {e}")

    # ============================================================
    # 设置页面（含主题颜色）
    # ============================================================
    def create_settings_page(self):
        """创建设置页面 - 包含主题颜色选择"""
        page = tk.Frame(self.main_content, bg=self.colors['bg'])
        page.pack_propagate(False)

        # 标题
        header = tk.Frame(page, bg=self.colors['bg'])
        header.pack(fill='x', padx=30, pady=(25, 0))

        tk.Label(header, text="设置",
                font=('Microsoft YaHei', 24, 'bold'),
                bg=self.colors['bg'],
                fg=self.colors['text']).pack(anchor='w')

        # 内容容器（带滚动条）
        content_outer = tk.Frame(page, bg=self.colors['bg'])
        content_outer.pack(fill='both', expand=True, padx=30, pady=20)

        canvas = tk.Canvas(content_outer, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_outer, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        content = tk.Frame(canvas, bg=self.colors['bg'])
        content_window = canvas.create_window((0, 0), window=content, anchor='nw')

        def update_scrollregion(_event=None):
            canvas.configure(scrollregion=canvas.bbox('all'))

        def resize_content(event=None):
            canvas_width = event.width
            canvas.itemconfig(content_window, width=canvas_width)

        content.bind('<Configure>', update_scrollregion)
        canvas.bind('<Configure>', resize_content)

        # 鼠标滚轮支持
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
            return 'break'

        def bind_mousewheel(widget):
            widget.bind('<MouseWheel>', on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel(child)

        canvas.bind('<MouseWheel>', on_mousewheel)

        # ---------- 主题设置卡片 ----------
        theme_card = tk.Frame(content, bg=self.colors['card'],
                             highlightbackground=self.colors['border_light'],
                             highlightthickness=1)
        theme_card.pack(fill='x', pady=(0, 20))

        theme_inner = tk.Frame(theme_card, bg=self.colors['card'])
        theme_inner.pack(fill='x', padx=20, pady=20)

        tk.Label(theme_inner, text="🎨  主题颜色",
                font=('Microsoft YaHei', 14, 'bold'),
                bg=self.colors['card'],
                fg=self.colors['text']).pack(anchor='w', pady=(0, 12))

        tk.Label(theme_inner, text="选择你喜欢的主题风格，重启程序后生效",
                font=('Microsoft YaHei', 10),
                bg=self.colors['card'],
                fg=self.colors['text_secondary']).pack(anchor='w', pady=(0, 12))

        # 主题选择行
        theme_select_frame = tk.Frame(theme_inner, bg=self.colors['card'])
        theme_select_frame.pack(fill='x', pady=(0, 12))

        tk.Label(theme_select_frame, text="当前主题:",
                font=('Microsoft YaHei', 11),
                bg=self.colors['card'],
                fg=self.colors['text']).pack(side='left', padx=(0, 10))

        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_combo = ttk.Combobox(theme_select_frame,
                                  textvariable=self.theme_var,
                                  state="readonly",
                                  values=list(self.themes.keys()),
                                  width=15,
                                  font=('Microsoft YaHei', 10))
        theme_combo.pack(side='left')

        # 主题预览画布
        preview_frame = tk.Frame(theme_inner, bg=self.colors['card'])
        preview_frame.pack(fill='x', pady=(8, 0))

        self.theme_preview_canvas = tk.Canvas(
            preview_frame, height=60, bg=self.colors['card'],
            highlightthickness=0
        )
        self.theme_preview_canvas.pack(fill='x')

        def draw_theme_preview(*args):
            """绘制主题预览色块"""
            self.theme_preview_canvas.delete("all")
            theme_name = self.theme_var.get()
            if theme_name not in self.themes:
                return
            theme = self.themes[theme_name]
            w = self.theme_preview_canvas.winfo_width()
            if w < 2:
                w = 400
            colors_to_show = [
                ("主背景", theme.get('bg', '#FFF')),
                ("侧边栏", theme.get('sidebar', '#F0F0F0')),
                ("强调色", theme.get('accent', '#1E88E5')),
                ("卡片", theme.get('card', '#FAFAFA')),
                ("文字", theme.get('text', '#212121')),
                ("成功", theme.get('success', '#43A047')),
                ("警告", theme.get('warning', '#FB8C00')),
                ("错误", theme.get('error', '#E53935')),
            ]
            block_w = min(80, (w - 20) // len(colors_to_show))
            gap = 8
            start_x = (w - (block_w * len(colors_to_show) + gap * (len(colors_to_show) - 1))) // 2
            for i, (label, color) in enumerate(colors_to_show):
                x = start_x + i * (block_w + gap)
                # 色块
                self.theme_preview_canvas.create_rectangle(
                    x, 0, x + block_w, 40, fill=color, outline=""
                )
                # 标签
                self.theme_preview_canvas.create_text(
                    x + block_w // 2, 52, text=label,
                    font=('Microsoft YaHei', 8),
                    fill=self.colors['text_secondary']
                )

        # 绑定更新事件
        self.theme_var.trace_add('write', draw_theme_preview)
        self.theme_preview_canvas.bind('<Configure>', draw_theme_preview)

        # 应用主题按钮
        btn_apply_theme = tk.Button(theme_inner, text="保存主题",
                                   font=('Microsoft YaHei', 11, 'bold'),
                                   bg=self.colors['primary_btn'],
                                   fg='white',
                                   activebackground=self.colors['primary_btn_hover'],
                                   activeforeground='white',
                                   bd=0, padx=20, pady=6,
                                   cursor='hand2',
                                   command=self.apply_theme)
        btn_apply_theme.pack(anchor='w')

        # ---------- 通用设置卡片 ----------
        card = tk.Frame(content, bg=self.colors['card'],
                       highlightbackground=self.colors['border_light'],
                       highlightthickness=1)
        card.pack(fill='x')

        card_inner = tk.Frame(card, bg=self.colors['card'])
        card_inner.pack(fill='x', padx=20, pady=20)

        tk.Label(card_inner, text="通用设置",
                font=('Microsoft YaHei', 14, 'bold'),
                bg=self.colors['card'],
                fg=self.colors['text']).pack(anchor='w', pady=(0, 12))

        # 当前缩放信息
        info_text = f"当前系统 DPI 缩放: {int(self.scale * 100)}%"
        tk.Label(card_inner, text=info_text,
                font=('Microsoft YaHei', 11),
                bg=self.colors['card'],
                fg=self.colors['text_secondary']).pack(anchor='w', pady=(0, 16))

        # 手动设置缩放
        scale_frame = tk.Frame(card_inner, bg=self.colors['card'])
        scale_frame.pack(fill='x', pady=(0, 8))

        tk.Label(scale_frame, text="界面缩放:",
                font=('Microsoft YaHei', 11),
                bg=self.colors['card'],
                fg=self.colors['text']).pack(side='left', padx=(0, 10))

        self.scale_var = tk.DoubleVar(value=self.scale)
        scale_combo = ttk.Combobox(scale_frame,
                                  textvariable=self.scale_var,
                                  state="readonly",
                                  values=[1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0],
                                  width=10,
                                  font=('Microsoft YaHei', 10))
        scale_combo.pack(side='left')

        def apply_scale():
            new_scale = self.scale_var.get()
            messagebox.showinfo("提示",
                              f"缩放比例设置为 {int(new_scale * 100)}%\n重启程序后生效。")
            self.scale = new_scale

        tk.Button(scale_frame, text="应用",
                  font=('Microsoft YaHei', 10),
                  bg=self.colors['accent'],
                  fg='white',
                  bd=0, padx=15, pady=4,
                  cursor='hand2',
                  command=apply_scale).pack(side='left', padx=(10, 0))

        # 分隔
        tk.Frame(card_inner, bg=self.colors['border'],
                height=1).pack(fill='x', pady=16)

        tk.Label(card_inner, text="提示：界面缩放、备份、打包等选项\n可在主界面右侧【选项】区域直接设置。",
                font=('Microsoft YaHei', 11),
                bg=self.colors['card'],
                fg=self.colors['text_secondary']).pack(anchor='w')

        # 分隔
        tk.Frame(card_inner, bg=self.colors['border'],
                height=1).pack(fill='x', pady=16)

        # 备份目录设置
        tk.Label(card_inner, text="备份目录",
                font=('Microsoft YaHei', 12, 'bold'),
                bg=self.colors['card'],
                fg=self.colors['text']).pack(anchor='w', pady=(0, 8))

        backup_dir_frame = tk.Frame(card_inner, bg=self.colors['card'])
        backup_dir_frame.pack(fill='x', pady=(0, 8))

        self.backup_dir_var = tk.StringVar()
        default_backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "save_backups")
        self.backup_dir_var.set(default_backup_dir)

        self.lbl_backup_dir = tk.Label(backup_dir_frame,
                                      textvariable=self.backup_dir_var,
                                      font=('Microsoft YaHei', 10),
                                      bg=self.colors['card'],
                                      fg=self.colors['text_secondary'],
                                      wraplength=500,
                                      justify='left')
        self.lbl_backup_dir.pack(side='left', fill='x', expand=True)

        def choose_backup_dir():
            from tkinter import filedialog
            new_dir = filedialog.askdirectory(
                title="选择备份目录",
                initialdir=self.backup_dir_var.get()
            )
            if new_dir:
                self.backup_dir_var.set(new_dir)
                self.log_msg(f"✓ 备份目录已更改: {new_dir}")

        tk.Button(backup_dir_frame, text="浏览...",
                  font=('Microsoft YaHei', 10),
                  bg=self.colors['accent'],
                  fg='white',
                  bd=0, padx=15, pady=4,
                  cursor='hand2',
                  command=choose_backup_dir).pack(side='right', padx=(10, 0))

        tk.Label(card_inner, text="提示：备份目录用于存放存档备份文件",
                font=('Microsoft YaHei', 9),
                bg=self.colors['card'],
                fg=self.colors['text_secondary']).pack(anchor='w')

        # 联系作者卡片
        contact_card = tk.Frame(content, bg=self.colors['card'],
                               highlightbackground=self.colors['border_light'],
                               highlightthickness=1)
        contact_card.pack(fill='x', pady=(20, 0))

        contact_inner = tk.Frame(contact_card, bg=self.colors['card'])
        contact_inner.pack(fill='x', padx=20, pady=20)

        tk.Label(contact_inner, text="联系作者",
                font=('Microsoft YaHei', 14, 'bold'),
                bg=self.colors['card'],
                fg=self.colors['text']).pack(anchor='w', pady=(0, 12))

        # 作者信息
        author_frame = tk.Frame(contact_inner, bg=self.colors['card'])
        author_frame.pack(fill='x', pady=(0, 8))

        tk.Label(author_frame, text="作者：",
                font=('Microsoft YaHei', 11),
                bg=self.colors['card'],
                fg=self.colors['text_secondary']).pack(side='left')

        tk.Label(author_frame, text="鸠十六",
                font=('Microsoft YaHei', 11, 'bold'),
                bg=self.colors['card'],
                fg=self.colors['text']).pack(side='left')

        # 邮箱信息
        email_frame = tk.Frame(contact_inner, bg=self.colors['card'])
        email_frame.pack(fill='x', pady=(0, 8))

        tk.Label(email_frame, text="邮箱：",
                font=('Microsoft YaHei', 11),
                bg=self.colors['card'],
                fg=self.colors['text_secondary']).pack(side='left')

        email_label = tk.Label(email_frame, text="LDi233@qq.com",
                              font=('Microsoft YaHei', 11),
                              bg=self.colors['card'],
                              fg=self.colors['accent'],
                              cursor='hand2')
        email_label.pack(side='left')

        # 点击邮箱复制到剪贴板
        def copy_email(event=None):
            self.root.clipboard_clear()
            self.root.clipboard_append("LDi233@qq.com")
            messagebox.showinfo("提示", "邮箱已复制到剪贴板！")

        email_label.bind('<Button-1>', copy_email)

        # 提示文字
        tk.Label(contact_inner, text="点击邮箱地址可复制",
                font=('Microsoft YaHei', 9),
                bg=self.colors['card'],
                fg=self.colors['text_secondary']).pack(anchor='w')

        # 绑定鼠标滚轮到所有内容子控件
        bind_mousewheel(content)

        # 初始更新滚动区域
        page.after(100, update_scrollregion)

        return page

    def apply_theme(self):
        """应用选中的主题"""
        theme_name = self.theme_var.get()
        if theme_name == self.current_theme:
            messagebox.showinfo("提示", f"当前已经是「{theme_name}」主题")
            return
        if theme_name not in self.themes:
            messagebox.showerror("错误", f"未知主题: {theme_name}")
            return

        if self._save_theme(theme_name):
            self.log_msg(f"✓ 主题已保存: {theme_name}")
            if messagebox.askyesno("重启确认",
                f"主题已保存为「{theme_name}」\n\n需要重启程序才能生效。\n是否立即退出？"):
                self.root.destroy()
        else:
            messagebox.showerror("错误", "保存主题配置失败，请检查文件权限")

    # ============================================================
    # 日志页面
    # ============================================================
    def create_log_page(self):
        """创建日志页面"""
        page = tk.Frame(self.main_content, bg=self.colors['bg'])
        page.pack_propagate(False)

        # 标题
        header = tk.Frame(page, bg=self.colors['bg'])
        header.pack(fill='x', padx=30, pady=(25, 0))

        tk.Label(header, text="操作日志",
                font=('Microsoft YaHei', 24, 'bold'),
                bg=self.colors['bg'],
                fg=self.colors['text']).pack(anchor='w')

        # 日志内容
        content = tk.Frame(page, bg=self.colors['bg'])
        content.pack(fill='both', expand=True, padx=30, pady=20)

        # 日志卡片
        log_card = tk.Frame(content, bg='#1E1E1E',
                           highlightbackground=self.colors['border_light'],
                           highlightthickness=1)
        log_card.pack(fill='both', expand=True)

        log_frame = tk.Frame(log_card, bg='#1E1E1E')
        log_frame.pack(fill='both', expand=True, padx=2, pady=2)

        self.log = tk.Text(log_frame,
                          font=('Consolas', 10),
                          bg='#1E1E1E',
                          fg='#E0E0E0',
                          bd=0,
                          padx=16, pady=12,
                          wrap='word',
                          insertbackground='#E0E0E0')
        self.log.pack(fill='both', expand=True, side='left')

        scrollbar = ttk.Scrollbar(log_frame, orient='vertical',
                                 command=self.log.yview)
        scrollbar.pack(fill='y', side='right')
        self.log.config(yscrollcommand=scrollbar.set)

        return page

    # ============================================================
    # 业务逻辑
    # ============================================================
    def log_msg(self, msg):
        """添加日志消息"""
        self.log.insert('end', f'{msg}\n')
        self.log.see('end')
        self.root.update_idletasks()

    def load_builtin_equipment(self):
        """加载装备数据"""
        self.all_items = []
        for eq_id in sorted(self.equipment_map.keys(),
                           key=lambda x: int(x) if x.isdigit() else x):
            names = sorted(self.equipment_map[eq_id])
            display = " / ".join(names)
            self.all_items.append((eq_id, f"ID {eq_id} - {display}"))

        self.unique_ids = self.all_items
        self.combo_target.config(values=[it[1] for it in self.all_items])
        if self.all_items:
            self.combo_target.current(0)

        self.log_msg(f"✓ 装备数据加载完成: {len(self.all_items)} 套装备")

    def on_search_change(self, *args):
        """搜索装备"""
        search_text = self.search_var.get().lower()
        if not search_text:
            filtered = self.all_items
        else:
            filtered = [(eq_id, display) for eq_id, display in self.all_items
                       if search_text in display.lower()]

        self.unique_ids = filtered
        self.combo_target.config(values=[it[1] for it in filtered])
        if filtered:
            self.combo_target.current(0)

    def browse_mod(self):
        """浏览文件"""
        filetypes = [("所有支持的格式", "*.zip;*.7z;*.rar")]
        if HAVE_ZIP:
            filetypes.append(("ZIP 压缩包", "*.zip"))
        if HAVE_7Z:
            filetypes.append(("7Z 压缩包", "*.7z"))
        if HAVE_RAR:
            filetypes.append(("RAR 压缩包", "*.rar"))
        filetypes.append(("所有文件", "*.*"))

        path = filedialog.askopenfilename(title="选择 mod 文件",
                                         filetypes=filetypes)
        if path:
            self.load_mod(path)
        else:
            path = filedialog.askdirectory(title="选择 mod 文件夹")
            if path:
                self.load_mod(path)

    def on_drop(self, event):
        """处理拖放"""
        raw = event.data.strip()
        paths = re.findall(r"\{([^}]+)\}|([^\s]+)", raw)
        files = [p[0] or p[1] for p in paths if p[0] or p[1]]
        if not files:
            return
        path = files[0]
        if not os.path.exists(path):
            messagebox.showerror("错误", f"无法访问路径:\n{path}")
            return
        self.load_mod(path)

    def load_mod(self, path):
        """加载 mod"""
        # 动态重新检测库可用性
        global HAVE_7Z, HAVE_RAR
        ext = os.path.splitext(path)[1].lower() if os.path.isfile(path) else ""

        if ext == ".7z" and not HAVE_7Z:
            # 尝试重新导入
            try:
                import py7zr
                HAVE_7Z = True
            except ImportError:
                pass

        if ext == ".rar" and not HAVE_RAR:
            try:
                import rarfile
                HAVE_RAR = True
            except ImportError:
                pass

        self.log_msg(f"📂 正在载入: {os.path.basename(path)}")
        self.mod_path = path
        self.is_archive = False
        self.work_path = None
        self.original_archive = path if os.path.isfile(path) else None

        if os.path.isfile(path):
            ext = os.path.splitext(path)[1].lower()
            if ext == ".zip" and HAVE_ZIP:
                self.work_path = self._extract_zip(path)
            elif ext == ".7z" and HAVE_7Z:
                self.work_path = self._extract_7z(path)
            elif ext == ".rar" and HAVE_RAR:
                self.work_path = self._extract_rar(path)
            else:
                # 给出更详细的错误信息
                missing = []
                if not HAVE_7Z:
                    missing.append("py7zr (用于 .7z)")
                if not HAVE_RAR:
                    missing.append("rarfile (用于 .rar)")

                # 尝试自动搜索包位置
                found_paths = []
                for search_path in sys.path:
                    for pkg in ["py7zr", "rarfile"]:
                        if pkg not in [m.split()[0] for m in missing]:
                            continue
                        candidate = os.path.join(search_path, pkg)
                        if os.path.exists(candidate) and pkg in [m.split()[0] for m in missing]:
                            found_paths.append(f"找到 {pkg} 在: {candidate}")

                hint = ""
                if missing:
                    hint = "\n请在命令提示符中运行：\npip install " + " ".join([m.split()[0] for m in missing])
                    if found_paths:
                        hint += "\n\n但发现以下位置存在包:\n" + "\n".join(found_paths)
                        hint += "\n请将这些文件夹添加到脚本开头的 EXTRA_PATHS 列表中"

                messagebox.showerror("错误",
                    f"不支持的压缩格式: {ext}\n"
                    f"请安装对应依赖{hint}")
                self.log_msg(f"❌ 压缩包处理失败: {ext}")
                return
            self.is_archive = True
        else:
            self.work_path = path

        self.lbl_path.config(text=f"📁 {self.work_path}")
        self.status_indicator.itemconfig(self.status_circle,
                                        fill=self.colors['accent'])

        self.scan_bone_files()
        self.scan_model_files()

    def _extract_zip(self, path):
        """解压 zip"""
        extract_to = tempfile.mkdtemp(prefix="mhr_mod_")
        with zipfile.ZipFile(path, "r") as z:
            z.extractall(extract_to)
        self.log_msg(f"✓ 已解压 ZIP")
        return extract_to

    def _extract_7z(self, path):
        """解压 7z"""
        extract_to = tempfile.mkdtemp(prefix="mhr_mod_")
        with py7zr.SevenZipFile(path, "r") as z:
            z.extractall(extract_to)
        self.log_msg(f"✓ 已解压 7Z")
        return extract_to

    def _extract_rar(self, path):
        """解压 rar"""
        extract_to = tempfile.mkdtemp(prefix="mhr_mod_")
        with rarfile.RarFile(path, "r") as r:
            r.extractall(extract_to)
        self.log_msg(f"✓ 已解压 RAR")
        return extract_to

    def identify_part(self, filename):
        """识别部位"""
        name_lower = filename.lower()
        for part, patterns in PART_PATTERNS.items():
            if any(p in name_lower for p in patterns):
                return part
        return None

    def scan_bone_files(self):
        """扫描骨骼文件"""
        self.detected_part_files = {}
        bone_dir = os.path.join(self.work_path, "reframework", "data",
                               "LUABoneSystem", "custom")
        if not os.path.isdir(bone_dir):
            self.lbl_bones.config(text="骨骼文件: 未找到")
            self.log_msg("⚠️ 未找到骨骼文件夹")
            return

        ids = set()
        found = []
        for filename in os.listdir(bone_dir):
            if not filename.lower().endswith(".json"):
                continue
            part = self.identify_part(filename)
            match = re.search(r"(\d+)", filename)
            if not part or not match:
                continue
            eq_id = int(match.group(1))
            filepath = os.path.join(bone_dir, filename)
            self.detected_part_files[part] = filepath
            ids.add(eq_id)
            found.append(f"{part}: {filename}")

        self.lbl_bones.config(
            text=f"骨骼文件: {', '.join(found)}" if found else "无")

        if not ids:
            self.detected_id = None
            self.lbl_equip_name.config(text="")
            self.lbl_detected.config(text="装备编号: --")
            return

        if len(ids) == 1:
            self.detected_id = ids.pop()
        else:
            counts = {}
            for part, fp in self.detected_part_files.items():
                m = re.search(r"(\d+)", os.path.basename(fp))
                if m:
                    counts[int(m.group(1))] = counts.get(int(m.group(1)), 0) + 1
            self.detected_id = max(counts, key=counts.get)
            self.log_msg(f"ℹ️ 检测到多个编号，使用最可能的: {self.detected_id}")

        # 显示装备名称
        equip_names = self.equipment_map.get(str(self.detected_id),
                                            ["未知装备"])
        equip_name = equip_names[0] if equip_names else "未知装备"
        self.lbl_equip_name.config(text=f"{equip_name}")
        self.lbl_detected.config(text=f"装备编号: {self.detected_id}")
        self.log_msg(f"✓ 识别到装备: {equip_name} (ID: {self.detected_id})")
        self.status_indicator.itemconfig(self.status_circle,
                                        fill=self.colors['success'])

    def scan_model_files(self):
        """扫描模型文件"""
        model_root = os.path.join(self.work_path, "natives", "STM",
                                 "player", "mod")
        if os.path.isdir(model_root):
            count = 0
            for root, dirs, files in os.walk(model_root):
                for d in dirs:
                    if self.detected_id and str(self.detected_id) in d:
                        count += 1
                if count > 20:
                    break
            self.log_msg(f"✓ 发现 {count} 个相关模型目录")
        else:
            self.log_msg("ℹ️ 未找到模型根目录")

    def get_target_id(self):
        """获取目标ID"""
        sel = self.combo_target.current()
        if sel < 0 or sel >= len(self.unique_ids):
            return None
        return self.unique_ids[sel][0]

    def preview_changes(self):
        """预览修改"""
        if not self.work_path:
            messagebox.showwarning("提示", "请先导入 mod")
            return
        if self.detected_id is None:
            messagebox.showwarning("提示", "未能识别到原装备编号")
            return
        target_id = self.get_target_id()
        if target_id is None:
            messagebox.showwarning("提示", "请选择目标套装")
            return

        changes = self._collect_changes(target_id)
        if not changes:
            messagebox.showinfo("预览", "找不到需要重命名的文件")
            return

        preview = "\n".join(f"{old}\n  → {new}\n" for old, new in changes[:30])
        if len(changes) > 30:
            preview += f"\n... 还有 {len(changes)-30} 项未显示 ..."

        messagebox.showinfo("修改预览",
                           f"共 {len(changes)} 处修改:\n\n{preview}")
        self.log_msg(
            f"👁 预览: {self.detected_id} → {target_id} ({len(changes)} 处)")

    def _collect_changes(self, target_id):
        """收集变更"""
        old_id = str(self.detected_id)
        new_id = str(target_id)
        changes = []

        for part, filepath in self.detected_part_files.items():
            old_name = os.path.basename(filepath)
            new_name = re.sub(rf"(?<!\d){old_id}(?!\d)", new_id, old_name)
            if new_name != old_name:
                changes.append(
                    (filepath, os.path.join(os.path.dirname(filepath), new_name)))

        for root, dirs, files in os.walk(self.work_path, topdown=False):
            for name in files + dirs:
                full_old = os.path.join(root, name)
                if re.search(rf"(?<!\d){old_id}(?!\d)", full_old):
                    new_name = re.sub(rf"(?<!\d){old_id}(?!\d)", new_id, name)
                    full_new = os.path.join(root, new_name)
                    if full_new != full_old:
                        changes.append((full_old, full_new))
        return changes

    def apply_changes(self):
        """应用修改"""
        if not self.work_path:
            messagebox.showwarning("提示", "请先导入 mod")
            return
        if self.detected_id is None:
            messagebox.showwarning("提示", "未能识别到原装备编号")
            return
        target_id = self.get_target_id()
        if target_id is None:
            messagebox.showwarning("提示", "请选择目标套装")
            return

        changes = self._collect_changes(target_id)
        if not changes:
            messagebox.showinfo("提示", "没有需要修改的文件")
            return

        if not messagebox.askyesno("确认",
            f"将把编号 {self.detected_id} 替换为 {target_id}\n"
            f"共 {len(changes)} 个文件/文件夹\n\n是否继续？"):
            return

        if self.backup_var.get():
            try:
                if self.is_archive and self.original_archive:
                    backup_path = self.original_archive + ".backup"
                    shutil.copy2(self.original_archive, backup_path)
                    self.log_msg(f"✓ 已备份原压缩包")
                else:
                    backup_path = self.work_path + "_backup"
                    if os.path.exists(backup_path):
                        shutil.rmtree(backup_path)
                    shutil.copytree(self.work_path, backup_path)
                    self.log_msg(f"✓ 已备份 mod 文件夹")
            except Exception as e:
                self.log_msg(f"⚠️ 备份失败: {e}")
                if not messagebox.askyesno("警告", "备份失败，是否继续修改？"):
                    return

        success = 0
        failed = []
        for old, new in changes:
            try:
                os.rename(old, new)
                success += 1
                self.log_msg(
                    f"✓ {os.path.basename(old)} → {os.path.basename(new)}")
            except Exception as e:
                failed.append((old, str(e)))
                self.log_msg(f"❌ 失败: {os.path.basename(old)}")

        if failed:
            messagebox.showwarning("完成",
                                  f"完成！\n成功: {success}\n失败: {len(failed)}")
        else:
            messagebox.showinfo("完成", f"修改完成！\n成功: {success}")

        self.scan_bone_files()
        self.scan_model_files()

        if self.is_archive and self.repack_var.get():
            self._repack_archive()

        # 应用后打开输出文件夹
        if self.open_folder_var.get():
            self.open_output_folder()

    def _repack_archive(self):
        """重新打包"""
        if not self.work_path:
            return
        base, _ = os.path.splitext(self.original_archive) if self.original_archive else (self.work_path, "")
        try:
            shutil.make_archive(base + "_modified", "zip", self.work_path)
            self.log_msg(f"✓ 已生成修改后的压缩包")
            messagebox.showinfo("打包完成", "已生成修改后的压缩包")
        except Exception as e:
            self.log_msg(f"❌ 重新打包失败: {e}")

    def open_output_folder(self):
        """打开输出文件夹"""
        try:
            if self.is_archive and self.original_archive:
                # 压缩包：打开原文件所在目录
                target_dir = os.path.dirname(self.original_archive)
            else:
                # 文件夹：打开工作目录
                target_dir = self.work_path

            if target_dir and os.path.isdir(target_dir):
                if sys.platform == 'win32':
                    os.startfile(target_dir)
                elif sys.platform == 'darwin':
                    os.system(f'open "{target_dir}"')
                else:
                    os.system(f'xdg-open "{target_dir}"')
                self.log_msg(f"✓ 已打开输出文件夹: {target_dir}")
        except Exception as e:
            self.log_msg(f"⚠️ 打开文件夹失败: {e}")
        except Exception as e:
            self.log_msg(f"❌ 重新打包失败: {e}")

    def cleanup_temp(self):
        """清理临时文件"""
        if self.is_archive and self.work_path and os.path.isdir(self.work_path):
            try:
                shutil.rmtree(self.work_path)
            except Exception:
                pass

    def get_dpi_scale(self):
        """获取系统 DPI 缩放比例"""
        if sys.platform != 'win32':
            return 1.0

        try:
            # 获取主屏幕的 DC
            hdc = ctypes.windll.user32.GetDC(0)
            # 获取 DPI
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
            ctypes.windll.user32.ReleaseDC(0, hdc)
            # 96 DPI 是 100% 缩放
            scale = dpi / 96.0
            # 限制缩放范围
            return max(1.0, min(scale, 3.0))
        except Exception:
            return 1.0

    def apply_dpi_scale(self):
        """对所有子组件应用 DPI 缩放"""
        # 缩放 tk 默认字体
        try:
            default_font = font.nametofont("TkDefaultFont")
            default_font.configure(size=int(10 * self.scale))
            text_font = font.nametofont("TkTextFont")
            text_font.configure(size=int(10 * self.scale))
        except Exception:
            pass

    def setup_ttk_style(self):
        """设置 ttk 样式以适应 DPI"""
        style = ttk.Style()
        style.configure("TCombobox", font=('Microsoft YaHei', 10))
        style.configure("TButton", font=('Microsoft YaHei', 10))
        style.configure("TScrollbar", arrowsize=13)

        # 设置下拉列表的样式
        self.root.option_add("*TCombobox*Listbox.font",
                           ('Microsoft YaHei', 10))


def main():
    try:
        if HAVE_DND:
            root = TkinterDnD.Tk()
        else:
            root = tk.Tk()
        app = PCL2ModTool(root)
        root.mainloop()
    except Exception as e:
        import traceback
        error_msg = f"程序出错:\n{str(e)}\n\n详细错误:\n{traceback.format_exc()}"
        print(error_msg)
        try:
            messagebox.showerror("错误", error_msg)
        except:
            pass
        input("\n按回车键退出...")
    finally:
        try:
            app.cleanup_temp()
        except:
            pass


if __name__ == "__main__":
    main()
