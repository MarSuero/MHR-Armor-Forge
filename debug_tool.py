#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试版本 - 用于找出闪退原因
"""

import sys
import traceback

try:
    import os
    import re
    import shutil
    import tempfile
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    print("✓ 基础导入成功")
except Exception as e:
    print(f"✗ 基础导入失败: {e}")
    traceback.print_exc()
    input("按回车键退出...")
    sys.exit(1)

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAVE_DND = True
    print("✓ tkinterdnd2 导入成功")
except ImportError:
    HAVE_DND = False
    print("✗ tkinterdnd2 未安装")

try:
    import zipfile
    HAVE_ZIP = True
    print("✓ zipfile 导入成功")
except ImportError:
    HAVE_ZIP = False

try:
    import py7zr
    HAVE_7Z = True
    print("✓ py7zr 导入成功")
except ImportError:
    HAVE_7Z = False

try:
    import rarfile
    HAVE_RAR = True
    print("✓ rarfile 导入成功")
except ImportError:
    HAVE_RAR = False

print("\n正在创建窗口...")

try:
    if HAVE_DND:
        root = TkinterDnD.Tk()
        print("✓ TkinterDnD.Tk() 创建成功")
    else:
        root = tk.Tk()
        print("✓ tk.Tk() 创建成功")

    root.title("调试窗口")
    root.geometry("400x300")

    # 测试基本组件
    frame = tk.Frame(root, bg="#0F172A")
    frame.pack(fill='both', expand=True)
    print("✓ Frame 创建成功")

    label = tk.Label(frame, text="调试成功！", fg="white", bg="#0F172A")
    label.pack(pady=20)
    print("✓ Label 创建成功")

    btn = tk.Button(frame, text="点击测试", command=lambda: print("按钮点击"))
    btn.pack(pady=10)
    print("✓ Button 创建成功")

    print("\n✓ 所有组件创建成功，窗口应该正常显示")
    print("如果窗口闪退，请检查：")
    print("1. 显卡驱动是否最新")
    print("2. 是否有其他程序占用显示资源")
    print("3. 系统主题设置是否正常")

    root.mainloop()

except Exception as e:
    print(f"\n✗ 错误: {e}")
    traceback.print_exc()
    input("按回车键退出...")
