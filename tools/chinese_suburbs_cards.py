"""为什么华人都住在这几个区：首页地图、移民时间线、五个区各一页、规律总结。
用法：python3 tools/chinese_suburbs_cards.py 图片目录 老杨图标目录 输出目录"""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
Image.MAX_IMAGE_PIXELS = None
W, H = 1080, 1440
SRC, ICONS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
BG = (244, 240, 230); INK = (24, 28, 40); BLUE = (14, 52, 108); GREY = (96, 92, 86); RED = (196, 52, 40); WATER = (196, 220, 232)
def zh(s, w="Bold"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def en(s): return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", s)
def crop(spec, w, h):
    spec = list(spec) if isinstance(spec, tuple) else [spec]
    name, fx, fy, z = spec + [.5, .5, 1.0][len(spec) - 1:]
    im = ImageOps.exif_transpose(Image.open(f"{SRC}/{name}")).convert("RGB")
    s = max(w / im.width, h / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    return ImageEnhance.Color(im.crop((round(x), round(y), round(x) + w, round(y) + h)).filter(ImageFilter.UnsharpMask(1.5, 30, 2))).enhance(1.05)
def icon(img, pose, x, y, h):
    ic = Image.open(f"{ICONS}/{pose}.png").convert("RGBA"); ic = ic.resize((round(ic.width * h / ic.height), h), Image.LANCZOS)
    img = img.convert("RGBA"); sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 255), (x + 4, y + 6), ic.split()[3].point(lambda v: int(v * .3)))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8))); img.alpha_composite(ic, (x, y)); return img.convert("RGB")
def wrap(text, font, width):
    toks = re.findall(r"[A-Za-z0-9&'.%$,:\-]+|.", text); lines, cur = [], ""
    for t in toks:
        if font.getlength(cur + t) > width and cur and t not in "，。、！？）：；%": lines.append(cur); cur = t.lstrip()
        else: cur += t
    if cur: lines.append(cur)
    return lines

SUB = {"车士活": ("Chatswood", 151.180, -33.797), "伊士活": ("Eastwood", 151.081, -33.791), "Rhodes": ("Rhodes", 151.087, -33.830),
       "宝活": ("Burwood", 151.104, -33.877), "好市围": ("Hurstville", 151.102, -33.967)}
CBD = (151.208, -33.869)
SEA = [(151.29, -33.70), (151.29, -34.05), (151.24, -34.05), (151.24, -33.99), (151.21, -33.995), (151.17, -34.0), (151.13, -33.99),
       (151.15, -33.965), (151.20, -33.955), (151.235, -33.965), (151.255, -33.93), (151.275, -33.89), (151.28, -33.85), (151.29, -33.80), (151.29, -33.70)]
HARB = [(151.285, -33.845), (151.26, -33.84), (151.235, -33.852), (151.21, -33.857), (151.18, -33.845), (151.15, -33.84), (151.12, -33.835),
        (151.09, -33.83), (151.06, -33.825), (151.03, -33.82), (151.00, -33.818)]

def locator(img, cur):
    d = ImageDraw.Draw(img); x0, y0, x1, y1 = 840, 24, 1040, 214
    d.rectangle((x0, y0, x1, y1), fill=(232, 226, 212), outline=GREY, width=2)
    lo0, lo1, la0, la1 = 151.04, 151.30, -33.76, -34.00
    X = lambda lo: x0 + 8 + (lo - lo0) / (lo1 - lo0) * (x1 - x0 - 16); Y = lambda la: y0 + 8 + (la - la0) / (la1 - la0) * (y1 - y0 - 16)
    d.polygon([(max(X(a), x0 + 2), Y(b)) for a, b in SEA if Y(b) >= y0], fill=WATER)
    p = [(X(a), Y(b)) for a, b in HARB if X(a) >= x0]
    for k in range(len(p) - 1): d.line((p[k], p[k + 1]), fill=WATER, width=6)
    d.rectangle((x0, y0, x1, y1), outline=GREY, width=2)
    cx, cy = X(CBD[0]), Y(CBD[1]); d.rectangle((cx - 6, cy - 6, cx + 6, cy + 6), fill=INK)
    for k, (e, lo, la) in SUB.items():
        x, y = X(lo), Y(la); r = 13 if k == cur else 7
        d.ellipse((x - r, y - r, x + r, y + r), fill=RED if k == cur else (150, 146, 138), outline="white", width=2)

