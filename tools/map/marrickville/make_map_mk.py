import sys, json
sys.path.insert(0, '.')
import tiles
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"b": "NotoSansCJK-Bold.ttc", "k": "NotoSansCJK-Black.ttc", "m": "NotoSansCJK-Medium.ttc"}[w], s, index=2)
DOT, INK = (150, 92, 52), (25, 28, 30)
vs = json.load(open("final.json"))
place = json.load(open("place.json"))
SCALE = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8
lats = [v["lat"] for v in vs]; lons = [v["lon"] for v in vs]
clat = (min(lats) + max(lats)) / 2; clon = (min(lons) + max(lons)) / 2
MAP_H = 1120
map_img, mpx = tiles.render(clat, clon, 17, W, MAP_H, scale=SCALE)
map_img = Image.blend(ImageEnhance.Color(map_img).enhance(0.45), Image.new("RGB", map_img.size, (250, 248, 244)), 0.28)
img = Image.new("RGB", (W, H), (250, 248, 244)); img.paste(map_img, (0, 0))
d = ImageDraw.Draw(img); f = F("b", 22)
pts = {v["name"]: mpx(v["lat"], v["lon"]) for v in vs}
for v in vs:
    x, y = pts[v["name"]]; side, dy = place.get(v["name"], ("r", 0))
    t = v["name"]; bw, bh = f.getlength(t) + 18, 34
    bx = x + 16 if side == "r" else x - 16 - bw
    bx = min(max(bx, 10), W - bw - 10); by_ = min(max(y + dy - bh / 2, 10), MAP_H - bh - 10)
    d.rounded_rectangle([bx, by_, bx + bw, by_ + bh], 8, fill="white", outline=DOT, width=3)
    d.text((bx + 9, by_ + 2), t, font=f, fill=INK)
for v in vs:
    x, y = pts[v["name"]]
    d.ellipse([x - 10, y - 10, x + 10, y + 10], fill="white"); d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=DOT)
DARK, ORANGE = (24, 24, 26), (255, 140, 60)
d.rectangle([0, MAP_H, W, H], fill=DARK)
f1 = F("k", 104)
d.text((76, MAP_H + 40), "悉尼Marrickville", font=f1, fill=(255, 255, 255))
d.text((76, MAP_H + 40 + 126), "咖啡喝什么？", font=f1, fill=ORANGE)
d.text((W - 180, MAP_H - 30), "© OpenStreetMap", font=F("m", 17), fill=(110, 105, 98))
img.save("mk_map.png")
print({k: (round(a), round(b)) for k, (a, b) in pts.items()})
