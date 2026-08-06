# -*- coding: utf-8 -*-
"""
虚拟小猫 · Kivy 版入口(Android 可打包)
运行:python main.py(桌面预览) / buildozer android debug(打包 APK)
"""
import os
import sys

os.environ.setdefault("KIVY_NO_ARGS", "1")

# Android 上 Kivy 默认字体(Roboto)不含中文字符,所有中文会显示为方块。
# 打包 simhei.ttf 并设为全局默认字体(桌面无此文件时自动回退系统字体)。
_FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "simhei.ttf")
if os.path.exists(_FONT_PATH):
    from kivy.core.text import LabelBase
    from kivy.config import Config
    LabelBase.register(name="Roboto", fn_regular=_FONT_PATH)  # 覆盖默认字体
    try:
        LabelBase.register(name="RobotoMono", fn_regular=_FONT_PATH)  # 顺带覆盖等宽
    except Exception:
        pass

import config as C
from game import Game, MAX_MICE, draw_cat, draw_kitten, draw_mouse, kid_label, sex_name

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from kivy.utils import get_color_from_hex


def hx(h):
    """16 进制颜色 → kivy (r,g,b,a)"""
    return get_color_from_hex(h)



# ==================== 绘制辅助(Kivy canvas) ====================
def ell(c, cx, cy, rx, ry, color, H=None, outline=None, ow=1.5):
    """以 (cx,cy) 为中心画椭圆。"""
    x, y = cx - rx, (H or 0) - (cy + ry) if H else cy - ry
    c.add(Color(*color))
    c.add(Ellipse(pos=(x, y), size=(2 * rx, 2 * ry)))
    if outline:
        c.add(Color(*outline))
        c.add(Line(ellipse=(x, y, 2 * rx, 2 * ry), width=ow))


def poly(c, pts, color):
    c.add(Color(*color))
    c.add(Line(points=pts, close=True))


def line(c, pts, color, width=2):
    c.add(Color(*color))
    c.add(Line(points=pts, width=width))


def draw_mouse(c, m, H):
    """老鼠:带轮廓线+耳朵+眼睛+胡须+尾巴(移植桌面版绘制)"""
    e = hx("#d9c9b8") if not m.gold else hx("#f0c75e")
    ec = hx("#c4b09a") if not m.gold else hx("#c9a23d")
    # 身体+头
    ell(c, m.x, m.y, 16, 10, e, H=H, outline=ec, ow=1.5)
    ell(c, m.x + 16, m.y - 2, 8, 7, e, H=H, outline=ec, ow=1.5)
    # 耳朵(圆形)
    ell(c, m.x - 10, m.y - 6, 4, 5, e, H=H, outline=ec, ow=1.2)
    ell(c, m.x + 2, m.y - 8, 4, 5, e, H=H, outline=ec, ow=1.2)
    ell(c, m.x - 10, m.y - 6, 2, 3, hx("#f4a8c0"), H=H)
    ell(c, m.x + 2, m.y - 8, 2, 3, hx("#f4a8c0"), H=H)
    # 眼睛
    ell(c, m.x - 6, m.y - 2, 1.8, 2.2, hx(C.DARK), H=H)
    ell(c, m.x + 5, m.y - 2, 1.8, 2.2, hx(C.DARK), H=H)
    # 鼻子
    ell(c, m.x + 11, m.y - 1, 2.5, 2, hx("#e8837a"), H=H)
    # 胡须
    line(c, [m.x + 8, m.y - 5, m.x + 16, m.y - 7], ec, 1)
    line(c, [m.x + 8, m.y + 1, m.x + 16, m.y + 2], ec, 1)
    # 尾巴(弯曲)
    line(c, [m.x - 16, m.y - 1, m.x - 24, m.y + 6, m.x - 22, m.y + 13], ec, 2)


def draw_tail(c, cx, cy, s, H=None):
    """猫尾巴:摇摆动画(移植桌面版)"""
    import time as _t
    a = _t.time() * 3.2
    sw = 14 * s
    pts = [cx + 71 * s, (H or 0) - (cy + 116 * s),
           cx + 115 * s, (H or 0) - (cy + 100 * s + sw * 0.3),
           cx + 123 * s, (H or 0) - (cy + 64 * s + sw),
           cx + 95 * s, (H or 0) - (cy + 38 * s + sw * 1.3)]
    c.add(Color(*hx(C.CAT_WHITE_D)))
    c.add(Line(points=pts, width=13 * s))


def draw_cat(c, cx, cy, s, gender, preg=0.0, H=None, equipped=None):
    """猫:完整移植桌面版(轮廓线+内耳+腮红+胡须+蝴蝶结+尾巴)"""
    fur = hx(C.CAT_MALE) if gender == "male" else hx(C.CAT_WHITE)
    fur_d = hx(C.CAT_WHITE_D)
    belly = hx(C.BELLY)
    # 尾巴(摆动)
    draw_tail(c, cx, cy, s, H=H)
    # 阴影
    ell(c, cx, cy + 158 * s, 80 * s, 8 * s, hx("#000000"), H=H)
    # 身体(带轮廓线)
    bw = (66 + 55 * min(1.0, preg / 100.0)) if preg > C.PREG_BELLY_SHOW else 65
    ell(c, cx, cy + 108 * s, bw * s, 44 * s, fur, H=H, outline=fur_d, ow=2)
    ell(c, cx, cy + 120 * s, (bw - 20) * s, 32 * s, belly, H=H)
    # 腿
    ell(c, cx - 28 * s, cy + 138 * s, 14 * s, 16 * s, fur, H=H, outline=fur_d, ow=2)
    ell(c, cx + 28 * s, cy + 138 * s, 14 * s, 16 * s, fur, H=H, outline=fur_d, ow=2)
    # 头(带轮廓线)
    ell(c, cx, cy, 62 * s, 62 * s, fur, H=H, outline=fur_d, ow=2)
    # 头顶毛发
    poly(c, [cx - 8 * s, (H or 0) - (cy - 58 * s), cx + 2 * s, (H or 0) - (cy - 80 * s),
             cx + 12 * s, (H or 0) - (cy - 58 * s)], fur_d)
    # 耳朵(外+内)
    poly(c, [cx - 57 * s, (H or 0) - (cy - 32 * s), cx - 77 * s, (H or 0) - (cy - 104 * s),
             cx - 13 * s, (H or 0) - (cy - 62 * s)], fur)
    poly(c, [cx - 53 * s, (H or 0) - (cy - 40 * s), cx - 65 * s, (H or 0) - (cy - 88 * s),
             cx - 25 * s, (H or 0) - (cy - 62 * s)], hx(C.INNER))
    poly(c, [cx + 57 * s, (H or 0) - (cy - 32 * s), cx + 77 * s, (H or 0) - (cy - 104 * s),
             cx + 13 * s, (H or 0) - (cy - 62 * s)], fur)
    poly(c, [cx + 53 * s, (H or 0) - (cy - 40 * s), cx + 65 * s, (H or 0) - (cy - 88 * s),
             cx + 25 * s, (H or 0) - (cy - 62 * s)], hx(C.INNER))
    # 眼睛(带高光,眨眼动画)
    import time as _tm
    _t_now = _tm.time()
    _blink = (_t_now % 3.5) < 0.18  # 每 3.5 秒眨眼 0.18 秒
    for dx in (-1, 1):
        ex = cx + dx * 23 * s
        if _blink:
            # 眨眼:闭眼(一条弧线)
            line(c, [ex - 9 * s, (H or 0) - (cy + 2 * s), ex + 9 * s, (H or 0) - (cy + 2 * s)], hx(C.DARK), 2.5)
        else:
            ell(c, ex, cy + 2 * s, 9 * s, 9 * s, hx(C.DARK), H=H)
            ell(c, ex - 3 * s, cy - 1 * s, 2.5 * s, 2.5 * s, hx("#ffffff"), H=H)
    # 鼻子
    poly(c, [cx - 6 * s, (H or 0) - (cy + 22 * s), cx + 6 * s, (H or 0) - (cy + 22 * s),
             cx, (H or 0) - (cy + 31 * s)], hx(C.NOSE))
    # 嘴(微笑弧线)
    line(c, [cx - 12 * s, (H or 0) - (cy + 26 * s), cx - 6 * s, (H or 0) - (cy + 33 * s),
             cx, (H or 0) - (cy + 26 * s)], hx(C.DARK), 2)
    line(c, [cx + 12 * s, (H or 0) - (cy + 26 * s), cx + 6 * s, (H or 0) - (cy + 33 * s),
             cx, (H or 0) - (cy + 26 * s)], hx(C.DARK), 2)
    # 腮红
    ell(c, cx - 38 * s, cy + 30 * s, 9 * s, 8 * s, hx(C.BLUSH), H=H)
    ell(c, cx + 38 * s, cy + 30 * s, 9 * s, 8 * s, hx(C.BLUSH), H=H)
    # 胡须
    for dx, y1, y2 in ((-1, 16, 8), (-1, 26, 26), (-1, 36, 44), (1, 16, 8), (1, 26, 26), (1, 36, 44)):
        line(c, [cx + 38 * dx * s, (H or 0) - (cy + y1 * s),
                 cx + 92 * dx * s, (H or 0) - (cy + y2 * s)], hx("#c99b6a"), 1.8)
    # 性别标记:公猫=蓝领结,母猫=蝴蝶结(带轮廓)
    if gender == "male":
        bx, by = cx, cy + 46 * s
        poly(c, [bx - 16 * s, (H or 0) - (by - 10 * s), bx, (H or 0) - (by + 8 * s),
                 bx + 16 * s, (H or 0) - (by - 10 * s)], hx("#5b93d0"))
        ell(c, bx, by, 4 * s, 4 * s, hx("#4a7dc0"), H=H)
    else:
        bx, by = cx - 58 * s, cy - 24 * s
        ell(c, bx - 15 * s, by - 12 * s, 9 * s, 11 * s, hx(C.BOW_PINK), H=H, outline=hx("#e889a9"), ow=1.5)
        ell(c, bx + 3 * s, by - 14 * s, 9 * s, 11 * s, hx(C.BOW_BLUE), H=H, outline=hx("#e889a9"), ow=1.5)
        ell(c, bx - 7 * s, by - 7 * s, 7 * s, 7 * s, hx("#e889a9"), H=H)
        line(c, [bx, by + 6 * s, bx - 3 * s, by + 18 * s], hx(C.BOW_PINK), 2)
        line(c, [bx + 2 * s, by + 6 * s, bx + 5 * s, by + 17 * s], hx(C.BOW_BLUE), 2)
    # ===== 服装穿搭渲染(移植桌面版 redraw_cloth 核心)=====
    if equipped:
        _redraw_cloth_kv(c, cx, cy, s, equipped, gender, H)


