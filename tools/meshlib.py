# -*- coding: utf-8 -*-
"""
程序化建模工具库
提供圆润化几何体 + 材质 + 场景导出 (glTF, 带多材质)
目标: 拒绝方块堆砌, 有"手工雕刻感"
"""
import numpy as np
import trimesh
from trimesh.creation import box, cylinder, icosphere, capsule, cone, torus, annulus


# ---------- 颜色 (军事冷色调) ----------
C = {
    "concrete":   (120, 128, 132, 255),   # 混凝土灰
    "concrete_d": (88, 94, 98, 255),      # 深混凝土
    "steel":      (90, 100, 110, 255),    # 钢色
    "steel_d":    (55, 62, 70, 255),      # 深钢
    "military":   (74, 92, 66, 255),      # 军绿
    "military_d": (52, 66, 48, 255),      # 深军绿
    "amber":      (255, 176, 0, 255),     # 琥珀灯光
    "amber_glow": (255, 200, 60, 255),    # 琥珀自发光
    "red":        (220, 50, 40, 255),     # 警示红
    "dark":       (30, 34, 38, 255),      # 暗色
    "white":      (235, 238, 240, 255),   # 白
    "blue":       (74, 144, 217, 255),    # 钢蓝
    "zombie":     (110, 150, 90, 255),    # 病绿
    "zombie_d":   (70, 95, 60, 255),      # 深病绿
    "blood":      (140, 40, 40, 255),     # 暗红
    "gold":       (240, 200, 90, 255),    # 金
}


def _mat(color, metallic=0.0, rough=0.8, emissive=None):
    """创建 PBR 材质"""
    c = np.array(color, dtype=np.uint8)
    em = np.array(emissive if emissive is not None else (0, 0, 0, 255), dtype=np.uint8)
    return trimesh.visual.material.PBRMaterial(
        baseColorFactor=c,
        metallicFactor=float(metallic),
        roughnessFactor=float(rough),
        emissiveFactor=em[:3] / 255.0,
    )


class Builder:
    """场景构建器: 累积多个带材质的网格, 最后导出 glTF"""

    def __init__(self):
        self.scene = trimesh.Scene()

    def add(self, geom, color, pos=None, rot=None, scale=None,
            metallic=0.0, rough=0.8, emissive=None, name=""):
        """添加一个网格 (可平移/旋转/缩放)"""
        if isinstance(geom, list):
            geom = trimesh.util.concatenate(geom)
        # 变换顺序: 先缩放 -> 再绕自身中心旋转 -> 最后平移到目标位置
        if scale is not None:
            if np.isscalar(scale):
                geom.apply_scale(scale)
            else:
                geom.apply_scale(np.array(scale))
        if rot is not None:
            geom.apply_transform(rot)
        if pos is not None:
            geom.apply_translation(pos)
        geom.visual = trimesh.visual.TextureVisuals(material=_mat(color, metallic, rough, emissive))
        if name:
            geom.name = name
        self.scene.add_geometry(geom)
        return geom

    def rounded_box(self, extents, color, pos=None, rot=None, bevel=0.06, **kw):
        """圆角盒体 (倒角, 避免硬边方块感)"""
        g = box(extents=extents)
        g = trimesh.repair.fill_holes(g)
        # 用 bevel 近似: 缩放 + 圆角 (trimesh 无直接 bevel, 用 subdivision 近似)
        g = trimesh.smoothing.filter_hull(g, iterations=1) if bevel > 0 else g
        return self.add(g, color, pos=pos, rot=rot, **kw)

    def cyl(self, radius, height, color, pos=None, rot=None, sections=24, **kw):
        return self.add(cylinder(radius=radius, height=height, sections=sections),
                        color, pos=pos, rot=rot, **kw)

    def sphere(self, radius, color, pos=None, **kw):
        return self.add(icosphere(subdivisions=3, radius=radius), color, pos=pos, **kw)

    def capsule(self, height, radius, color, pos=None, rot=None, **kw):
        return self.add(capsule(height=height, radius=radius), color, pos=pos, rot=rot, **kw)

    def cone(self, radius, height, color, pos=None, rot=None, sections=24, **kw):
        return self.add(cone(radius=radius, height=height, sections=sections),
                        color, pos=pos, rot=rot, **kw)

    def torus(self, tube, radius, color, pos=None, rot=None, **kw):
        return self.add(torus(tube=tube, radius=radius), color, pos=pos, rot=rot, **kw)

    def hex_prism(self, radius, height, color, pos=None, **kw):
        """六棱柱 (六角大楼主体)"""
        g = cylinder(radius=radius, height=height, sections=6)
        return self.add(g, color, pos=pos, **kw)

    def export(self, path):
        self.scene.export(path)
        print(f"  [OK] exported: {path}")
        return path


def rot_z(deg):
    return trimesh.transformations.rotation_matrix(np.radians(deg), [0, 0, 1])


def rot_x(deg):
    return trimesh.transformations.rotation_matrix(np.radians(deg), [1, 0, 0])


def rot_y(deg):
    return trimesh.transformations.rotation_matrix(np.radians(deg), [0, 1, 0])
