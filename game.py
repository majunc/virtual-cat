# -*- coding: utf-8 -*-
"""
虚拟小猫 · Kivy 版(Android 可打包)
在 PC(tkinter)版基础上迁移:全部功能保留——猫抓老鼠/成长/结婚/孕周/医院科室/
商店/银行/市场/文具/宠物/衣柜/学校/公交/鱼缸/小鸟/造经验机/存档。
"""
import math
import os
import random
import time

import config as C
import save as S

MAX_MICE = 3


def hx(h):
    """#RRGGBB → (r,g,b,a) 0~1,纯 Python 实现,不依赖 Kivy。"""
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0,
            int(h[4:6], 16) / 255.0, 1.0)


def sex_name(sex):
    return "母" if sex == C.SEX_F else "公"


def kid_label(k):
    return "小猫#%d(%d代%s)" % (k["id"], k["gen"], sex_name(k["sex"]))


class Mouse:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self._px, self._py = x, y
        self.gold = random.random() < C.GOLD_RATE
        self._turn = random.uniform(0.5, 1.2)
        self.speed = random.uniform(120, 180)
        self.flee = random.uniform(300, 380)
        self.vx = random.uniform(-60, 60)
        self.vy = random.uniform(-60, 60)

    def update(self, dt, cat_x, cat_y):
        self._px, self._py = self.x, self.y
        self._turn -= dt
        d = math.hypot(cat_x - self.x, cat_y - self.y)
        sp = self.flee if d < 120 else self.speed
        if d < 120:
            self.vx = (self.x - cat_x) / d * sp
            self.vy = (self.y - cat_y) / d * sp
        elif self._turn <= 0:
            self._turn = random.uniform(0.5, 1.2)
            a = random.uniform(0, 6.283)
            self.vx = math.cos(a) * sp
            self.vy = math.sin(a) * sp * 0.7
        self.x += self.vx * dt
        self.y += self.vy * dt
        e = 26
        if self.x < e:
            self.x, self.vx = e, abs(self.vx)
        elif self.x > C.CW - e:
            self.x, self.vx = C.CW - e, -abs(self.vx)
        if self.y < 290:
            self.y, self.vy = 290, abs(self.vy)
        elif self.y > C.GROUND_Y - e:
            self.y, self.vy = C.GROUND_Y - e, -abs(self.vy)


