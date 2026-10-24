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
# 标签紧贴圆点，不用引线：side 表示标签在点的左边还是右边，dy 是标签中心相对点的上下偏移
place = {
 "Paperboy": ("l", 0), "Mattina": ("r", 0), "ThreeOneNine": ("r", 0),
 "雄起厨房": ("r", -22), "Abhi's Indian": ("r", 24),
 "Frango": ("l", -30), "Daikoku Teppanyaki": ("l", 4), "Maranello's": ("l", 36), "Organica": ("r", 6),
 "Late Night Table": ("r", -22), "Myeong Dong": ("r", 20), "Bar Biscotti": ("l", -24), "August Coffee": ("l", 24),
 "Da Franco": ("r", 0),
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
# 标题卡片
cx0, cy0, cw, ch = 352, 330, 540, 300
shadow = Image.new("RGBA", img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(shadow)
sd.rounded_rectangle([cx0 + 8, cy0 + 10, cx0 + cw + 8, cy0 + ch + 10], 26, fill=(0, 0, 0, 60))
from PIL import ImageFilter
shadow = shadow.filter(ImageFilter.GaussianBlur(10))
img.paste(shadow, (0, 0), shadow); d = ImageDraw.Draw(img)
d.rounded_rectangle([cx0, cy0, cx0 + cw, cy0 + ch], 26, fill=(255, 253, 249))
d.rectangle([cx0, cy0 + 28, cx0 + 14, cy0 + ch - 28], fill=RED)
d.text((cx0 + 46, cy0 + 22), "Concord一带", font=F("k", 72), fill=INK)
qf = F("k", 112)
d.rectangle([cx0 + 46, cy0 + 196, cx0 + 46 + qf.getlength("吃什么？") - 40, cy0 + 222], fill=(255, 214, 102))
d.text((cx0 + 40, cy0 + 96), "吃什么？", font=qf, fill=RED)
lf = F("m", 21); lx, ly = cx0 + cw - 150, cy0 + ch - 44
for c, t in [(RED, "餐厅"), (TEAL, "咖啡")]:
    d.ellipse([lx, ly + 6, lx + 16, ly + 22], fill=c); d.text((lx + 22, ly), t, font=lf, fill=INK); lx += 74
d.text((W - 180, H - 32), "© OpenStreetMap", font=F("m", 17), fill=(110, 105, 98))
img.save("concord_map.png")
print({k: (round(a), round(b)) for k, (a, b) in pts.items()})