def header(img, title, sub, cur=None):
    d = ImageDraw.Draw(img); d.text((60, 44), title, font=zh(76, "Black"), fill=INK); d.text((62, 150), sub, font=zh(38, "Medium"), fill=GREY)
    if cur: locator(img, cur)

def stats(d, y, items):
    n = len(items); gap = 16; w = (W - 120 - gap * (n - 1)) // n
    for i, (num, lab) in enumerate(items):
        x = 60 + i * (w + gap); d.rounded_rectangle((x, y, x + w, y + 170), radius=14, fill=BLUE)
        fn = en(78); d.text((x + (w - fn.getlength(num)) / 2, y + 18), num, font=fn, fill="white")
        fl = zh(32, "Medium"); d.text((x + (w - fl.getlength(lab)) / 2, y + 114), lab, font=fl, fill=(210, 222, 240))

def tag(img, x, y, t, col):
    d = ImageDraw.Draw(img); f = zh(34, "Black"); w = f.getlength(t) + 32
    d.rectangle((x, y, x + w, y + 54), fill=col); d.text((x + 16, y + 4), t, font=f, fill="white")

def page(fn, key, title, sub, photo, st, text, old=None, oldtag=""):
    img = Image.new("RGB", (W, H), BG); header(img, title, sub, key); d = ImageDraw.Draw(img)
    f = zh(34, "Medium"); lines = wrap(text, f, 960)
    ph = H - 240 - 200 - len(lines) * 52 - 50
    hw = (W - 140) // 2
    img.paste(crop(old, hw, ph).convert("L").convert("RGB"), (60, 240)); img.paste(crop(photo, hw, ph), (80 + hw, 240))
    tag(img, 60, 240 + ph - 54, oldtag, INK); tag(img, 80 + hw, 240 + ph - 54, "今天", RED)
    y = 240 + ph + 20
    stats(d, y, st); y += 200
    for ln in lines: d.text((60, y), ln, font=f, fill=INK); y += 52
    assert y < H - 8 and ph > 380, (fn, y, ph)
    img.save(f"{OUT}/{fn}", quality=93)

