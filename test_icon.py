#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图标生成
"""

import os
import sys

print("Python version:", sys.version)
print("Current directory:", os.getcwd())

try:
    from PIL import Image, ImageDraw
    print("Pillow imported successfully")
except ImportError as e:
    print("Error importing Pillow:", e)
    print("Installing...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Pillow'])
    from PIL import Image, ImageDraw
    print("Pillow installed and imported")

# 创建简单图标
size = 256
img = Image.new('RGB', (size, size), (41, 128, 185))
draw = ImageDraw.Draw(img)

# 绘制简单图形
draw.rectangle([50, 50, 206, 206], fill=(255, 255, 255))

# 保存
output = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_icon.ico')
img.save(output, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

if os.path.exists(output):
    print(f"Icon created: {output}")
    print(f"Size: {os.path.getsize(output)} bytes")
else:
    print("Failed to create icon!")
