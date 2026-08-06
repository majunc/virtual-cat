# -*- coding: utf-8 -*-
"""
config.py — 虚拟小猫 4.0 全部可调配置
颜色、数值、至臻皮肤、家具目录、科技目录、食物、药品、场景布局、台词、称号。
"""
import os

# ---------------- 窗口与画布 ----------------
# 全屏模式:启动即全屏;F11 切换;退出全屏按钮在右上角
FULLSCREEN = True
W, H = 0, 0                 # 运行时按屏幕设置
CW, CH = 1400, 800          # 画布尺寸默认值,运行时按实际画布更新
CANVAS_X = 0
GROUND_Y = 0                # 运行时按画布尺寸设置
CAT_SCALE = 0.7             # 大猫缩放(全屏后变小)
KITTEN_SCALE = 0.45         # 幼猫缩放

# ---------------- 配色 ----------------
BG         = "#fff6ec"
TEXT       = "#5a4632"
MUTED      = "#a08a72"
CAT_WHITE  = "#fff9f0"
CAT_WHITE_D = "#e8ddd0"
CAT_MALE   = "#f4efe8"
BELLY      = "#fff3e6"
INNER      = "#f7b9c9"
BOW_BLUE   = "#7db6e8"
BOW_PINK   = "#f4a8c0"
BOW_RED    = "#e26d5c"
NOSE       = "#e8837a"
BLUSH      = "#ffcfc0"
DARK       = "#3a2a1a"
WHITE      = "#ffffff"
GREEN      = "#7bc47f"
YELLOW     = "#f0c75e"
RED        = "#e26d5c"
INFO       = "#85b7eb"
HEALTH     = "#9f8fd6"
GOLD       = "#f0c75e"
BTN_BG     = "#ffd9a8"
BTN_ACT    = "#ffc98a"
CODE_TAG   = "#df8b3f"

# 别墅场景配色
WALL     = "#f7ead6"   # 墙面
FLOOR    = "#e8d5b8"   # 地板
FLOOR_LINE = "#d9c3a3"
WINDOW   = "#cfe8f5"
WOOD     = "#b98a5a"   # 家具木色
WOOD_D   = "#9a6f42"
METAL    = "#c8c8c8"

# ---------------- 核心数值 ----------------
MAX_ENERGY   = 1000
ENERGY_CATCH = 5
ENERGY_GOLD  = 10
ENERGY_PET   = 80
ENERGY_PLAY  = 20
ENERGY_SLEEP = 150
ENERGY_REGEN = 2
REGEN_INTERVAL = 3.0

FOOD_PER_CATCH = 50
GOLD_FOOD      = 100
GOLD_RATE      = 0.01
CATCH_DISTANCE = 52        # 抓取判定(猫缩小后略调小)

EXP_CATCH   = 10
EXP_GOLD    = 20
EXP_PET     = 5
EXP_FEED    = 2
EXP_PLAY    = 2
EXP_PER_LEVEL = 200
MAX_LEVEL   = 100

PET_COOLDOWN  = 1.5
FEED_COOLDOWN = 1.0
PLAY_COOLDOWN = 1.0
BREED_COOLDOWN = 60.0      # 分娩冷却

HUNGER_DECAY    = 0.25
HAPPINESS_DECAY = 0.18
HEALTH_DECAY    = 0.0015
SICK_THRESHOLD  = 30
TICK_INTERVAL   = 2.5
MAIN_FPS        = 30

EXCHANGE_RATE = 100
INTEREST_PER_YUAN = 0.1
INTEREST_INTERVAL = 30.0

# 生育(无数量限制,想生多少生多少)
BREED_FOOD_COST = 60
BREED_HEALTH_MIN = 60      # 母猫健康需 >= 60 才能分娩
POST_DELIVERY_TIME = 90    # 产后休养时长(秒),期间母猫不能抓鼠
PREGNANCY_PERIOD = 300     # 孕周:产后休养后 300 秒涨满,满了才能分娩
BABIES_PER_BIRTH = 3       # 一窝三只
BABY_BOW_COLORS = ["pink", "red", "blue"]
KITTEN_MAX = 60            # 小猫总数软上限(防止无限膨胀卡死),一般用不到

