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
    e = hx("#d9c9b8") if not m.gold else hx("#f0c75e")
    ec = hx("#c4b09a") if not m.gold else hx("#c9a23d")
    ell(c, m.x, m.y, 16, 10, e, H=H)
    ell(c, m.x + 16, m.y - 2, 8, 7, e, H=H)
    ell(c, m.x - 8, m.y + 4, 3, 3, e, H=H)
    ell(c, m.x - 14, m.y - 6, 4, 4, e, H=H)
    ell(c, m.x + 18, m.y - 6, 4, 4, e, H=H)
    line(c, [m.x - 4, m.y - 8, m.x - 14, m.y - 18], ec, 2)
    line(c, [m.x + 6, m.y - 8, m.x + 10, m.y - 20], ec, 2)


def draw_cat(c, cx, cy, s, gender, preg=0.0, H=None):
    fur = hx(C.CAT_MALE) if gender == "male" else hx(C.CAT_WHITE)
    belly = hx(C.BELLY)
    ell(c, cx, cy + 158 * s, 80 * s, 8 * s, hx("#000000"), H=H)
    bw = (66 + 55 * min(1.0, preg / 100.0)) if preg > C.PREG_BELLY_SHOW else 65
    ell(c, cx, cy + 108 * s, bw * s, 44 * s, fur, H=H)
    ell(c, cx, cy + 120 * s, (bw - 20) * s, 32 * s, belly, H=H)
    ell(c, cx, cy, 62 * s, 62 * s, fur, H=H)
    poly(c, [cx - 57 * s, (H or 0) - (cy - 32 * s), cx - 77 * s, (H or 0) - (cy - 104 * s),
             cx - 13 * s, (H or 0) - (cy - 62 * s)], fur)
    poly(c, [cx + 57 * s, (H or 0) - (cy - 32 * s), cx + 77 * s, (H or 0) - (cy - 104 * s),
             cx + 13 * s, (H or 0) - (cy - 62 * s)], fur)
    poly(c, [cx - 53 * s, (H or 0) - (cy - 40 * s), cx - 65 * s, (H or 0) - (cy - 88 * s),
             cx - 25 * s, (H or 0) - (cy - 62 * s)], hx(C.INNER))
    poly(c, [cx + 53 * s, (H or 0) - (cy - 40 * s), cx + 65 * s, (H or 0) - (cy - 88 * s),
             cx + 25 * s, (H or 0) - (cy - 62 * s)], hx(C.INNER))
    poly(c, [cx - 6 * s, (H or 0) - (cy + 22 * s), cx + 6 * s, (H or 0) - (cy + 22 * s),
             cx, (H or 0) - (cy + 31 * s)], hx(C.NOSE))
    ell(c, cx - 29 * s, cy + 36 * s, 9 * s, 8 * s, hx(C.BLUSH), H=H)
    ell(c, cx + 29 * s, cy + 36 * s, 9 * s, 8 * s, hx(C.BLUSH), H=H)
    for dx, y1, y2 in ((-1, 16, 8), (-1, 26, 26), (-1, 36, 44), (1, 16, 8), (1, 26, 26), (1, 36, 44)):
        line(c, [cx + 38 * dx * s, (H or 0) - (cy + y1 * s),
                 cx + 92 * dx * s, (H or 0) - (cy + y2 * s)], hx("#c99b6a"), 1.8)
    if gender == "male":
        bx, by = cx, cy + 46 * s
        poly(c, [bx - 16 * s, (H or 0) - (by - 10 * s), bx, (H or 0) - (by + 8 * s),
                 bx + 16 * s, (H or 0) - (by - 10 * s)], hx("#5b93d0"))
        ell(c, bx, by, 4 * s, 4 * s, hx("#4a7dc0"), H=H)
    else:
        bx, by = cx - 58 * s, cy - 24 * s
        ell(c, bx - 6 * s, by - 1 * s, 9 * s, 11 * s, hx(C.BOW_PINK), H=H)
        ell(c, bx + 6 * s, by - 3 * s, 9 * s, 11 * s, hx(C.BOW_BLUE), H=H)
        ell(c, bx, by, 7 * s, 7 * s, hx("#e889a9"), H=H)


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
        ell(c, cx, cy + 108 * s, bw * s, 44 * s, fur, H=H)
        if k["stage"] == "school":
            ell(c, cx, cy + 90 * s, 46 * s, 30 * s, hx("#4a6ea8"), H=H)
            poly(c, [cx - 12 * s, (H or 0) - (cy + 66 * s), cx + 12 * s, (H or 0) - (cy + 66 * s),
                     cx, (H or 0) - (cy + 104 * s)], hx("#d84a4a"))
        ell(c, cx, cy, 62 * s, 62 * s, fur, H=H)
        if sex == C.SEX_M:
            bx, by = cx, cy + 40 * s
            poly(c, [bx - 13 * s, (H or 0) - (by - 8 * s), bx, (H or 0) - (by + 6 * s),
                     bx + 13 * s, (H or 0) - (by - 8 * s)], hx("#5b93d0"))
            ell(c, bx, by, 3 * s, 3 * s, hx("#4a7dc0"), H=H)
        else:
            bx, by = cx - 58 * s, cy - 24 * s
            ell(c, bx - 6 * s, by - 1 * s, 8 * s, 10 * s, hx(C.BOW_PINK), H=H)
            ell(c, bx + 6 * s, by - 2 * s, 8 * s, 10 * s, hx(C.BOW_BLUE), H=H)
        ell(c, cx - 23 * s, cy + 2 * s, 9 * s, 9 * s, hx(C.DARK), H=H)
        ell(c, cx + 23 * s, cy + 2 * s, 9 * s, 9 * s, hx(C.DARK), H=H)
        ell(c, cx - 23 * s, cy - 1 * s, 2 * s, 2 * s, hx("#ffffff"), H=H)
        ell(c, cx + 23 * s, cy - 1 * s, 2 * s, 2 * s, hx("#ffffff"), H=H)
        poly(c, [cx - 6 * s, (H or 0) - (cy + 22 * s), cx + 6 * s, (H or 0) - (cy + 22 * s),
                 cx, (H or 0) - (cy + 31 * s)], hx(C.NOSE))




