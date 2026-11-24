# -*- coding: utf-8 -*-
"""六角大楼 v5: 现代白色高层大楼
设计原则 (像真楼):
- 高瘦比例: 10 层 x 3m + 4.5m 大堂 = 34.5m 高, 六边形宽 12m
- 每层整条玻璃窗带 (ribbon window) + 白色窗间墙, 现代办公楼样式
- 细白色竖框 (mullion) 分隔玻璃
- 6 个角白色角柱, 俯瞰清晰六边形
- 底层大堂玻璃幕墙 + 雨棚
- 楼顶: 女儿墙 + 机房 + 天线 + 6 角各 2 挺机枪
"""
import numpy as np
import trimesh
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from meshlib import Builder, rot_z, rot_x, rot_y
from trimesh.creation import box, cylinder

OUT = r"D:\01-ai-game\丧尸围城\assets\models\HQ_HexBuilding.glb"

WHITE   = (245, 245, 242, 255)   # 白色外墙
WHITE_D = (222, 222, 218, 255)   # 白墙阴影
GLASS   = (38, 62, 92, 255)      # 玻璃 (深蓝灰)
GLASS_L = (255, 205, 110, 255)   # 亮灯
MG_DARK = (40, 45, 50, 255)
MG_STEEL= (105, 115, 125, 255)

b = Builder()

R = 8.0                          # 六边形顶点半径 (面宽 = 8m, 整体做大)
F = R * np.cos(np.radians(30))   # 面到中心距离 6.93
BASE_H = 4.0                     # 大堂层高
FLOORS = 3                       # 3 层楼
FH = 3.5
H = BASE_H + FLOORS * FH         # 14.5m (约 3 层楼高)

# ============ 1. 主体: 白色六边形大楼 ============
b.hex_prism(R, H, WHITE, pos=[0, H/2, 0], rough=0.7)

# 六条角柱 (顶点处, 白色, 强化六边形轮廓)
for i in range(6):
    a = np.radians(i * 60)
    dx, dz = np.cos(a), np.sin(a)
    b.cyl(0.5, H, WHITE_D, pos=[dx * (R - 0.15), H/2, dz * (R - 0.15)], rough=0.7)

# ============ 2. 每层整条玻璃窗带 (6 面 x 10 层) ============
GLASS_H = 2.0
for f in range(FLOORS):
    y = BASE_H + f * FH + FH * 0.55
    for i in range(6):
        th = np.radians(i * 60 + 30)
        fx, fz = np.cos(th), np.sin(th)
        tx, tz = -np.sin(th), np.cos(th)
        # 薄边 (Z) 转到墙面法线方向: 绕 Y 轴
        rz = rot_y(90 - (i * 60 + 30))
        # 整条玻璃带 (面宽 7.2m)
        b.add(box(extents=[7.2, GLASS_H, 0.18]), GLASS,
              pos=[fx * (F + 0.06), y, fz * (F + 0.06)], rot=rz, rough=0.25)
        # 亮灯段 (每层随机 1-2 段亮)
        if (f + i) % 3 == 0:
            off = 2.4 if (f + i) % 2 == 0 else -2.4
            b.add(box(extents=[2.0, GLASS_H - 0.1, 0.2]), GLASS_L,
                  pos=[fx * (F + 0.08) + tx * off, y, fz * (F + 0.08) + tz * off],
                  rot=rz, emissive=(255, 200, 100, 255), rough=0.3)
        # 白色竖框 mullion (5 根)
        for off in [-3.6, -1.8, 0, 1.8, 3.6]:
            b.add(box(extents=[0.16, GLASS_H + 0.15, 0.22]), WHITE,
                  pos=[fx * (F + 0.1) + tx * off, y, fz * (F + 0.1) + tz * off],
                  rot=rz, rough=0.7)

# ============ 3. 底层大堂 (加高, 玻璃幕墙 + 雨棚) ============
b.hex_prism(R + 0.35, BASE_H, WHITE_D, pos=[0, BASE_H/2, 0], rough=0.75)
# 大堂玻璃幕墙 (正面整条)
b.add(box(extents=[7.0, 3.0, 0.2]), GLASS,
      pos=[0, 1.6, F + 0.35], rough=0.25)