# 性别
SEX_F = "f"
SEX_M = "m"
# 出生标记:母=粉蝴蝶结,公=蓝色小领结
KITTEN_BOW = {SEX_F: "pink", SEX_M: "blue"}

# 小鸟
BIRD_EGG_INTERVAL = 150    # 每只成年鸟每 150 秒下一颗蛋
MAX_BIRD_EGGS = 10
CHICK_GROW_TIME = 180      # 小鸟宝宝孵化后 180 秒长大成鸟
BIRD_MEAT_FOOD = 10        # 1 只成年鸟做成 10 份猫粮
INITIAL_BIRDS = 1          # 初始成年鸟数

# 鱼缸
FISH_BIRTH_INTERVAL = 90   # 每 90 秒生 1 条小鱼
MAX_FISH = 20
FISH_TO_DRY = 3            # 3 条鱼做 1 份小鱼干

# 猫奶(生小猫后,可不停产奶,无上限)
MILK_COOLDOWN = 20         # 产奶冷却(秒),点击"产奶"得 1 份

# 宝宝成长(三段:裹布 1 岁 → 上学 → 成年进度 → 成年猫)
BABY_GROW_PERIOD = 480     # 宝宝 1 岁所需秒数(8 分钟),1 岁后裹布解开
SCHOOL_TIME = 300          # 学习 300 秒毕业,获得学生卡
ADULT_PERIOD = 300         # 毕业后 300 秒变成成年猫(可卖)
BABY_SWADDLE = True        # 刚出生裹毛巾布
SCHOOL_BAG_REQUIRED = False # 上学不强制买文具,没有也能学(有文具加速)
SCHOOL_BAG_BONUS = 0.10    # 每件文具 +10% 学习速度(最多 90%)

# 造经验机(家电):购买后自动产生经验
EXP_MACHINE_INTERVAL = 30   # 每 30 秒产一次
EXP_MACHINE_GAIN = 50       # 每次 +50 经验

# 结婚系统:任何成年未婚异性小猫可结婚,婚后雌猫孕周涨满可分娩,无次数/代际限制
COUPLE_PREGNANCY_PERIOD = 30    # 婚后孕周 30 秒涨满(快 10 倍)
MARRIAGE_COST = 50              # 结婚需要 50 经验
# 怀孕显示:孕周 > PREG_BELLY_SHOW 时肚子变大
PREG_BELLY_SHOW = 20       # 孕周 20% 起显肚子
PREG_EMOJI_SHOW = 10       # 孕周 10% 起头顶显示 🤰

# 体检科
CHECKUP_PRICE = 30         # 体检花费(经验)
CHECKUP_HEAL = 15          # 体检恢复健康
CHECKUP_PROTECT = 90       # 体检保护期(秒),期间不会生病

# 宠物商店
SELL_ADULT_PRICE = 5.0     # 卖 1 只成年小猫得 5 元
PETS = [
    dict(id="dog",    name="金毛犬",   price=6.0, emoji="🐶", desc="忠实的好朋友"),
    dict(id="rabbit", name="小兔子",   price=3.0, emoji="🐰", desc="蹦蹦跳跳"),
    dict(id="hamster", name="仓鼠",    price=2.0, emoji="🐹", desc="圆滚滚"),
    dict(id="parrot", name="鹦鹉",     price=4.0, emoji="🦜", desc="会学猫叫"),
    dict(id="turtle", name="小乌龟",   price=5.0, emoji="🐢", desc="慢慢来"),
    dict(id="cat2",   name="布偶猫",   price=8.0, emoji="🐱", desc="家里再多一只猫"),
]
PET_BY_ID = {p["id"]: p for p in PETS}