BTN = {"size_hint_y": None, "height": dp(46), "background_normal": "",
       "background_color": hx("#f5a25d"), "color": hx("#5a4632"),
       "font_size": sp(13), "bold": True}
DIS = {"size_hint_y": None, "height": dp(46), "background_normal": "",
       "background_color": hx("#e8dfd0"), "color": hx("#b09e88"),
       "font_size": sp(13), "bold": True}


def mkbtn(text, on, **kw):
    b = Button(text=text, **BTN)
    b.bind(on_release=on)
    for k, v in kw.items():
        setattr(b, k, v)
    return b


class CatCanvas(Widget):
    def __init__(self, game, **kw):
        super().__init__(**kw)
        self.game = game
        self._need_redraw = True

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
            return
        C.CW, C.CH = W, H
        C.GROUND_Y = H - 60
        c = self.canvas
        c.clear()
        s = C.CAT_SCALE
        # 背景
        c.add(Color(*hx("#fdf3e4")))
        c.add(Rectangle(pos=(0, 0), size=(W, H)))
        c.add(Color(*hx("#e8d5b8")))
        c.add(Rectangle(pos=(0, 0), size=(W, 60)))
        # 简化家具(沙发/电视/桌子色块)
        for fx, fy, fw, fh, col in ((W * 0.08, 70, 160, 90, "#c98a5a"), (W * 0.72, 70, 170, 95, "#8a5a3a"),
                                    (W * 0.42, 70, 140, 80, "#b98a5a")):
            c.add(Color(*hx(col)))
            c.add(Rectangle(pos=(fx, fy), size=(fw, fh)))
        # 母猫
        draw_cat(c, g.cat_x, g.cat_y, s, "female", preg=g.pregnancy, H=H)
        # 公猫
        draw_cat(c, g.male_x, g.male_y, s, "male", H=H)
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

    def on_touch_up(self, touch):
        return super().on_touch_up(touch)


