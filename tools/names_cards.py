"""悉尼区名中文译名：路牌风。首页地图、规律卡、来历卡。
用法：python3 tools/names_cards.py 老杨图标目录 输出目录"""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1440
ICONS, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
BG = (244, 240, 230); INK = (24, 28, 40); SIGN = (14, 52, 108); GREY = (92, 90, 86); RED = (196, 52, 40)
def zh(s, w="Bold"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def en(s): return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", s)
def icon(img, pose, x, y, h):
    ic = Image.open(f"{ICONS}/{pose}.png").convert("RGBA"); ic = ic.resize((round(ic.width * h / ic.height), h), Image.LANCZOS)
    img = img.convert("RGBA"); sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 255), (x + 4, y + 6), ic.split()[3].point(lambda v: int(v * .3)))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8))); img.alpha_composite(ic, (x, y)); return img.convert("RGB")
def wrap(text, font, width):
    toks = re.findall(r"[A-Za-z0-9&'.$,:\-]+|.", text); lines, cur = [], ""
    for t in toks:
        if font.getlength(cur + t) > width and cur and t not in "，。、！？）：；": lines.append(cur); cur = t.lstrip()
        else: cur += t
    if cur: lines.append(cur)
    return lines

def sign(d, x, y, w, h, cn, eng):
    d.rounded_rectangle((x, y, x + w, y + h), radius=14, fill=SIGN)
    d.rounded_rectangle((x + 8, y + 8, x + w - 8, y + h - 8), radius=10, outline="white", width=3)
    fc = zh(int(h * .52), "Black"); d.text((x + 34, y + (h - fc.size) / 2 - 10), cn, font=fc, fill="white")
    fe = en(int(h * .26)); d.text((x + w - 34 - fe.getlength(eng), y + (h - fe.size) / 2), eng, font=fe, fill="white")