# 门框竖框
for mx in [-3.5, -1.2, 1.2, 3.5]:
    b.add(box(extents=[0.2, 3.0, 0.26]), WHITE, pos=[mx, 1.6, F + 0.4], rough=0.7)
# 雨棚
b.add(box(extents=[7.4, 0.15, 2.2]), WHITE, pos=[0, 3.3, F + 1.4], rough=0.7)
# 雨棚支柱
for px in [-3.2, 3.2]:
    b.cyl(0.14, 3.3, MG_STEEL, pos=[px, 1.65, F + 2.3], metallic=0.5, rough=0.5)
# 台阶
for s in range(3):
    b.add(box(extents=[6.6 - s * 0.5, 0.22, 1.4 - s * 0.35]), WHITE_D,
          pos=[0, 0.11 + s * 0.22, F + 1.5 - s * 0.35], rough=0.85)

# ============ 4. 楼顶 ============
top_y = H
# 女儿墙 (白色矮墙)
b.add(cylinder(radius=R + 0.15, height=0.9, sections=6), WHITE,
      pos=[0, top_y + 0.45, 0], rough=0.7)
b.add(cylinder(radius=R - 0.15, height=0.92, sections=6), (228, 228, 224, 255),
      pos=[0, top_y + 0.45, 0], rough=0.8)
# 中央机房 (白色, 收进)
b.add(box(extents=[4.0, 2.2, 4.0]), WHITE, pos=[0, top_y + 1.1, 0], rough=0.7)
b.add(box(extents=[4.4, 0.15, 4.4]), WHITE_D, pos=[0, top_y + 2.25, 0], rough=0.8)
# 机房窗
for side in [0, 90, 180, 270]:
    a = np.radians(side)
    b.add(box(extents=[2.4, 0.8, 0.12]), GLASS,
          pos=[np.cos(a) * 2.02, top_y + 1.3, np.sin(a) * 2.02],
          rot=rot_y(90 - side), rough=0.25)
# 天线
b.cyl(0.08, 3.0, MG_STEEL, pos=[0, top_y + 3.7, 0], metallic=0.5, rough=0.5)
b.sphere(0.14, (200, 50, 40, 255), pos=[0, top_y + 5.2, 0],
         emissive=(180, 40, 30, 255), rough=0.4)

# ---- 6 角各 2 挺机枪 (共 12 挺) ----
def add_mg(x, z, aim_deg, y):
    a = np.radians(aim_deg)
    dx, dz = np.cos(a), np.sin(a)
    # 枪身长轴/枪管 (+Z) 指向 aim 方向: 绕 Y 轴
    rz = rot_y(90 - aim_deg)
    b.cyl(0.3, 0.22, MG_DARK, pos=[x, y + 0.11, z], metallic=0.4, rough=0.6)
    b.add(box(extents=[0.5, 0.4, 0.7]), MG_STEEL,
          pos=[x, y + 0.42, z], rot=rz, metallic=0.5, rough=0.45)
    for side in [-0.13, 0.13]:
        tx, tz = -np.sin(a), np.cos(a)
        sx, sz = x + tx * side, z + tz * side
        barrel = cylinder(radius=0.06, height=1.1, sections=10)
        barrel.apply_transform(rot_x(90))
        b.add(barrel, MG_DARK, pos=[sx + dx * 0.6, y + 0.5, sz + dz * 0.6],
              rot=rz, metallic=0.5, rough=0.4)
    b.add(box(extents=[0.7, 0.32, 0.08]), MG_STEEL,
          pos=[x + dx * 0.4, y + 0.45, z + dz * 0.4],
          rot=rz, metallic=0.5, rough=0.45)

for i in range(6):
    a = np.radians(i * 60)
    dx, dz = np.cos(a), np.sin(a)
    cx, cz = dx * (R - 0.7), dz * (R - 0.7)
    y = top_y + 0.9
    add_mg(cx - dz * 0.6, cz + dx * 0.6, i * 60 + 30, y)
    add_mg(cx + dz * 0.6, cz - dx * 0.6, i * 60 - 30 + 360, y)

b.export(OUT)
print("hex building v5 done")
