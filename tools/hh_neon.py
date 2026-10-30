"""悉尼Happy Hour：霓虹灯招牌风格整套图（封面、暗色地图、一周日历、清单）。
用法：python3 hh_neon.py 输出目录 geo.json"""
import sys, json, re
sys.path.insert(0, "tools"); sys.path.insert(0, "tools/map")
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
import tiles
from hh_pages import CAL, OY, OY2, DR
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"k": "NotoSansCJK-Black.ttc", "b": "NotoSansCJK-Bold.ttc", "m": "NotoSansCJK-Medium.ttc", "r": "NotoSansCJK-Regular.ttc"}[w], s, index=2)
BG = (12, 10, 22)
PINK, CYAN, YEL, WHITE = (255, 70, 170), (60, 230, 255), (255, 214, 80), (245, 240, 255)
od, geo = sys.argv[1], json.load(open(sys.argv[2]))

def neon(img, xy, text, font, col, glow=14, anchor="la"):
    """霓虹字：同色多层模糊光晕，中间白芯。"""
    lay = Image.new("L", img.size, 0); ImageDraw.Draw(lay).text(xy, text, font=font, fill=255, anchor=anchor)
    out = img.copy()
    for r, a in ((glow * 2.2, .55), (glow, .8), (glow * .4, 1.0)):
        g = lay.filter(ImageFilter.GaussianBlur(r)); g = g.point(lambda v: min(255, int(v * a * 1.6)))
        out = Image.composite(Image.new("RGB", img.size, col), out, g)
    core = Image.new("RGB", img.size, tuple(int(c * .35 + 255 * .65) for c in col))
    out = Image.composite(core, out, lay)
    img.paste(out)

def frame(d, col, pad=36, w=4):
    d.rounded_rectangle([pad, pad, W - pad, H - pad], 40, outline=col, width=w)