# ==================== 绘制猫/鼠/场景 ====================
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
    fud = hx(C.CAT_WHITE_D)
    belly = hx(C.BELLY)
    # 阴影
    ell(c, cx, cy + 158 * s, 80 * s, 8 * s, hx("#000000"), H=H)
    # 身体(孕肚)
    bw = (66 + 55 * min(1.0, preg / 100.0)) if preg > C.PREG_BELLY_SHOW else 65
    ell(c, cx, cy + 108 * s, bw * s, 44 * s, fur, H=H)
    ell(c, cx, cy + 120 * s, (bw - 20) * s, 32 * s, belly, H=H)
    # 头
    ell(c, cx, cy, 62 * s, 62 * s, fur, H=H)
    # 耳朵
    poly(c, [cx - 57 * s, (H or 0) - (cy - 32 * s), cx - 77 * s, (H or 0) - (cy - 104 * s),
             cx - 13 * s, (H or 0) - (cy - 62 * s)], fur)
    poly(c, [cx + 57 * s, (H or 0) - (cy - 32 * s), cx + 77 * s, (H or 0) - (cy - 104 * s),
             cx + 13 * s, (H or 0) - (cy - 62 * s)], fur)
    poly(c, [cx - 53 * s, (H or 0) - (cy - 40 * s), cx - 65 * s, (H or 0) - (cy - 88 * s),
             cx - 25 * s, (H or 0) - (cy - 62 * s)], hx(C.INNER))
    poly(c, [cx + 53 * s, (H or 0) - (cy - 40 * s), cx + 65 * s, (H or 0) - (cy - 88 * s),
             cx + 25 * s, (H or 0) - (cy - 62 * s)], hx(C.INNER))
    # 鼻子/腮红
    poly(c, [cx - 6 * s, (H or 0) - (cy + 22 * s), cx + 6 * s, (H or 0) - (cy + 22 * s),
             cx, (H or 0) - (cy + 31 * s)], hx(C.NOSE))
    ell(c, cx - 29 * s, cy + 36 * s, 9 * s, 8 * s, hx(C.BLUSH), H=H)
    ell(c, cx + 29 * s, cy + 36 * s, 9 * s, 8 * s, hx(C.BLUSH), H=H)
    # 胡须(贴近脸颊)
    for dx, y1, y2 in ((-1, 16, 8), (-1, 26, 26), (-1, 36, 44), (1, 16, 8), (1, 26, 26), (1, 36, 44)):
        line(c, [cx + 38 * dx * s, (H or 0) - (cy + y1 * s),
                 cx + 92 * dx * s, (H or 0) - (cy + y2 * s)], hx("#c99b6a"), 1.8)
    # 性别标记:母=蝴蝶结,公=领结
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
    """小猫:swaddle=裹布+宝宝帽+奶嘴+性别标记;school=校服+红领巾;adult=正常。"""
    fur = hx(C.CAT_WHITE)
    fud = hx(C.CAT_WHITE_D)
    sex = k["sex"]
    if k["stage"] == "swaddle":
        ell(c, cx, cy + 100 * s, 46 * s, 48 * s, hx("#fdf6ec"), H=H)
        ell(c, cx, cy + 102 * s, 34 * s, 40 * s, hx("#f7e9d8"), H=H)
        cap = hx("#f4a8c0") if sex == C.SEX_F else hx("#7fb3e8")
        ell(c, cx, cy - 8 * s, 30 * s, 22 * s, hx("#fdf6ec"), outline=cap, ow=3, H=H)
        ell(c, cx, cy - 50 * s, 12 * s, 10 * s, cap, H=H)
        # 奶嘴
        ell(c, cx, cy + 31 * s, 5 * s, 5 * s, hx("#ffffff"), H=H)
        ell(c, cx, cy + 39 * s, 9 * s, 5 * s, hx("#f7c8d8"), H=H)
        # 性别标记
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
        # 性别标记
        if sex == C.SEX_M:
            bx, by = cx, cy + 40 * s
            poly(c, [bx - 13 * s, (H or 0) - (by - 8 * s), bx, (H or 0) - (by + 6 * s),
                     bx + 13 * s, (H or 0) - (by - 8 * s)], hx("#5b93d0"))
            ell(c, bx, by, 3 * s, 3 * s, hx("#4a7dc0"), H=H)
        else:
            bx, by = cx - 58 * s, cy - 24 * s
            ell(c, bx - 6 * s, by - 1 * s, 8 * s, 10 * s, hx(C.BOW_PINK), H=H)
            ell(c, bx + 6 * s, by - 2 * s, 8 * s, 10 * s, hx(C.BOW_BLUE), H=H)
        # 五官
        ell(c, cx - 23 * s, cy + 2 * s, 9 * s, 9 * s, hx(C.DARK), H=H)
        ell(c, cx + 23 * s, cy + 2 * s, 9 * s, 9 * s, hx(C.DARK), H=H)
        ell(c, cx - 23 * s, cy - 1 * s, 2 * s, 2 * s, hx("#ffffff"), H=H)
        ell(c, cx + 23 * s, cy - 1 * s, 2 * s, 2 * s, hx("#ffffff"), H=H)
        poly(c, [cx - 6 * s, (H or 0) - (cy + 22 * s), cx + 6 * s, (H or 0) - (cy + 22 * s),
                 cx, (H or 0) - (cy + 31 * s)], hx(C.NOSE))


