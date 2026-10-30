"""悉尼蓝花楹封面：卡通版悉尼地图，9棵卡通蓝花楹树标在打卡地上。用法：python3 cartoon_cover.py out.jpg"""
import sys, math, random
sys.path.insert(0, '..')
import tiles
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"k": "NotoSansCJK-Black.ttc", "b": "NotoSansCJK-Bold.ttc"}[w], s, index=2)
TOP = 300                      # 顶部标题区高度
MAP_H = H - TOP
SPOTS = [("Hunters Hill", -33.8348, 151.1541), ("Greenwich", -33.8385, 151.1816),
         ("Lavender Bay", -33.8448, 151.2068), ("Kirribilli", -33.8442, 151.2138),
         ("The Rocks", -33.8608, 151.2091), ("皇家植物园", -33.8628, 151.2157),
         ("Woolloomooloo", -33.8723, 151.2159), ("Paddington", -33.8823, 151.2283),
         ("悉尼大学", -33.8858, 151.1890)]
LAND, LAND_EDGE, WATER, WATER_DK = (252, 243, 222), (214, 196, 160), (150, 205, 232), (118, 182, 218)
PARK = (196, 226, 170)

(la0, la1), (lo0, lo1) = (-33.8905, -33.8310), (151.1470, 151.2330)
Z = 15
x0, y0 = tiles.merc(la1, lo0, Z); x1, y1 = tiles.merc(la0, lo1, Z)
s = min(W / (x1 - x0), MAP_H / (y1 - y0))
base, mpx = tiles.render((la0 + la1) / 2, (lo0 + lo1) / 2, Z, W, MAP_H, scale=s)
a = np.asarray(base).astype(int)
water = (abs(a[..., 0] - 170) < 22) & (abs(a[..., 1] - 211) < 22) & (abs(a[..., 2] - 223) < 22)
park = (abs(a[..., 0] - 200) < 25) & (abs(a[..., 1] - 236) < 18) & (abs(a[..., 2] - 200) < 30) & (a[..., 1] > a[..., 0] + 15)
def smooth(m, r):
    im = Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(r))
    return np.asarray(im) > 127
water = smooth(water, 3); park = smooth(smooth(park, 6), 4) & ~water
img = Image.new("RGB", (W, H), (255, 236, 246))
mp = np.zeros((MAP_H, W, 3), "uint8"); mp[:] = LAND
mp[park] = PARK; mp[water] = WATER
# 海岸描边
wm = Image.fromarray((water * 255).astype("uint8"))
edge = np.asarray(wm.filter(ImageFilter.MaxFilter(7))) > 127
edge &= ~water
mp[edge] = LAND_EDGE
m = Image.fromarray(mp)
d = ImageDraw.Draw(m)
# 水面小波浪
random.seed(3)
for _ in range(160):
    x, y = random.randint(20, W - 40), random.randint(20, MAP_H - 20)
    if water[y, x] and water[y, min(x + 30, W - 1)] and water[max(y - 8, 0), x]:
        d.arc([x, y, x + 16, y + 10], 200, 340, fill=WATER_DK, width=3)
        d.arc([x + 14, y, x + 30, y + 10], 200, 340, fill=WATER_DK, width=3)
img.paste(m, (0, TOP))
d = ImageDraw.Draw(img)

# 海港大桥小图标
def bridge(cx, cy):
    d.arc([cx - 46, cy - 30, cx + 46, cy + 40], 200, 340, fill=(90, 90, 110), width=7)
    d.line([cx - 52, cy + 6, cx + 52, cy + 6], fill=(90, 90, 110), width=6)
    for k in (-44, 44):
        d.rectangle([cx + k - 6, cy - 6, cx + k + 6, cy + 16], fill=(120, 110, 100))
bx, by = mpx(-33.8523, 151.2108); bridge(bx, by + TOP)
# 歌剧院小图标（几片白色帆）
def opera(cx, cy):
    for i, (dx, h) in enumerate(((-18, 30), (0, 38), (16, 28))):
        d.polygon([(cx + dx - 14, cy + 12), (cx + dx + 10, cy + 12), (cx + dx + 2, cy + 12 - h)], fill="white", outline=(150, 150, 160))
    d.rectangle([cx - 36, cy + 12, cx + 30, cy + 18], fill=(210, 190, 160))