# 自动说话(每 30~60 秒随机一句)
AUTO_LINES = [
    "喵呜~ 今天天气真好呀 ☀️",
    "呼噜呼噜… 好舒服~",
    "主人,陪我玩一会儿嘛~",
    "喵喵?晚饭吃什么呀?",
    "我今天抓到了好多老鼠!",
    "宝宝们在长大,好幸福呀~",
    "洗澡?不要不要~ 喵!",
    "窗外的鸟叫真好听 🐦",
    "喵~ 我爱你哦主人 ❤️",
]

# 公交站票价(元)
FARE_BABY = 0.0            # 宝宝免费
FARE_STUDENT = 0.5         # 学生卡半价
FARE_ADULT = 1.0           # 成年猫全价

FEED_SAT = 35

# ---------------- 存档 ----------------
def get_save_file():
    """Android 上使用应用私有目录(可写);桌面用脚本所在目录。
    惰性求值:每次读写时调用,确保 App 已创建、user_data_dir 可用。"""
    import sys as _sys
    try:
        if getattr(_sys, "android_runtime", False) or os.environ.get("ANDROID_ARGUMENT"):
            from kivy.app import App
            app = App.get_running_app()
            if app is not None:
                d = app.user_data_dir
                os.makedirs(d, exist_ok=True)
                return os.path.join(d, "cat_save.json")
    except Exception:
        pass
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "cat_save.json")


# 兼容旧引用(模块加载时求值,Android 上为兜底值;实际读写用 get_save_file())
SAVE_FILE = get_save_file()
SAVE_INTERVAL = 2.0

# ---------------- 服饰目录 ----------------
# premium = 至臻皮肤(600+ 经验,带金色/发光效果)
WARDROBE = [
    # 衣服
    dict(id="dress_pink",    name="粉色连衣裙",   category="top",    price=75, desc="公主必备"),
    dict(id="dress_white",   name="白色纱裙",     category="top",    price=135, desc="婚礼主角"),
    dict(id="dungaree_blue", name="蓝色背带裤",   category="top",    price=90, desc="牛仔风"),
    dict(id="apron_yellow",  name="黄色小围裙",   category="top",    price=105, desc="做饭美美哒"),
    dict(id="hoodie_purple", name="紫色卫衣",     category="top",    price=120, desc="慵懒周末"),
    dict(id="sailor_red",    name="红色水手服",   category="top",    price=150, desc="扬帆起航"),
    dict(id="dino_green",    name="恐龙连体衣",   category="top",    price=180, desc="吼吼吼"),
    # 裤子
    dict(id="jeans_blue",    name="蓝色牛仔裤",   category="bottom", price=60, desc="百搭款"),
    dict(id="shorts_black",  name="黑色短裤",     category="bottom", price=72, desc="运动风"),
    dict(id="pants_khaki",   name="卡其休闲裤",   category="bottom", price=84, desc="文艺范"),
    dict(id="pants_gray",    name="灰色运动裤",   category="bottom", price=78, desc="居家必备"),
    # 鞋子
    dict(id="shoe_red",      name="红色小皮鞋",   category="shoe",   price=36, desc="蹦蹦跳跳"),
    dict(id="shoe_white",    name="白色运动鞋",   category="shoe",   price=45, desc="跑得更快"),
    dict(id="shoe_blue",     name="蓝色运动鞋",   category="shoe",   price=54, desc="活力蓝"),
    dict(id="boot_yellow",   name="黄色雨靴",     category="shoe",   price=54, desc="下雨天"),
    dict(id="sandals_green", name="绿色凉鞋",     category="shoe",   price=60, desc="清爽"),
    dict(id="boot_brown",    name="棕色小靴",     category="shoe",   price=66, desc="秋冬百搭"),
    # 帽子
    dict(id="cap_yellow",    name="黄色鸭舌帽",   category="hat",    price=45, desc="阳光男孩"),
    dict(id="beret_red",     name="红色贝雷帽",   category="hat",    price=60, desc="艺术家"),
    dict(id="sunhat_blue",   name="蓝色遮阳帽",   category="hat",    price=75, desc="遮阳又可爱"),
    dict(id="beanie_pink",   name="粉色毛线帽",   category="hat",    price=84, desc="暖呼呼"),
    dict(id="wizard_purple", name="紫色巫师帽",   category="hat",    price=114, desc="魔法喵师"),
    # 首饰
    dict(id="necklace_pearl", name="珍珠项链",    category="acc",    price=54, desc="优雅"),
    dict(id="collar_red",    name="红色项圈",     category="acc",    price=60, desc="乖孩子"),
    dict(id="bell_gold",     name="金色铃铛",     category="acc",    price=75, desc="叮当响"),
    dict(id="necklace_blue", name="蓝水晶项链",   category="acc",    price=105, desc="闪闪发光"),
    dict(id="crown_silver",  name="银色小皇冠",   category="acc",    price=150, desc="小公主"),
    # 至臻皮肤(600+)
    dict(id="prem_star",    name="星光礼裙",     category="premium", price=210, desc="✨ 至臻:星光织成"),
    dict(id="prem_gold",    name="金冠圣装",     category="premium", price=240, desc="👑 至臻:金色传说"),
    dict(id="prem_unicorn", name="彩虹独角兽装", category="premium", price=270, desc="🦄 至臻:梦幻彩虹"),
    dict(id="prem_dark",    name="暗夜金斗篷",   category="premium", price=300, desc="🌙 至臻:暗夜贵族"),
    dict(id="prem_angel",   name="天使圣装",     category="premium", price=360, desc="😇 至臻:圣光降临"),
]
WARDROBE_BY_ID = {w["id"]: w for w in WARDROBE}
SKIRT_IDS = {"dress_pink", "dress_white", "prem_star", "prem_angel"}
PREMIUM_IDS = {"prem_star", "prem_gold", "prem_unicorn", "prem_dark", "prem_angel"}
# 女性专属(裙子):只有母猫能穿
GIRL_ONLY_IDS = SKIRT_IDS | {"necklace_pearl", "necklace_blue"}

