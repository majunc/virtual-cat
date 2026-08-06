# -*- coding: utf-8 -*-
"""
save.py — 存档读写(8.0)
小猫独立模型:每只小猫有自己的 id/性别/代际/成长阶段/婚姻/孕周/文具/穿着,
无数量限制。旧档(7.0 及以前)自动迁移。
"""
import json
import os
import time

import config as C
from config import SAVE_FILE, INITIAL_ITEMS, INITIAL_TECH

CATS = ["female", "male"]

DEFAULTS = {
    "foods": {"cat_food": 5},
    "exp": 1000000,            # 经验余额(开局送 100 万,可花)
    "total_exp": 0,            # 累计获得经验(决定等级,开局 0 级)
    "hunger": 80.0,
    "happiness": 80.0,
    "energy": 1000.0,
    "health": 100.0,
    "wallet": 1000.0,          # 开局 1000 元
    "deposit": 0.0,
    "owned": [],
    "equipped": {},            # female/male -> {category: id}
    "medicines": {},
    "kittens": [],             # 每只: {id, sex, gen, bow, stage, age, school, adult,
                               #         graduated, married_to, preg, stationery, equipped}
    "kid_next_id": 1,
    "pregnancy": 0.0,          # 母猫孕周(0-100)
    "post_delivery_left": 0,
    "furniture": list(INITIAL_ITEMS),
    "tech": list(INITIAL_TECH),
    "fish": 5,
    "birds": 1,
    "chicks": 0,
    "chick_accum": 0.0,
    "vehicles": [],
    "pets": [],
    "illness": None,
    "checkup_protect": 0.0,
    "saved_at": 0.0,
}


def _clean_kitten(k):
    """规范化一只小猫数据。"""
    k = dict(k)
    k["id"] = int(k.get("id", 0))
    k["sex"] = k.get("sex") if k.get("sex") in (C.SEX_F, C.SEX_M) else C.SEX_F
    k["gen"] = max(1, int(k.get("gen", 2)))
    k["bow"] = k.get("bow") if k.get("bow") in ("pink", "blue", "red", "gold") else "pink"
    for key in ("age", "school", "adult", "preg"):
        try:
            k[key] = float(k.get(key, 0))
        except (TypeError, ValueError):
            k[key] = 0.0
    k["graduated"] = bool(k.get("graduated", False))
    mt = k.get("married_to")
    k["married_to"] = int(mt) if isinstance(mt, (int, float)) else None
    stat = k.get("stationery", [])
    k["stationery"] = [s for s in stat if isinstance(s, str)] if isinstance(stat, list) else []
    eq = k.get("equipped", {})
    k["equipped"] = {kk: vv for kk, vv in eq.items()
                     if isinstance(kk, str) and isinstance(vv, str)} if isinstance(eq, dict) else {}
    stage = k.get("stage")
    if stage not in ("swaddle", "school", "adult"):
        # 按进度推断阶段
        if k["age"] < C.BABY_GROW_PERIOD:
            stage = "swaddle"
        elif k["school"] < C.SCHOOL_TIME:
            stage = "school"
        else:
            stage = "adult"
    k["stage"] = stage
    # 性别与蝴蝶结一致性(公猫蝴蝶结改领结,母猫默认粉)
    if k["sex"] == C.SEX_M and k["bow"] in ("pink", "red"):
        k["bow"] = "blue"
    if k["sex"] == C.SEX_F and k["bow"] not in ("pink", "red"):
        k["bow"] = "pink"
    return k