class MainApp(App):
    def build(self):
        self.game = Game(self)
        Window.clearcolor = hx("#fff6ec")
        # 横屏布局:左侧画布 + 右侧控制面板(平板横屏为主)
        root = BoxLayout(orientation="horizontal", padding=dp(6), spacing=dp(6))
        # ---- 左侧画布(占大部分宽度) ----
        self.canvas = CatCanvas(self.game)
        root.add_widget(self.canvas)
        # ---- 右侧控制面板(固定较窄宽度,内容超高时可滚动) ----
        panel = BoxLayout(orientation="vertical", size_hint_x=None, width=dp(330),
                          spacing=dp(4))
        # 顶部信息
        self.title_l = Label(text="", size_hint_y=None, height=dp(28),
                             font_size=sp(15), bold=True, color=hx("#5a4632"),
                             halign="left", valign="middle")
        self.title_l.bind(size=self.title_l.setter("text_size"))
        panel.add_widget(self.title_l)
        self.res_l = Label(text="", size_hint_y=None, height=dp(20),
                           font_size=sp(11), color=hx("#a08a72"), halign="left", valign="middle")
        self.res_l.bind(size=self.res_l.setter("text_size"))
        panel.add_widget(self.res_l)
        self.state_l = Label(text="", size_hint_y=None, height=dp(20),
                             font_size=sp(12), bold=True, color=hx("#e889a9"),
                             halign="center", valign="middle")
        self.state_l.bind(size=self.state_l.setter("text_size"))
        panel.add_widget(self.state_l)
        # 状态条
        self.bars = {}
        for key, label, col in (("hunger", "🍖 饱腹", "#97c459"), ("happiness", "💗 快乐", "#f0c75e"),
                                ("energy", "⚡ 体力", "#85b7eb"), ("health", "❤️ 健康", "#e27979")):
            row = BoxLayout(size_hint_y=None, height=dp(16), spacing=dp(6))
            row.add_widget(Label(text=label, size_hint_x=None, width=dp(80), font_size=sp(10),
                                 color=hx("#5a4632")))
            pb = ProgressBar(max=100, value=80)
            row.add_widget(pb)
            self.bars[key] = pb
            panel.add_widget(row)
        # 三小条
        self.minis = {}
        for key, label, col in (("grow", "🍼成长", "#f4a8c0"), ("study", "🎓学业", "#85b7eb"),
                                ("preg", "🤰孕周", "#e889a9")):
            row = BoxLayout(size_hint_y=None, height=dp(12), spacing=dp(6))
            row.add_widget(Label(text=label, size_hint_x=None, width=dp(64), font_size=sp(9),
                                 color=hx("#a08a72")))
            pb = ProgressBar(max=100, value=0)
            row.add_widget(pb)
            self.minis[key] = pb
            panel.add_widget(row)
        # 按钮区(右侧窄面板,竖排更紧凑,超高可滚动)
        btn_rows = [
            [("🍚 喂食", self.open_feed), ("🤚 抚摸", self.do_pet)],
            [("🧶 玩耍", self.do_play), ("😴 睡觉", self.do_sleep)],
            [("🤱 产奶", self.do_milk), ("🛍 服饰", self.open_shop)],
            [("👗 衣柜", self.open_wardrobe), ("🛒 市场", self.open_market)],
            [("🛋 家具", self.open_furniture), ("📱 科技", self.open_tech)],
            [("🐾 宠物", self.open_petshop), ("🏦 银行", self.open_bank)],
            [("🏥 医院", self.open_hospital), ("✏️ 文具", self.open_stationery)],
            [("💍 结婚", self.open_marriage), ("🏫 学校", self.open_school)],
            [("🚏 公交", self.open_busstop), ("🐟 鱼缸", self.open_fish)],
            [("🐦 小鸟", self.open_bird), ("⏻ 全屏", self.toggle_fs)],
        ]
        sv = ScrollView(size_hint_y=None, height=dp(10))  # 高度稍后由 grid 撑开
        sv.do_scroll_x = False
        grid = GridLayout(cols=2, size_hint_y=None, width=panel.width - dp(12),
                          spacing=dp(4), padding=dp(2))
        grid.bind(minimum_height=grid.setter("height"))
        for row in btn_rows:
            for text, fn in row:
                b = Button(text=text, **BTN)
                b.bind(on_release=lambda w, f=fn: f())
                grid.add_widget(b)
        sv.add_widget(grid)
        panel.add_widget(sv)
        root.add_widget(panel)
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
        if self.canvas._marks:
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
        body.add_widget(sv, weight=1)
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
        row.add_widget(lb, weight=1)
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
