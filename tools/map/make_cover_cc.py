import sys, json
sys.path.insert(0, '.')
import tiles
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
W, H = 1080, 1440
IMG = "/home/claude/sydney_xhs/data/post_img/"
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"b": "NotoSansCJK-Bold.ttc", "k": "NotoSansCJK-Black.ttc", "m": "NotoSansCJK-Medium.ttc"}[w], s, index=2)
RED, TEAL, INK = (214, 69, 65), (0, 128, 128), (25, 28, 30)
DARK, ORANGE = (24, 24, 26), (255, 140, 60)
PHOTO_H = int(sys.argv[1]) if len(sys.argv) > 1 else 560
tiles_spec = json.loads(sys.argv[2]) if len(sys.argv) > 2 else [["cc_frango_08.jpg", [0.5, 0.5]], ["cc_myeongdong_09.jpg", [0.45, 0.6]], ["cc_abhis_05.jpg", [0.5, 0.45]]]
def pop(im):
    return im
img = Image.new("RGB", (W, H), DARK)
n = len(tiles_spec); gap = 6; tw = (W - gap * (n - 1)) // n
x = 0
for i, (f, c) in enumerate(tiles_spec):
    w = W - x if i == n - 1 else tw
    t = ImageOps.fit(Image.open(IMG + f).convert("RGB"), (w, PHOTO_H), Image.LANCZOS, centering=tuple(c))
    img.paste(pop(t), (x, 0)); x += w + gap
# 照片底部渐变，标题压在照片上
grad = Image.new("L", (1, PHOTO_H))
for yy in range(PHOTO_H):
    k = max(0, (yy - PHOTO_H * 0.5) / (PHOTO_H * 0.5)); grad.putpixel((0, yy), int(235 * k ** 1.4))
shade = Image.new("RGB", (W, PHOTO_H), DARK)
top = img.crop((0, 0, W, PHOTO_H)); top.paste(shade, (0, 0), grad.resize((W, PHOTO_H))); img.paste(top, (0, 0))
d = ImageDraw.Draw(img)
f1 = F("k", 100)
d.text((60, PHOTO_H - 262), "悉尼Concord附近", font=f1, fill=(255, 255, 255))
d.text((60, PHOTO_H - 262 + 118), "吃什么？", font=f1, fill=ORANGE)
# 地图
vs = json.load(open("final.json")); col = lambda v: RED if v["cat"] == "r" else TEAL
MAP_Y = PHOTO_H + 8; MAP_H = H - MAP_Y
lats = [v["lat"] for v in vs]; lons = [v["lon"] for v in vs]
clat = (min(lats) + max(lats)) / 2; clon = (min(lons) + max(lons)) / 2 + 0.0002
SCALE = float(sys.argv[3]) if len(sys.argv) > 3 else 0.62
m, mpx = tiles.render(clat, clon, 16, W, MAP_H, scale=SCALE)
m = Image.blend(ImageEnhance.Color(m).enhance(0.45), Image.new("RGB", m.size, (250, 248, 244)), 0.28)
img.paste(m, (0, MAP_Y)); d = ImageDraw.Draw(img)
px = lambda la, lo: (mpx(la, lo)[0], mpx(la, lo)[1] + MAP_Y)
f = F("b", 21)
place = {
 "Paperboy": ("l", 0), "Mattina": ("r", -12), "ThreeOneNine": ("r", 4),
 "雄起厨房": ("l", -16), "Abhi's Indian": ("r", 20),
 "Frango": ("l", -22), "Daikoku Teppanyaki": ("r", -32), "Maranello's": ("l", 22), "Organica": ("r", 8),
 "Late Night Table": ("r", -22), "Myeong Dong": ("r", 18), "Bar Biscotti": ("l", -22), "August Coffee": ("l", 22),
 "Da Franco": ("r", 0), "Pajuok 파주옥": ("l", 32),
}
pts = {v["name"]: px(v["lat"], v["lon"]) for v in vs}
for v in vs:
    x, y = pts[v["name"]]; side, dy = place[v["name"]]
    t = v["name"]; bw, bh = f.getlength(t) + 16, 32
    bx = x + 15 if side == "r" else x - 15 - bw
    bx = min(max(bx, 10), W - bw - 10)
    by_ = min(max(y + dy - bh / 2, MAP_Y + 8), H - bh - 8)
    d.rounded_rectangle([bx, by_, bx + bw, by_ + bh], 8, fill="white", outline=col(v), width=3)
    d.text((bx + 8, by_ + 2), t, font=f, fill=INK)
for v in vs:
    x, y = pts[v["name"]]
    d.ellipse([x - 9, y - 9, x + 9, y + 9], fill="white"); d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=col(v))
lf = F("m", 18); lx, ly = 22, H - 42
d.rounded_rectangle([lx - 10, ly - 6, lx + 186, ly + 28], 14, fill="white")
for c, t in [(RED, "餐厅"), (TEAL, "咖啡店")]:
    d.ellipse([lx, ly + 5, lx + 13, ly + 18], fill=c); d.text((lx + 19, ly - 2), t, font=lf, fill=(90, 90, 90)); lx += 82
d.text((W - 170, H - 28), "© OpenStreetMap", font=F("m", 16), fill=(110, 105, 98))
img.save("cover.png")
print({k: (round(a), round(b)) for k, (a, b) in pts.items()})
