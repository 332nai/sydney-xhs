"""悉尼深夜食堂封面：单张夜景美食图 + 白色大字。用法：python3 late_cover.py out.jpg 图片 fx fy zoom"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def F(s): return ImageFont.truetype(NOTO + "NotoSansCJK-Black.ttc", s, index=2)
out, src, fx, fy, z = sys.argv[1], sys.argv[2], *map(float, sys.argv[3:6])
im = Image.open(src).convert("RGB")
s = max(W / im.width, H / im.height) * z
im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
x = min(max(fx * im.width - W / 2, 0), im.width - W); y = min(max(fy * im.height - H / 2, 0), im.height - H)
img = im.crop((round(x), round(y), round(x) + W, round(y) + H)).filter(ImageFilter.UnsharpMask(2, 80, 2))
img = ImageEnhance.Contrast(ImageEnhance.Color(img).enhance(1.25)).enhance(1.06)
# 上部压暗，放标题
ov = Image.new("L", (1, H))
for yy in range(H):
    t = max(0, 1 - yy / (H * .5))
    ov.putpixel((0, yy), int(t ** 1.2 * 200))
img = Image.composite(Image.new("RGB", (W, H), (6, 6, 10)), img, ov.resize((W, H)))
d = ImageDraw.Draw(img)
def st(y, t, f, sw):
    d.text(((W - f.getlength(t)) / 2, y), t, font=f, fill="white", stroke_width=sw, stroke_fill=(0, 0, 0))
st(90, "悉尼", F(96), 6)
st(200, "深夜食堂", F(230), 10)
st(505, "开到深夜的8家店", F(84), 7)
img.save(out, quality=93)