# ---------------- 家具目录 ----------------
FURNITURE = [
    dict(id="sofa",     name="大沙发",   price=84, desc="窝着看剧最舒服"),
    dict(id="chair",    name="单人沙发", price=66, desc="一个人的角落"),
    dict(id="table",    name="餐桌",     price=78, desc="全家一起吃饭"),
    dict(id="desk",     name="书桌",     price=72, desc="工作学习两不误"),
    dict(id="bed",      name="大床",     price=105, desc="滚来滚去"),
    dict(id="crib",     name="婴儿床",   price=120, desc="小宝宝的家"),
    dict(id="rug",      name="毛绒地毯", price=54, desc="软软的"),
    dict(id="plant",    name="绿植",     price=45, desc="净化空气"),
    dict(id="bookshelf", name="书架",    price=90, desc="满满的书香"),
    dict(id="lamp",     name="落地灯",   price=60, desc="暖光伴读"),
    dict(id="painting", name="挂画",     price=51, desc="艺术气息"),
]
FURNITURE_BY_ID = {f["id"]: f for f in FURNITURE}



# ---------------- 交通工具目录 ----------------
VEHICLES = [
    dict(id="scooter",  name="滑板车",   price=80,  desc="入门首选,风吹过耳朵"),
    dict(id="bike",     name="自行车",   price=150, desc="健康环保,铃铛叮当"),
    dict(id="moto",     name="小摩托",   price=250, desc="酷酷的猫骑士"),
    dict(id="e_bike",   name="电动车",   price=300, desc="不用蹬,真香"),
    dict(id="kart",     name="卡丁车",   price=350, desc="迷你赛车的快乐"),
    dict(id="car",      name="小汽车",   price=500, desc="全家出游兜风"),
    dict(id="bus",      name="公交车",   price=400, desc="上班上学都靠它"),
    dict(id="school_bus", name="专属校车", price=700, desc="送宝宝上学不迟到"),
]
VEHICLE_BY_ID = {v["id"]: v for v in VEHICLES}