P = [
 ("02.jpg", "车士活", "车士活 Chatswood", "左：1936年的Kings戏院", ("chats1.jpg", .5, .5),
  [("23.3%", "在家说普通话"), ("12.3%", "在家说粤语"), ("5.5%", "香港出生")],
  "车士活1876年开始有人定居，1890年北岸铁路通车，1932年海港大桥通车后人口越来越多。华人在这里很早就有根：1885年的悉尼名录里，华人菜园就分布在车士活所在的Willoughby。1980年代起，香港、马来西亚、新加坡来的粤语专业人士家庭多选北岸。1990年代车士活开始盖高楼，吸引了更多华人和韩国人。2001年左右，购物区已经有50家香港人开的店，1996年建了华人文化中心。",
  ("old_chats1936.jpg", .5, .5), "1936"),
 ("03.jpg", "伊士活", "伊士活 Eastwood", "左：1947年Odeon戏院里看电影的孩子", ("eastwood2.jpg", .5, .5),
  [("48.8%", "华人血统"), ("28.3%", "在家说普通话"), ("14.5%", "在家说粤语")],
  "伊士活火车站1886年开通。100年前这里是果园和菜园，1920年代末已经有14个华人菜园。左边照片里的Odeon戏院，1976年拆了改成今天的伊士活购物中心。1960年代先来的是意大利人和希腊人，1980年代初起华人和韩国人陆续搬来。2001年说粤语的居民还比说普通话的多，到2011年反了过来。",
  ("old_eastwood1947.jpg", .5, .45), "1947"),
 ("04.jpg", "好市围", "好市围 Hurstville", "左：1951年的Forest Road", ("hurst1.jpg", .5, .55),
  [("47.1%", "华人血统"), ("26.1%", "在家说普通话"), ("16.2%", "在家说粤语")],
  "好市围1884年通火车，Forest Road是一百多年的老商业街。1960年代末起，希腊人、意大利人从内城往南搬到这里，后来又来了前南斯拉夫的移民，那时是一个工薪阶层的区。1980年代末开始有中国大陆出生的人搬来，1990年代来了很多香港移民，2000年后大陆移民快速增加。2001年中国出生的居民占16%，2016年升到37%。",
  ("old_hurst1951.jpg", .5, .5), "1951"),
 ("05.jpg", "宝活", "宝活 Burwood", "左：1938年Astor戏院的大堂", ("burwood1.jpg", .5, .5),
  [("48.3%", "华人血统"), ("32.1%", "在家说普通话"), ("10.8%", "在家说粤语")],
  "宝活是悉尼最老的郊区之一，1855年通火车时是悉尼到Parramatta线上最早的6个站之一。二战后，Burwood Road旁边的老宅Woodstock做过移民宿舍。学者发现，从中国北方、华东和上海来的留学生，以及1980年代末获准留下的那批中国学生，很多住进了宝活、Canterbury和Concord一带。今天在家说普通话的居民占三成以上，是这几个区里最高的。",
  ("old_burwood1938.jpg", .5, .5), "1938"),
 ("06.jpg", "Rhodes", "Rhodes", "左：2009年，化工厂原址还在清理污染", ("rhodes1.jpg", .5, .5),
  [("43.2%", "华人血统"), ("30.2%", "在家说普通话"), ("11.6%", "韩裔")],
  "1911年这里建起一家大型铸铁管厂，工业从此进来。从1930年代到1980年代中期，Rhodes西边一直是化工厂。1986年ICI工厂爆炸，5个工人遇难。工厂搬走后，原址花了很多年清理污染，2000年代起建起大片公寓，如今四成多居民有华人血统。靠近火车站、全是新公寓，是新一代华人区的样子。",
  ("old_rhodes2009.jpg", .5, .5), "2009"),
]
for fn, key, title, sub, ph_, st, tx, od, ot in P: page(fn, key, title, sub, ph_, st, tx, od, ot)

# 01 时间线
img = Image.new("RGB", (W, H), BG); header(img, "华人是怎么来的", "1970年代到今天，三波移民"); d = ImageDraw.Draw(img)
T = [("1970s", "白澳政策取消", "第一批新移民里，大约八成来自香港、台湾和东南亚，两成来自中国大陆。"),
     ("1980s", "技术和商业移民增加", "香港、台湾的技术移民和商业移民在1980、1990年代大幅增加。"),
     ("1980年代末", "中国留学生获准留下", "1980年代末，澳洲政府给了当时在澳的2万名中国留学生临时居留，后来很多人留了下来。"),
     ("2000s", "大陆移民快速增加", "今天在中国大陆出生的人，是澳洲第二大海外出生群体，仅次于英国出生的人。")]
y = 270; x = 150
d.line((x, y + 20, x, y + 4 * 270 - 120), fill=BLUE, width=8)
for yr, t, s in T:
    d.ellipse((x - 26, y - 6, x + 26, y + 46), fill=RED, outline="white", width=4)
    d.text((x + 60, y - 18 if yr.isascii() else y - 24), yr, font=en(56) if yr.isascii() else zh(56, "Black"), fill=RED); d.text((x + 60, y + 50), t, font=zh(48, "Black"), fill=INK)
    yy = y + 118
    for ln in wrap(s, zh(34, "Medium"), 820): d.text((x + 60, yy), ln, font=zh(34, "Medium"), fill=GREY); yy += 50
    y += 270
img.save(f"{OUT}/01.jpg", quality=93)

# 07 规律
img = Image.new("RGB", (W, H), BG); header(img, "华人选区的三条规律", "研究悉尼华人分布的学者总结"); d = ImageDraw.Draw(img)
R = [("1", "跟着同乡和方言走", "说粤语的香港、东南亚家庭多去北岸，从华北、华东来的说普通话的移民多去Burwood一带。同乡多的地方，买菜、看病、找工作都方便。"),
     ("2", "跟着学校和补习班走", "伊士活的老居民说，很多人是看中这里学生成绩好才搬来的；好市围火车站边上有二十几家补习班。有孩子的家庭会为了上学搬家。"),
     ("3", "跟着火车站走", "这几个华人区都长在大火车站旁边：宝活1855年、好市围1884年、伊士活1886年、车士活1890年通火车。有车站就有商圈，进城上班也方便。")]