# ==================== 主游戏 ====================
class Game:
    def __init__(self, canvas=None):
        self.canvas = canvas
        data = S.load()
        self.foods = {k: int(v) for k, v in data["foods"].items()}
        self.exp = int(data["exp"])
        self.total_exp = int(data.get("total_exp", 0))
        self.hunger = float(data["hunger"])
        self.happiness = float(data["happiness"])
        self.energy = float(data["energy"])
        self.health = float(data["health"])
        self.wallet = float(data["wallet"])
        self.deposit = float(data["deposit"])
        self.owned = set(data["owned"])
        self.equipped = {c: dict(data["equipped"].get(c, {})) for c in S.CATS}
        self.medicines = {k: int(v) for k, v in data["medicines"].items()}
        self.furniture = set(data["furniture"])
        self.tech = set(data["tech"])
        self.fish = int(data["fish"])
        self.post_delivery_left = int(data.get("post_delivery_left", 0))
        self.birds = int(data.get("birds", 1))
        self.chicks = int(data.get("chicks", 0))
        self.chick_accum = float(data.get("chick_accum", 0))
        self.vehicles = set(data.get("vehicles", []))
        self.pets = list(data.get("pets", []))
        self.pregnancy = float(data.get("pregnancy", 0))
        self.kittens = data.get("kittens", [])
        self.kid_next_id = int(data.get("kid_next_id", 1))
        self.illness = data.get("illness")
        self.checkup_protect = float(data.get("checkup_protect", 0))
        self.male_hunger = float(data["hunger"])
        self.male_happiness = float(data["happiness"])
        self.asleep = False
        self.sick = False
        self.level = min(self.total_exp // C.EXP_PER_LEVEL, C.MAX_LEVEL)
        self.cooldowns = {}
        self._save_t = 0.0
        self._expm = 0.0
        self._talk = 25.0
        self._last = time.monotonic()
        self.mice = []
        self._respawn = 0.5
        self.cat_x, self.cat_y = C.CW * 0.45, C.GROUND_Y - 110
        self.tx, self.ty = self.cat_x, self.cat_y
        self.male_x, self.male_y = C.CW * 0.3, C.GROUND_Y - 110
        self._mt = 0.0
        self.bubble = ""
        self._bub_t = 0.0
        self._ensure_mice()

    # ---------- 工具 ----------
    def _kid(self, i):
        for k in self.kittens:
            if k["id"] == i:
                return k
        return None

    def _swaddled(self):
        return [k for k in self.kittens if k["stage"] == "swaddle"]

    def _pregnant_kids(self):
        return [k for k in self.kittens if k["sex"] == C.SEX_F and k["preg"] > 0]

    def _married_pairs(self):
        pairs, seen = [], set()
        for k in self.kittens:
            if k["id"] in seen or k["married_to"] is None:
                continue
            m = self._kid(k["married_to"])
            if m and m["married_to"] == k["id"] and m["id"] not in seen:
                pairs.append((k, m))
                seen.add(k["id"])
                seen.add(m["id"])
        return pairs

    def _can_act(self, key, cd):
        now = time.monotonic()
        if self.cooldowns.get(key, 0) > now:
            return False
        self.cooldowns[key] = now + cd
        return True

    def _add_exp(self, n):
        old = self.level
        self.total_exp += n
        self.exp += n
        self.level = min(self.total_exp // C.EXP_PER_LEVEL, C.MAX_LEVEL)
        if self.level > old:
            self.say("🎉 升到 Lv.%d %s!" % (self.level, C.level_title(self.level)))

    def _ensure_mice(self):
        while len(self.mice) < MAX_MICE:
            self.mice.append(Mouse(random.uniform(200, C.CW - 200),
                                   random.uniform(300, C.GROUND_Y - 40)))

    def _try_catch(self, x, y, allow=True):
        if not allow or self.energy < C.ENERGY_CATCH:
            return
        for m in self.mice:
            if math.hypot(m.x - x, m.y - y) < C.CATCH_DISTANCE:
                gold = m.gold
                self.mice.remove(m)
                self.energy -= C.ENERGY_GOLD if gold else C.ENERGY_CATCH
                gain = C.GOLD_FOOD if gold else C.FOOD_PER_CATCH
                self.foods["cat_food"] = self.foods.get("cat_food", 0) + gain
                self._add_exp(C.EXP_GOLD if gold else C.EXP_CATCH)
                self.say(("👑 金老鼠!" if gold else "🐭 抓到啦!") + " +%d 猫粮 +%d 经验" %
                         (gain, C.EXP_GOLD if gold else C.EXP_CATCH))
                return

    # ---------- 互动 ----------
    def feed_food(self, fid, target):
        if not self._can_act("feed", C.FEED_COOLDOWN):
            return False, "刚喂过啦"
        food = C.FOODS.get(fid)
        if not food or self.foods.get(fid, 0) <= 0:
            return False, C.NO_FOOD
        if fid == "cat_milk":
            kid = None
            if isinstance(target, str) and target[0] in "kb":
                kid = self._kid(int(target[1:]))
            if not kid or kid["stage"] != "swaddle":
                return False, "猫奶只给裹布宝宝喝"
            if kid.get("_sat", 80) >= 100:
                return False, C.FULL_SAT
            self.foods["cat_milk"] -= 1
            kid["_sat"] = min(100, kid.get("_sat", 80) + food["sat"])
            kid["_happy"] = min(100, kid.get("_happy", 80) + food["happy"])
            self._add_exp(C.EXP_FEED)
            return True, "%s 喝了猫奶 🍼" % kid_label(kid)
        if isinstance(target, str) and target[0] in "kb":
            kid = self._kid(int(target[1:]))
            if not kid or kid["stage"] != "adult":
                return False, "只有成年小猫能吃"
            if kid.get("_sat", 80) >= 100:
                return False, C.FULL_SAT
            self.foods[fid] -= 1
            kid["_sat"] = min(100, kid.get("_sat", 80) + food["sat"])
            kid["_happy"] = min(100, kid.get("_happy", 80) + food["happy"])
            who = kid_label(kid)
        elif target == "male":
            if self.male_hunger >= 100:
                return False, C.FULL_SAT
            self.foods[fid] -= 1
            self.male_hunger = min(100, self.male_hunger + food["sat"])
            self.male_happiness = min(100, self.male_happiness + food["happy"])
            who = "公猫"
        else:
            if self.hunger >= 100:
                return False, C.FULL_SAT
            self.foods[fid] -= 1
            self.hunger = min(100, self.hunger + food["sat"])
            self.happiness = min(100, self.happiness + food["happy"])
            who = "母猫"
        self._add_exp(C.EXP_FEED)
        return True, "喂了 %s 一份%s" % (who, food["name"])

    def pet(self):
        if self.asleep:
            self._wake()
        if not self._can_act("pet", C.PET_COOLDOWN):
            return
        self.happiness = min(100, self.happiness + 26)
        self.male_happiness = min(100, self.male_happiness + 10)
        self.energy = min(C.MAX_ENERGY, self.energy + C.ENERGY_PET)
        self._add_exp(C.EXP_PET)
        self.say("呼噜呼噜… 好舒服~")

    def play(self):
        if self.asleep:
            self._wake()
        if not self._can_act("play", C.PLAY_COOLDOWN):
            return
        if self.energy < C.ENERGY_PLAY:
            self.say("没力气啦 Zzz")
            return
        self.happiness = min(100, self.happiness + 24)
        self.male_happiness = min(100, self.male_happiness + 12)
        self.energy = max(0, self.energy - C.ENERGY_PLAY)
        self._add_exp(C.EXP_PLAY)
        self.say("毛线球冲鸭!")

    def sleep_toggle(self):
        self.asleep = not self.asleep
        self.say("💤 Zzz" if self.asleep else "早上好~")

    def _wake(self):
        self.asleep = False

    def produce_milk(self):
        if self.post_delivery_left <= 0:
            self.say("生宝宝后才有奶哦")
            return
        if not self._can_act("milk", C.MILK_COOLDOWN):
            self.say("奶还没攒好")
            return
        self.foods["cat_milk"] = self.foods.get("cat_milk", 0) + 1
        self.say("产了一份猫奶 🍼(+1,共 %d)" % self.foods["cat_milk"])

    # ---------- 生育 ----------
    def _birth(self, gen, mother_id=None):
        n = max(2, C.BABIES_PER_BIRTH)
        plan = [C.SEX_F, C.SEX_M] + [random.choice([C.SEX_F, C.SEX_M]) for _ in range(n - 2)]
        random.shuffle(plan)
        for sex in plan[:n]:
            self.kittens.append({"id": self.kid_next_id, "sex": sex, "gen": gen,
                                 "bow": C.KITTEN_BOW[sex], "stage": "swaddle",
                                 "age": 0.0, "school": 0.0, "adult": 0.0,
                                 "graduated": False, "married_to": None, "preg": 0.0,
                                 "stationery": [], "equipped": {}, "mother_id": mother_id,
                                 "_sat": 80.0, "_happy": 80.0})
            self.kid_next_id += 1

    def deliver(self):
        if self.post_delivery_left > 0:
            return False, C.POST_DELIVERY_MSG
        if self.pregnancy < 100:
            return False, "母猫孕周 %d%%" % int(self.pregnancy)
        if self.health < C.BREED_HEALTH_MIN:
            return False, "母猫健康不足"
        if self.foods.get("cat_food", 0) < C.BREED_FOOD_COST:
            return False, "分娩需 %d 猫粮" % C.BREED_FOOD_COST
        if len(self.kittens) >= C.KITTEN_MAX:
            return False, "小猫太多啦"
        self.foods["cat_food"] -= C.BREED_FOOD_COST
        n0 = len(self.kittens)
        self._birth(2)
        self.post_delivery_left = C.POST_DELIVERY_TIME
        self.pregnancy = 0.0
        self.foods["cat_milk"] = self.foods.get("cat_milk", 0) + 4
        self.say("🎉 生了 %d 只裹布宝宝!" % (len(self.kittens) - n0))
        return True, "分娩成功!"

    def deliver_kid(self, kid_id):
        k = self._kid(kid_id)
        if not k or k["sex"] != C.SEX_F or k["married_to"] is None or k["stage"] != "adult":
            return False, "不能分娩"
        if k["preg"] < 100:
            return False, "孕周 %d%%" % int(k["preg"])
        if self.foods.get("cat_food", 0) < C.BREED_FOOD_COST:
            return False, "分娩需猫粮"
        if len(self.kittens) >= C.KITTEN_MAX:
            return False, "小猫太多"
        self.foods["cat_food"] -= C.BREED_FOOD_COST
        n0 = len(self.kittens)
        self._birth(k["gen"] + 1, mother_id=k["id"])
        k["preg"] = 0.0
        self.say("🎉 %s 生了 %d 只宝宝!" % (kid_label(k), len(self.kittens) - n0))
        return True, "分娩成功!"

    def marry_auto(self):
        if self.exp < C.MARRIAGE_COST:
            return False, "结婚需要 %d 经验" % C.MARRIAGE_COST
        by_gen = {}
        for k in self.kittens:
            if k["stage"] == "adult" and k["married_to"] is None:
                by_gen.setdefault(k["gen"], []).append(k)
        for gen in sorted(by_gen):
            g = by_gen[gen]
            girls = [k for k in g if k["sex"] == C.SEX_F]
            boys = [k for k in g if k["sex"] == C.SEX_M]
            if girls and boys:
                self.exp -= C.MARRIAGE_COST
                girls[0]["married_to"] = boys[0]["id"]
                boys[0]["married_to"] = girls[0]["id"]
                girls[0]["preg"] = 0.0
                self.say("💍 %s 和 %s 结婚啦!" % (kid_label(girls[0]), kid_label(boys[0])))
                return True, "结婚成功!"
        return False, "没有同代成年未婚异性可配对"

    # ---------- 经济/商店 ----------
    def buy_stationery(self, sid, kid_id=None):
        s = C.STATIONERY_BY_ID.get(sid)
        kid = self._kid(kid_id) if kid_id is not None else None
        if not s or kid is None:
            return False, "请选择给哪只小猫买"
        if self.exp < s["price"]:
            return False, "经验不够(需 %d)" % s["price"]
        if sid in kid.get("stationery", []):
            return False, "已有这件文具"
        self.exp -= s["price"]
        kid.setdefault("stationery", []).append(sid)
        kid.pop("gear_used", None)
        return True, "给%s买了%s" % (kid_label(kid), s["name"])

    def buy_food(self, fid):
        f = C.FOODS.get(fid)
        if not f or f.get("price", 0) <= 0 or self.exp < f["price"]:
            return False, "经验不够"
        self.exp -= f["price"]
        self.foods[fid] = self.foods.get(fid, 0) + 1
        return True, "买了%s" % f["name"]

    def buy_furniture(self, fid):
        f = C.FURNITURE_BY_ID.get(fid)
        if not f or fid in self.furniture or self.exp < f["price"]:
            return False, "买不了"
        self.exp -= f["price"]
        self.furniture.add(fid)
        return True, "%s 摆好了" % f["name"]

    def buy_tech(self, tid):
        t = C.TECH_BY_ID.get(tid)
        if not t or tid in self.tech or self.exp < t["price"]:
            return False, "买不了"
        self.exp -= t["price"]
        self.tech.add(tid)
        return True, "%s 装好了" % t["name"]

    def buy_medicine(self, mid):
        m = C.MEDICINE_BY_ID.get(mid)
        if not m or self.exp < m["price"]:
            return False, "经验不够"
        self.exp -= m["price"]
        self.medicines[mid] = self.medicines.get(mid, 0) + 1
        return True, "买了%s" % m["name"]

    def use_medicine(self, mid):
        m = C.MEDICINE_BY_ID.get(mid)
        if not m or self.medicines.get(mid, 0) <= 0:
            return False, "没有这种药"
        self.medicines[mid] -= 1
        if self.sick and m["cures"]:
            if m["cures"] == self.illness:
                self.health = min(100, self.health + m["heal"])
                self.illness = None
                msg = "药到病除!"
            else:
                self.health = min(100, self.health + m["heal"] * 0.5)
                msg = "不对症…去对科室"
        else:
            self.health = min(100, self.health + m["heal"])
            msg = "吃了%s" % m["name"]
        self.sick = self.health < C.SICK_THRESHOLD and self.checkup_protect <= 0
        if not self.sick:
            self.illness = None
        return True, msg

    def do_checkup(self):
        if self.exp < C.CHECKUP_PRICE:
            return False, "体检需 %d 经验" % C.CHECKUP_PRICE
        self.exp -= C.CHECKUP_PRICE
        self.health = min(100, self.health + C.CHECKUP_HEAL)
        self.checkup_protect = C.CHECKUP_PROTECT
        self.illness = None
        self.sick = False
        return True, "体检完成,保护期 %ds" % C.CHECKUP_PROTECT

    def exchange_exp(self, n):
        if n < C.EXCHANGE_RATE or n > self.exp:
            return False, "兑换不了"
        self.exp -= n
        self.wallet += n // C.EXCHANGE_RATE
        return True, "换了 %d 元" % (n // C.EXCHANGE_RATE)

    def deposit_money(self, n):
        if n <= 0 or self.wallet < n:
            return False, "钱不够"
        self.wallet -= n
        self.deposit += n
        return True, "存入 %.0f 元" % n

    def withdraw_money(self, n):
        if n <= 0 or self.deposit < n:
            return False, "存款不够"
        self.deposit -= n
        self.wallet += n
        return True, "取出 %.0f 元" % n

    def buy_pet(self, pid):
        p = C.PET_BY_ID.get(pid)
        if not p or pid in self.pets or self.wallet < p["price"]:
            return False, "买不了"
        self.wallet -= p["price"]
        self.pets.append(pid)
        return True, "%s 领养成功" % p["name"]

    def buy_vehicle(self, vid):
        v = C.VEHICLE_BY_ID.get(vid)
        if not v or vid in self.vehicles or self.exp < v["price"]:
            return False, "买不了"
        self.exp -= v["price"]
        self.vehicles.add(vid)
        return True, "买了%s" % v["name"]

    def ride_bus(self):
        cost = C.FARE_ADULT * 2 + len(self._swaddled()) * C.FARE_BABY + \
               sum(1 for k in self.kittens if k["stage"] == "school") * C.FARE_STUDENT + \
               sum(1 for k in self.kittens if k["stage"] == "adult") * C.FARE_ADULT
        if self.wallet < cost:
            return False, "钱不够(需 ¥%.1f)" % cost
        self.wallet -= cost
        return True, "全家乘车 ¥%.1f" % cost

    def sell_adult(self, kid_id=None):
        if kid_id is None:
            avail = [k for k in self.kittens if k["stage"] == "adult" and k["married_to"] is None]
            if not avail:
                return False, "没有可卖成年小猫"
            kid_id = avail[0]["id"]
        k = self._kid(kid_id)
        if not k or k["stage"] != "adult":
            return False, "还没成年"
        if k["married_to"] is not None:
            return False, "已婚不能卖"
        self.kittens.remove(k)
        self.wallet += C.SELL_ADULT_PRICE
        return True, "卖出%s,赚了 ¥%.0f" % (kid_label(k), C.SELL_ADULT_PRICE)

    def toggle_wear(self, item_id, target="female"):
        item = C.WARDROBE_BY_ID.get(item_id)
        if not item:
            return False, ""
        if target == "female":
            sex, eq, label = C.SEX_F, self.equipped.setdefault("female", {}), "母猫"
        elif target == "male":
            sex, eq, label = C.SEX_M, self.equipped.setdefault("male", {}), "公猫"
        else:
            k = self._kid(int(target[1:]))
            sex, eq, label = k["sex"], k.setdefault("equipped", {}), kid_label(k)
        if item_id in C.GIRL_ONLY_IDS and sex == C.SEX_M:
            return False, "公猫不能穿裙子"
        if eq.get(item["category"]) == item_id:
            del eq[item["category"]]
            self.say("给%s脱下%s" % (label, item["name"]))
        else:
            if item["category"] == "top" and item_id in C.SKIRT_IDS:
                eq.pop("bottom", None)
            if item["category"] == "premium":
                eq["top"] = item_id
            eq[item["category"]] = item_id
            self.say("给%s穿上%s ✨" % (label, item["name"]))
        return True, ""

    def hatch_egg(self):
        if self.foods.get("bird_egg", 0) <= 0 or self.chicks >= 6:
            return False, "不能孵化"
        self.foods["bird_egg"] -= 1
        self.chicks += 1
        return True, "孵出小鸟宝宝 🐣"

    def make_bird_meat(self):
        if self.birds <= 1:
            return False, "至少要留一只鸟"
        self.birds -= 1
        self.foods["cat_food"] = self.foods.get("cat_food", 0) + C.BIRD_MEAT_FOOD
        return True, "做成 %d 份猫粮" % C.BIRD_MEAT_FOOD

    def say(self, text):
        self.bubble = text
        self._bub_t = 2.5

    # ---------- 主更新 ----------
    def update(self, dt):
        self._last = time.monotonic()
        # 母猫跟随触摸
        self.cat_x += (self.tx - self.cat_x) * 0.16
        self.cat_y += (self.ty - self.cat_y) * 0.16
        # 公猫 AI
        self._mt -= dt
        if self._mt <= 0:
            self._mt = random.uniform(1.5, 3.0)
            self._mtx = random.uniform(120, C.CW - 120)
            self._mty = random.uniform(200, C.GROUND_Y - 115)
        self.male_x += (getattr(self, "_mtx", self.male_x) - self.male_x) * 0.035
        self.male_y += (getattr(self, "_mty", self.male_y) - self.male_y) * 0.035
        # 小猫成长
        for k in self.kittens:
            if k["stage"] == "swaddle":
                k["age"] += dt
                if k["age"] >= C.BABY_GROW_PERIOD:
                    k["age"] = C.BABY_GROW_PERIOD
                    k["stage"] = "school"
                    self.say("🎉 %s 1 岁啦,去上学!" % kid_label(k))
            elif k["stage"] == "school":
                if not k.get("gear_used"):
                    if k.get("stationery"):
                        acc = sum(1 for s in k["stationery"] if s != "bag")
                        k["_bonus"] = min(0.9, acc * C.SCHOOL_BAG_BONUS)
                        k["stationery"] = []
                    k["gear_used"] = True
                k["school"] += dt * (1 + k.get("_bonus", 0))
                if k["school"] >= C.SCHOOL_TIME:
                    k["school"] = C.SCHOOL_TIME
                    k["graduated"] = True
                    k["stage"] = "adult"
                    k["adult"] = 0.0
                    self.say("🎓 %s 毕业啦!" % kid_label(k))
            else:
                k["adult"] += dt
                if k["adult"] >= C.ADULT_PERIOD:
                    k["adult"] = C.ADULT_PERIOD
                    if not k.get("_adult_ann"):
                        k["_adult_ann"] = True
                        self.say("🐱 %s 成年啦!" % kid_label(k))
        # 已婚小猫孕周
        for k in self.kittens:
            if k["sex"] == C.SEX_F and k["stage"] == "adult" and k["married_to"] is not None:
                m = self._kid(k["married_to"])
                if m and m["married_to"] == k["id"] and k["preg"] < 100:
                    k["preg"] = min(100.0, k["preg"] + dt / C.COUPLE_PREGNANCY_PERIOD * 100.0)
        # 母猫孕周 + 休养
        if self.post_delivery_left <= 0 and self.pregnancy < 100:
            self.pregnancy = min(100.0, self.pregnancy + dt / C.PREGNANCY_PERIOD * 100.0)
        if self.post_delivery_left > 0:
            self.post_delivery_left = max(0, self.post_delivery_left - dt)
        # 造经验机
        if "exp_machine" in self.tech:
            self._expm += dt
            if self._expm >= C.EXP_MACHINE_INTERVAL:
                self._expm -= C.EXP_MACHINE_INTERVAL
                self._add_exp(C.EXP_MACHINE_GAIN)
                self.say("⚙️ 造经验机 +%d" % C.EXP_MACHINE_GAIN)
        # 体力恢复/利息/鸟/鱼
        if not self.asleep:
            self.energy = min(C.MAX_ENERGY, self.energy + C.ENERGY_REGEN * dt / C.REGEN_INTERVAL)
        self._expm_t = self._expm
        # 状态衰减(简化:2.5s tick)
        self._tick_acc = getattr(self, "_tick_acc", 0.0) + dt
        if self._tick_acc >= C.TICK_INTERVAL:
            self._tick_acc -= C.TICK_INTERVAL
            if self.asleep:
                self.energy = min(C.MAX_ENERGY, self.energy + C.ENERGY_SLEEP)
            else:
                decay = 1.0 if not self.sick else 2.0
                self.hunger = max(0, self.hunger - C.HUNGER_DECAY * decay)
                self.happiness = max(0, self.happiness - C.HAPPINESS_DECAY * decay)
                self.male_hunger = max(0, self.male_hunger - C.HUNGER_DECAY * decay * 0.8)
                self.male_happiness = max(0, self.male_happiness - C.HAPPINESS_DECAY * decay * 0.8)
            self.checkup_protect = max(0.0, self.checkup_protect - C.TICK_INTERVAL)
            self.health = max(0, self.health - C.HEALTH_DECAY)
            if self.health < C.SICK_THRESHOLD and self.checkup_protect <= 0:
                if not self.sick:
                    self.illness = random.choice(C.ADULT_ILLNESS_POOL)
                    self.say("😷 生病了:%s" % C.ILLNESS_NAMES.get(self.illness, ""))
                self.sick = True
            else:
                self.sick = False
                if self.health >= C.SICK_THRESHOLD:
                    self.illness = None
        # 鸟蛋/鱼
        self._egg = getattr(self, "_egg", 0.0) + dt
        if self._egg >= C.BIRD_EGG_INTERVAL and self.birds > 0 and self.foods.get("bird_egg", 0) < C.MAX_BIRD_EGGS:
            self._egg -= C.BIRD_EGG_INTERVAL
            self.foods["bird_egg"] = self.foods.get("bird_egg", 0) + 1
        self._fsh = getattr(self, "_fsh", 0.0) + dt
        if self._fsh >= C.FISH_BIRTH_INTERVAL and self.fish < C.MAX_FISH:
            self._fsh -= C.FISH_BIRTH_INTERVAL
            self.fish += 1
        if self.chicks > 0:
            self._chick = getattr(self, "_chick", 0.0) + dt
            if self._chick >= C.CHICK_GROW_TIME:
                self._chick = 0
                self.chicks -= 1
                self.birds += 1
        # 利息
        self._int = getattr(self, "_int", 0.0) + dt
        if self._int >= C.INTEREST_INTERVAL and self.deposit > 0:
            self._int -= C.INTEREST_INTERVAL
            gain = self.deposit * C.INTEREST_PER_YUAN * (C.INTEREST_INTERVAL / 60.0)
            if gain >= 1:
                self.exp += int(gain)
                self.total_exp += int(gain)
        # 老鼠
        if len(self.mice) < MAX_MICE:
            self._respawn -= dt
            if self._respawn <= 0:
                self._respawn = random.uniform(1.0, 2.0)
                self._ensure_mice()
        for m in self.mice:
            m.update(dt, self.cat_x, self.cat_y)
        self._try_catch(self.cat_x, self.cat_y, allow=self.pregnancy <= 0 and self.post_delivery_left <= 0)
        self._try_catch(self.male_x, self.male_y)
        for k in self.kittens:
            if k["stage"] == "adult" and not (k["sex"] == C.SEX_F and k["preg"] > 0):
                self._try_catch(k.get("_x", 0), k.get("_y", 0))
        # 气泡
        if self._bub_t > 0:
            self._bub_t -= dt
            if self._bub_t <= 0:
                self.bubble = ""
        # 自动说话
        self._talk -= dt
        if self._talk <= 0:
            self._talk = random.uniform(25, 60)
            if not self.sick and self.hunger < 30:
                self.say("喵…好饿呀")
            elif not self.sick:
                self.say(random.choice(C.AUTO_LINES))
        # 自动保存
        self._save_t += dt
        if self._save_t >= 3.0:
            self._save_t = 0.0
            self.save()

    def save(self):
        S.save(self._snapshot())

    def _snapshot(self):
        return {
            "foods": {k: v for k, v in self.foods.items() if v > 0},
            "exp": self.exp, "total_exp": self.total_exp,
            "hunger": round(self.hunger, 1), "happiness": round(self.happiness, 1),
            "energy": round(self.energy, 1), "health": round(self.health, 1),
            "wallet": round(self.wallet, 2), "deposit": round(self.deposit, 2),
            "owned": sorted(self.owned), "equipped": self.equipped,
            "medicines": {k: v for k, v in self.medicines.items() if v > 0},
            "kittens": [dict(k) for k in self.kittens],
            "kid_next_id": self.kid_next_id,
            "pregnancy": round(self.pregnancy, 1),
            "post_delivery_left": int(self.post_delivery_left),
            "furniture": sorted(self.furniture), "tech": sorted(self.tech),
            "fish": self.fish, "birds": self.birds, "chicks": self.chicks,
            "chick_accum": round(self.chick_accum, 1),
            "vehicles": sorted(self.vehicles), "pets": list(self.pets),
            "illness": self.illness, "checkup_protect": round(self.checkup_protect, 1),
        }