def _redraw_cloth_kv(c, cx, cy, s, equipped, gender, H):
    """按 equipped {category: id} 绘制服装(通用形状,带至臻金色皮肤)。"""
    top_id = equipped.get("top")
    bottom_id = equipped.get("bottom")
    hat_id = equipped.get("hat")
    acc_id = equipped.get("acc")
    premium = any(t in C.PREMIUM_IDS for t in (top_id, bottom_id, hat_id, acc_id))
    # 至臻皮肤:身体+头 金色描边/光晕
    if premium:
        ell(c, cx, cy + 108 * s, 72 * s, 50 * s, hx("#fff3d6"), H=H, outline=hx("#f0c75e"), ow=2.5)
        ell(c, cx, cy, 68 * s, 68 * s, hx("#fff3d6"), H=H, outline=hx("#f0c75e"), ow=2.5)
    # 上衣(top)
    if top_id:
        if top_id == "dress_pink":
            ell(c, cx, cy + 98 * s, 44 * s, 30 * s, hx("#f4a8c0"), H=H, outline=hx("#e08aa6"), ow=1.5)
            poly(c, [cx - 38 * s, (H or 0) - (cy + 132 * s), cx - 28 * s, (H or 0) - (cy + 104 * s),
                     cx + 28 * s, (H or 0) - (cy + 104 * s), cx + 38 * s, (H or 0) - (cy + 132 * s)], hx("#ef8fb2"))
        elif top_id == "dress_white":
            ell(c, cx, cy + 98 * s, 44 * s, 30 * s, hx("#f7f0ea"), H=H, outline=hx("#d8cfc6"), ow=1.5)
            poly(c, [cx - 38 * s, (H or 0) - (cy + 132 * s), cx - 28 * s, (H or 0) - (cy + 104 * s),
                     cx + 28 * s, (H or 0) - (cy + 104 * s), cx + 38 * s, (H or 0) - (cy + 132 * s)], hx("#efe6dd"))
        elif top_id == "dungaree_blue":
            ell(c, cx, cy + 98 * s, 42 * s, 28 * s, hx("#3f6fb0"), H=H)
            line(c, [cx - 22 * s, (H or 0) - (cy + 76 * s), cx - 30 * s, (H or 0) - (cy + 108 * s)], hx("#3f6fb0"), 5)
            line(c, [cx + 22 * s, (H or 0) - (cy + 76 * s), cx + 30 * s, (H or 0) - (cy + 108 * s)], hx("#3f6fb0"), 5)
        elif top_id == "apron_yellow":
            ell(c, cx, cy + 98 * s, 42 * s, 28 * s, hx("#f7d774"), H=H)
            line(c, [cx - 22 * s, (H or 0) - (cy + 76 * s), cx - 30 * s, (H or 0) - (cy + 108 * s)], hx("#e8c850"), 4)
            line(c, [cx + 22 * s, (H or 0) - (cy + 76 * s), cx + 30 * s, (H or 0) - (cy + 108 * s)], hx("#e8c850"), 4)
        elif top_id == "hoodie_purple":
            ell(c, cx, cy + 98 * s, 44 * s, 30 * s, hx("#9a7bc8"), H=H, outline=hx("#7d5fa8"), ow=1.5)
            ell(c, cx, cy + 112 * s, 10 * s, 8 * s, hx("#ffffff"), H=H)
        elif top_id == "sailor_red":
            ell(c, cx, cy + 98 * s, 44 * s, 30 * s, hx("#d84a4a"), H=H, outline=hx("#b03a3a"), ow=1.5)
            ell(c, cx, cy + 90 * s, 30 * s, 16 * s, hx("#ffffff"), H=H)
        elif top_id == "dino_green":
            ell(c, cx, cy + 98 * s, 46 * s, 32 * s, hx("#6bbf59"), H=H, outline=hx("#4a9a3a"), ow=1.5)
            for dx in (-1, 0, 1):
                poly(c, [cx + dx * 22 * s, (H or 0) - (cy + 84 * s), cx + dx * 22 * s - 8 * s,
                         (H or 0) - (cy + 68 * s), cx + dx * 22 * s + 8 * s, (H or 0) - (cy + 68 * s)], hx("#4a9a3a"))
        else:  # 其他上衣:通用色块
            ell(c, cx, cy + 98 * s, 42 * s, 28 * s, hx("#f4a8c0"), H=H, outline=hx("#e08aa6"), ow=1.5)
    # 下装(bottom)
    if bottom_id:
        if bottom_id == "jeans_blue":
            ell(c, cx - 20 * s, cy + 140 * s, 16 * s, 18 * s, hx("#4a7dc0"), H=H)
            ell(c, cx + 20 * s, cy + 140 * s, 16 * s, 18 * s, hx("#4a7dc0"), H=H)
        elif bottom_id == "shorts_black":
            ell(c, cx - 20 * s, cy + 138 * s, 15 * s, 14 * s, hx("#3a3a3a"), H=H)
            ell(c, cx + 20 * s, cy + 138 * s, 15 * s, 14 * s, hx("#3a3a3a"), H=H)
        elif bottom_id == "pants_khaki":
            ell(c, cx - 20 * s, cy + 140 * s, 16 * s, 20 * s, hx("#c9b98a"), H=H)
            ell(c, cx + 20 * s, cy + 140 * s, 16 * s, 20 * s, hx("#c9b98a"), H=H)
        else:
            ell(c, cx - 20 * s, cy + 140 * s, 15 * s, 16 * s, hx("#b09e88"), H=H)
            ell(c, cx + 20 * s, cy + 140 * s, 15 * s, 16 * s, hx("#b09e88"), H=H)
    # 帽子(hat)
    if hat_id:
        if hat_id == "cap":
            ell(c, cx, cy - 40 * s, 34 * s, 14 * s, hx("#d84a4a"), H=H)
            ell(c, cx, cy - 54 * s, 26 * s, 20 * s, hx("#e86a6a"), H=H)
        elif hat_id == "beret":
            ell(c, cx, cy - 48 * s, 32 * s, 18 * s, hx("#9a7bc8"), H=H, outline=hx("#7d5fa8"), ow=1.5)
        elif hat_id == "sunhat":
            ell(c, cx, cy - 44 * s, 40 * s, 12 * s, hx("#f7d774"), H=H)
            ell(c, cx, cy - 56 * s, 22 * s, 18 * s, hx("#f9e39a"), H=H)
        else:
            ell(c, cx, cy - 48 * s, 30 * s, 16 * s, hx("#e8837a"), H=H)
    # 配饰(acc)
    if acc_id:
        if acc_id == "crown":
            poly(c, [cx - 20 * s, (H or 0) - (cy - 62 * s), cx - 20 * s, (H or 0) - (cy - 82 * s),
                     cx - 10 * s, (H or 0) - (cy - 72 * s), cx, (H or 0) - (cy - 88 * s),
                     cx + 10 * s, (H or 0) - (cy - 72 * s), cx + 20 * s, (H or 0) - (cy - 82 * s),
                     cx + 20 * s, (H or 0) - (cy - 62 * s)], hx("#f0c75e"))
        elif acc_id == "pearl":
            ell(c, cx - 30 * s, cy - 6 * s, 4 * s, 4 * s, hx("#ffffff"), H=H)
            ell(c, cx - 20 * s, cy - 8 * s, 4 * s, 4 * s, hx("#ffffff"), H=H)
            ell(c, cx - 10 * s, cy - 6 * s, 4 * s, 4 * s, hx("#ffffff"), H=H)
        elif acc_id == "bell":
            ell(c, cx, cy + 52 * s, 7 * s, 9 * s, hx("#f0c75e"), H=H, outline=hx("#c9a23d"), ow=1)
        else:
            ell(c, cx - 24 * s, cy + 44 * s, 6 * s, 6 * s, hx("#e8837a"), H=H)
            ell(c, cx + 24 * s, cy + 44 * s, 6 * s, 6 * s, hx("#e8837a"), H=H)