y = 270
for n, t, s in R:
    d.ellipse((60, y, 160, y + 100), fill=BLUE); d.text((110 - en(60).getlength(n) / 2, y + 16), n, font=en(60), fill="white")
    d.text((190, y + 14), t, font=zh(54, "Black"), fill=INK); yy = y + 120
    for ln in wrap(s, zh(36, "Medium"), 830): d.text((190, yy), ln, font=zh(36, "Medium"), fill=GREY); yy += 56
    y = yy + 60
assert y < H, y
img.save(f"{OUT}/07.jpg", quality=93)

# 首页：地图+数字
c = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(c)
d.text((60, 60), "为什么华人", font=zh(120, "Black"), fill=INK); d.text((60, 210), "都住在这几个区", font=zh(120, "Black"), fill=RED)
d.text((64, 370), "在家说普通话或粤语的居民比例", font=zh(44, "Bold"), fill=GREY)
lo0, lo1, la0, la1 = 150.98, 151.30, -33.74, -34.01; y0, y1 = 430, 1400
X = lambda lo: 30 + (lo - lo0) / (lo1 - lo0) * (W - 60); Y = lambda la: y0 + (la - la0) / (la1 - la0) * (y1 - y0)
d.polygon([(X(a), Y(b)) for a, b in SEA], fill=WATER)
p = [(X(a), Y(b)) for a, b in HARB]
for k in range(len(p) - 1): d.line((p[k], p[k + 1]), fill=WATER, width=max(8, 26 - 2 * k))
cx, cy = X(CBD[0]), Y(CBD[1]); d.rectangle((cx - 12, cy - 12, cx + 12, cy + 12), fill=INK); d.text((cx - 30, cy + 18), "市中心", font=zh(34, "Bold"), fill=INK)
PCT = {"车士活": "35.6%", "伊士活": "42.8%", "Rhodes": "38.5%", "宝活": "42.9%", "好市围": "42.3%"}
OFFS = {"车士活": (30, -60), "伊士活": (-180, -150), "Rhodes": (-250, -10), "宝活": (30, -40), "好市围": (30, -70)}
for k, (e, lo, la) in SUB.items():
    x, y = X(lo), Y(la); d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=RED, outline="white", width=3)
    ox, oy = OFFS[k]; bx, by = x + ox, y + oy; f = zh(52, "Black"); fp = en(56)
    w = max(f.getlength(k), fp.getlength(PCT[k])) + 36
    d.rounded_rectangle((bx, by, bx + w, by + 140), radius=12, fill=BLUE)
    d.text((bx + 18, by + 6), k, font=f, fill="white"); d.text((bx + 18, by + 72), PCT[k], font=fp, fill=(255, 214, 64))
icon(c, "13_探店", W - 220, 1210, 180).save(f"{OUT}/cover.jpg", quality=93)
print("ok")

# ===== 深度分析页 =====
def tpage(title, sub):
    img = Image.new("RGB", (W, H), BG); header(img, title, sub); return img, ImageDraw.Draw(img)
def para(d, y, text, size=38, color=INK, width=960, lh=None):
    f = zh(size, "Medium"); lh = lh or int(size * 1.55)
    for ln in wrap(text, f, width): d.text((60, y), ln, font=f, fill=color); y += lh
    return y

# A01 三步
img, d = tpage("华人区是怎么形成的", "三步：种子、分流、滚雪球")
steps = [("种子", "1960年代，一些区已经住着少量华人，很多跟早年的华人菜园有关。"),
         ("分流", "1980年代以后的新移民，按方言和出身，去了不同的区。"),
         ("滚雪球", "先有人，再有店；店多了、学校好了，又吸引更多人搬来。")]
