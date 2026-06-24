#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel装备数据嵌入脚本

使用方法：
1. 将此脚本和Excel装备对照表放在 MHR_Armor_Bone_Renamer.py 同目录下
2. 运行: python embed_excel_data.py
3. 脚本会自动读取Excel中的装备数据并嵌入到主程序中
"""

import json
import os
import re

try:
    import openpyxl
except ImportError:
    print("请先安装 openpyxl：pip install openpyxl")
    raise

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
main_script = os.path.join(script_dir, "MHR_Armor_Bone_Renamer.py")

# 查找同目录下的Excel文件
excel_files = [f for f in os.listdir(script_dir) if f.endswith(".xlsx") or f.endswith(".xls")]

if not excel_files:
    print("错误：未找到Excel文件！")
    print("请将Excel装备对照表放在此脚本同目录下，然后重新运行。")
    exit(1)

# 使用找到的第一个Excel文件
excel_path = os.path.join(script_dir, excel_files[0])
print(f"正在读取Excel文件: {excel_files[0]}")

# 读取Excel数据
wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
ws = wb.active

data = {}
rows = list(ws.iter_rows(values_only=True))

# 判断是否有标题行
start = 0
if rows and len(rows[0]) >= 4:
    first_d = str(rows[0][3]).replace("﻿", "").strip()
    if not first_d.isdigit():
        start = 1
        print("检测到标题行，已跳过")

# 读取数据
for i, row in enumerate(rows[start:], start=start):
    if len(row) < 4:
        continue

    name = str(row[2]).strip() if row[2] is not None else ""
    eq_id = str(row[3]).replace("﻿", "").strip() if row[3] is not None else ""

    if not name or not eq_id:
        continue

    # 只保留纯数字编号
    if re.fullmatch(r"\d+", eq_id):
        data.setdefault(eq_id, []).append(name)

print(f"成功读取 {len(data)} 个装备编号")

# 生成EQUIPMENT_TABLE代码
json_text = json.dumps(data, ensure_ascii=False, indent=4)
new_block = f"EQUIPMENT_TABLE = {json_text}\n"

# 读取主脚本
with open(main_script, "r", encoding="utf-8") as f:
    content = f.read()

# 替换EQUIPMENT_TABLE定义
pattern = r"^EQUIPMENT_TABLE = \{.*?^\}"
content = re.sub(pattern, new_block.strip(), content, flags=re.MULTILINE | re.DOTALL)

# 写回主脚本
with open(main_script, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n成功！装备数据已嵌入到 {main_script}")
print(f"共内置 {len(data)} 个装备编号")
print("\n现在可以直接运行 MHR_Armor_Bone_Renamer.py，无需再依赖Excel文件。")