def tree(cx, cy, sc=1.0):
    blobs = [(-26, -12, 24), (26, -12, 24), (0, -30, 28), (-14, 6, 20), (16, 6, 20), (0, -6, 26)]
    for dx, dy, r in blobs:
        r = r * sc; x, y = cx + dx * sc, cy + dy * sc
        d.ellipse([x - r - 3, y - r - 3, x + r + 3, y + r + 3], fill=(70, 40, 110))
    for dx, dy, r in blobs:
        r = r * sc; x, y = cx + dx * sc, cy + dy * sc
        d.ellipse([x - r, y - r, x + r, y + r], fill=(150, 104, 220))
    for dx, dy, r in ((-18, -24, 8), (10, -38, 7), (22, -18, 6), (-4, -14, 5)):
        x, y = cx + dx * sc, cy + dy * sc
        d.ellipse([x - r * sc, y - r * sc, x + r * sc, y + r * sc], fill=(206, 176, 250))
    t = int(12 * sc)
    d.rounded_rectangle([cx - t // 2, cy + 18 * sc, cx + t // 2, cy + 46 * sc], 4, fill=(124, 84, 54), outline=(70, 45, 30), width=2)
    random.seed(int(cx * 7 + cy))
    for _ in range(6):
        x = cx + random.uniform(-40, 40) * sc; y = cy + random.uniform(44, 52) * sc
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(170, 125, 230))

fl = F("b", 28)
OFF = {"Kirribilli": (95, -40), "Lavender Bay": (-150, -10), "The Rocks": (-110, -30), "皇家植物园": (110, -40),
       "Woolloomooloo": (-40, 34), "Paddington": (0, 34), "悉尼大学": (0, 34), "Hunters Hill": (0, 34), "Greenwich": (0, 34)}
pts = []
for n, la, lo in SPOTS:
    x, y = mpx(la, lo); pts.append((n, x, y + TOP)); print(n, int(x), int(y + TOP))
for n, x, y in sorted(pts, key=lambda p: p[2]):
    tree(x, y - 46, 1.0)
for n, x, y in pts:
    dx, dy = OFF.get(n, (0, 80))
    tw = fl.getlength(n) + 28
    lx, ly = x + dx - tw / 2, y + dy - 18
    lx = min(max(lx, 10), W - tw - 10)
    d.rounded_rectangle([lx, ly, lx + tw, ly + 46], 23, fill="white", outline=(110, 70, 170), width=3)
    d.text((lx + 14, ly + 4), n, font=fl, fill=(50, 30, 80))
ox, oy = mpx(-33.8568, 151.2153); opera(ox + 6, oy + TOP - 6)
def boat(cx, cy):
    d.polygon([(cx - 26, cy), (cx + 26, cy), (cx + 18, cy + 12), (cx - 18, cy + 12)], fill=(240, 200, 60), outline=(90, 70, 40))
    d.rectangle([cx - 12, cy - 12, cx + 10, cy], fill="white", outline=(90, 70, 40))
for la, lo in ((-33.8545, 151.1900), (-33.8480, 151.2250), (-33.8420, 151.1650)):
    x, y = mpx(la, lo)
    if water[int(y), int(x)]: boat(x, y + TOP)
# 标题
d.rectangle([0, 0, W, TOP], fill=(255, 236, 246))
ft = F("k", 128); t = "悉尼蓝花楹"
d.text(((W - ft.getlength(t)) / 2, 34), t, font=ft, fill=(120, 70, 190), stroke_width=8, stroke_fill="white")
fs = F("k", 64); t2 = "9个最美打卡地"
d.text(((W - fs.getlength(t2)) / 2, 196), t2, font=fs, fill=(60, 36, 100))
d.text((W - 150, H - 26), "© OpenStreetMap", font=F("b", 14), fill=(150, 140, 130))
img.save(sys.argv[1], quality=93)