y = 270
for i, (t, s) in enumerate(steps):
    d.rounded_rectangle((60, y, W - 60, y + 300), radius=18, fill=(232, 226, 212))
    d.ellipse((90, y + 40, 210, y + 160), fill=BLUE); d.text((150 - en(70).getlength(str(i + 1)) / 2, y + 58), str(i + 1), font=en(70), fill="white")
    d.text((240, y + 50), t, font=zh(64, "Black"), fill=INK)
    yy = y + 150
    for ln in wrap(s, zh(36, "Medium"), 760): d.text((240, yy), ln, font=zh(36, "Medium"), fill=GREY); yy += 52
    y += 330
para(d, y + 10, "下面一步一步看。", 38)
img.save(f"{OUT}/a01.jpg", quality=93)

# A03 种子：1966年华人最多的十个区
img, d = tpage("第一步：种子", "1966年，华人最多的地方政府区里的9个")
L = [("Canterbury", 151.117, -33.912), ("Marrickville", 151.165, -33.928), ("Ashfield", 151.135, -33.890),
     ("Rockdale", 151.138, -33.952), ("Waverley", 151.255, -33.893), ("Willoughby", 151.190, -33.800), ("Ku-ring-gai", 151.150, -33.73),
     ("Burwood", 151.104, -33.877), ("Ryde", 151.105, -33.815)]
NOTE = {"Willoughby": "今天的车士活", "Ryde": "伊士活一部分", "Rockdale": "好市围旁边", "Burwood": "宝活"}
lo0, lo1, la0, la1 = 151.02, 151.30, -33.70, -33.99; y0, y1 = 240, 1060
X = lambda lo: 40 + (lo - lo0) / (lo1 - lo0) * (W - 80); Y = lambda la: y0 + (la - la0) / (la1 - la0) * (y1 - y0)
d.polygon([(X(a), Y(b)) for a, b in SEA], fill=WATER)
p = [(X(a), Y(b)) for a, b in HARB]
for k in range(len(p) - 1): d.line((p[k], p[k + 1]), fill=WATER, width=max(8, 24 - 2 * k))
for n, lo, la in L:
    x, y = X(lo), Y(la); hot = n in NOTE
    d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=RED if hot else BLUE, outline="white", width=3)
    f = en(30); d.text((x + 20, y - 34), n, font=f, fill=INK)
    if hot: d.text((x + 20, y + 2), NOTE[n], font=zh(30, "Bold"), fill=RED)
y = para(d, 1090, "那时白澳政策还没完全取消，悉尼华人不多，但已经散在这些区。很多小聚居点跟早年的华人菜园有关：1885年的悉尼名录里，华人菜园就分布在Willoughby、Canterbury、Marrickville一带。1951年起来读书的东南亚、香港学生，不少也留了下来。后来的新移民，很多就落在这些已经有华人的地方。", 34)
assert y < H, y
img.save(f"{OUT}/a03.jpg", quality=93)

# A04 分流
img, d = tpage("第二步：按方言和出身分流", "学者Burnley在2001年的研究发现")
rows = [("香港、马来西亚、新加坡来的\n粤语专业人士家庭", "上北岸\nHornsby等"),
        ("大陆来的粤语移民\n多是技术移民的亲属和80年代末留下的学生", "好市围\nStrathfield等"),
        ("华北、华东和上海来的\n说普通话的留学生", "宝活\nConcord等"),
        ("华南来的收入较低的移民", "Fairfield")]
y = 260
for a, b in rows:
    d.rounded_rectangle((60, y, 600, y + 190), radius=14, fill=(232, 226, 212)); d.rounded_rectangle((690, y, W - 60, y + 190), radius=14, fill=BLUE)
    yy = y + 26
    for ln in a.split("\n"):
        for l2 in wrap(ln, zh(32, "Bold"), 500): d.text((86, yy), l2, font=zh(32, "Bold"), fill=INK); yy += 46
    d.polygon([(612, y + 70), (676, y + 95), (612, y + 120)], fill=RED)
    yy = y + 40
    for k, ln in enumerate(b.split("\n")):
        f = zh(44 if k == 0 else 30, "Black" if k == 0 else "Medium"); d.text((716, yy), ln, font=f, fill="white"); yy += 64 if k == 0 else 44
    y += 215
y = para(d, y + 10, "同一个方言、同一种出身的人住在一起，买菜、看病、找工作都方便。后来的同乡，又顺着这条路找过来。", 34)
assert y < H, y
img.save(f"{OUT}/a04.jpg", quality=93)

