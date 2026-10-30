"""Common Supply封面三个方案：都带品牌logo（logo从官方图里抠出来）。用法：python3 cs_covers.py 输出目录"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W, H = 1080, 1440
P = "data/post_img/"
def F(s): return ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc", s, index=2)
od = sys.argv[1]

# 从官方图左侧色块抠出 logo 字样，做成白色透明图
src = Image.open(P + "cs_b_00.jpg").convert("RGB").crop((20, 45, 345, 200))
a = np.asarray(src).astype(int); lum = a.mean(axis=2)
bg = np.median(lum)
alpha = np.clip((lum - bg - 18) * 6, 0, 255).astype("uint8")
logo = Image.new("RGBA", src.size, (255, 255, 255, 0)); logo.putalpha(Image.fromarray(alpha))
bbox = logo.getbbox(); logo = logo.crop(bbox)
def logo_at(img, cx, cy, w, color=(255, 255, 255)):
    lg = logo.resize((w, round(logo.height * w / logo.width)), Image.LANCZOS)
    solid = Image.new("RGBA", lg.size, color + (255,)); solid.putalpha(lg.getchannel("A"))
    sh = Image.new("RGBA", lg.size, (0, 0, 0, 255)); sh.putalpha(lg.getchannel("A").filter(ImageFilter.GaussianBlur(6)))
    img.paste(sh, (int(cx - lg.width / 2) + 3, int(cy - lg.height / 2) + 3), sh)
    img.paste(solid, (int(cx - lg.width / 2), int(cy - lg.height / 2)), solid)
    return lg.height

def fill(path, w, h, fx=.5, fy=.5, z=1.0, box=None):
    im = Image.open(path).convert("RGB")
    if box: im = im.crop(box)
    s = max(w / im.width, h / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    im = im.crop((round(x), round(y), round(x) + w, round(y) + h)).filter(ImageFilter.UnsharpMask(2, 70, 2))
    return ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.12)).enhance(1.05)

def grad(img, top=True, k=.5, a=200):
    ov = Image.new("L", (1, H))
    for yy in range(H):
        t = (1 - yy / (H * k)) if top else (yy - H * (1 - k)) / (H * k)
        ov.putpixel((0, yy), int(max(0, min(1, t)) ** 1.1 * a))
    return Image.composite(Image.new("RGB", (W, H), (8, 8, 10)), img, ov.resize((W, H)))

def ctext(d, y, t, size, sw=8, fill="white"):
    f = F(size)
    while f.getlength(t) > W - 80: size -= 4; f = F(size)
    d.text(((W - f.getlength(t)) / 2, y), t, font=f, fill=fill, stroke_width=sw, stroke_fill=(0, 0, 0))
    return f.size

# 方案A：排队照片，顶部大logo，下面标题
img = grad(fill(P + "cs_a_03.jpg", W, H, .5, .6), True, .55, 210)
d = ImageDraw.Draw(img)
h = logo_at(img, W / 2, 210, 600)
y = 210 + h / 2 + 60
y += ctext(d, y, "悉尼版Erewhon", 84, 6) + 30
ctext(d, y, "凭什么排队排到街角", 104, 8)
img.save(f"{od}/cs_cover_A.jpg", quality=93)

# 方案B：Bondi门店夜景，招牌本身就是logo；标题放在底部
img = grad(ImageEnhance.Brightness(fill(P + "cs_b_00.jpg", W, H, .5, .5, 1.0, box=(368, 0, 1234, 800))).enhance(1.25), False, .45, 225)
d = ImageDraw.Draw(img)
y = H - 470
y += ctext(d, y, "悉尼版Erewhon", 84, 6) + 30
y += ctext(d, y, "凭什么排队排到街角", 104, 8) + 60
logo_at(img, W / 2, y + 50, 340)
img.save(f"{od}/cs_cover_B.jpg", quality=93)

# 方案C：上半排队、下半Bondi门店招牌，中间一条深色带放logo和标题
TOPH, BOTH = 520, 480
img = Image.new("RGB", (W, H), (20, 18, 16))
img.paste(fill(P + "cs_a_03.jpg", W, TOPH, .5, .62), (0, 0))
img.paste(ImageEnhance.Brightness(fill(P + "cs_b_00.jpg", W, BOTH, .3, .55, 1.0, box=(368, 0, 1234, 800))).enhance(1.2), (0, H - BOTH))
d = ImageDraw.Draw(img)
d.rectangle([0, TOPH, W, H - BOTH], fill=(28, 26, 24))
logo_at(img, W / 2, TOPH + 95, 420)
ctext(d, TOPH + 200, "悉尼版Erewhon凭什么", 80, 0)
ctext(d, TOPH + 305, "排队排到街角", 88, 0, fill=(236, 222, 196))
img.save(f"{od}/cs_cover_C.jpg", quality=93)
