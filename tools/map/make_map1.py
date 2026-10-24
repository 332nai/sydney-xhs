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
TOP = 150
map_img, mpx = tiles.render(clat, clon, 16, W, H - TOP, scale=0.9)
map_img = Image.blend(ImageEnhance.Color(map_img).enhance(0.45), Image.new("RGB", map_img.size, (250, 248, 244)), 0.28)
img = Image.new("RGB", (W, H), (250, 248, 244)); img.paste(map_img, (0, TOP))
px = lambda la, lo: (mpx(la, lo)[0], mpx(la, lo)[1] + TOP)
d = ImageDraw.Draw(img)
f = F("b", 22)
# 标签紧贴圆点，不用引线：side 表示标签在点的左边还是右边，dy 是标签中心相对点的上下偏移
place = {
 "Paperboy": ("l", 0), "Mattina": ("r", -10), "ThreeOneNine": ("r", 0),
 "雄起厨房": ("r", -22), "Abhi's Indian": ("r", 24),
 "Frango": ("l", -30), "Daikoku Teppanyaki": ("l", 4), "Maranello's": ("l", 36), "Organica": ("r", 6),
 "Late Night Table": ("r", -22), "Myeong Dong": ("r", 20), "Bar Biscotti": ("l", -24), "August Coffee": ("l", 24),
 "Da Franco": ("r", 0), "Pajuok 파주옥": ("r", 6),
}
pts = {v["name"]: px(v["lat"], v["lon"]) for v in vs}
for v in vs:
    x, y = pts[v["name"]]; side, dy = place[v["name"]]
    t = v["name"]; tw = f.getlength(t); bw, bh = tw + 18, 34
    bx = x + 16 if side == "r" else x - 16 - bw
    bx = min(max(bx, 10), W - bw - 10)
    by_ = y + dy - bh / 2
    d.rounded_rectangle([bx, by_, bx + bw, by_ + bh], 8, fill="white", outline=col(v), width=3)
    d.text((bx + 9, by_ + 2), t, font=f, fill=INK)
for v in vs:
    x, y = pts[v["name"]]
    d.ellipse([x - 10, y - 10, x + 10, y + 10], fill="white")
    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=col(v))
# 标题：顶部通栏，不悬浮
d.rectangle([0, 0, W, TOP], fill=(250, 248, 244))
d.line([(0, TOP), (W, TOP)], fill=INK, width=3)
t1, t2 = "Concord一带", "吃什么？"
f1 = F("k", 76)
d.text((44, 26), t1, font=f1, fill=INK)
d.text((44 + f1.getlength(t1) + 6, 26), t2, font=f1, fill=RED)
lf = F("m", 22); lx, ly = W - 230, 62
for c, t in [(RED, "餐厅"), (TEAL, "咖啡店")]:
    d.ellipse([lx, ly + 6, lx + 18, ly + 24], fill=c); d.text((lx + 26, ly), t, font=lf, fill=INK); lx += 100
d.text((W - 180, H - 32), "© OpenStreetMap", font=F("m", 17), fill=(110, 105, 98))
img.save("concord_map.png")
print({k: (round(a), round(b)) for k, (a, b) in pts.items()})
