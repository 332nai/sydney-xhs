"""米其林厨师在悉尼的店：整张照片铺满的封面，上方三颗普通金色星星（不是米其林官方标志）。
用法：python3 mich_cover2.py out.jpg 图片 fx fy"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def S(w, s): return ImageFont.truetype(NOTO + f"NotoSerifCJK-{w}.ttc", s, index=2)
def K(w, s): return ImageFont.truetype(NOTO + f"NotoSansCJK-{w}.ttc", s, index=2)
GOLD = (232, 190, 92)
out, src, fx, fy = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
im = Image.open(src).convert("RGB")
s = max(W / im.width, H / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
x = min(max(fx * im.width - W / 2, 0), im.width - W); y = min(max(fy * im.height - H / 2, 0), im.height - H)
img = im.crop((round(x), round(y), round(x) + W, round(y) + H)).filter(ImageFilter.UnsharpMask(2, 90, 2))
img = ImageEnhance.Contrast(ImageEnhance.Color(img).enhance(1.12)).enhance(1.06)
ov = Image.new("L", (1, H))
for yy in range(H):
    t = (yy - H * .45) / (H * .55)
    ov.putpixel((0, yy), int(max(0, min(1, t)) ** 1.1 * 225))
img = Image.composite(Image.new("RGB", (W, H), (10, 8, 6)), img, ov.resize((W, H)))
d = ImageDraw.Draw(img)
def star(cx, cy, r, col):
    import math
    pts = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * .42
        pts.append((cx + rr * math.cos(a), cy - rr * math.sin(a)))
    d.polygon(pts, fill=col)
y0 = H - 560
for i in range(3): star(84 + 30 + i * 74, y0 + 30, 30, GOLD)
d.text((80, y0 + 84), "米其林厨师", font=S("Black", 150), fill="white")
d.text((80, y0 + 288), "在悉尼开的店", font=S("SemiBold", 84), fill="white")
d.text((84, y0 + 420), "5家已经开业，3家2027年开", font=K("Medium", 38), fill=(225, 218, 205))
img.save(out, quality=93)
