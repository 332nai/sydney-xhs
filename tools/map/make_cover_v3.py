"""合集封面v3：深色底，白色标题，圆角地图卡片，圆角美食小图。"""
import sys, json
sys.path.insert(0, '/tmp/claude-0/-home-claude/d2aa705a-a3c9-5391-b5c6-802034136ddf/scratchpad/v3')
import tiles
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps, ImageFilter
cfg = json.load(open(sys.argv[1]))
W, H = 1080, 1440
IMG = "/home/claude/sydney_xhs/data/post_img/"
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"b": "NotoSansCJK-Bold.ttc", "k": "NotoSansCJK-Black.ttc", "m": "NotoSansCJK-Medium.ttc"}[w], s, index=2)
BG = (22, 22, 24); WHITE = (255, 255, 255)
RED, TEAL, INK = (220, 72, 62), (0, 132, 130), (30, 30, 32)
M = 40; R = 26
img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)

def rounded(im, r):
    mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], r, fill=255)
    return mask
def pop(im):
    im = ImageEnhance.Color(im).enhance(1.25); im = ImageEnhance.Contrast(im).enhance(1.05)
    return ImageEnhance.Brightness(im).enhance(1.03)

# 标题
ft = F("k", cfg.get("title_size", 92))
d.text((M + 4, 44), cfg["title1"], font=ft, fill=WHITE)
d.text((M + 4, 44 + int(cfg.get("title_size", 92) * 1.18)), "吃什么？", font=ft, fill=WHITE)

# 地图卡片
MY = cfg.get("map_y", 292); MH = cfg.get("map_h", 680); MW = W - 2 * M
vs = json.load(open(cfg["venues"]))
lats = [v["lat"] for v in vs]; lons = [v["lon"] for v in vs]
clat = (min(lats) + max(lats)) / 2 + cfg.get("dlat", 0); clon = (min(lons) + max(lons)) / 2 + cfg.get("dlon", 0)
m, mpx = tiles.render(clat, clon, cfg["zoom"], MW, MH, scale=cfg["scale"])
m = ImageEnhance.Color(m).enhance(0.25)
m = Image.blend(m, Image.new("RGB", m.size, (246, 243, 236)), 0.35)
md = ImageDraw.Draw(m)
col = lambda v: RED if v["cat"] == "r" else TEAL
place = cfg["place"]; f = F("b", 21)
pts = {v["name"]: mpx(v["lat"], v["lon"]) for v in vs}
# 标签：白色胶囊，带柔和阴影，无描边
shadow = Image.new("L", m.size, 0); sd = ImageDraw.Draw(shadow)
boxes = []
for v in vs:
    x, y = pts[v["name"]]; side, dy = place[v["name"]]
    t = v["name"]; bw, bh = f.getlength(t) + 26, 34
    bx = x + 14 if side == "r" else x - 14 - bw
    bx = min(max(bx, 10), MW - bw - 10); by_ = min(max(y + dy - bh / 2, 10), MH - bh - 10)
    boxes.append((v, t, bx, by_, bw, bh)); sd.rounded_rectangle([bx, by_ + 3, bx + bw, by_ + bh + 3], bh // 2, fill=90)
shadow = shadow.filter(ImageFilter.GaussianBlur(5))
m.paste(Image.new("RGB", m.size, (60, 50, 40)), (0, 0), shadow)
md = ImageDraw.Draw(m)
for v, t, bx, by_, bw, bh in boxes:
    md.rounded_rectangle([bx, by_, bx + bw, by_ + bh], bh // 2, fill=WHITE)
    md.text((bx + 13, by_ + 3), t, font=f, fill=INK)
for v in vs:
    x, y = pts[v["name"]]
    md.ellipse([x - 11, y - 11, x + 11, y + 11], fill=WHITE); md.ellipse([x - 7, y - 7, x + 7, y + 7], fill=col(v))
# 图例和版权
lf = F("m", 18); lx, ly = 22, MH - 44
lw = 30 + sum(lf.getlength(t) + 44 for _, t in cfg["legend"])
md.rounded_rectangle([lx - 8, ly - 4, lx - 8 + lw, ly + 30], 17, fill=WHITE)
for c, t in cfg["legend"]:
    c = RED if c == "r" else TEAL
    md.ellipse([lx + 6, ly + 7, lx + 20, ly + 21], fill=c); md.text((lx + 26, ly), t, font=lf, fill=(80, 80, 80)); lx += lf.getlength(t) + 44
md.text((MW - 160, MH - 30), "© OpenStreetMap", font=F("m", 15), fill=(120, 115, 108))
img.paste(m, (M, MY), rounded(m, R))

# 美食小图
PY = MY + MH + 18; PH = H - M - PY; gap = 14
tw = (MW - 2 * gap) / 3; th = (PH - gap) / 2
for i, (fn, c) in enumerate(cfg["photos"]):
    r, q = divmod(i, 3)
    x0 = M + round(q * (tw + gap)); y0 = PY + round(r * (th + gap))
    x1 = M + round(q * (tw + gap) + tw); y1 = PY + round(r * (th + gap) + th)
    t = pop(ImageOps.fit(Image.open(IMG + fn).convert("RGB"), (x1 - x0, y1 - y0), Image.LANCZOS, centering=tuple(c)))
    img.paste(t, (x0, y0), rounded(t, 18))
img.save(cfg["out"])
print({k: (round(a), round(b)) for k, (a, b) in pts.items()})
