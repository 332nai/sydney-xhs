"""通用单图大字封面：一张图铺满，上部压暗，白字三行（小、大、中）。
用法：python3 text_cover.py out.jpg 图片 fx fy zoom 第一行 第二行 第三行"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W, H = 1080, 1440
def F(s): return ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc", s, index=2)
out, src, fx, fy, z, l1, l2, l3 = sys.argv[1], sys.argv[2], *map(float, sys.argv[3:6]), *sys.argv[6:9]
im = Image.open(src).convert("RGB")
s = max(W / im.width, H / im.height) * z
im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
x = min(max(fx * im.width - W / 2, 0), im.width - W); y = min(max(fy * im.height - H / 2, 0), im.height - H)
img = im.crop((round(x), round(y), round(x) + W, round(y) + H)).filter(ImageFilter.UnsharpMask(2, 70, 2))
img = ImageEnhance.Contrast(ImageEnhance.Color(img).enhance(1.15)).enhance(1.05)
ov = Image.new("L", (1, H))
for yy in range(H):
    ov.putpixel((0, yy), int(max(0, 1 - yy / (H * .55)) ** 1.1 * 190))
img = Image.composite(Image.new("RGB", (W, H), (8, 8, 10)), img, ov.resize((W, H)))
d = ImageDraw.Draw(img)
def fit(t, mx, lim):
    f = mx
    while F(f).getlength(t) > lim: f -= 4
    return F(f)
def st(y, t, f, sw):
    d.text(((W - f.getlength(t)) / 2, y), t, font=f, fill="white", stroke_width=sw, stroke_fill=(0, 0, 0))
f1 = fit(l1, 90, 960); f2 = fit(l2, 200, 1000); f3 = fit(l3, 96, 980)
st(90, l1, f1, 6); y2 = 90 + f1.size + 40; st(y2, l2, f2, 10); st(y2 + f2.size + 50, l3, f3, 7)
img.save(out, quality=93)
