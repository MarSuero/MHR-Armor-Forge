#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复制 py7zr / rarfile / tkinterdnd2 到目标 Python 的 site-packages
"""

import os
import shutil
import sys

# 已安装的库路径（D 盘的 Python）
SOURCE_BASE = r"D:\lib\site-packages"

# 目标 Python 的 site-packages
TARGET_BASE = r"C:\Users\MarSuero\AppData\Local\Programs\Python\Python314\Lib\site-packages"

# 需要复制的包
PACKAGES = ["py7zr", "rarfile", "tkinterdnd2", "tkinterdnd2-0.5.0.dist-info"]

def copy_package(name):
    src = os.path.join(SOURCE_BASE, name)
    dst = os.path.join(TARGET_BASE, name)

    if not os.path.exists(src):
        print(f"✗ 源不存在: {src}")
        return False

    if os.path.exists(dst):
        print(f"⊙ 已存在: {dst}")
        return True

    try:
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        print(f"✓ 已复制: {name}")
        return True
    except Exception as e:
        print(f"✗ 复制失败 {name}: {e}")
        return False

def main():
    print(f"源路径: {SOURCE_BASE}")
    print(f"目标路径: {TARGET_BASE}")
    print()

    if not os.path.isdir(SOURCE_BASE):
        print(f"错误: 源路径不存在 {SOURCE_BASE}")
        return

    if not os.path.isdir(TARGET_BASE):
        print(f"错误: 目标路径不存在 {TARGET_BASE}")
        return

    # 确保目标目录存在
    os.makedirs(TARGET_BASE, exist_ok=True)

    # 列出源目录内容用于调试
    print("源目录下的包:")
    for item in sorted(os.listdir(SOURCE_BASE)):
        if item.lower().startswith(("py7zr", "rarfile", "tkinterdnd2")):
            print(f"  - {item}")
    print()

    success = 0
    for pkg in PACKAGES:
        if copy_package(pkg):
            success += 1

    # 尝试列出所有相关包
    print()
    print("尝试复制所有相关包...")
    for item in os.listdir(SOURCE_BASE):
        item_lower = item.lower()
        if any(kw in item_lower for kw in ["py7zr", "rarfile", "tkinterdnd2"]):
            if copy_package(item):
                success += 1

    print()
    print(f"完成: {success} 个包")

    # 验证
    print()
    print("验证导入...")
    test_target = TARGET_BASE
    print(f"请在新窗口运行: C:\\Users\\MarSuero\\AppData\\Local\\Programs\\Python\\Python314\\python.exe -c \"import py7zr; print('OK')\"")

if __name__ == "__main__":
    main()
    input("\n按回车退出...")