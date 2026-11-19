"""跨年烟花首页：十种不同风格，都带地图。用法：python3 tools/nye_covers.py 瓦片目录 输出目录"""
import sys, os, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harbour_map import water_mask, _txy
TILES, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "nye_cards.py")).read()
ns = {"__file__": __file__}; sys.argv = [sys.argv[0], TILES, "/tmp/claude-0/_nye_tmp"]
exec(src[:src.index("def place_labels")], ns); S = ns["S"]
W, H = 1080, 1440
def zh(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def serif(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSerifCJK-{w}.ttc", s, index=2)

def tmin(t):
    h, m = (t[:-2].split(":") + ["0"])[:2]; return (int(h) % 12 + (12 if t.endswith("pm") else 0)) * 60 + int(m)
def band(s):
    t = s[5]
    if not t: return 3
    m = tmin(t); return 0 if m <= 12 * 60 else (1 if m <= 17 * 60 else 2)
LAB = ["通常中午前满", "通常下午满", "通常傍晚后满", "其他免费看点"]

def bounds(w, h, lon_span=.064, c=(-33.856, 151.207)):
    la_span = lon_span * math.cos(math.radians(33.86)) * h / w
    return (c[0] + la_span / 2, c[0] - la_span / 2, c[1] - lon_span / 2, c[1] + lon_span / 2)

LAST = {}
def mapmask(w, h, b, S2=2):
    LAST["wh"] = (w, h)
    m = water_mask(b, TILES).resize((w * S2, h * S2), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3 * S2))
    m = m.point(lambda v: 255 if v > 128 else 0).resize((w, h), Image.LANCZOS)
    la0, la1, lo0, lo1 = b; X0, Y0 = _txy(la0, lo0); X1, Y1 = _txy(la1, lo1)
    def xy(la, lo):
        X, Y = _txy(la, lo); return ((X - X0) / (X1 - X0) * w, (Y - Y0) / (Y1 - Y0) * h)
    return m, xy

def edge(m, k=3):
    hard = m.point(lambda v: 255 if v > 128 else 0)
    return ImageChops.subtract(hard.filter(ImageFilter.MaxFilter(k)), hard)

def grain(img, amt=.07, seed=1):
    random.seed(seed); n = Image.effect_noise(img.size, 40).convert("RGB")
    return Image.blend(img.convert("RGB"), n, amt)

def dots(d, xy, ox, oy, cols, r=19, outline=None, ow=3):
    for s in S:
        x, y = xy(*s[3])
        mw, mh = LAST["wh"]
        if not (r < x < mw - r and r < y < mh - r): continue
        x += ox; y += oy
        d.ellipse((x - r, y - r, x + r, y + r), fill=cols[band(s)], outline=outline, width=ow if outline else 0)

def legend(d, x, y, cols, f, fill, colw=500, rowh=86, r=22):
    for k in range(4):
        xx = x + (k % 2) * colw; yy = y + (k // 2) * rowh
        d.ellipse((xx, yy + f.size / 2 - r + 6, xx + 2 * r, yy + f.size / 2 + r + 6), fill=cols[k])
        d.text((xx + 2 * r + 18, yy), LAB[k], font=f, fill=fill)

def wobble(d, cx, cy, rx, ry, col, w=5, seed=0):
    random.seed(seed)
    for p in range(2):
        pts = []; ph = random.random() * 6
        for k in range(0, 380, 8):
            a = math.radians(k + ph * 10); j = 1 + .08 * math.sin(a * 3 + ph) + random.uniform(-.03, .03)
            pts.append((cx + rx * j * math.cos(a), cy + ry * j * math.sin(a)))
        d.line(pts, fill=col, width=w, joint="curve")

# 1 报纸
def c1():
    bg = (243, 237, 222); ink = (24, 22, 20)
    img = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(img)
    d.rectangle((50, 46, W - 50, 52), fill=ink); d.rectangle((50, 58, W - 50, 60), fill=ink)
    d.text((50, 80), "跨年烟花", font=serif(170), fill=ink)
    d.text((54, 290), "免费看点通常几点满", font=serif(84), fill=(176, 36, 30))
    d.rectangle((50, 410, W - 50, 412), fill=ink)
    mw, mh = W - 100, 700; m, xy = mapmask(mw, mh, bounds(mw, mh))
    hatch = Image.new("RGB", (mw, mh), bg); hd = ImageDraw.Draw(hatch)
    for k in range(-mh, mw, 9): hd.line((k, 0, k + mh, mh), fill=(120, 116, 106), width=2)
    layer = Image.new("RGB", (mw, mh), bg); layer.paste(hatch, (0, 0), m); layer.paste(ink, (0, 0), edge(m))
    img.paste(layer, (50, 440)); d = ImageDraw.Draw(img)
    d.rectangle((50, 440, W - 50, 440 + mh), outline=ink, width=3)
    cols = [(176, 36, 30), (222, 120, 40), (232, 190, 40), (70, 120, 90)]
    dots(d, xy, 50, 440, cols, r=19, outline=bg)
    legend(d, 60, 1190, cols, serif(50), ink)
    return grain(img, .05)

# 2 笔记本
def c2():
    img = Image.new("RGB", (W, H), (252, 251, 246)); d = ImageDraw.Draw(img)
    for x in range(0, W, 36): d.line((x, 0, x, H), fill=(214, 228, 240), width=1)
    for y in range(0, H, 36): d.line((0, y, W, y), fill=(214, 228, 240), width=1)
    d.rectangle((60, 238, 740, 330), fill=(255, 236, 110))
    d.text((60, 60), "悉尼跨年烟花", font=zh(140), fill=(30, 30, 34))
    d.text((66, 236), "免费看点几点满", font=zh(88), fill=(30, 30, 34))
    mw, mh = W - 100, 760; m, xy = mapmask(mw, mh, bounds(mw, mh))
    lay = Image.new("RGBA", (mw, mh), (0, 0, 0, 0)); lay.paste((150, 196, 226, 200), (0, 0), m)
    lay.paste((70, 70, 80, 255), (0, 0), edge(m, 3))
    img.paste(lay, (50, 400), lay); d = ImageDraw.Draw(img)
    cols = [(220, 40, 40), (240, 140, 30), (235, 200, 30), (60, 160, 110)]
    dots(d, xy, 50, 400, cols, r=19)
    early = [s for s in S if band(s) == 0]
    xs = [xy(*s[3])[0] + 50 for s in early]; ys = [xy(*s[3])[1] + 400 for s in early]
    wobble(d, sum(xs) / len(xs), sum(ys) / len(ys), (max(xs) - min(xs)) / 2 + 50, (max(ys) - min(ys)) / 2 + 45, (220, 40, 40), 6, 3)
    tape = Image.new("RGBA", (220, 64), (240, 222, 170, 190)).rotate(-28, expand=True); img.paste(tape, (860, 360), tape)
    legend(d, 60, 1200, cols, zh(50), (30, 30, 34))
    return img

# 3 孔版印刷
def c3():
    pink = (255, 72, 150); blue = (0, 110, 190); paper = (246, 242, 232)
    img = Image.new("RGB", (W, H), paper)
    mw, mh = W, 900; m, xy = mapmask(mw, mh, bounds(mw, mh, .06))
    bl = Image.new("RGB", (W, H), paper); bl.paste(blue, (0, 380), m)
    img = ImageChops.multiply(img, bl)
    pl = Image.new("RGB", (W, H), paper); pd = ImageDraw.Draw(pl)
    pd.text((46, 40), "跨年烟花", font=zh(180), fill=pink); pd.text((50, 250), "免费看点", font=zh(110), fill=pink)
    for s in S:
        x, y = xy(*s[3]); r = 20 if band(s) < 3 else 11
        if not (0 < x < mw and 0 < y < mh): continue
        y += 380
        pd.ellipse((x - r + 5, y - r + 4, x + r + 5, y + r + 4), fill=pink)
    img = ImageChops.multiply(img, pl); d = ImageDraw.Draw(img)
    d.text((50, 1310), "粉色大点通常当天就满", font=zh(64), fill=blue)
    return grain(img, .1, 3)

# 4 票根
def c4():
    img = Image.new("RGB", (W, H), (18, 26, 46)); d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 60, 70, W - 60, H - 70; tc = (250, 240, 214)
    d.rounded_rectangle((x0, y0, x1, y1), radius=30, fill=tc)
    for cy in (y0 + 330,):
        d.ellipse((x0 - 34, cy - 34, x0 + 34, cy + 34), fill=(18, 26, 46)); d.ellipse((x1 - 34, cy - 34, x1 + 34, cy + 34), fill=(18, 26, 46))
        for x in range(x0 + 50, x1 - 40, 30): d.line((x, cy, x + 14, cy), fill=(150, 140, 120), width=4)
    d.text((110, 110), "12月31日", font=zh(80), fill=(200, 50, 40)); d.text((110, 200), "跨年烟花免费看点", font=zh(86), fill=(30, 30, 40))
    mw, mh = x1 - x0 - 80, 640; m, xy = mapmask(mw, mh, bounds(mw, mh))
    lay = Image.new("RGB", (mw, mh), (236, 222, 190)); lay.paste((40, 64, 104), (0, 0), m)
    img.paste(lay, (x0 + 40, y0 + 380)); d = ImageDraw.Draw(img)
    cols = [(255, 90, 80), (255, 170, 60), (255, 225, 100), (140, 220, 180)]
    dots(d, xy, x0 + 40, y0 + 380, cols, r=19, outline=(40, 64, 104))
    legend(d, 110, y0 + 1060, cols, zh(48), (30, 30, 40), colw=470)
    return grain(img, .04)

# 5 航海图
def c5():
    paper = (236, 222, 190); ink = (70, 50, 30)
    img = Image.new("RGB", (W, H), paper); d = ImageDraw.Draw(img)
    mw, mh = W, 980; m, xy = mapmask(mw, mh, bounds(mw, mh, .066))
    land = ImageOps.invert(m); lay = Image.new("RGB", (mw, mh), (214, 200, 166)); lay.paste(paper, (0, 0), land)
    for k, a in ((14, 150), (30, 110), (50, 80)):
        ring = ImageChops.subtract(land.filter(ImageFilter.MaxFilter(k + 1)), land.filter(ImageFilter.MaxFilter(k - 1)))
        lay.paste((160, 130, 90), (0, 0), ring.point(lambda v: a if v > 0 else 0))
    lay.paste(ink, (0, 0), edge(m))
    img.paste(lay, (0, 230)); d = ImageDraw.Draw(img)
    cx, cy, R = 930, 1060, 90
    for k in range(16):
        a = math.radians(k * 22.5); rr = R if k % 4 == 0 else (R * .6 if k % 2 == 0 else R * .4)
        b1 = math.radians(k * 22.5 + 90); w = 10
        d.polygon([(cx + rr * math.cos(a), cy + rr * math.sin(a)), (cx + w * math.cos(b1), cy + w * math.sin(b1)), (cx - w * math.cos(b1), cy - w * math.sin(b1))], fill=ink if k % 2 == 0 else (160, 130, 90))
    d.ellipse((cx - R - 8, cy - R - 8, cx + R + 8, cy + R + 8), outline=ink, width=2)
    d.text((50, 50), "悉尼跨年烟花免费看点", font=serif(82), fill=ink); d.text((52, 150), "按通常几点满分颜色", font=serif(52, "Bold"), fill=(150, 40, 30))
    cols = [(170, 40, 30), (200, 110, 30), (210, 170, 40), (60, 100, 90)]
    dots(d, xy, 0, 230, cols, r=19, outline=paper)
    legend(d, 60, 1240, cols, serif(50), ink)
    return grain(img, .08, 5)

# 6 明信片
def c6():
    img = Image.new("RGB", (W, H), (196, 162, 120)); img = grain(img, .12, 6); d = ImageDraw.Draw(img)
    d.text((60, 50), "悉尼跨年烟花", font=zh(130), fill=(255, 250, 238)); d.text((62, 210), "免费看点通常几点满", font=zh(76), fill=(40, 30, 24))
    card = Image.new("RGB", (900, 1000), (252, 250, 244)); cd = ImageDraw.Draw(card)
    mw, mh = 840, 640; m, xy = mapmask(mw, mh, bounds(mw, mh))
    lay = Image.new("RGB", (mw, mh), (240, 232, 210)); lay.paste((96, 170, 210), (0, 0), m); lay.paste((50, 60, 70), (0, 0), edge(m))
    card.paste(lay, (30, 30)); cols = [(220, 50, 50), (240, 150, 40), (240, 210, 60), (70, 160, 110)]
    dots(cd, xy, 30, 30, cols, r=19, outline="white")
    cd.rectangle((700, 700, 860, 880), outline=(200, 60, 60), width=6); cd.ellipse((720, 730, 840, 850), fill=(220, 60, 60))
    cd.text((742, 768), "31", font=zh(46), fill="white")
    for k in range(4):
        xx = 40 + (k % 2) * 330; yy = 710 + (k // 2) * 90
        cd.ellipse((xx, yy + 14, xx + 40, yy + 54), fill=cols[k]); cd.text((xx + 54, yy), LAB[k][2:] if k < 3 else "其他看点", font=zh(46), fill=(40, 30, 24))
    card = card.rotate(3, expand=True, fillcolor=(0, 0, 0, 0), resample=Image.BICUBIC)
    sh = Image.new("L", card.size, 0); sh.paste(90, (0, 0), card.convert("L").point(lambda v: 255 if v > 0 else 0))
    img.paste((60, 40, 20), (90, 380), sh.filter(ImageFilter.GaussianBlur(12))); img.paste(card, (70, 360), card.convert("L").point(lambda v: 255 if v > 0 else 0))
    return img

# 7 满版地图加贴纸
def c7():
    m, xy = mapmask(W, H, bounds(W, H, .05, (-33.857, 151.208)))
    img = Image.new("RGB", (W, H), (245, 236, 214)); img.paste((88, 168, 176), (0, 0), m); img.paste((40, 60, 70), (0, 0), edge(m, 5))
    d = ImageDraw.Draw(img); cols = [(230, 50, 60), (250, 150, 40), (250, 214, 60), (255, 255, 255)]
    dots(d, xy, 0, 0, cols, r=20, outline=(30, 40, 50), ow=4)
    note = Image.new("RGB", (780, 420), (255, 252, 240)); nd = ImageDraw.Draw(note)
    nd.text((40, 30), "跨年烟花", font=zh(130), fill=(30, 30, 34)); nd.text((44, 200), "免费看点", font=zh(96), fill=(230, 50, 60))
    nd.text((46, 320), "红点通常中午前满", font=zh(54), fill=(30, 30, 34))
    note = note.convert("RGBA").rotate(-3, expand=True, resample=Image.BICUBIC)
    img.paste(note, (40, 60), note)
    for x, y, a in ((80, 50, 20), (700, 60, -15)):
        t = Image.new("RGBA", (180, 56), (236, 220, 170, 200)).rotate(a, expand=True); img.paste(t, (x, y), t)
    return img

# 8 蓝图
def c8():
    bg = (22, 72, 140); img = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(img)
    for x in range(0, W, 30): d.line((x, 0, x, H), fill=(44, 92, 160), width=1)
    for y in range(0, H, 30): d.line((0, y, W, y), fill=(44, 92, 160), width=1)
    mw, mh = W - 80, 820; m, xy = mapmask(mw, mh, bounds(mw, mh))
    img.paste((255, 255, 255), (40, 360), edge(m, 5)); d = ImageDraw.Draw(img)
    d.text((40, 40), "悉尼跨年烟花", font=zh(130), fill="white"); d.text((44, 200), "免费看点通常几点满", font=zh(80), fill=(255, 220, 90))
    cols = [(255, 90, 90), (255, 170, 60), (255, 230, 100), (150, 230, 255)]
    dots(d, xy, 40, 360, cols, r=19, outline="white")
    legend(d, 50, 1220, cols, zh(50), "white")
    return img

# 9 翻牌告示板
def c9():
    img = Image.new("RGB", (W, H), (16, 16, 18)); d = ImageDraw.Draw(img)
    def flap(text, y, size, col):
        f = zh(size); x = 40
        for ch in text:
            w = size + 18; d.rounded_rectangle((x, y, x + w, y + size + 36), radius=10, fill=(40, 40, 44))
            d.line((x, y + (size + 36) / 2, x + w, y + (size + 36) / 2), fill=(16, 16, 18), width=3)
            d.text((x + 9, y + 6), ch, font=f, fill=col); x += w + 8
    flap("跨年烟花", 50, 150, (255, 255, 255)); flap("免费看点", 270, 110, (255, 196, 40))
    mw, mh = W - 80, 760; m, xy = mapmask(mw, mh, bounds(mw, mh))
    lay = Image.new("RGB", (mw, mh), (16, 16, 18)); lay.paste((36, 36, 42), (0, 0), m); lay.paste((255, 196, 40), (0, 0), edge(m, 3))
    img.paste(lay, (40, 460)); d = ImageDraw.Draw(img)
    cols = [(255, 70, 70), (255, 150, 40), (255, 230, 120), (120, 220, 170)]
    dots(d, xy, 40, 460, cols, r=19)
    legend(d, 50, 1250, cols, zh(48), "white")
    return img

# 10 大数字海报
def c10():
    bg = (236, 76, 50); img = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(img)
    d.text((380, 860), "26", font=zh(760), fill=(244, 104, 76))
    d.text((50, 60), "26个", font=zh(150), fill=(255, 244, 222)); d.text((50, 240), "跨年烟花免费看点", font=zh(92), fill=(30, 20, 20))
    mw, mh = W - 100, 820; m, xy = mapmask(mw, mh, bounds(mw, mh))
    lay = Image.new("RGB", (mw, mh), (255, 244, 222)); lay.paste((30, 40, 70), (0, 0), m)
    rm = Image.new("L", (mw, mh), 0); ImageDraw.Draw(rm).rounded_rectangle((0, 0, mw, mh), radius=40, fill=255)
    img.paste(lay, (50, 400), rm); d = ImageDraw.Draw(img)
    cols = [(236, 76, 50), (255, 170, 60), (255, 230, 110), (140, 220, 190)]
    dots(d, xy, 50, 400, cols, r=19, outline=(30, 40, 70))
    legend(d, 60, 1250, cols, zh(48), (255, 244, 222))
    return img

for i, f in enumerate([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10]):
    f().convert("RGB").save(f"{OUT}/cover_{i + 1:02d}.jpg", quality=93); print(i + 1)