def draw_kitten(c, cx, cy, s, k, H=None):
    fur = hx(C.CAT_WHITE)
    sex = k["sex"]
    if k["stage"] == "swaddle":
        ell(c, cx, cy + 100 * s, 46 * s, 48 * s, hx("#fdf6ec"), H=H)
        ell(c, cx, cy + 102 * s, 34 * s, 40 * s, hx("#f7e9d8"), H=H)
        cap = hx("#f4a8c0") if sex == C.SEX_F else hx("#7fb3e8")
        ell(c, cx, cy - 8 * s, 30 * s, 22 * s, hx("#fdf6ec"), outline=cap, ow=3, H=H)
        ell(c, cx, cy - 50 * s, 12 * s, 10 * s, cap, H=H)
        ell(c, cx, cy + 31 * s, 5 * s, 5 * s, hx("#ffffff"), H=H)
        ell(c, cx, cy + 39 * s, 9 * s, 5 * s, hx("#f7c8d8"), H=H)
        if sex == C.SEX_M:
            bx, by = cx, cy + 78 * s
            poly(c, [bx - 12 * s, (H or 0) - (by - 8 * s), bx, (H or 0) - (by + 6 * s),
                     bx + 12 * s, (H or 0) - (by - 8 * s)], hx("#5b93d0"))
            ell(c, bx, by, 3 * s, 3 * s, hx("#4a7dc0"), H=H)
        else:
            bx, by = cx - 22 * s, cy + 78 * s
            ell(c, bx - 4 * s, by, 6 * s, 7 * s, hx(C.BOW_PINK), H=H)
            ell(c, bx + 4 * s, by - 1 * s, 6 * s, 7 * s, hx(C.BOW_BLUE), H=H)
    else:
        bw = (66 + 50 * min(1.0, k.get("preg", 0) / 100.0)) if (k["sex"] == C.SEX_F and k.get("preg", 0) > C.PREG_BELLY_SHOW) else 65
        fur_d = hx(C.CAT_WHITE_D)
        ell(c, cx, cy + 108 * s, bw * s, 44 * s, fur, H=H, outline=fur_d, ow=1.5)
        if k["stage"] == "school":
            ell(c, cx, cy + 90 * s, 46 * s, 30 * s, hx("#4a6ea8"), H=H)
            poly(c, [cx - 12 * s, (H or 0) - (cy + 66 * s), cx + 12 * s, (H or 0) - (cy + 66 * s),
                     cx, (H or 0) - (cy + 104 * s)], hx("#d84a4a"))
        ell(c, cx, cy, 62 * s, 62 * s, fur, H=H, outline=fur_d, ow=1.5)
        if sex == C.SEX_M:
            bx, by = cx, cy + 40 * s
            poly(c, [bx - 13 * s, (H or 0) - (by - 8 * s), bx, (H or 0) - (by + 6 * s),
                     bx + 13 * s, (H or 0) - (by - 8 * s)], hx("#5b93d0"))
            ell(c, bx, by, 3 * s, 3 * s, hx("#4a7dc0"), H=H)
        else:
            bx, by = cx - 58 * s, cy - 24 * s
            ell(c, bx - 6 * s, by - 1 * s, 8 * s, 10 * s, hx(C.BOW_PINK), H=H)
            ell(c, bx + 6 * s, by - 2 * s, 8 * s, 10 * s, hx(C.BOW_BLUE), H=H)
        # 眼睛(带高光)+ 鼻子 + 微笑嘴
        ell(c, cx - 23 * s, cy + 2 * s, 9 * s, 9 * s, hx(C.DARK), H=H)
        ell(c, cx + 23 * s, cy + 2 * s, 9 * s, 9 * s, hx(C.DARK), H=H)
        ell(c, cx - 23 * s, cy - 1 * s, 2.5 * s, 2.5 * s, hx("#ffffff"), H=H)
        ell(c, cx + 23 * s, cy - 1 * s, 2.5 * s, 2.5 * s, hx("#ffffff"), H=H)
        poly(c, [cx - 6 * s, (H or 0) - (cy + 22 * s), cx + 6 * s, (H or 0) - (cy + 22 * s),
                 cx, (H or 0) - (cy + 31 * s)], hx(C.NOSE))
        line(c, [cx - 11 * s, (H or 0) - (cy + 26 * s), cx - 5 * s, (H or 0) - (cy + 32 * s),
                 cx, (H or 0) - (cy + 26 * s)], hx(C.DARK), 1.5)
        line(c, [cx + 11 * s, (H or 0) - (cy + 26 * s), cx + 5 * s, (H or 0) - (cy + 32 * s),
                 cx, (H or 0) - (cy + 26 * s)], hx(C.DARK), 1.5)
        # 腮红
        ell(c, cx - 34 * s, cy + 28 * s, 6 * s, 5 * s, hx(C.BLUSH), H=H)
        ell(c, cx + 34 * s, cy + 28 * s, 6 * s, 5 * s, hx(C.BLUSH), H=H)




BTN = {"size_hint_y": None, "height": dp(36), "background_normal": "",
       "background_color": hx("#f5a25d"), "color": hx("#5a4632"),
       "font_size": sp(11), "bold": True}
DIS = {"size_hint_y": None, "height": dp(36), "background_normal": "",
       "background_color": hx("#e8dfd0"), "color": hx("#b09e88"),
       "font_size": sp(11), "bold": True}


def mkbtn(text, on, **kw):
    b = Button(text=text, **BTN)
    b.bind(on_release=on)
    for k, v in kw.items():
        setattr(b, k, v)
    return b


# ==================== 场景家具绘制(Kivy 移植桌面版 _draw_item) ====================
_FUR_ANCHOR_KV = {
    "sofa": (0.16, 0.68), "chair": (0.06, 0.74), "table": (0.56, 0.72),
    "desk": (0.80, 0.62), "bed": (0.34, 0.58), "crib": (0.64, 0.64),
    "rug": (0.35, 0.84), "plant": (0.045, 0.58), "bookshelf": (0.93, 0.30),
    "lamp": (0.75, 0.46), "painting": (0.68, 0.15),
    "phone": (0.525, 0.32), "tablet": (0.575, 0.30), "computer": (0.78, 0.60),
    "tv": (0.885, 0.54), "fridge": (0.95, 0.60), "washer": (0.91, 0.66),
    "ac": (0.48, 0.09), "robot": (0.70, 0.86),
    "birdcage": (0.11, 0.44), "fishbowl": (0.945, 0.70),
    "baby_table_1": (0.18, 0.80), "baby_table_2": (0.50, 0.80), "baby_table_3": (0.82, 0.80),
}


def _scene_pos_kv(w, h, key):
    fx, fy = _FUR_ANCHOR_KV.get(key, (0.5, 0.5))
    return w * fx, h * (1.0 - fy)  # Kivy y 从底部算,翻转桌面锚点


