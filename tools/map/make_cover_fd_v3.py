"""Five Dock封面：上方不对称拼图+白色标题，中间满版地图，底部三张小图。"""
import sys, json
sys.path.insert(0, '/tmp/claude-0/-home-claude/d2aa705a-a3c9-5391-b5c6-802034136ddf/scratchpad/v3')
import tiles
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps, ImageFilter
cfg = json.load(open(sys.argv[1]))
W, H = 1080, 1440
IMG = "/home/claude/sydney_xhs/data/post_img/"
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"b": "NotoSansCJK-Bold.ttc", "k": "NotoSansCJK-Black.ttc", "m": "NotoSansCJK-Medium.ttc"}[w], s, index=2)
BG = (28, 22, 18); WHITE = (255, 255, 255)
RED, TEAL, INK = (214, 70, 58), (0, 128, 120), (30, 28, 26)
G = 8
img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
def pop(im):
    im = ImageEnhance.Color(im).enhance(1.25); im = ImageEnhance.Contrast(im).enhance(1.05)
    return ImageEnhance.Brightness(im).enhance(1.04)
def put(fn, c, box):
    x0, y0, x1, y1 = box
    img.paste(pop(ImageOps.fit(Image.open(IMG + fn).convert("RGB"), (x1 - x0, y1 - y0), Image.LANCZOS, centering=tuple(c))), (x0, y0))
P = cfg["photos"]
TOPH = cfg.get("top_h", 450); HW = 680
put(*P[0], (0, 0, HW, TOPH))
put(*P[1], (HW + G, 0, W, (TOPH - G) // 2))
put(*P[2], (HW + G, (TOPH - G) // 2 + G, W, TOPH))
# 标题：压在拼图底部，渐变压暗
gh = 230; grad = Image.new("L", (1, gh))
for yy in range(gh): grad.putpixel((0, yy), int(225 * (yy / gh) ** 1.3))
band = img.crop((0, TOPH - gh, W, TOPH)); band.paste(Image.new("RGB", band.size, BG), (0, 0), grad.resize(band.size)); img.paste(band, (0, TOPH - gh))
ft = F("k", cfg.get("title_size", 74)); title = cfg["title1"] + "吃什么？"
d = ImageDraw.Draw(img); d.text((44, TOPH - 112), title, font=ft, fill=WHITE)
# 地图满版
BOTH = cfg.get("bottom_h", 250)
MY = TOPH + G; MH = H - BOTH - G - MY
vs = json.load(open(cfg["venues"]))
lats = [v["lat"] for v in vs]; lons = [v["lon"] for v in vs]
clat = (min(lats) + max(lats)) / 2 + cfg.get("dlat", 0); clon = (min(lons) + max(lons)) / 2 + cfg.get("dlon", 0)
m, mpx = tiles.render(clat, clon, cfg["zoom"], W, MH, scale=cfg["scale"])
m = ImageEnhance.Color(m).enhance(0.3)
m = Image.blend(m, Image.new("RGB", m.size, (247, 241, 230)), 0.33)
col = lambda v: RED if v["cat"] == "r" else TEAL
place = cfg["place"]; f = F("b", 21)
pts = {v["name"]: mpx(v["lat"], v["lon"]) for v in vs}
shadow = Image.new("L", m.size, 0); sd = ImageDraw.Draw(shadow); boxes = []
for v in vs:
    x, y = pts[v["name"]]; side, dy = place[v["name"]]
    t = v["name"]; bw, bh = f.getlength(t) + 26, 34
    bx = x + 14 if side == "r" else x - 14 - bw
    bx = min(max(bx, 10), W - bw - 10); by_ = min(max(y + dy - bh / 2, 10), MH - bh - 10)
    boxes.append((t, bx, by_, bw, bh)); sd.rounded_rectangle([bx, by_ + 3, bx + bw, by_ + bh + 3], bh // 2, fill=90)
m.paste(Image.new("RGB", m.size, (60, 50, 40)), (0, 0), shadow.filter(ImageFilter.GaussianBlur(5)))
md = ImageDraw.Draw(m)
for t, bx, by_, bw, bh in boxes:
    md.rounded_rectangle([bx, by_, bx + bw, by_ + bh], bh // 2, fill=WHITE); md.text((bx + 13, by_ + 3), t, font=f, fill=INK)
for v in vs:
    x, y = pts[v["name"]]
    md.ellipse([x - 11, y - 11, x + 11, y + 11], fill=WHITE); md.ellipse([x - 7, y - 7, x + 7, y + 7], fill=col(v))
lf = F("m", 18); lx, ly = 24, MH - 46
lw = 30 + sum(lf.getlength(t) + 44 for _, t in cfg["legend"])
md.rounded_rectangle([lx - 8, ly - 4, lx - 8 + lw, ly + 30], 17, fill=WHITE)
for c, t in cfg["legend"]:
    c = RED if c == "r" else TEAL
    md.ellipse([lx + 6, ly + 7, lx + 20, ly + 21], fill=c); md.text((lx + 26, ly), t, font=lf, fill=(80, 80, 80)); lx += lf.getlength(t) + 44
md.text((W - 165, MH - 30), "© OpenStreetMap", font=F("m", 15), fill=(120, 115, 108))
img.paste(m, (0, MY))
# 底部三张
by0 = H - BOTH; tw = (W - 2 * G) / 3
for i in range(3):
    x0 = round(i * (tw + G)); x1 = round(i * (tw + G) + tw)
    put(*P[3 + i], (x0, by0, x1, H))
img.save(cfg["out"])
print({k: (round(a), round(b)) for k, (a, b) in pts.items()})