def _migrate(data):
    """旧档(有 babies/grandkids/kid_married)迁移到 kittens 列表。"""
    if isinstance(data.get("kittens"), list) and data["kittens"]:
        data["kittens"] = [_clean_kitten(k) for k in data["kittens"]]
        return data
    kittens = []
    nid = int(data.get("kid_next_id", 1))
    # 旧二代宝宝(共享成长进度)
    n_babies = int(data.get("babies", 0))
    baby_age = float(data.get("baby_age", 0))
    school_accum = float(data.get("school_accum", 0))
    adult_accum = float(data.get("adult_accum", 0))
    graduated = bool(data.get("graduated", False))
    old_married = {int(k): int(v) for k, v in data.get("kid_married", {}).items()}
    for i in range(n_babies):
        bow = C.BABY_BOW_COLORS[i] if i < len(C.BABY_BOW_COLORS) else "pink"
        sex = C.SEX_F if bow in ("pink", "red") else C.SEX_M
        if baby_age < C.BABY_GROW_PERIOD:
            stage, age, sch, adl = "swaddle", baby_age, 0.0, 0.0
        elif not graduated:
            stage, age, sch, adl = "school", baby_age, school_accum, 0.0
        elif adult_accum < C.ADULT_PERIOD:
            stage, age, sch, adl = "adult", baby_age, C.SCHOOL_TIME, adult_accum
        else:
            stage, age, sch, adl = "adult", baby_age, C.SCHOOL_TIME, C.ADULT_PERIOD
        kittens.append(_clean_kitten({
            "id": nid, "sex": sex, "gen": 2, "bow": bow, "stage": stage,
            "age": age, "school": sch, "adult": adl, "graduated": graduated,
            "married_to": old_married.get(i), "preg": 0.0,
            "stationery": [], "equipped": data.get("equipped", {}).get("baby%d" % i, {}),
        }))
        nid += 1
    # 旧第三代宝宝
    for g in data.get("grandkids", []):
        bow = g.get("bow", "pink")
        sex = C.SEX_F if bow in ("pink", "red") else C.SEX_M
        age = float(g.get("age", 0))
        sch = float(g.get("school", 0))
        adl = float(g.get("adult", 0))
        if age < C.BABY_GROW_PERIOD:
            stage = "swaddle"
        elif sch < C.SCHOOL_TIME:
            stage = "school"
        else:
            stage = "adult"
        kittens.append(_clean_kitten({
            "id": nid, "sex": sex, "gen": 3, "bow": bow, "stage": stage,
            "age": age, "school": sch, "adult": adl, "graduated": sch >= C.SCHOOL_TIME,
            "married_to": None, "preg": 0.0, "stationery": [], "equipped": {},
        }))
        nid += 1
    # 夫妻孕周迁移到已婚雌性小猫
    if old_married and kittens:
        paired = set()
        for i, j in old_married.items():
            if i in paired or j in paired:
                continue
            paired.add(i)
            paired.add(j)
        for idx in paired:
            for k in kittens:
                if k["id"] == idx + 1 and k["sex"] == C.SEX_F:
                    k["preg"] = float(data.get("couple_preg", 0))
    data["kittens"] = kittens
    data["kid_next_id"] = nid
    return data


def _clean(data):
    data["foods"] = {k: max(0, int(v)) for k, v in data.get("foods", {}).items()
                     if isinstance(v, (int, float)) and v > 0}
    data["medicines"] = {k: max(0, int(v)) for k, v in data.get("medicines", {}).items()
                         if isinstance(v, (int, float)) and v > 0}
    data["owned"] = [i for i in data.get("owned", []) if isinstance(i, str)]
    eq = data.get("equipped", {})
    if eq and not any(k in CATS for k in eq):
        eq = {"female": {k: v for k, v in eq.items()
                         if isinstance(k, str) and isinstance(v, str)}}
    else:
        eq = {k: {kk: vv for kk, vv in v.items() if isinstance(kk, str) and isinstance(vv, str)}
              for k, v in eq.items() if k in CATS and isinstance(v, dict)}
    data["equipped"] = eq
    data["furniture"] = [i for i in data.get("furniture", []) if isinstance(i, str)]
    data["tech"] = [i for i in data.get("tech", []) if isinstance(i, str)]
    data["vehicles"] = [i for i in data.get("vehicles", []) if isinstance(i, str)]
    data["pets"] = [i for i in data.get("pets", []) if isinstance(i, str)]
    data["kittens"] = [_clean_kitten(k) for k in data.get("kittens", [])]
    data["kid_next_id"] = max(1, int(data.get("kid_next_id", 1)))
    if any(k["id"] >= data["kid_next_id"] for k in data["kittens"]):
        data["kid_next_id"] = max([k["id"] for k in data["kittens"]] + [0]) + 1
    if data.get("illness") not in (None, "cold", "stomach", "wound", "infection", "baby"):
        data["illness"] = None
    for key in ("exp", "hunger", "happiness", "energy", "health", "wallet", "deposit",
                "pregnancy", "checkup_protect", "chick_accum", "total_exp"):
        data[key] = float(data.get(key, DEFAULTS[key]))
    # 旧档迁移:无 total_exp 时按已有经验视为总获得(保持等级)
    if data.get("total_exp", 0) <= 0:
        data["total_exp"] = max(0.0, float(data.get("exp", 0)))
    # 等级 0 的旧档视为"刚开局",补新初始资源(经验 100 万 + 1000 元)
    if float(data.get("total_exp", 0)) <= 0 and float(data.get("exp", 0)) < 1000000:
        data["exp"] = 1000000.0
        data["wallet"] = max(float(data.get("wallet", 0)), 1000.0)
    for key in ("fish", "birds", "chicks", "post_delivery_left"):
        data[key] = max(0, int(data.get(key, DEFAULTS[key])))
    return data


def load():
    data = dict(DEFAULTS)
    data["foods"] = dict(DEFAULTS["foods"])
    data["medicines"] = dict(DEFAULTS["medicines"])
    data["furniture"] = list(DEFAULTS["furniture"])
    data["tech"] = list(DEFAULTS["tech"])
    data["vehicles"] = list(DEFAULTS["vehicles"])
    data["pets"] = list(DEFAULTS["pets"])
    data["equipped"] = {}
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                for k in DEFAULTS:
                    if k in loaded:
                        data[k] = loaded[k]
                data = _migrate(data)
                data = _clean(data)
    except Exception:
        pass
    return data


def save(data):
    try:
        data["saved_at"] = time.time()
        tmp = SAVE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, SAVE_FILE)
    except Exception:
        pass
