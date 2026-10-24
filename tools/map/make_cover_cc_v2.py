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
PHOTO_H = int(sys.argv[1]) if len(sys.argv) > 1 else 410
tiles_spec = json.loads(sys.argv[2])
TB = 262
def pop(im):
    im = ImageEnhance.Color(im).enhance(1.28)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    return ImageEnhance.Brightness(im).enhance(1.03)
img = Image.new("RGB", (W, H), DARK)
# 顶部标题：白色，两行左对齐
d = ImageDraw.Draw(img)
TITLE = "悉尼Concord附近"
f1 = F("k", 86)
d.text((62, 30), TITLE, font=f1, fill=(255, 255, 255))
d.text((62, 30 + 104), "吃什么？", font=f1, fill=(255, 255, 255))
# 底部照片：3×2，白色细缝
PY = H - PHOTO_H
gap = 6; cols, rows = 3, 2
tw = (W - gap * (cols - 1)) / cols; th = (PHOTO_H - gap) / rows
img.paste((250, 248, 244), (0, PY - gap, W, H))
for i, (f, c) in enumerate(tiles_spec):
    r, q = divmod(i, cols)
    x0, y0 = round(q * (tw + gap)), PY + round(r * (th + gap))
    x1, y1 = round(q * (tw + gap) + tw), PY + round(r * (th + gap) + th)
    t = ImageOps.fit(Image.open(IMG + f).convert("RGB"), (x1 - x0, y1 - y0), Image.LANCZOS, centering=tuple(c))
    img.paste(pop(t), (x0, y0))
# 地图
vs = json.load(open("final.json")); col = lambda v: RED if v["cat"] == "r" else TEAL
MAP_Y = TB; MAP_H = H - PHOTO_H - 6 - MAP_Y; MAP_B = MAP_Y + MAP_H
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
    by_ = min(max(y + dy - bh / 2, MAP_Y + 8), MAP_B - bh - 8)
    d.rounded_rectangle([bx, by_, bx + bw, by_ + bh], 8, fill="white", outline=col(v), width=3)
    d.text((bx + 8, by_ + 2), t, font=f, fill=INK)
for v in vs:
    x, y = pts[v["name"]]
    d.ellipse([x - 9, y - 9, x + 9, y + 9], fill="white"); d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=col(v))
lf = F("m", 18); lx, ly = 22, MAP_B - 42
d.rounded_rectangle([lx - 10, ly - 6, lx + 186, ly + 28], 14, fill="white")
for c, t in [(RED, "餐厅"), (TEAL, "咖啡店")]:
    d.ellipse([lx, ly + 5, lx + 13, ly + 18], fill=c); d.text((lx + 19, ly - 2), t, font=lf, fill=(90, 90, 90)); lx += 82
d.text((W - 170, MAP_B - 28), "© OpenStreetMap", font=F("m", 16), fill=(110, 105, 98))
img.save("cover.png")
print({k: (round(a), round(b)) for k, (a, b) in pts.items()})
