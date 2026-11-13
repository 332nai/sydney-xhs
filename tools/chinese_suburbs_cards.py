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

def page(fn, key, title, sub, photo, st, text):
    img = Image.new("RGB", (W, H), BG); header(img, title, sub, key); d = ImageDraw.Draw(img)
    f = zh(36, "Medium"); lines = wrap(text, f, 960)
    ph = H - 240 - 200 - len(lines) * 56 - 60
    img.paste(crop(photo, W - 120, ph), (60, 240)); y = 240 + ph + 20
    stats(d, y, st); y += 200
    for ln in lines: d.text((60, y), ln, font=f, fill=INK); y += 56
    assert y < H - 8 and ph > 420, (fn, y, ph)
    img.save(f"{OUT}/{fn}", quality=93)

P = [
 ("02.jpg", "车士活", "车士活 Chatswood", "北岸最大的商圈和换乘站", ("chats1.jpg", .5, .5),
  [("23.3%", "在家说普通话"), ("12.3%", "在家说粤语"), ("5.5%", "香港出生")],
  "1980年代起，香港、台湾和东南亚来的专业人士家庭多选北岸。研究悉尼华人分布的学者发现，从香港、马来西亚、新加坡来的粤语家庭，很多落脚在Hornsby、Ku-ring-gai这些收入较高的北岸地区。Chatswood是北岸最大的商圈和换乘站，2001年的研究统计，购物区里已经有50家香港人开的店，1996年还建了华人文化中心。"),
 ("03.jpg", "伊士活", "伊士活 Eastwood", "从果园小镇到华人和韩国人的生活区", ("eastwood2.jpg", .5, .5),
  [("48.8%", "华人血统"), ("28.3%", "在家说普通话"), ("14.5%", "在家说粤语")],
  "100年前这里是果园和菜园，到1920年代末已经有14个华人菜园。1980年代起华人和韩国人陆续搬来，2001年说粤语的居民还比说普通话的多，到2011年反了过来。研究者发现，这里学区有几所口碑很好的公立学校，周末开着5所中文学校，离麦考瑞大学不到5公里，是典型的家庭型华人区。"),
 ("04.jpg", "好市围", "好市围 Hurstville", "澳洲华人最集中的城区之一", ("hurst1.jpg", .5, .55),
  [("47.1%", "华人血统"), ("26.1%", "在家说普通话"), ("16.2%", "在家说粤语")],
  "1980年代末开始有中国大陆出生的人搬来，1990年代来了很多香港移民，2000年后大陆移民快速增加。2001年中国出生的居民占16%，2016年升到37%，比澳洲出生的还多。研究者在火车站周围数到至少二十几家补习班，周末全悉尼的华人家庭都会把孩子送来上课。"),
 ("05.jpg", "宝活", "宝活 Burwood", "说普通话的人比例最高", ("burwood1.jpg", .5, .5),
  [("48.3%", "华人血统"), ("32.1%", "在家说普通话"), ("10.8%", "在家说粤语")],
  "学者发现，从中国北方、华东和上海来的留学生，以及1989年后获准留下的那批中国学生，很多住进了Burwood、Canterbury和Concord一带。今天Burwood Road旁边有一条宝活中国城美食街，在家说普通话的居民占三成以上，是这几个区里最高的。"),
 ("06.jpg", "Rhodes", "Rhodes", "化工厂原址上长出来的新华人区", ("rhodes1.jpg", .5, .5),
  [("43.2%", "华人血统"), ("30.2%", "在家说普通话"), ("11.6%", "韩裔")],
  "1930年代到1980年代中期，Rhodes西边是化工厂。工厂搬走后，2000年代原址建起大片公寓，如今四成多居民有华人血统。这类靠近火车站、全是新公寓的区，是新一代华人区的样子，市中心南边的Zetland也是一样，那里一半以上的华人居民是学生。"),
]
for fn, key, title, sub, ph_, st, tx in P: page(fn, key, title, sub, ph_, st, tx)

# 01 时间线
img = Image.new("RGB", (W, H), BG); header(img, "华人是怎么来的", "1970年代到今天，三波移民"); d = ImageDraw.Draw(img)
T = [("1970s", "白澳政策取消", "第一批新移民里，大约八成来自香港、台湾和东南亚，两成来自中国大陆。"),
     ("1980s", "技术和商业移民增加", "香港、台湾的技术移民和商业移民在1980、1990年代大幅增加。"),
     ("1989", "中国留学生获准留下", "澳洲政府给了当时在澳的2万名中国留学生四年临时居留，后来很多人留了下来。"),
     ("2000s", "大陆移民快速增加", "今天在中国大陆出生的人，是澳洲第二大海外出生群体，仅次于英国出生的人。")]
y = 270; x = 150
d.line((x, y + 20, x, y + 4 * 270 - 120), fill=BLUE, width=8)
for yr, t, s in T:
    d.ellipse((x - 26, y - 6, x + 26, y + 46), fill=RED, outline="white", width=4)
    d.text((x + 60, y - 18), yr, font=en(56), fill=RED); d.text((x + 60, y + 50), t, font=zh(48, "Black"), fill=INK)
    yy = y + 118
    for ln in wrap(s, zh(34, "Medium"), 820): d.text((x + 60, yy), ln, font=zh(34, "Medium"), fill=GREY); yy += 50
    y += 270
img.save(f"{OUT}/01.jpg", quality=93)

# 07 规律
img = Image.new("RGB", (W, H), BG); header(img, "华人选区的三条规律", "研究悉尼华人分布的学者总结"); d = ImageDraw.Draw(img)
R = [("1", "跟着同乡和方言走", "说粤语的香港、东南亚家庭多去北岸，从华北、华东来的说普通话的移民多去Burwood一带。同乡多的地方，买菜、看病、找工作都方便。"),
     ("2", "跟着学校和补习班走", "Eastwood学区有好公立学校，周末有中文学校；Hurstville火车站边上二十几家补习班。有孩子的家庭会为了上学搬家。"),
     ("3", "先读书，后落脚", "研究发现，不少在悉尼读完书的华人先住在UNSW所在的Randwick，住满大约十年后，再搬去上北岸、Hurstville和Kogarah。")]
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
