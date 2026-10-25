import sys, json
sys.path.insert(0, '.')
import tiles
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"b": "NotoSansCJK-Bold.ttc", "k": "NotoSansCJK-Black.ttc", "m": "NotoSansCJK-Medium.ttc"}[w], s, index=2)
BROWN, GREEN, INK = (214, 69, 65), (0, 128, 128), (25, 28, 30)
col = lambda v: BROWN if v["cat"] == "r" else GREEN
vs = json.load(open("final.json"))
place = json.load(open("place.json"))
SCALE = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8
lats = [v["lat"] for v in vs]; lons = [v["lon"] for v in vs]
clat = (min(lats) + max(lats)) / 2 - 0.0004; clon = (min(lons) + max(lons)) / 2
MAP_H = 1120
map_img, mpx = tiles.render(clat, clon, 16, W, MAP_H, scale=SCALE)
map_img = Image.blend(ImageEnhance.Color(map_img).enhance(0.45), Image.new("RGB", map_img.size, (250, 248, 244)), 0.28)
img = Image.new("RGB", (W, H), (250, 248, 244)); img.paste(map_img, (0, 0))
d = ImageDraw.Draw(img); f = F("b", 22)
pts = {v["name"]: mpx(v["lat"], v["lon"]) for v in vs}
for v in vs:
    x, y = pts[v["name"]]; side, dy = place.get(v["name"], ("r", 0))
    t = v["name"]; bw, bh = f.getlength(t) + 18, 34
    bx = x + 16 if side == "r" else x - 16 - bw
    bx = min(max(bx, 10), W - bw - 10); by_ = min(max(y + dy - bh / 2, 10), MAP_H - bh - 10)
    d.rounded_rectangle([bx, by_, bx + bw, by_ + bh], 8, fill="white", outline=col(v), width=3)
    d.text((bx + 9, by_ + 2), t, font=f, fill=INK)
for v in vs:
    x, y = pts[v["name"]]
    d.ellipse([x - 10, y - 10, x + 10, y + 10], fill="white"); d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=col(v))
DARK, ORANGE = (24, 24, 26), (255, 140, 60)
d.rectangle([0, MAP_H, W, H], fill=DARK)
f1 = F("k", 104)
d.text((76, MAP_H + 40), "悉尼Mosman附近", font=f1, fill=(255, 255, 255))
d.text((76, MAP_H + 40 + 126), "吃什么？", font=f1, fill=ORANGE)
lf = F("m", 19); lx, ly = 22, MAP_H - 44
d.rounded_rectangle([lx - 10, ly - 6, lx + 236, ly + 30], 14, fill=(255, 255, 255))
for c, t in [(BROWN, "餐厅"), (GREEN, "咖啡下午茶")]:
    d.ellipse([lx, ly + 5, lx + 14, ly + 19], fill=c); d.text((lx + 20, ly - 2), t, font=lf, fill=(90, 90, 90)); lx += 100
d.text((W - 180, MAP_H - 30), "© OpenStreetMap", font=F("m", 17), fill=(110, 105, 98))
img.save("mos_map.png")
print({k: (round(a), round(b)) for k, (a, b) in pts.items()})
