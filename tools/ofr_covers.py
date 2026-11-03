"""Overflow Room 封面三选一（日本巷子角度）。
用法：python3 tools/ofr_covers.py 图片目录 输出目录"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

W, H = 1080, 1440
SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
L0, L1, L2, L3 = "Algorithm新店", "悉尼这家新咖啡店", "有点东京那味了", ""

def sans(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def serif(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSerifCJK-{w}.ttc", s, index=2)

def warm(img, k=1.0):
    img = img.filter(ImageFilter.UnsharpMask(2, 60, 2))
    img = ImageEnhance.Color(ImageEnhance.Contrast(img).enhance(1.08)).enhance(1 + .18 * k)
    r, g, b = img.split()
    r = r.point(lambda v: min(255, int(v * (1 + .05 * k)))); b = b.point(lambda v: int(v * (1 - .07 * k)))
    return Image.merge("RGB", (r, g, b))

def crop(name, fx, fy, z=1.0, k=1.0):
    im = Image.open(f"{SRC}/{name}.webp").convert("RGB")
    s = max(W / im.width, H / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - W / 2, 0), im.width - W); y = min(max(fy * im.height - H / 2, 0), im.height - H)
    return warm(im.crop((round(x), round(y), round(x) + W, round(y) + H)), k)

def fade(img, color, depth, power, alpha):
    ov = Image.new("L", (1, H))
    for yy in range(H):
        ov.putpixel((0, yy), int(max(0, 1 - yy / (H * depth)) ** power * alpha))
    return Image.composite(Image.new("RGB", (W, H), color), img, ov.resize((W, H)))

def text(img, ink, acc, sub, stroke=None, y0=96):
    d = ImageDraw.Draw(img)
    kw = dict(stroke_width=3, stroke_fill=stroke) if stroke else {}
    d.text((80, y0), L0, font=sans(42, "Bold"), fill=acc, **kw)
    d.text((76, y0 + 70), L1, font=serif(112), fill=ink)
    d.text((76, y0 + 206), L2, font=serif(112), fill=ink)
    if L3: d.text((80, y0 + 360), L3, font=sans(44), fill=sub, **kw)
    return img

# A：蓝花楹小巷，浅色杂志风，深色字
a = fade(crop("o030", .63, .62, 1.0, .7), (246, 241, 232), .48, 1.0, 240)
text(a, (30, 27, 24), (160, 82, 48), (40, 36, 32)).save(f"{OUT}/cover_A.jpg", quality=93)

# B：门店正面，暖色吧台，白字
b = fade(crop("o018", .52, .5), (14, 11, 9), .5, 1.1, 215)
text(b, "white", (240, 200, 170), (245, 240, 232), (20, 15, 12)).save(f"{OUT}/cover_B.jpg", quality=93)

# C：饮品特写，暗背景，白字
c = crop("o021", .5, .5, 1.0).transpose(Image.FLIP_TOP_BOTTOM)
c = fade(c, (12, 9, 7), .5, 1.2, 225).transpose(Image.FLIP_TOP_BOTTOM)
text(c, "white", (232, 190, 150), (238, 230, 220), (12, 9, 7), y0=1000).save(f"{OUT}/cover_C.jpg", quality=93)
print("ok")