def _draw_item_kv(c, w, h, item_id):
    """按锚点绘制单个家具/科技/装饰(Kivy 版)。"""
    x, y = _scene_pos_kv(w, h, item_id)
    u = min(w, h) / 350.0  # 参考单位(用较小边,避免大屏过度拉伸)
    if item_id == "sofa":
        c.add(Color(*hx("#e8837a")))
        c.add(Rectangle(pos=(x - 60 * u, y + 30 * u), size=(120 * u, 60 * u)))
        c.add(Color(*hx("#d06a58")))
        c.add(Rectangle(pos=(x - 60 * u, y + 30 * u), size=(15 * u, 60 * u)))
        c.add(Rectangle(pos=(x + 45 * u, y + 30 * u), size=(15 * u, 60 * u)))
        c.add(Color(*hx("#f0957b")))
        c.add(Rectangle(pos=(x - 55 * u, y + 42 * u), size=(110 * u, 14 * u)))
    elif item_id == "chair":
        c.add(Color(*hx("#85b7eb")))
        c.add(Rectangle(pos=(x - 28 * u, y + 24 * u), size=(56 * u, 52 * u)))
        c.add(Color(*hx("#a3c8f0")))
        c.add(Rectangle(pos=(x - 28 * u, y + 32 * u), size=(56 * u, 12 * u)))
    elif item_id == "table":
        c.add(Color(*hx(C.WOOD)))
        c.add(Rectangle(pos=(x - 55 * u, y + 12 * u), size=(110 * u, 8 * u)))
        c.add(Color(*hx(C.WOOD_D)))
        c.add(Rectangle(pos=(x - 40 * u, y + 4 * u), size=(8 * u, 30 * u)))
        c.add(Rectangle(pos=(x + 32 * u, y + 4 * u), size=(8 * u, 30 * u)))
    elif item_id == "desk":
        c.add(Color(*hx("#a5714f")))
        c.add(Rectangle(pos=(x - 50 * u, y + 10 * u), size=(100 * u, 8 * u)))
        c.add(Color(*hx("#83583c")))
        c.add(Rectangle(pos=(x - 44 * u, y + 2 * u), size=(8 * u, 24 * u)))
        c.add(Rectangle(pos=(x + 36 * u, y + 2 * u), size=(8 * u, 24 * u)))
    elif item_id == "bed":
        c.add(Color(*hx("#a3c8f0")))
        c.add(Rectangle(pos=(x - 70 * u, y + 20 * u), size=(140 * u, 54 * u)))
        c.add(Color(*hx("#ffffff")))
        c.add(Rectangle(pos=(x - 64 * u, y + 12 * u), size=(128 * u, 38 * u)))
        c.add(Color(*hx("#ffffff")))
        c.add(Ellipse(pos=(x - 30 * u, y + 24 * u), size=(24 * u, 16 * u)))
    elif item_id == "crib":
        c.add(Color(*hx("#e8d5b8")))
        c.add(Rectangle(pos=(x - 50 * u, y + 26 * u), size=(100 * u, 48 * u)))
        c.add(Color(*hx("#fff6ec")))
        c.add(Rectangle(pos=(x - 44 * u, y + 20 * u), size=(88 * u, 34 * u)))
        c.add(Color(*hx("#b8a07a")))
        c.add(Rectangle(pos=(x - 48 * u, y + 22 * u), size=(6 * u, 18 * u)))
        c.add(Rectangle(pos=(x + 42 * u, y + 22 * u), size=(6 * u, 18 * u)))
    elif item_id == "rug":
        c.add(Color(*hx("#f7c1c1")))
        c.add(Ellipse(pos=(x - 70 * u, y + 20 * u), size=(140 * u, 40 * u)))
        c.add(Color(*hx("#fbeaf0")))
        c.add(Ellipse(pos=(x - 45 * u, y + 12 * u), size=(90 * u, 24 * u)))
    elif item_id == "plant":
        c.add(Color(*hx("#c9714f")))
        c.add(Rectangle(pos=(x - 10 * u, y + 8 * u), size=(20 * u, 18 * u)))
        c.add(Color(*hx("#97c459")))
        c.add(Ellipse(pos=(x - 18 * u, y + 4 * u), size=(36 * u, 20 * u)))
    elif item_id == "bookshelf":
        c.add(Color(*hx("#c9a06a")))
        c.add(Rectangle(pos=(x - 26 * u, y + 34 * u), size=(52 * u, 68 * u)))
        c.add(Color(*hx("#9a7a4a")))
        for i in range(4):
            c.add(Line(points=[x - 26 * u, y + 34 * u + (i + 1) * 17 * u,
                               x + 26 * u, y + 34 * u + (i + 1) * 17 * u], width=2))
        colors = ["#e8837a", "#85b7eb", "#f0c75e"]
        for i in range(6):
            c.add(Color(*hx(colors[i % 3])))
            c.add(Rectangle(pos=(x - 20 * u + (i % 3) * 14 * u, y + 30 * u + (i // 3) * 30 * u),
                            size=(10 * u, 14 * u)))
    elif item_id == "lamp":
        c.add(Color(*hx("#9a7a4a")))
        c.add(Rectangle(pos=(x - 4 * u, y + 6 * u), size=(8 * u, 36 * u)))
        c.add(Color(*hx("#f0c75e")))
        c.add(Ellipse(pos=(x - 16 * u, y + 26 * u), size=(32 * u, 28 * u)))
    elif item_id == "painting":
        c.add(Color(*hx("#efe3cf")))
        c.add(Rectangle(pos=(x - 35 * u, y + 25 * u), size=(70 * u, 50 * u)))
        c.add(Color(*hx("#e8837a")))
        c.add(Line(points=[x - 25 * u, y + 13 * u, x - 3 * u, y + 7 * u], width=3))
        c.add(Color(*hx("#7bc47f")))
        c.add(Line(points=[x - 3 * u, y + 7 * u, x + 23 * u, y + 11 * u], width=3))
    elif item_id == "phone":
        c.add(Color(*hx("#e8837a")))
        c.add(Rectangle(pos=(x - 10 * u, y + 20 * u), size=(20 * u, 38 * u)))
        c.add(Color(*hx("#ffffff")))
        c.add(Rectangle(pos=(x - 7 * u, y + 17 * u), size=(14 * u, 22 * u)))
    elif item_id == "tablet":
        c.add(Color(*hx("#85b7eb")))
        c.add(Rectangle(pos=(x - 14 * u, y + 22 * u), size=(28 * u, 36 * u)))
        c.add(Color(*hx("#ffffff")))
        c.add(Rectangle(pos=(x - 11 * u, y + 19 * u), size=(22 * u, 26 * u)))
    elif item_id == "computer":
        c.add(Color(*hx("#5b5b5b")))
        c.add(Rectangle(pos=(x - 20 * u, y + 22 * u), size=(40 * u, 30 * u)))
        c.add(Color(*hx("#85b7eb")))
        c.add(Rectangle(pos=(x - 18 * u, y + 20 * u), size=(36 * u, 26 * u)))
        c.add(Color(*hx("#5b5b5b")))
        c.add(Rectangle(pos=(x - 22 * u, y + 8 * u), size=(44 * u, 6 * u)))
    elif item_id == "tv":
        c.add(Color(*hx("#4a4a4a")))
        c.add(Rectangle(pos=(x - 30 * u, y + 24 * u), size=(60 * u, 40 * u)))
        c.add(Color(*hx("#85b7eb")))
        c.add(Rectangle(pos=(x - 27 * u, y + 21 * u), size=(54 * u, 34 * u)))
        c.add(Color(*hx("#4a4a4a")))
        c.add(Rectangle(pos=(x - 12 * u, y + 16 * u), size=(24 * u, 6 * u)))
    elif item_id == "fridge":
        c.add(Color(*hx("#d8e8f5")))
        c.add(Rectangle(pos=(x - 25 * u, y + 35 * u), size=(50 * u, 70 * u)))
        c.add(Color(*hx("#b8d4ea")))
        c.add(Rectangle(pos=(x - 25 * u, y + 35 * u), size=(50 * u, 6 * u)))
        c.add(Color(*hx("#b8d4ea")))
        c.add(Rectangle(pos=(x - 25 * u, y + 2 * u), size=(50 * u, 6 * u)))
    elif item_id == "washer":
        c.add(Color(*hx("#e8e8e8")))
        c.add(Rectangle(pos=(x - 25 * u, y + 30 * u), size=(50 * u, 60 * u)))
        c.add(Color(*hx("#85b7eb")))
        c.add(Ellipse(pos=(x - 12 * u, y + 16 * u), size=(24 * u, 24 * u)))
    elif item_id == "ac":
        c.add(Color(*hx("#e8e8e8")))
        c.add(Rectangle(pos=(x - 40 * u, y + 18 * u), size=(80 * u, 30 * u)))
        c.add(Color(*hx("#c8c8c8")))
        c.add(Line(points=[x - 35 * u, y + 12 * u, x + 35 * u, y + 12 * u], width=2))
        c.add(Line(points=[x - 35 * u, y + 4 * u, x + 35 * u, y + 4 * u], width=2))
    elif item_id == "robot":
        c.add(Color(*hx("#c8c8c8")))
        c.add(Rectangle(pos=(x - 18 * u, y + 25 * u), size=(36 * u, 40 * u)))
        c.add(Color(*hx("#85b7eb")))
        c.add(Ellipse(pos=(x - 12 * u, y + 12 * u), size=(24 * u, 16 * u)))
        c.add(Color(*hx("#c8c8c8")))
        c.add(Rectangle(pos=(x - 14 * u, y + 15 * u), size=(28 * u, 8 * u)))
        c.add(Color(*hx("#c8c8c8")))
        c.add(Rectangle(pos=(x - 18 * u, y + 35 * u), size=(36 * u, 8 * u)))
    elif item_id == "birdcage":
        c.add(Color(*hx("#d8c8a8")))
        c.add(Rectangle(pos=(x - 22 * u, y + 30 * u), size=(44 * u, 40 * u)))
        c.add(Color(*hx("#b8a07a")))
        c.add(Line(points=[x - 22 * u, y + 30 * u, x + 22 * u, y + 30 * u], width=2))
        c.add(Line(points=[x - 22 * u, y + 30 * u, x - 22 * u, y + 10 * u], width=1))
        c.add(Line(points=[x + 22 * u, y + 30 * u, x + 22 * u, y + 10 * u], width=1))
        c.add(Line(points=[x - 22 * u, y + 10 * u, x + 22 * u, y + 10 * u], width=1))
        c.add(Color(*hx("#f0c75e")))
        c.add(Ellipse(pos=(x - 6 * u, y + 16 * u), size=(12 * u, 14 * u)))
    elif item_id == "fishbowl":
        c.add(Color(*hx("#cfe8f5")))
        c.add(Ellipse(pos=(x - 22 * u, y + 16 * u), size=(44 * u, 34 * u)))
        c.add(Color(*hx("#b8d4ea")))
        c.add(Line(points=[x - 14 * u, y + 16 * u, x - 14 * u, y + 22 * u], width=2))
        c.add(Line(points=[x + 14 * u, y + 16 * u, x + 14 * u, y + 22 * u], width=2))
    elif item_id == "baby_table_1" or item_id == "baby_table_2" or item_id == "baby_table_3":
        c.add(Color(*hx(C.WOOD)))
        c.add(Rectangle(pos=(x - 20 * u, y + 12 * u), size=(40 * u, 8 * u)))
        c.add(Color(*hx(C.WOOD_D)))
        c.add(Rectangle(pos=(x - 16 * u, y + 4 * u), size=(6 * u, 18 * u)))
        c.add(Rectangle(pos=(x + 10 * u, y + 4 * u), size=(6 * u, 18 * u)))


class CatCanvas(Widget):
    def __init__(self, game, **kw):
        super().__init__(**kw)
        self.game = game
        self._need_redraw = True
        self._marks = []
        self._marks_l = None
        # 画布有一个明显的米色背景(防止空白区显示 Kivy 黑色默认背景)
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle as R
            Color(*hx("#fdf3e4"))
            self._bg_rect = R(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            self.game.tx = touch.x
            self.game.ty = touch.y
            return True
        return super().on_touch_move(touch)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.game.tx = touch.x
            self.game.ty = touch.y
            return True
        return super().on_touch_down(touch)

    def draw(self):
        g = self.game
        W, H = self.width, self.height
        if W < 50:
            self._marks = []
            return
        C.CW, C.CH = W, H
        C.GROUND_Y = H - 60
        c = self.canvas
        try:
            c.clear()
            s = C.CAT_SCALE
            # ===== 完整场景绘制(Kivy 坐标:y=0 在底部,向上增长)=====
            ground = 60  # 地板在底部 60px
            # 墙面(占满除底部地板外区域)
            c.add(Color(*hx(C.WALL)))
            c.add(Rectangle(pos=(0, ground), size=(W, H - ground)))
            # 地板(底部 60px,带木纹线)
            c.add(Color(*hx(C.FLOOR)))
            c.add(Rectangle(pos=(0, 0), size=(W, ground)))
            for i in range(0, int(W), 90):
                c.add(Color(*hx(C.FLOOR_LINE)))
                c.add(Line(points=[i, 0, i, ground], width=1))
            # 踢脚线
            c.add(Color(*hx("#d9c3a3")))
            c.add(Rectangle(pos=(0, ground - 8), size=(W, 8)))
            # 窗户(左上,靠近顶部)
            wx, wy = W * 0.05, H * 0.06
            c.add(Color(*hx(C.WINDOW)))
            c.add(Rectangle(pos=(wx, H - 100 - H * 0.06), size=(min(130, W * 0.2), 100)))
            c.add(Color(*hx("#b8a07a")))
            c.add(Line(points=[wx + 65, H - 100 - H * 0.06, wx + 65, H - H * 0.06], width=2))
            c.add(Line(points=[wx, H - 50 - H * 0.06, wx + 130, H - 50 - H * 0.06], width=2))
            # 门(右侧,底部贴地)
            dx = W * 0.98 - 110
            c.add(Color(*hx("#c9a06a")))
            c.add(Rectangle(pos=(dx, ground), size=(90, 130)))
            c.add(Color(*hx("#9a7a4a")))
            c.add(Line(points=[dx, ground, dx, ground + 130, dx + 90, ground + 130, dx + 90, ground], width=2))
            c.add(Color(*hx("#f0c75e")))
            c.add(Ellipse(pos=(dx + 68, ground + 55), size=(8, 8)))
            # 挂画(顶部)
            px, py = W * 0.70, H - 50 - H * 0.10
            c.add(Color(*hx("#efe3cf")))
            c.add(Rectangle(pos=(px, py), size=(70, 50)))
            c.add(Color(*hx("#b8a07a")))
            c.add(Line(points=[px, py, px + 70, py, px + 70, py + 50, px, py + 50, px, py], width=2))
            c.add(Color(*hx("#e8837a")))
            c.add(Line(points=[px + 10, py + 38, px + 32, py + 18], width=3))
            c.add(Color(*hx("#7bc47f")))
            c.add(Line(points=[px + 32, py + 18, px + 58, py + 36], width=3))
            # 家具/科技/装饰(动态,按已购集合)
            for fid in (list(getattr(g, "furniture", [])) + list(getattr(g, "tech", [])) + list(C.SCENE_DECOR)):
                _draw_item_kv(c, W, H, fid)
            # 鱼缸小鱼(数量,鱼缸在底部区域)
            fx, fy = W * 0.945, ground + H * 0.16
            for i in range(min(getattr(g, "fish", 0), 10)):
                c.add(Color(*hx("#e8837a")))
                c.add(Ellipse(pos=(fx - 22 + (i % 5) * 10, fy - 8 + (i // 5) * 14), size=(6, 4)))
            # 小鸟(鸟笼)
            if getattr(g, "birds", 0) > 0:
                bx, by = W * 0.11, H * 0.44
                c.add(Color(*hx("#f0c75e")))
                c.add(Ellipse(pos=(bx - 8, by - 6), size=(10, 12)))
                c.add(Ellipse(pos=(bx - 6, by - 9), size=(5, 5)))
                c.add(Color(*hx("#e8837a")))
                c.add(Line(points=[bx - 5, by - 7, bx - 1, by - 5, bx - 5, by - 4], width=1))
            # 母猫
            draw_cat(c, g.cat_x, g.cat_y, s, "female", preg=g.pregnancy, H=H,
                     equipped=g.equipped.get("female", {}) if hasattr(g, "equipped") else None)
            # 公猫
            draw_cat(c, g.male_x, g.male_y, s, "male", H=H,
                     equipped=g.equipped.get("male", {}) if hasattr(g, "equipped") else None)
            # 小猫站位
            sw = g._swaddled()
            others = [k for k in g.kittens if k["stage"] != "swaddle"]
            for i, k in enumerate(sw):
                dx = W * (0.2 + 0.3 * (i % 3))
                draw_kitten(c, dx, C.GROUND_Y - 70, C.KITTEN_SCALE, k, H=H)
            for i, k in enumerate(others):
                dx = W * 0.15 + (i % 6) * 100
                if k["stage"] == "adult":
                    k["_x"], k["_y"] = dx, C.GROUND_Y - 110
                draw_kitten(c, dx, C.GROUND_Y - 110, C.KITTEN_SCALE * 1.2, k, H=H)
            # 老鼠
            for m in g.mice:
                draw_mouse(c, m, H)
            # 标记(💍🤰😷)用文字层
            self._marks = []
            marks = []
            if g.pregnancy > C.PREG_EMOJI_SHOW:
                marks.append((g.cat_x + 40, g.cat_y - 80, "🤰"))
            for k in g.kittens:
                mm = ""
                if k["married_to"] is not None:
                    mm += "💍"
                if k["sex"] == C.SEX_F and k["preg"] > C.PREG_EMOJI_SHOW:
                    mm += "🤰"
                if mm:
                    marks.append((k.get("_x", 0) or k.get("_y", 0), k.get("_y", 0), mm))
            if g.sick:
                marks.append((g.cat_x + 35, g.cat_y - 70, "😷"))
                marks.append((g.male_x + 35, g.male_y - 70, "😷"))
            self._marks = marks
        except Exception:
            # 绘制任何异常都不能导致崩溃,记录并保证 _marks 存在
            self._marks = []
            try:
                import traceback
                traceback.print_exc()
            except Exception:
                pass

    def on_touch_up(self, touch):
        return super().on_touch_up(touch)


class MainApp(App):
    def build(self):
        self.game = Game(self)
        Window.clearcolor = hx("#fff6ec")
        # ===== 桌面版风格:竖向布局(顶部信息 + 画布 + 底部按钮)=====
        root = BoxLayout(orientation="vertical", padding=dp(4), spacing=dp(3))
        # ---- 顶部信息条(标题 + 资源)----
        top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30), spacing=dp(8))
        self.title_l = Label(text="", size_hint_x=None, width=dp(280), font_size=sp(13),
                             bold=True, color=hx("#5a4632"), halign="left", valign="middle")
        self.title_l.bind(size=self.title_l.setter("text_size"))
        top.add_widget(self.title_l)
        self.res_l = Label(text="", font_size=sp(10), color=hx("#a08a72"),
                           halign="right", valign="middle")
        self.res_l.bind(size=self.res_l.setter("text_size"))
        top.add_widget(self.res_l)
        root.add_widget(top)
        # ---- 状态行(状态文字)----
        self.state_l = Label(text="", size_hint_y=None, height=dp(18), font_size=sp(11),
                             bold=True, color=hx("#e889a9"), halign="center", valign="middle")
        self.state_l.bind(size=self.state_l.setter("text_size"))
        root.add_widget(self.state_l)
        # ---- 状态条(2x2)----
        bars_grid = GridLayout(cols=2, size_hint_y=None, height=dp(56), spacing=dp(2))
        self.bars = {}
        for key, label, col in (("hunger", "🍖饱腹", "#97c459"), ("happiness", "💗快乐", "#f0c75e"),
                                ("energy", "⚡体力", "#85b7eb"), ("health", "❤️健康", "#e27979")):
            row = BoxLayout(size_hint_y=None, height=dp(13), spacing=dp(2))
            row.add_widget(Label(text=label, size_hint_x=None, width=dp(52), font_size=sp(8),
                                 color=hx("#5a4632")))
            pb = ProgressBar(max=100, value=80, size_hint_y=None, height=dp(9))
            row.add_widget(pb)
            self.bars[key] = pb
            bars_grid.add_widget(row)
        root.add_widget(bars_grid)
        # ---- 三小条 ----
        minis_grid = GridLayout(cols=3, size_hint_y=None, height=dp(20), spacing=dp(2))
        self.minis = {}
        for key, label, col in (("grow", "🍼成长", "#f4a8c0"), ("study", "🎓学业", "#85b7eb"),
                                ("preg", "🤰孕周", "#e889a9")):
            row = BoxLayout(size_hint_y=None, height=dp(12), spacing=dp(2))
            row.add_widget(Label(text=label, size_hint_x=None, width=dp(40), font_size=sp(7),
                                 color=hx("#a08a72")))
            pb = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(8))
            row.add_widget(pb)
            self.minis[key] = pb
            minis_grid.add_widget(row)
        root.add_widget(minis_grid)
        # ---- 中间:画布(占剩余空间)----
        self.canvas = CatCanvas(self.game)
        root.add_widget(self.canvas)
        # ---- 底部:按钮(3 行,桌面版风格)----
        btn_rows = [
            [("🍚 喂食", self.open_feed), ("🤚 抚摸", self.do_pet), ("🧶 玩耍", self.do_play),
             ("😴 睡觉", self.do_sleep), ("🤱 产奶", self.do_milk)],
            [("🛍 服饰", self.open_shop), ("👗 衣柜", self.open_wardrobe), ("🛒 市场", self.open_market),
             ("🛋 家具", self.open_furniture), ("📱 科技", self.open_tech), ("🐾 宠物", self.open_petshop)],
            [("🏦 银行", self.open_bank), ("🏥 医院", self.open_hospital), ("🐟 鱼缸", self.open_fish),
             ("🐦 小鸟", self.open_bird), ("🏫 学校", self.open_school), ("🚏 公交", self.open_busstop),
             ("💍 结婚", self.open_marriage), ("✏️ 文具", self.open_stationery), ("⏻ 全屏", self.toggle_fs)],
        ]
        btns_area = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(2))
        for row in btn_rows:
            r = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(32), spacing=dp(3))
            for text, fn in row:
                b = Button(text=text, **BTN)
                b.bind(on_release=lambda w, f=fn: f())
                r.add_widget(b)
            btns_area.add_widget(r)
        root.add_widget(btns_area)
        Clock.schedule_interval(self._update, 1.0 / 30.0)
        return root

    # ---------------- 更新 ----------------
    def _update(self, dt):
        g = self.game
        g.update(dt)
        g.level = min(g.total_exp // C.EXP_PER_LEVEL, C.MAX_LEVEL)
        self.title_l.text = "🐱 我的别墅 · Lv.%d %s" % (g.level, C.level_title(g.level))
        cur = g.exp % C.EXP_PER_LEVEL if g.level < C.MAX_LEVEL else "MAX"
        self.res_l.text = ("🐭猫粮×%d ⭐%s 💰%.0f 🏦%.0f 🐦蛋×%d 🐟%d条 🐱小猫×%d"
                           % (g.foods.get("cat_food", 0), cur, g.wallet, g.deposit,
                              g.foods.get("bird_egg", 0), g.fish, len(g.kittens)))
        st = ""
        if g.post_delivery_left > 0:
            st = "🤱 产后休养 %ds" % g.post_delivery_left
        elif g.sick:
            st = "😷 %s · 去%s" % (C.ILLNESS_NAMES.get(g.illness, ""), C.ILLNESS_DEPT.get(g.illness, ""))
        elif g.pregnancy >= 100:
            st = "🤰 母猫可分娩!"
        elif g._pregnant_kids():
            st = "🤰 %d 只怀孕中" % len(g._pregnant_kids())
        elif "exp_machine" in g.tech:
            st = "⚙️ 造经验机工作中"
        if g.bubble:
            st = (st + "  " if st else "") + g.bubble
        self.state_l.text = st
        for key, pb in self.bars.items():
            pb.value = max(0.0, min(100.0, getattr(g, key)))
        ratios = {"grow": 0.0, "study": 0.0, "preg": 0.0}
        sw = g._swaddled()
        if sw:
            ratios["grow"] = max(k["age"] for k in sw) / C.BABY_GROW_PERIOD * 100
        st2 = [k for k in g.kittens if k["stage"] == "school"]
        if st2:
            ratios["study"] = max(k["school"] for k in st2) / C.SCHOOL_TIME * 100
        allp = [g.pregnancy] + [k["preg"] for k in g._pregnant_kids()]
        ratios["preg"] = max(allp)
        for key, pb in self.minis.items():
            pb.value = max(0.0, min(100.0, ratios[key]))
        self.canvas.draw()
        if getattr(self, "_marks_l", None):
            self.canvas.canvas.remove(self._marks_l)
        if getattr(self.canvas, "_marks", None):
            c = self.canvas.canvas
            for (mx, my, txt) in self.canvas._marks:
                pass

    def toggle_fs(self, *_):
        Window.fullscreen = not Window.fullscreen

    # ---------------- 交互 ----------------
    def do_pet(self, *_):
        self.game.pet()

    def do_play(self, *_):
        self.game.play()

    def do_sleep(self, *_):
        self.game.sleep_toggle()

    def do_milk(self, *_):
        self.game.produce_milk()

    # ---------------- Popup 工具 ----------------
    def _pop(self, title, build):
        body = BoxLayout(orientation="vertical", spacing=dp(4))
        sv = ScrollView()
        inner = GridLayout(cols=1, size_hint_y=None, spacing=dp(4), padding=dp(8))
        inner.bind(minimum_height=inner.setter("height"))
        sv.add_widget(inner)
        body.add_widget(sv)
        body.add_widget(Button(text="关闭", **BTN), )
        body.children[0].bind(on_release=lambda w: p.dismiss())
        build(inner)
        p = Popup(title=title, content=body, size_hint=(0.9, 0.85))
        p.open()
        return p, inner

    def _row(self, inner, text, btn_text=None, fn=None, can=True, tip=""):
        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        lb = Label(text=text, font_size=sp(11), color=hx("#5a4632"), halign="left", valign="middle")
        lb.bind(size=lb.setter("text_size"))
        row.add_widget(lb)
        if btn_text:
            b = Button(text=btn_text, **(BTN if can else DIS))
            if can:
                b.bind(on_release=lambda w, f=fn: f())
            row.add_widget(b, size_hint_x=None, width=dp(110))
        inner.add_widget(row)
        if tip:
            inner.add_widget(Label(text=tip, font_size=sp(9), color=hx("#a08a72"),
                                   size_hint_y=None, height=dp(18)))

    # ---------------- 喂食 ----------------
    def open_feed(self, *_):
        g = self.game
        p, inner = self._pop("🍚 喂食", lambda i: None)
        for fid, cnt in g.foods.items():
            f = C.FOODS.get(fid)
            if not f or cnt <= 0:
                continue
            if fid == "cat_milk":
                for k in g._swaddled():
                    self._row(inner, "%s ×%d → 🍼%s" % (f["name"], cnt, kid_label(k)), "喂",
                              lambda w, x=fid, t="b%d" % k["id"]: self._feed(x, t, p))
            else:
                targets = [("母猫", "female"), ("公猫", "male")]
                targets += [("%s%d" % (sex_name(k["sex"]), k["id"]), "k%d" % k["id"])
                            for k in g.kittens if k["stage"] == "adult"]
                for name, t in targets:
                    self._row(inner, "%s ×%d → %s" % (f["name"], cnt, name), "喂",
                              lambda w, x=fid, y=t: self._feed(x, y, p))

    def _feed(self, fid, target, pop):
        ok, msg = self.game.feed_food(fid, target)
        self.game.say(msg)
        pop.dismiss()
        self.open_feed()

    # ---------------- 服饰店 ----------------
    def open_shop(self, *_):
        g = self.game
        p, inner = self._pop("🛍 服饰商店(经验 %d)" % g.exp, lambda i: None)
        for item in C.WARDROBE:
            own = "✓" if item["id"] in g.owned else ""
            self._row(inner, "%s %s(⭐%d)%s" % (item["name"], item["desc"], item["price"], own),
                      "已拥有" if own else "⭐%d 买" % item["price"],
                      lambda w, i=item: self._buy_item(i, p), can=not own and g.exp >= item["price"])

    def _buy_item(self, item, pop):
        g = self.game
        if g.exp < item["price"]:
            self.game.say("经验不够")
            return
        g.exp -= item["price"]
        g.owned.add(item["id"])
        self.game.say("买了%s" % item["name"])
        pop.dismiss()
        self.open_shop()

    # ---------------- 衣柜 ----------------
    def open_wardrobe(self, *_):
        g = self.game
        opts = [("🐱 母猫", "female"), ("🐱 公猫", "male")]
        opts += [("🐱 %s" % kid_label(k), "k%d" % k["id"]) for k in g.kittens if k["stage"] != "swaddle"]
        p, inner = self._pop("👗 衣柜", lambda i: None)
        for label, t in opts:
            if t == "female":
                eq, sn = g.equipped.setdefault("female", {}), C.SEX_F
            elif t == "male":
                eq, sn = g.equipped.setdefault("male", {}), C.SEX_M
            else:
                k = g._kid(int(t[1:]))
                eq, sn = k.setdefault("equipped", {}), k["sex"]
            have = [w for w in C.WARDROBE if w["id"] in g.owned]
            for item in have:
                wearing = eq.get(item["category"]) == item["id"]
                girl = item["id"] in C.GIRL_ONLY_IDS and sn == C.SEX_M
                self._row(inner, "【%s】%s%s" % (label, item["name"], "👗" if item["id"] in C.GIRL_ONLY_IDS else ""),
                          "脱下" if wearing else "穿上",
                          lambda w, i=item, tt=t: self._wear(i, tt, p),
                          can=not girl, tip="女装" if girl else "")

    def _wear(self, item, target, pop):
        ok, msg = self.game.toggle_wear(item["id"], target)
        if msg:
            self.game.say(msg)
        pop.dismiss()
        self.open_wardrobe()

    # ---------------- 市场 ----------------
    def open_market(self, *_):
        g = self.game
        p, inner = self._pop("🛒 市场(经验 %d)" % g.exp, lambda i: None)
        for fid, f in C.FOODS.items():
            if f.get("price", 0) <= 0:
                continue
            self._row(inner, "%s ×%d(%s)" % (f["name"], g.foods.get(fid, 0), f["desc"]),
                      "⭐%d 买" % f["price"], lambda w, x=fid: self._mkt_buy(x, p),
                      can=g.exp >= f["price"])

    def _mkt_buy(self, fid, pop):
        ok, msg = self.game.buy_food(fid)
        self.game.say(msg)
        pop.dismiss()
        self.open_market()

    # ---------------- 银行 ----------------
    def open_bank(self, *_):
        g = self.game
        p, inner = self._pop("🏦 银行", lambda i: None)
        self._row(inner, "经验 %d · 钱包 %.0f · 存款 %.0f" % (g.exp, g.wallet, g.deposit))
        self._row(inner, "100 经验 → 1 元", "兑换 1000", lambda w: self._bank("ex", p))
        self._row(inner, "存 100 元吃利息", "存入", lambda w: self._bank("de", p), can=g.wallet >= 100)
        self._row(inner, "取 100 元", "取出", lambda w: self._bank("wi", p), can=g.deposit >= 100)

    def _bank(self, op, pop):
        g = self.game
        if op == "ex":
            ok, msg = g.exchange_exp(min(1000, g.exp))
        elif op == "de":
            ok, msg = g.deposit_money(min(100, g.wallet))
        else:
            ok, msg = g.withdraw_money(min(100, g.deposit))
        self.game.say(msg)
        pop.dismiss()
        self.open_bank()

    # ---------------- 家具/科技 ----------------
    def open_furniture(self, *_):
        g = self.game
        p, inner = self._pop("🛋 家具店", lambda i: None)
        for fid, f in C.FURNITURE_BY_ID.items():
            self._row(inner, "%s(%s)" % (f["name"], f["desc"]), "已摆" if fid in g.furniture else "⭐%d 买" % f["price"],
                      lambda w, x=fid: self._generic_buy(x, "furniture", p),
                      can=fid not in g.furniture and g.exp >= f["price"])

    def open_tech(self, *_):
        g = self.game
        p, inner = self._pop("📱 科技店", lambda i: None)
        for tid, t in C.TECH_BY_ID.items():
            self._row(inner, "%s(%s)" % (t["name"], t["desc"]), "已装" if tid in g.tech else "⭐%d 买" % t["price"],
                      lambda w, x=tid: self._generic_buy(x, "tech", p),
                      can=tid not in g.tech and g.exp >= t["price"])

    def _generic_buy(self, xid, kind, pop):
        g = self.game
        ok, msg = (g.buy_furniture(xid) if kind == "furniture" else g.buy_tech(xid))
        self.game.say(msg)
        pop.dismiss()
        self.open_furniture() if kind == "furniture" else self.open_tech()

    # ---------------- 文具 ----------------
    def open_stationery(self, *_):
        g = self.game
        p, inner = self._pop("✏️ 文具店(经验 %d)" % g.exp, lambda i: None)
        for k in g.kittens:
            has = " ".join(C.STATIONERY_BY_ID[s]["name"] for s in k.get("stationery", [])) or "无"
            self._row(inner, "🎒 %s:%s" % (kid_label(k), has))
            for sid, s in C.STATIONERY_BY_ID.items():
                if sid not in k.get("stationery", []):
                    self._row(inner, "  %s" % s["name"], "⭐%d" % s["price"],
                              lambda w, x=sid, y=k["id"]: self._stat_buy(x, y, p),
                              can=g.exp >= s["price"])

    def _stat_buy(self, sid, kid_id, pop):
        ok, msg = self.game.buy_stationery(sid, kid_id)
        self.game.say(msg)
        pop.dismiss()
        self.open_stationery()

    # ---------------- 宠物店 ----------------
    def open_petshop(self, *_):
        g = self.game
        p, inner = self._pop("🐾 宠物商店", lambda i: None)
        for pid, pet in C.PET_BY_ID.items():
            self._row(inner, "%s %s(%s)" % (pet["emoji"], pet["name"], pet["desc"]),
                      "已养" if pid in g.pets else "¥%.0f" % pet["price"],
                      lambda w, x=pid: self._pet_buy(x, p),
                      can=pid not in g.pets and g.wallet >= pet["price"])
        inner.add_widget(Label(text="── 卖成年小猫(¥%.0f/只)──" % C.SELL_ADULT_PRICE,
                               font_size=sp(11), bold=True, color=hx("#7f77dd"), size_hint_y=None, height=dp(24)))
        for k in g.kittens:
            if k["stage"] == "adult":
                st = "💍已婚" if k["married_to"] is not None else "¥%.0f" % C.SELL_ADULT_PRICE
                self._row(inner, "%s(%d代%s)" % (kid_label(k), k["gen"], sex_name(k["sex"])), st,
                          lambda w, x=k["id"]: self._pet_sell(x, p),
                          can=k["married_to"] is None)

    def _pet_buy(self, pid, pop):
        ok, msg = self.game.buy_pet(pid)
        self.game.say(msg)
        pop.dismiss()
        self.open_petshop()

    def _pet_sell(self, kid_id, pop):
        ok, msg = self.game.sell_adult(kid_id)
        self.game.say(msg)
        pop.dismiss()
        self.open_petshop()

    # ---------------- 结婚 ----------------
    def open_marriage(self, *_):
        g = self.game
        p, inner = self._pop("💍 婚姻登记处(需 %d 经验)" % C.MARRIAGE_COST, lambda i: None)
        by_gen = {}
        for k in g.kittens:
            if k["stage"] == "adult" and k["married_to"] is None:
                by_gen.setdefault(k["gen"], []).append(k)
        pairs = sum(1 for gen, grp in by_gen.items()
                    if any(k["sex"] == C.SEX_F for k in grp) and any(k["sex"] == C.SEX_M for k in grp))
        self._row(inner, "可自动配对 %d 对(同代成年未婚)" % pairs)
        self._row(inner, "点按钮自动找一对同代小猫结婚", "🎲 自动配对", lambda w: self._marry_auto(p),
                  can=pairs > 0 and g.exp >= C.MARRIAGE_COST)

    def _marry_auto(self, pop):
        ok, msg = self.game.marry_auto()
        self.game.say(msg)
        pop.dismiss()
        self.open_marriage()

    # ---------------- 医院 ----------------
    def open_hospital(self, *_):
        g = self.game
        p, inner = self._pop("🏥 医院", lambda i: None)
        self._row(inner, "健康 %d/100 · %s" % (g.health, "😷生病" if g.sick else "良好"))
        inner.add_widget(Label(text="── 🍼 产科 ──", font_size=sp(11), bold=True, color=hx("#7f77dd"),
                               size_hint_y=None, height=dp(24)))
        self._row(inner, "母猫孕周 %d%%" % int(g.pregnancy), "进产房", lambda w: self._to_delivery(p))
        for k in g.kittens:
            if k["sex"] == C.SEX_F and k["stage"] == "adult" and k["married_to"] is not None:
                self._row(inner, "💍%s 孕周 %d%%" % (kid_label(k), int(k["preg"])), "🤱 分娩",
                          lambda w, x=k["id"]: self._deliver_kid(x, p),
                          can=k["preg"] >= 100 and g.foods.get("cat_food", 0) >= C.BREED_FOOD_COST)
        for dept in ("内科", "外科", "儿保"):
            inner.add_widget(Label(text="── %s ──" % dept, font_size=sp(11), bold=True,
                                   color=hx("#7f77dd"), size_hint_y=None, height=dp(24)))
            for mid, m in C.MEDICINES.items():
                if m["dept"] == dept:
                    self._row(inner, "%s(%s)" % (m["name"], m["desc"]),
                              "⭐%d 买" % m["price"] if g.medicines.get(mid, 0) == 0 else "背包×%d 用" % g.medicines[mid],
                              lambda w, x=mid: self._med_buy(x, p) if g.medicines.get(x, 0) == 0 else self._med_use(x, p),
                              can=g.exp >= m["price"] if g.medicines.get(mid, 0) == 0 else True)
        inner.add_widget(Label(text="── 🩻 体检科 ──", font_size=sp(11), bold=True, color=hx("#7f77dd"),
                               size_hint_y=None, height=dp(24)))
        self._row(inner, "健康+%d,保护 %ds" % (C.CHECKUP_HEAL, C.CHECKUP_PROTECT), "⭐%d 体检" % C.CHECKUP_PRICE,
                  lambda w: self._checkup(p), can=g.exp >= C.CHECKUP_PRICE)

    def _med_buy(self, mid, pop):
        ok, msg = self.game.buy_medicine(mid)
        self.game.say(msg)
        pop.dismiss()
        self.open_hospital()

    def _med_use(self, mid, pop):
        ok, msg = self.game.use_medicine(mid)
        self.game.say(msg)
        pop.dismiss()
        self.open_hospital()

    def _checkup(self, pop):
        ok, msg = self.game.do_checkup()
        self.game.say(msg)
        pop.dismiss()
        self.open_hospital()

    def _to_delivery(self, pop):
        pop.dismiss()
        self.open_delivery()

    def _deliver_kid(self, kid_id, pop):
        ok, msg = self.game.deliver_kid(kid_id)
        self.game.say(msg)
        pop.dismiss()
        self.open_hospital()

    def open_delivery(self, *_):
        g = self.game
        p, inner = self._pop("🛏 产房", lambda i: None)
        self._row(inner, "母猫:健康 %d · 猫粮 %d" % (g.health, g.foods.get("cat_food", 0)))
        self._row(inner, "孕周 %d%%" % int(g.pregnancy), "🤱 分娩(一窝3只)",
                  lambda w: self._deliver(p),
                  can=g.pregnancy >= 100 and g.health >= C.BREED_HEALTH_MIN
                       and g.foods.get("cat_food", 0) >= C.BREED_FOOD_COST and g.post_delivery_left <= 0)
        for k in g.kittens:
            if k["sex"] == C.SEX_F and k["stage"] == "adult" and k["married_to"] is not None:
                self._row(inner, "💍%s 孕周 %d%%" % (kid_label(k), int(k["preg"])), "🤱 分娩",
                          lambda w, x=k["id"]: self._deliver_kid(x, p),
                          can=k["preg"] >= 100 and g.foods.get("cat_food", 0) >= C.BREED_FOOD_COST)

    def _deliver(self, pop):
        ok, msg = self.game.deliver()
        self.game.say(msg)
        pop.dismiss()
        self.open_delivery()

    # ---------------- 学校 / 公交 ----------------
    def open_school(self, *_):
        g = self.game
        p, inner = self._pop("🏫 小猫学校", lambda i: None)
        for k in g.kittens:
            if k["stage"] == "swaddle":
                self._row(inner, "🍼 %s:裹布中 %d%%" % (kid_label(k), k["age"] / C.BABY_GROW_PERIOD * 100))
            elif k["stage"] == "school":
                b = k.get("_bonus", 0)
                self._row(inner, "🎒 %s:学习 %d%%%s" % (kid_label(k), k["school"] / C.SCHOOL_TIME * 100,
                                                        " 加速×%.1f" % (1 + b) if b else ""))
            else:
                self._row(inner, "🐱 %s:成年%s" % (kid_label(k), "💍" if k["married_to"] else ""))

    def open_busstop(self, *_):
        g = self.game
        p, inner = self._pop("🚏 公交站", lambda i: None)
        self._row(inner, "钱包 %.0f · 宝宝免费/学生半价/成年全价" % g.wallet, "🚌 全家乘车",
                  lambda w: self._ride(p), can=g.wallet >= 1)
        for vid, v in C.VEHICLE_BY_ID.items():
            self._row(inner, "%s(%s)" % (v["name"], v["desc"]), "已买" if vid in g.vehicles else "⭐%d" % v["price"],
                      lambda w, x=vid: self._veh_buy(x, p),
                      can=vid not in g.vehicles and g.exp >= v["price"])

    def _ride(self, pop):
        ok, msg = self.game.ride_bus()
        self.game.say(msg)
        pop.dismiss()
        self.open_busstop()

    def _veh_buy(self, vid, pop):
        ok, msg = self.game.buy_vehicle(vid)
        self.game.say(msg)
        pop.dismiss()
        self.open_busstop()

    # ---------------- 鱼缸 / 小鸟 ----------------
    def open_fish(self, *_):
        g = self.game
        p, inner = self._pop("🐟 鱼缸", lambda i: None)
        self._row(inner, "小鱼 %d 条 · 小鱼干 ×%d" % (g.fish, g.foods.get("fish_dry", 0)))
        self._row(inner, "3 条鱼 → 1 份小鱼干", "制作", lambda w: self._fish_make(p), can=g.fish >= C.FISH_TO_DRY)

    def _fish_make(self, pop):
        g = self.game
        if g.fish >= C.FISH_TO_DRY:
            g.fish -= C.FISH_TO_DRY
            g.foods["fish_dry"] = g.foods.get("fish_dry", 0) + 1
            self.game.say("做了小鱼干 🐟")
        pop.dismiss()
        self.open_fish()

    def open_bird(self, *_):
        g = self.game
        p, inner = self._pop("🐦 小鸟", lambda i: None)
        self._row(inner, "成年鸟 %d · 小鸟宝 %d · 蛋 ×%d" % (g.birds, g.chicks, g.foods.get("bird_egg", 0)))
        self._row(inner, "用蛋孵小鸟宝", "孵化", lambda w: self._hatch(p),
                  can=g.foods.get("bird_egg", 0) > 0 and g.chicks < 6)
        self._row(inner, "成年鸟做成猫粮(+%d)" % C.BIRD_MEAT_FOOD, "做鸟肉", lambda w: self._bird_meat(p),
                  can=g.birds > 1)

    def _hatch(self, pop):
        ok, msg = self.game.hatch_egg()
        self.game.say(msg)
        pop.dismiss()
        self.open_bird()

    def _bird_meat(self, pop):
        ok, msg = self.game.make_bird_meat()
        self.game.say(msg)
        pop.dismiss()
        self.open_bird()

    def on_stop(self):
        try:
            self.game.save()
        except Exception:
            pass


def main():
    Window.size = (480, 800)
    MainApp().run()


if __name__ == "__main__":
    main()