def base():
    img = Image.new("RGB", (W, H), BG)
    # 砖墙暗纹
    d = ImageDraw.Draw(img)
    for y in range(0, H, 46):
        off = 0 if (y // 46) % 2 == 0 else 60
        for x in range(-120 + off, W, 120):
            d.rectangle([x + 3, y + 3, x + 117, y + 43], fill=(18, 15, 32))
    return img

def glowline(img, box, col, width=4, r=10):
    lay = Image.new("L", img.size, 0); ImageDraw.Draw(lay).rounded_rectangle(box, 30, outline=255, width=width)
    g = lay.filter(ImageFilter.GaussianBlur(r)).point(lambda v: min(255, v * 2))
    img.paste(Image.composite(Image.new("RGB", img.size, col), img, g))
    img.paste(Image.composite(Image.new("RGB", img.size, tuple(int(c * .4 + 153) for c in col)), img, lay))

# 1 封面：压暗的生蚝照片 + 霓虹招牌
ph = Image.open("data/post_img/hh_pier.jpg").convert("RGB")
s = max(W / ph.width, H / ph.height); ph = ph.resize((round(ph.width * s), round(ph.height * s)))
x = (ph.width - W) // 2; ph = ph.crop((x, 0, x + W, H))
ph = ImageEnhance.Brightness(ImageEnhance.Color(ph).enhance(1.2)).enhance(.45)
img = Image.blend(ph, Image.new("RGB", (W, H), BG), .25)
glowline(img, [60, 150, W - 60, 760], PINK, 6, 14)
neon(img, (W // 2, 250), "悉尼", F("k", 92), CYAN, 12, "mm")
neon(img, (W // 2, 420), "HAPPY", F("k", 190), PINK, 18, "mm")
neon(img, (W // 2, 600), "HOUR", F("k", 190), PINK, 18, "mm")
neon(img, (W // 2, 900), "生蚝$1起", F("k", 130), YEL, 16, "mm")
neon(img, (W // 2, 1050), "啤酒$5一杯", F("k", 96), CYAN, 12, "mm")
img.save(f"{od}/n1_cover.png")

# 2 暗色地图：瓦片反色压暗，霓虹点
(la0, la1), (lo0, lo1) = (-33.9030, -33.8500), (151.1780, 151.2720)
MAPH = 1120; TOP = 230
Z = 15
x0, y0 = tiles.merc(la1, lo0, Z); x1, y1 = tiles.merc(la0, lo1, Z)
sc = min(W / (x1 - x0), MAPH / (y1 - y0))
m, mpx = tiles.render((la0 + la1) / 2, (lo0 + lo1) / 2, Z, W, MAPH, scale=sc)
a = np.asarray(m.convert("L")).astype(float)
water = np.asarray(m).astype(int); wmask = (abs(water[..., 0] - 170) < 25) & (abs(water[..., 1] - 211) < 25) & (abs(water[..., 2] - 223) < 25)
dark = (255 - a) * .22 + 14
rgb = np.stack([dark * .9, dark * .8, dark * 1.25], -1)
rgb[wmask] = (16, 22, 48)
mm = Image.fromarray(np.clip(rgb, 0, 255).astype("uint8"))
img = Image.new("RGB", (W, H), BG); img.paste(mm, (0, TOP))
neon(img, (W // 2, 120), "悉尼Happy Hour地图", F("k", 84), PINK, 14, "mm")
geo["charles"] = [-33.8681, 151.2086]; geo["jane"] = [-33.886948, 151.2155]
PTS = [("batball", "$1", "Bat & Ball", 1), ("harbourview", "$1.5", "Harbour View", 1), ("pier", "$2", "Pier Bar", 1), ("rover", "$2", "The Rover", -1),
       ("charles", "$2", "The Charles", 1), ("morrison", "$2", "The Morrison", -1), ("roos", "$2", "The Roosevelt", 1), ("corner", "$2", "Corner House", -1),
       ("erko", "$2", "The Erko", 1), ("rose", "$2.5", "Rose of Aus", 1), ("jane", "$3", "Jane", 1), ("winery", "$4", "The Winery", 1),
       ("london", "$4", "The London", 1), ("frisco", "$6", "Frisco", -1), ("moshpit", "$5", "MoshPit", 1), ("fourinhand", "$6", "Four in Hand", 1), ("coopers", "$6", "Coopers", 1)]
DRINK = {"frisco", "moshpit", "fourinhand", "coopers"}
OFFY = {"coopers": -60, "erko": -18, "rose": 24, "moshpit": 66, "pier": -14, "harbourview": 12, "morrison": -6, "winery": 10, "rover": -4}
fl, fp = F("b", 25), F("k", 27)
for k, price, name, side in PTS:
    x, y = mpx(*geo[k]); y += TOP; col = CYAN if k in DRINK else PINK
    lay = Image.new("L", (W, H), 0); ImageDraw.Draw(lay).ellipse([x - 9, y - 9, x + 9, y + 9], fill=255)
    img.paste(Image.composite(Image.new("RGB", (W, H), col), img, lay.filter(ImageFilter.GaussianBlur(9)).point(lambda v: min(255, v * 3))))
    ImageDraw.Draw(img).ellipse([x - 5, y - 5, x + 5, y + 5], fill=WHITE)
    t = f"{price} {name}"; tw = fp.getlength(price) + 8 + fl.getlength(name)
    ty = y - 16 + OFFY.get(k, 0)
    tx = x + 16 if side > 0 else x - 16 - tw
    tx = min(max(tx, 14), W - tw - 14)
    dd = ImageDraw.Draw(img)
    ax = tx - 8 if tx > x else tx + tw + 8
    if abs(ty + 16 - y) > 14: dd.line([(x, y), (ax, ty + 16)], fill=col, width=2)
    dd.rounded_rectangle([tx - 8, ty - 2, tx + tw + 8, ty + 34], 10, fill=(10, 8, 20))
    dd.text((tx, ty - 2), price, font=fp, fill=YEL if k not in DRINK else CYAN)
    dd.text((tx + fp.getlength(price) + 8, ty + 1), name, font=fl, fill=WHITE)
dd = ImageDraw.Draw(img)
neon(img, (70, TOP + MAPH + 46), "● 生蚝", F("k", 40), PINK, 8)
neon(img, (300, TOP + MAPH + 46), "● 便宜酒", F("k", 40), CYAN, 8)
dd.text((560, TOP + MAPH + 54), "Chatswood还有一家$5啤酒", font=F("m", 30), fill=(170, 165, 200))
dd.text((W - 160, TOP + MAPH - 26), "© OpenStreetMap", font=F("m", 14), fill=(110, 105, 140))
img.save(f"{od}/n2_map.png")

# 3 一周日历：每天一块霓虹灯牌
img = base(); d = ImageDraw.Draw(img)
neon(img, (W // 2, 120), "一周生蚝日历", F("k", 86), YEL, 14, "mm")
COL7 = [PINK, CYAN, PINK, CYAN, PINK, YEL, YEL]
def wrap(text, font, maxw):
    lines, cur = [], ""
    for tok in re.findall(r"[A-Za-z&'$.0-9()（）]+(?: [A-Za-z&'][A-Za-z&'.]*)*|.", text):
        if font.getlength(cur + tok) > maxw and cur: lines.append(cur); cur = tok.lstrip("、")
        else: cur += tok
    return lines + [cur]
y = 220; ft = F("m", 33)
for (day, txt), col in zip(CAL, COL7):
    ls = wrap(txt, ft, W - 330)
    h = max(110, 36 + len(ls) * 46)
    glowline(img, [60, y, W - 60, y + h], col, 3, 8)
    neon(img, (90, y + h // 2), day, F("k", 52), col, 8, "lm")
    d = ImageDraw.Draw(img)
    for i, l in enumerate(ls): d.text((250, y + (h - len(ls) * 46) // 2 + i * 46), l, font=ft, fill=WHITE)
    y += h + 22
img.save(f"{od}/n3_cal.png")

# 4-6 清单：价格是霓虹大字
def listpage(title, rows, col, out):
    img = base()
    neon(img, (W // 2, 120), title, F("k", 80), col, 14, "mm")
    n = len(rows); rh = min(176, (H - 260 - 60) // n); y = 240
    for price, name, area, when, extra in rows:
        neon(img, (180, y + rh // 2 - 10), price, F("k", 70 if len(price) <= 2 else 56), YEL, 10, "mm")
        d = ImageDraw.Draw(img)
        d.text((310, y + 6), name, font=F("k", 42), fill=WHITE)
        d.text((310 + F("k", 42).getlength(name) + 16, y + 18), area, font=F("m", 27), fill=(170, 165, 200))
        d.text((310, y + 62), when, font=F("b", 31), fill=col)
        d.text((310, y + 106), extra, font=F("r", 29), fill=(200, 196, 220))
        y += rh
        d.line([(80, y - 10), (W - 80, y - 10)], fill=(50, 44, 80), width=2)
    img.save(out)
listpage("生蚝Happy Hour", OY, PINK, f"{od}/n4_oy1.png")
listpage("还有这些生蚝", OY2, PINK, f"{od}/n5_oy2.png")
listpage("$5到$6喝一杯", DR, CYAN, f"{od}/n6_dr.png")