# ---------------- 科技目录(家电便宜 50%) ----------------
TECH = [
    dict(id="phone",    name="智能手机", price=33, desc="拍猫猫必备"),
    dict(id="tablet",   name="平板电脑", price=45, desc="躺着刷剧"),
    dict(id="computer", name="台式电脑", price=60, desc="程序员猫的家"),
    dict(id="tv",       name="大电视",   price=52, desc="全家看猫片"),
    dict(id="fridge",   name="冰箱",     price=75, desc="囤小鱼干"),
    dict(id="washer",   name="洗衣机",   price=67, desc="干净猫猫"),
    dict(id="ac",       name="空调",     price=90, desc="冬暖夏凉"),
    dict(id="robot",    name="扫地机器人", price=48, desc="自己会跑"),
    dict(id="exp_machine", name="造经验机", price=200, desc="⚙️ 每 30 秒自动产 50 经验"),
]
TECH_BY_ID = {t["id"]: t for t in TECH}

# 初始自带家具/科技(场景基础布置)
INITIAL_ITEMS = ["sofa", "tv", "crib", "table", "rug", "plant", "birdcage", "fishbowl"]
INITIAL_TECH = ["tv"]
# 场景装饰(不可购买):鸟笼 / 鱼缸 / 两张宝宝小桌
SCENE_DECOR = ["birdcage", "fishbowl", "baby_table_1", "baby_table_2", "baby_table_3"]

# ---------------- 食物/零食目录 ----------------
FOODS = {
    "cat_food":  dict(name="猫粮",     price=6,  sat=35, happy=0,  desc="基础口粮"),
    "fish_dry":  dict(name="小鱼干",   price=9,  sat=50, happy=5,  desc="鲜香可口"),
    "meat_bar":  dict(name="鸡肉条",   price=12,  sat=40, happy=10, desc="高蛋白"),
    "can_food":  dict(name="金枪鱼罐头", price=16, sat=65, happy=5, desc="豪华大餐"),
    "biscuit":   dict(name="小鱼饼干", price=6,  sat=10, happy=15, desc="小零嘴"),
    "catnip":    dict(name="猫薄荷",   price=10,  sat=5,  happy=25, desc="快乐源泉"),
    "cream":     dict(name="奶油泡芙", price=14,  sat=15, happy=25, desc="甜品时间"),
    "bird_egg":  dict(name="小鸟蛋",   price=1,   sat=20, happy=5,  desc="小鸟下的蛋,营养"),
    "cat_milk":  dict(name="猫奶",     price=1,   sat=40, happy=8,  desc="猫妈妈的奶,宝宝专用"),
}
FOOD_BY_ID = FOODS

# ---------------- 药品目录(按科室) ----------------
# dept: 所属科室;cures: 能治的病种(None = 通用保健,不治病)
MEDICINES = {
    "cold_pill":      dict(name="感冒药",   price=15, heal=30, dept="内科", cures="cold",     desc="治感冒"),
    "stomach_pill":   dict(name="肠胃药",   price=18, heal=25, dept="内科", cures="stomach",  desc="治肠胃炎"),
    "wound_pill":     dict(name="跌打药",   price=20, heal=35, dept="外科", cures="wound",    desc="治摔伤"),
    "infection_pill": dict(name="消炎药",   price=24, heal=30, dept="外科", cures="infection", desc="治感染"),
    "probiotic":      dict(name="益生菌",   price=15, heal=20, dept="儿保", cures="baby",     desc="宝宝肠胃"),
    "vitamin":        dict(name="维生素片", price=24, heal=20, dept="内科", cures=None,       desc="日常保健"),
    "nutrition":      dict(name="营养膏",   price=36, heal=45, dept="内科", cures=None,       desc="大病初愈"),
    "tonic":          dict(name="特级补品", price=60, heal=70, dept="内科", cures=None,       desc="立竿见影"),
}
MEDICINE_BY_ID = MEDICINES
# 病种 -> (名称, 科室, 提示)
ILLNESS_TYPES = {
    "cold":      ("感冒",   "内科", "打喷嚏流鼻涕,去内科开点感冒药吧"),
    "stomach":   ("肠胃炎", "内科", "肚子咕噜咕噜痛,去内科看看"),
    "wound":     ("摔伤",   "外科", "跑太快摔了一跤,去外科上药"),
    "infection": ("感染",   "外科", "伤口有点发炎,去外科开消炎药"),
    "baby":      ("儿保不适", "儿保", "宝宝不舒服,去儿保科开益生菌"),
}
ILLNESS_NAMES = {k: v[0] for k, v in ILLNESS_TYPES.items()}
ILLNESS_DEPT = {k: v[1] for k, v in ILLNESS_TYPES.items()}
ILLNESS_LINES = {k: v[2] for k, v in ILLNESS_TYPES.items()}
ADULT_ILLNESS_POOL = ["cold", "stomach", "wound", "infection"]

