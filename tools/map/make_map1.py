import sys, json
sys.path.insert(0, '.')
import tiles
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"b": "NotoSansCJK-Bold.ttc", "k": "NotoSansCJK-Black.ttc", "m": "NotoSansCJK-Medium.ttc"}[w], s, index=2)
RED, TEAL, INK, LINEC = (214, 69, 65), (0, 128, 128), (25, 28, 30), (60, 60, 60)
vs = json.load(open("final.json"))
by = {v["name"]: v for v in vs}
col = lambda v: RED if v["cat"] == "r" else TEAL
lats = [v["lat"] for v in vs]; lons = [v["lon"] for v in vs]
clat = (min(lats) + max(lats)) / 2 + 0.0001; clon = (min(lons) + max(lons)) / 2 + 0.0002
img, px = tiles.render(clat, clon, 16, W, H, scale=0.96)
img = ImageEnhance.Color(img).enhance(0.45)
img = Image.blend(img, Image.new("RGB", img.size, (250, 248, 244)), 0.28)
d = ImageDraw.Draw(img)
f = F("b", 22)
# 标签相对点的位置（像素偏移），挤在一起的店往外拉开
off = {
 "Paperboy": (-150, 40), "Mattina": (40, -10), "ThreeOneNine": (40, 30),
 "Abhi's Indian": (60, 40), "雄起厨房": (60, -40),
 "Frango": (-190, -95), "Daikoku Teppanyaki": (-250, -40), "Maranello's": (-190, 20), "Organica": (60, 30),
 "Late Night Table": (110, -90), "Myeong Dong": (120, 20), "Bar Biscotti": (-60, -100), "August Coffee": (-40, 80),
 "Da Franco": (50, -30),
}
pts = {v["name"]: px(v["lat"], v["lon"]) for v in vs}
# 先画引线和标签，再画点，点永远在最上面
for v in vs:
    x, y = pts[v["name"]]; dx, dy = off[v["name"]]
    t = v["name"]; tw = f.getlength(t); bw, bh = tw + 20, 36
    bx = x + dx if dx >= 0 else x + dx - bw / 2 + 60
    bx = min(max(bx, 14), W - bw - 14)
    by_ = y + dy - bh / 2
    # 引线接到标签最近的一边
    cx = min(max(x, bx), bx + bw); cy = min(max(y, by_), by_ + bh)
    d.line([(x, y), (cx, cy)], fill=LINEC, width=2)
    d.rounded_rectangle([bx, by_, bx + bw, by_ + bh], 8, fill="white", outline=col(v), width=3)
    d.text((bx + 10, by_ + 3), t, font=f, fill=INK)
for v in vs:
    x, y = pts[v["name"]]
    d.ellipse([x - 10, y - 10, x + 10, y + 10], fill="white")
    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=col(v))
# 标题和图例
TY = 395; M0 = 360
d.rounded_rectangle([M0, TY, M0 + 520, TY + 132], 16, fill="white", outline=(210, 205, 198), width=2)
d.text((M0 + 24, TY + 12), "Concord一带吃什么", font=F("k", 42), fill=INK)
lf = F("m", 22); lx, ly = M0 + 26, TY + 86
for c, t in [(RED, "餐厅"), (TEAL, "咖啡店")]:
    d.ellipse([lx, ly + 6, lx + 18, ly + 24], fill=c); d.text((lx + 26, ly), t, font=lf, fill=INK); lx += 130
d.text((W - 180, H - 32), "© OpenStreetMap", font=F("m", 17), fill=(110, 105, 98))
img.save("concord_map.png")
print({k: (round(a), round(b)) for k, (a, b) in pts.items()})