def rule_card(fn, head, sub, items, text):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    fhd = zh(72, "Black")
    while fhd.getlength(head) > W - 120: fhd = zh(fhd.size - 4, "Black")
    d.text((60, 50), head, font=fhd, fill=INK); d.text((62, 150), sub, font=zh(38, "Medium"), fill=GREY)
    n = len(items); ft = zh(40, "Medium"); tl = wrap(text, ft, 960)
    avail = H - 250 - len(tl) * 60 - 60
    blk = min(avail // n, 420); sh = int(blk * .62)
    y = 250
    for cn, eng, yue, pu in items:
        sign(d, 60, y, W - 120, sh, cn, eng); y += sh + 20
        f = zh(40, "Medium")
        d.text((70, y), f"粤语读 {yue}", font=f, fill=RED); d.text((570, y), f"普通话读 {pu}", font=f, fill=GREY)
        y += blk - sh - 20
    y += 20
    for ln in tl: d.text((60, y), ln, font=ft, fill=INK); y += 60
    assert y < H - 10, (fn, y)
    img.save(f"{OUT}/{fn}", quality=93)

R = [
 ("02.jpg", "wood，念成「活」", "规律一",
  [("车士活", "Chatswood", "che si wut", "che shi huo"), ("伊士活", "Eastwood", "yi si wut", "yi shi huo"), ("宝活", "Burwood", "bou wut", "bao huo")],
  "粤语里「活」读wut，跟英文的wood几乎一样。香港把好莱坞叫「荷里活」，也是这个道理。用普通话一念，wood就变成了huo，所以听着特别怪。"),
 ("03.jpg", "field，念成「菲」", "规律二",
  [("艾士菲", "Ashfield", "ngaai si fei", "ai shi fei"), ("史卓菲", "Strathfield", "si cheuk fei", "shi zhuo fei")],
  "「菲」的粤语和普通话都读fei，所以这组用普通话念也还算像。但「卓」粤语读cheuk，比普通话的zhuo更接近strath。字数也省：老译名只取最响的几个音，Ashfield三个字就够了。"),
 ("04.jpg", "ville念「围」，wick念「域」", "规律三",
  [("好市围", "Hurstville", "hou si wai", "hao shi wei"), ("兰域", "Randwick", "laan wik", "lan yu")],
  "「围」粤语读wai，接近ville；「域」粤语读wik，跟wick几乎一模一样。用普通话读成「兰yu」，就完全听不出是Randwick了。好市围还有好事围、乐士围等写法。"),
 ("05.jpg", "town，干脆翻成「镇」", "规律四",
  [("宾士镇", "Bankstown", "ban si jan", "bin shi zhen"), ("霹雳镇", "Blacktown", "pik lik jan", "pi li zhen")],
  "town本来就是小镇的意思，所以老译名前面音译、后面意译。Bankstown另一个写法叫「班士厅」，厅的粤语读teng，又回到了音译。霹雳读pik lik，是在模仿Black的发音。"),
 ("06.jpg", "老华侨的直接音译", "规律五",
  [("巴拉马打", "Parramatta", "baa laai maa daa", "ba la ma da"), ("马斯觉", "Mascot", "maa si gok", "ma si jue"), ("赖德", "Ryde", "laai dak", "lai de")],
  "这几个是整词音译，粤语念起来跟英文很接近。「觉」粤语读gok，正好对上cot。Ryde还有个更老的译名叫「孻」，粤语读laai，是一个字的地名。"),
]
for r in R: rule_card(*r)

# 07 为什么是粤语
img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
d.text((60, 50), "为什么都是粤语？", font=zh(72, "Black"), fill=INK); d.text((62, 150), "同一个区，两种叫法", font=zh(38, "Medium"), fill=GREY)
rows = [("Chatswood", "车士活", "查茨伍德"), ("Burwood", "宝活", "伯伍德"), ("Eastwood", "伊士活", "伊士伍德"), ("Hurstville", "好市围", "赫斯特维尔"), ("Parramatta", "巴拉马打", "帕拉马塔"), ("Randwick", "兰域", "兰德威克")]
y = 260; fh = zh(38, "Bold"); fr = zh(50, "Bold")
d.text((60, y), "英文", font=fh, fill=GREY); d.text((400, y), "老译名", font=fh, fill=RED); d.text((720, y), "普通话译名", font=fh, fill=GREY)
y += 66
for e, o, m in rows:
    d.line((60, y - 10, W - 60, y - 10), fill=(214, 206, 190), width=2)
    d.text((60, y + 6), e, font=en(40), fill=INK); d.text((400, y - 4), o, font=fr, fill=RED); d.text((720, y - 4), m, font=fr, fill=INK); y += 100
f = zh(40, "Medium"); y += 30
txt = "悉尼最早的华人大多来自广东，说粤语。很长一段时间里，悉尼华人社区以说粤语的人为主，这些译名在店铺招牌和中文报纸上慢慢叫开了。后来说普通话的新移民越来越多，又出现了一套按普通话音译的名字，所以今天一个区常常有两种叫法。"
for ln in wrap(txt, f, 960): d.text((60, y), ln, font=f, fill=INK); y += 60
assert y < H - 10, y
img.save(f"{OUT}/07.jpg", quality=93)

# 01 地图 + 首页
PL = [("车士活", "Chatswood", -33.797, 151.180), ("伊士活", "Eastwood", -33.791, 151.081), ("宝活", "Burwood", -33.877, 151.104),
      ("艾士菲", "Ashfield", -33.888, 151.125), ("好市围", "Hurstville", -33.967, 151.102), ("巴拉马打", "Parramatta", -33.815, 151.001),
      ("兰域", "Randwick", -33.914, 151.241), ("宾士镇", "Bankstown", -33.917, 151.034), ("霹雳镇", "Blacktown", -33.771, 150.906),
      ("马斯觉", "Mascot", -33.928, 151.193), ("赖德", "Ryde", -33.815, 151.105)]
OFF = {"宝活": (-90, 0), "艾士菲": (60, 140), "赖德": (70, 0), "伊士活": (-10, -40), "车士活": (50, 0), "马斯觉": (-100, 150), "兰域": (90, 0), "巴拉马打": (-70, 10), "宾士镇": (-30, 150), "好市围": (0, 150), "霹雳镇": (30, 0)}
WATER = (196, 220, 232)
SEA = [(151.29, -33.70), (151.29, -34.05), (151.24, -34.05), (151.24, -33.99), (151.21, -33.995), (151.17, -34.0), (151.13, -33.99),
       (151.15, -33.965), (151.20, -33.955), (151.235, -33.965), (151.255, -33.93), (151.275, -33.89), (151.28, -33.85), (151.29, -33.80), (151.29, -33.70)]
HARB = [(151.285, -33.845), (151.26, -33.84), (151.235, -33.852), (151.21, -33.857), (151.18, -33.845), (151.15, -33.84), (151.12, -33.835),
        (151.09, -33.83), (151.06, -33.825), (151.03, -33.82), (151.00, -33.818)]
def mapimg(y0, y1, big, labels=True):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    lon0, lon1, lat0, lat1 = 150.84, 151.30, -33.72, -34.01
    X = lambda lo: 40 + (lo - lon0) / (lon1 - lon0) * (W - 80); Y = lambda la: y0 + (la - lat0) / (lat1 - lat0) * (y1 - y0)
    d.polygon([(X(a), Y(b)) for a, b in SEA], fill=WATER)
    pts = [(X(a), Y(b)) for a, b in HARB]
    for k in range(len(pts) - 1): d.line((pts[k], pts[k + 1]), fill=WATER, width=max(6, 22 - k * 2))
    cx, cy = X(151.208), Y(-33.869)
    d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=INK); d.text((cx - 40, cy + 18), "市中心", font=zh(32, "Bold"), fill=INK)
    f = zh(52 if big else 48, "Black"); fe = en(26)
    for cn, e, la, lo in PL:
        x, y = X(lo), Y(la)
        w = max(f.getlength(cn), fe.getlength(e)) + 30; h = f.size + 46
        dx, dy = OFF.get(cn, (0, 0))
        bx, by = x - w / 2 + dx, y - h - 20 + dy
        d.line((x, y, bx + w / 2, by + h if dy <= 0 else by), fill=SIGN, width=3)
        d.rounded_rectangle((bx, by, bx + w, by + h), radius=10, fill=SIGN)
        d.text((bx + 15, by + 2), cn, font=f, fill="white"); d.text((bx + 17, by + f.size + 8), e, font=fe, fill=(210, 220, 240))
        d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=RED, outline="white", width=3)
    return img, d
img, d = mapimg(300, 1350, False)
d.text((60, 50), "悉尼区名的老译名", font=zh(72, "Black"), fill=INK); d.text((62, 150), "大多按粤语音译", font=zh(38, "Medium"), fill=GREY)
img.save(f"{OUT}/01.jpg", quality=93)
c, d = mapimg(560, 1390, True)
d.text((60, 70), "悉尼这些区名", font=zh(110, "Black"), fill=INK); d.text((60, 210), "中文为什么这么怪", font=zh(110, "Black"), fill=RED)
d.text((62, 370), "车士活、宝活、好市围、兰域……", font=zh(52, "Bold"), fill=GREY)
icon(c, "13_探店", W - 230, 380, 170).save(f"{OUT}/cover.jpg", quality=93)
print("ok")