# ---------------- 文具目录 ----------------
STATIONERY = [
    dict(id="pencil",     name="铅笔",       price=20, desc="写字必备"),
    dict(id="eraser",     name="橡皮",       price=15, desc="擦擦改改"),
    dict(id="ruler",      name="尺子",       price=18, desc="画直线"),
    dict(id="sharpener",  name="卷笔刀",     price=15, desc="削尖铅笔"),
    dict(id="crayon",     name="蜡笔",       price=24, desc="画彩虹"),
    dict(id="marker",     name="彩笔",       price=24, desc="画画涂涂"),
    dict(id="notebook",   name="笔记本",     price=28, desc="记笔记"),
    dict(id="case",       name="文具盒",     price=30, desc="装文具"),
    dict(id="watercup",   name="小水杯",     price=22, desc="喝水解渴"),
    dict(id="bag",        name="小书包",     price=15, desc="🎒 上学必备"),
]
STATIONERY_BY_ID = {s["id"]: s for s in STATIONERY}
STATIONERY_ACCEL_IDS = {s["id"] for s in STATIONERY if s["id"] != "bag"}

# ---------------- 台词 ----------------
FEED_LINES  = ["喵呜~ 真好吃!", "吧唧吧唧… 好吃!(>ω<)", "谢谢主人,肚肚圆滚滚啦"]
PET_LINES   = ["呼噜呼噜… 好舒服~", "喵~ 主人的手手最温暖了", "咕噜咕噜,再摸一会儿嘛"]
PLAY_LINES  = ["毛线球冲鸭!", "喵喵喵!追不上我~", "主人陪我玩最开心啦!"]
WAKE_LINES  = ["喵~ 睡饱啦,精神满满!", "Zzz… 啊,天亮了吗?早上好~"]
CATCH_LINES = ["喵呜!抓到啦!", "嘿嘿,老鼠哪里跑!", "今天的晚饭有着落啦~"]
GOLD_LINES  = ["哇!!是金老鼠!", "金色的!发财啦!"]
NO_ENERGY   = "没力气啦,休息一下再抓吧 Zzz"
NO_FOOD     = "背包里没有吃的了,去市场买点或抓老鼠吧!"
SICK_MSG    = "生病了…先去医院看看吧 😷"
NO_MONEY    = "钱不够哦,去银行换点吧"
NO_BREED    = "暂时不能生宝宝哦"
POST_DELIVERY_MSG = "母猫产后休养中,让她歇一会儿吧 🤱"
LEVELUP_MSG = "🎉 升到 Lv.{lv} 啦!称号:{title}"
FULL_SAT    = "喵?肚子好饱,吃不下了 (>ω<)"

# ---------------- 等级称号 ----------------
LEVEL_TITLES = [
    (9,   "小奶猫"), (19,  "顽皮猫"), (29,  "捕鼠能手"), (39,  "猫咪冒险家"),
    (49,  "森林猫王"), (59,  "捕鼠大师"), (69,  "猫咪贵族"), (79,  "猫界传说"),
    (89,  "猫咪霸主"), (100, "猫神"),
]

def level_title(level):
    t = "小奶猫"
    for limit, name in LEVEL_TITLES:
        if level >= limit:
            t = name
    return t
