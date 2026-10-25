import sys, json
sys.path.insert(0, '.')
import tiles
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"b": "NotoSansCJK-Bold.ttc", "k": "NotoSansCJK-Black.ttc", "m": "NotoSansCJK-Medium.ttc"}[w], s, index=2)
venues, place_f, line2, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
DOT, INK = (140, 82, 44), (25, 28, 30)
vs = json.load(open(venues)); place = json.load(open(place_f))
lats = [v["lat"] for v in vs]; lons = [v["lon"] for v in vs]
clat = (min(lats) + max(lats)) / 2 + (float(sys.argv[6]) if len(sys.argv) > 6 else 0); clon = (min(lons) + max(lons)) / 2 + (float(sys.argv[5]) if len(sys.argv) > 5 else 0)
MAP_H = 1120
PADX, PADY = 230, 110
for Z in (17, 16):
    x0, y0 = tiles.merc(max(lats), min(lons), Z); x1, y1 = tiles.merc(min(lats), max(lons), Z)
    scale = min((W - 2 * PADX) / max(x1 - x0, 1), (MAP_H - 2 * PADY) / max(y1 - y0, 1))
    if scale >= 0.55 or Z == 16: break
scale = min(scale, 1.6)
m, mpx = tiles.render(clat, clon, Z, W, MAP_H, scale=scale)
m = Image.blend(ImageEnhance.Color(m).enhance(0.45), Image.new("RGB", m.size, (250, 248, 244)), 0.28)
img = Image.new("RGB", (W, H), (250, 248, 244)); img.paste(m, (0, 0))
d = ImageDraw.Draw(img); f = F("b", 21)
pts = {v["name"]: mpx(v["lat"], v["lon"]) for v in vs}
for v in vs:
    x, y = pts[v["name"]]; side, dy = place.get(v["name"], ("r", 0))
    t = v["name"]; bw, bh = f.getlength(t) + 18, 32
    bx = x + 15 if side == "r" else x - 15 - bw
    bx = min(max(bx, 10), W - bw - 10); by_ = min(max(y + dy - bh / 2, 10), MAP_H - bh - 10)
    d.rounded_rectangle([bx, by_, bx + bw, by_ + bh], 8, fill="white", outline=DOT, width=3)
    d.text((bx + 9, by_ + 2), t, font=f, fill=INK)
for v in vs:
    x, y = pts[v["name"]]
    d.ellipse([x - 9, y - 9, x + 9, y + 9], fill="white"); d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=DOT)
DARK, ORANGE = (24, 24, 26), (255, 140, 60)
d.rectangle([0, MAP_H, W, H], fill=DARK)
f1 = F("k", 104)
d.text((76, MAP_H + 40), "悉尼精品咖啡地图", font=f1, fill=(255, 255, 255))
d.text((76, MAP_H + 40 + 126), line2, font=f1, fill=ORANGE)
d.text((W - 180, MAP_H - 30), "© OpenStreetMap", font=F("m", 17), fill=(110, 105, 98))
img.save(out)
print({k: (round(a), round(b)) for k, (a, b) in pts.items()})