# A05 滚雪球
img, d = tpage("第三步：先有人，再有店", "店是结果，不是原因")
img.paste(crop(("eastwood1.jpg", .5, .5), W - 120, 520), (60, 240))
y = para(d, 790, "研究悉尼族裔社区的学者发现，华人超市、餐馆、社团通常是在华人住多了之后才出现的，并不是它们先把人吸引过来。伊士活就是这样：1990年代以前这里还是白人为主的老区，先是开了一两家亚洲小店，后来越开越多，买菜方便了，又有火车站，搬来的华人家庭也越来越多。车士活在2001年左右，购物区已经有50家香港人开的店。店一多，新来的人更愿意住这里，雪球就滚起来了。", 36)
assert y < H, y
img.save(f"{OUT}/a05.jpg", quality=93)

# A06 学校和火车站
img, d = tpage("两个加速器", "学校和火车站")
img.paste(crop(("hurst2.jpg", .5, .5), (W - 140) // 2, 420), (60, 240)); img.paste(crop(("chats1.jpg", .5, .5), (W - 140) // 2, 420), (80 + (W - 140) // 2, 240))
y = 700
d.text((60, y), "学校", font=zh(54, "Black"), fill=RED); y += 80
y = para(d, y, "在伊士活住了多年的居民说，很多人搬来是看中这里的学生成绩好。好市围火车站周围至少有二十几家补习班，放学后和周六，全悉尼的华人家庭都会送孩子过来。", 34)
y += 20; d.text((60, y), "火车站", font=zh(54, "Black"), fill=RED); y += 80
y = para(d, y, "这几个华人区都是围着大火车站长出来的：好市围站1884年开通，伊士活站1886年开通，镇中心就沿着车站发展。有车站就有商圈，坐火车进城上班也方便。", 34)
assert y < H, y
img.save(f"{OUT}/a06.jpg", quality=93)

# A07 换代：粤语变普通话
img, d = tpage("粤语区，变成了普通话区", "在家说粤语和普通话的居民比例")
data = [("好市围", 2001, 18, 11), ("好市围", 2016, 18, 32), ("伊士活", 2001, 13, 6), ("伊士活", 2016, 15, 25)]
y = 280; bw = 600
d.rectangle((60, y, 100, y + 40), fill=(220, 150, 60)); d.text((112, y - 2), "粤语", font=zh(36, "Bold"), fill=INK)
d.rectangle((260, y, 300, y + 40), fill=BLUE); d.text((312, y - 2), "普通话", font=zh(36, "Bold"), fill=INK)
y += 90
for name, yr, ca, ma in data:
    d.text((60, y + 30), f"{name} {yr}", font=zh(40, "Black"), fill=INK)
    for k, (v, col) in enumerate(((ca, (220, 150, 60)), (ma, BLUE))):
        yy = y + k * 62; d.rectangle((380, yy, 380 + v * 18, yy + 50), fill=col); d.text((390 + v * 18, yy + 4), f"{v}%", font=en(40), fill=INK)
    y += 160
y = para(d, y + 10, "1990年代先到的是香港来的粤语移民，2000年以后大陆来的普通话移民越来越多。第二波人选择落脚的地方，正好是第一波人已经住熟了的区。所以今天走在好市围的Forest Road，既能看到老式港式茶餐厅和烧腊店，也能看到新开的奶茶店。", 34)
assert y < H, y
img.save(f"{OUT}/a07.jpg", quality=93)

# A08 华人区也会搬家
img, d = tpage("华人区也会搬家", "老的会散，新的会长")
img.paste(crop(("rhodes1.jpg", .5, .5), W - 120, 460), (60, 240))
y = para(d, 740, "1966年华人最多的十个区里有东区的Waverley，到了2000年代，那里已经不算华人聚居区了。与此同时，Rhodes、Zetland这些新公寓区冒了出来：Rhodes原来是化工厂，Zetland的华人居民一半以上是学生，因为离市中心的大学近。研究者说，族裔聚居区本来就是临时的，它跟着每一代移民所处的阶段在变。", 36)
assert y < H, y
img.save(f"{OUT}/a08.jpg", quality=93)
print("deep ok")
