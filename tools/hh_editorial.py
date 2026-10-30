"""悉尼Happy Hour：克制的杂志编辑风（白纸、黑字、宋体标题、一种墨绿点缀）。
用法：python3 hh_editorial.py 输出目录 geo.json"""
import sys, json
sys.path.insert(0, "tools"); sys.path.insert(0, "tools/map")
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import tiles
from hh_pages import OY, OY2, DR
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def S(w, s): return ImageFont.truetype(NOTO + f"NotoSerifCJK-{w}.ttc", s, index=2)
def K(w, s): return ImageFont.truetype(NOTO + f"NotoSansCJK-{w}.ttc", s, index=2)
PAPER, INK, GREY, RULE, ACC = (250, 248, 244), (22, 22, 22), (128, 124, 118), (214, 208, 198), (30, 78, 64)
M = 80
od, geo = sys.argv[1], json.load(open(sys.argv[2]))
geo["charles"] = [-33.8681, 151.2086]; geo["jane"] = [-33.886948, 151.2155]
KEYS = {"Bat & Ball Hotel": "batball", "Harbour View Hotel": "harbourview", "Pier Bar": "pier", "The Rover": "rover", "The Charles": "charles",
        "The Morrison": "morrison", "The Roosevelt": "roos", "The Corner House": "corner", "The Erko": "erko", "Rose of Australia": "rose",
        "Jane": "jane", "The Winery": "winery", "The London Hotel": "london", "MoshPit": "moshpit", "The Chatswood": "chatswood",
        "Frisco Hotel": "frisco", "Four in Hand": "fourinhand", "Coopers Hotel": "coopers"}
ALL = [(i + 1,) + r for i, r in enumerate(OY + OY2 + DR)]   # (编号, 价格, 店名, 区, 时间, 备注)

def header(d, kicker, title, y=M):
    d.text((M, y), kicker, font=K("Medium", 26), fill=ACC)
    d.text((M, y + 44), title, font=S("Bold", 74), fill=INK)
    d.line([(M, y + 160), (W - M, y + 160)], fill=INK, width=3)
    return y + 190

# 1 封面：上部照片，下部白纸宋体标题
img = Image.new("RGB", (W, H), PAPER)
ph = Image.open("data/post_img/hh_pier.jpg").convert("RGB")
PH = 860; s = max(W / ph.width, PH / ph.height); ph = ph.resize((round(ph.width * s), round(ph.height * s)), Image.LANCZOS)
x = (ph.width - W) // 2; y = (ph.height - PH) // 2; ph = ph.crop((x, y, x + W, y + PH))
img.paste(ImageEnhance.Color(ph).enhance(1.05), (0, 0))
d = ImageDraw.Draw(img)
d.text((M, PH + 60), "SYDNEY HAPPY HOUR", font=K("Medium", 28), fill=ACC)
d.text((M, PH + 108), "悉尼Happy Hour指南", font=S("Black", 92), fill=INK)
d.line([(M, PH + 250), (M + 120, PH + 250)], fill=INK, width=3)
d.text((M, PH + 282), "生蚝1刀起，啤酒5刀一杯", font=S("Medium", 46), fill=INK)
d.text((M, PH + 360), "内城18家，按星期和价格整理", font=K("Regular", 32), fill=GREY)
img.save(f"{od}/e1_cover.png")

# 2 地图：灰度底图，编号黑点，下方两栏图例
img = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(img)
y0 = header(d, "地图", "18家都在这里")
MAPH = 760
(la0, la1), (lo0, lo1) = (-33.9020, -33.8520), (151.1800, 151.2700)
Z = 15; x0, yy0 = tiles.merc(la1, lo0, Z); x1, yy1 = tiles.merc(la0, lo1, Z)
sc = min((W - 2 * M) / (x1 - x0), MAPH / (yy1 - yy0))
m, mpx = tiles.render((la0 + la1) / 2, (lo0 + lo1) / 2, Z, W - 2 * M, MAPH, scale=sc)
g = ImageEnhance.Contrast(m.convert("L")).enhance(1.1).point(lambda v: int(v * .62 + 88))
img.paste(Image.merge("RGB", (g, g, g)), (M, y0))
d = ImageDraw.Draw(img)
f = K("Bold", 22)
for n, price, name, area, when, extra in ALL:
    k = KEYS[name]
    if k == "chatswood": continue
    px, py = mpx(*geo[k]); px += M; py += y0
    jx, jy = {"erko": (-14, -16), "rose": (18, 8), "moshpit": (-18, 22), "coopers": (0, -6)}.get(k, (0, 0)); px += jx; py += jy
    col = ACC if n > 13 else INK
    d.ellipse([px - 17, py - 17, px + 17, py + 17], fill=col, outline=PAPER, width=3)
    t = str(n); d.text((px - f.getlength(t) / 2, py - 15), t, font=f, fill=PAPER)
