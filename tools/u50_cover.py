"""人均50以内帽子餐厅封面：6张高饱和近拍 + 中间压暗带 + 超大金色$50。"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"k": "NotoSansCJK-Black.ttc", "b": "NotoSansCJK-Bold.ttc"}[w], s, index=2)
GOLD, RED = (255, 200, 50), (220, 40, 40)
SRC = "/home/claude/cheap/img/"
TILES = [("tida_05", .55, .5), ("postino_05", .6, .5), ("hojiak_04", .5, .5),
         ("yan_01", .5, .55), ("yeo_04", .5, .45), ("pork_03", .42, .5)]

def fill(src, w, h, fx, fy, z=1.0):
    im = Image.open(src).convert("RGB")
    s = max(w / im.width, h / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    im = im.crop((round(x), round(y), round(x) + w, round(y) + h))
    im = im.filter(ImageFilter.UnsharpMask(2, 80, 2))
    return ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.35)).enhance(1.08)

def hat(d, cx, cy, s, col):
    # 厨师帽：三个圆 + 帽箍
    r = s * .32
    for dx, dy in ((-r * .9, 0), (r * .9, 0), (0, -r * .45)):
        d.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r], fill=col)
    d.rectangle([cx - r * 1.25, cy, cx + r * 1.25, cy + s * .55], fill=col)

def stroke_text(d, xy, t, f, fill, sw=8):
    d.text(xy, t, font=f, fill=fill, stroke_width=sw, stroke_fill=(0, 0, 0))

img = Image.new("RGB", (W, H))
cw, ch = W // 2, H // 3
for i, (n, fx, fy) in enumerate(TILES):
    img.paste(fill(SRC + n + ".jpg", cw, ch, fx, fy, 1.25), ((i % 2) * cw, (i // 2) * ch))
# 中间压暗带
ov = Image.new("L", (1, H))
for y in range(H):
    c = abs(y - H * .5) / (H * .26)
    ov.putpixel((0, y), int(max(0, 1 - c) ** .7 * 215))
img = Image.composite(Image.new("RGB", (W, H), (8, 6, 6)), img, ov.resize((W, H)))
d = ImageDraw.Draw(img)
cy = H // 2
# 第一行
f1 = F("k", 84); t1 = "悉尼人均"
# 大号 $50
fb = F("k", 300); big = "$50"; fu = F("k", 110); unit = "以内"
bw = fb.getlength(big); uw = fu.getlength(unit)
tx = (W - bw - uw - 16) / 2
stroke_text(d, ((W - f1.getlength(t1)) / 2, cy - 310), t1, f1, "white", 6)
stroke_text(d, (tx, cy - 250), big, fb, GOLD, 10)
stroke_text(d, (tx + bw + 16, cy - 25), unit, fu, GOLD, 8)
# 第三行
f3 = F("k", 82); t3 = "也能吃到的10家帽子餐厅"
stroke_text(d, ((W - f3.getlength(t3)) / 2, cy + 140), t3, f3, "white", 7)
img.save(sys.argv[1], quality=93)
