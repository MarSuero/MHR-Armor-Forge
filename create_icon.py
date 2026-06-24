#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 MHR Mod Tool 的图标
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # 创建大图标 (256x256)
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 背景渐变 - 蓝色系
    for y in range(size):
        r = int(41 + (25 - 41) * y / size)
        g = int(128 + (118 - 128) * y / size)
        b = int(185 + (210 - 185) * y / size)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # 绘制圆角矩形背景
    corner_radius = 40
    draw.rounded_rectangle(
        [10, 10, size-10, size-10],
        radius=corner_radius,
        fill=(41, 128, 185, 230)
    )

    # 绘制内部高光
    draw.rounded_rectangle(
        [15, 15, size-15, size//2],
        radius=corner_radius-5,
        fill=(52, 152, 219, 100)
    )

    # 绘制剑/武器图标
    sword_color = (255, 255, 255, 240)

    # 剑刃
    blade_points = [
        (size//2, 40),      # 剑尖
        (size//2 + 20, 100), # 右侧
        (size//2 + 10, 100), # 右侧内
        (size//2 + 10, 180), # 右侧下
        (size//2 - 10, 180), # 左侧下
        (size//2 - 10, 100), # 左侧内
        (size//2 - 20, 100), # 左侧
    ]
    draw.polygon(blade_points, fill=sword_color)

    # 剑柄
    draw.rectangle(
        [size//2 - 15, 180, size//2 + 15, 200],
        fill=(189, 195, 199, 255)
    )

    # 护手
    draw.rectangle(
        [size//2 - 30, 195, size//2 + 30, 210],
        fill=(241, 196, 15, 255)
    )

    # 保存多尺寸 ICO
    icon_sizes = [16, 32, 48, 64, 128, 256]
    icons = []

    for icon_size in icon_sizes:
        resized = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        icons.append(resized)

    # 保存为 ICO 文件
    output_path = os.path.join(os.path.dirname(__file__), 'app_icon.ico')
    icons[0].save(
        output_path,
        format='ICO',
        sizes=[(s, s) for s in icon_sizes],
        append_images=icons[1:]
    )

    print(f"图标已生成: {output_path}")
    return output_path

if __name__ == '__main__':
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("正在安装 Pillow...")
        import subprocess
        subprocess.run(['pip', 'install', 'Pillow'], check=True)
        from PIL import Image, ImageDraw

    create_icon()
    print("完成！")