d.text((W - M - 230, y0 + MAPH - 30), "© OpenStreetMap", font=K("Regular", 16), fill=GREY)
y = y0 + MAPH + 34
fl = K("Regular", 25); fb = K("Bold", 25)
for i, (n, price, name, *_) in enumerate(ALL):
    cx = M + (i // 9) * 470; cy = y + (i % 9) * 40
    d.text((cx, cy), f"{n:>2}", font=fb, fill=ACC if n > 13 else INK)
    d.text((cx + 46, cy), name + ("（图外）" if KEYS[name] == "chatswood" else ""), font=fl, fill=INK)
    d.text((cx + 410, cy), price, font=fb, fill=INK, anchor="ra")
img.save(f"{od}/e2_map.png")

# 3 一周时间表：店 × 星期 的点阵
DAYS = {"batball": "六", "harbourview": "四", "pier": "一二三四五", "rover": "一二三四五六", "charles": "一二三四五六日",
        "morrison": "三", "roos": "一二三四五六日", "corner": "三四五六日", "erko": "六日", "rose": "五",
        "jane": "一二三四五六日", "winery": "一二三四五", "london": "五"}
img = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(img)
y = header(d, "一周时间表", "哪天去哪家")
cols = "一二三四五六日"; cx0 = 520; cw = (W - M - cx0) / 7
for j, c in enumerate(cols):
    d.text((cx0 + cw * j + cw / 2, y + 10), c, font=S("Bold", 34), fill=INK, anchor="ma")
y += 70
rh = (H - y - 120) / 13
for n, price, name, area, when, extra in ALL[:13]:
    k = KEYS[name]
    d.text((M, y + rh / 2), f"{n}", font=K("Bold", 26), fill=GREY, anchor="lm")
    d.text((M + 46, y + rh / 2), name.replace(" Hotel", ""), font=S("SemiBold", 32), fill=INK, anchor="lm")
    d.text((cx0 - 24, y + rh / 2), price, font=K("Bold", 28), fill=ACC, anchor="rm")
    for j, c in enumerate(cols):
        cx = cx0 + cw * j + cw / 2; cy = y + rh / 2
        if c in DAYS[k]: d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=INK)
        else: d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RULE)
    y += rh
    d.line([(M, y), (W - M, y)], fill=RULE, width=1)
d.text((M, H - 92), "价格是一只生蚝的价格", font=K("Regular", 28), fill=GREY)
img.save(f"{od}/e3_week.png")

# 4-6 清单：编号和地图对应
def listpage(kicker, title, rows, out):
    img = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(img)
    y = header(d, kicker, title) + 10
    rh = min(190, (H - y - 60) / len(rows))
    for n, price, name, area, when, extra in rows:
        d.text((M, y), f"{n:02d}", font=K("Medium", 26), fill=ACC)
        d.text((M + 70, y - 8), name, font=S("Bold", 44), fill=INK)
        d.text((W - M, y - 10), price, font=S("Bold", 52), fill=INK, anchor="ra")
        d.text((M + 70, y + 54), area + "　" + when, font=K("Regular", 29), fill=INK)
        d.text((M + 70, y + 96), extra, font=K("Regular", 27), fill=GREY)
        y += rh
        d.line([(M, y - 26), (W - M, y - 26)], fill=RULE, width=1)
    img.save(out)
listpage("生蚝  1/2", "一只生蚝1到2刀", ALL[:7], f"{od}/e4_oy1.png")
listpage("生蚝  2/2", "一只生蚝2到4刀", ALL[7:13], f"{od}/e5_oy2.png")
listpage("便宜酒", "一杯5到6刀", ALL[13:], f"{od}/e6_dr.png")
