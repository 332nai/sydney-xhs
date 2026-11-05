"""Paddington咖啡店卡片：封面单图大字，内页2x2拼图，店名压在中线。
用法：python3 tools/pad_cards.py 图片目录 输出目录"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

W, H = 1080, 1440
SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
EN = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
def en(s): return ImageFont.truetype(EN, s)
def zh(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)

def warm(img):
    img = img.filter(ImageFilter.UnsharpMask(2, 50, 2))
    img = ImageEnhance.Color(ImageEnhance.Contrast(img).enhance(1.06)).enhance(1.12)
    r, g, b = img.split()
    r = r.point(lambda v: min(255, int(v * 1.04))); b = b.point(lambda v: int(v * .95))
    return Image.merge("RGB", (r, g, b))

def crop(spec, w, h):
    spec = list(spec) if isinstance(spec, tuple) else [spec]
    name, fx, fy, z = spec + [.5, .5, 1.0][len(spec) - 1:]
    im = Image.open(f"{SRC}/{name}").convert("RGB")
    s = max(w / im.width, h / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    return warm(im.crop((round(x), round(y), round(x) + w, round(y) + h)))

def shadow_text(img, items):
    """items: (x_center, y, text, font). 先画模糊阴影再画白字。"""
    sh = Image.new("L", img.size, 0); d = ImageDraw.Draw(sh)
    for cx, y, t, f in items:
        d.text((cx - f.getlength(t) / 2, y), t, font=f, fill=200, stroke_width=4, stroke_fill=200)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    img.paste(Image.new("RGB", img.size, (0, 0, 0)), (0, 0), sh.point(lambda v: int(v * .75)))
    d = ImageDraw.Draw(img)
    for cx, y, t, f in items:
        d.text((cx - f.getlength(t) / 2, y), t, font=f, fill="white")

def card(fn, no, name, tag, photos):
    img = Image.new("RGB", (W, H))
    cw, ch = W // 2, H // 2
    for i, p in enumerate(photos):
        img.paste(crop(p, cw, ch), ((i % 2) * cw, (i // 2) * ch))
    f = en(92)
    while f.getlength(name) > 980: f = en(f.size - 4)
    shadow_text(img, [(W / 2, ch - 106, f"( {no} )", en(36)), (W / 2, ch - 46, name, f), (W / 2, ch + 64, tag, zh(40))])
    img.save(f"{OUT}/{fn}", quality=93)

# 封面
c = crop(("ak006.webp", .42, .5, 1.0), W, H)
shadow_text(c, [(W / 2, 440, "A Little Cafe Guide To", en(50)), (W / 2, 520, "PADDINGTON", en(150)), (W / 2, 700, "悉尼Paddington咖啡小指南", zh(48))])
c.save(f"{OUT}/00.jpg", quality=93)

card("01.jpg", "01", "ADELAIDE'S KITCHEN", "这栋老房子第一次开成咖啡店",
     [("ak012.webp", .5, .5), ("ak027.webp", .5, .55), ("ak022.webp", .5, .5), ("ak031.webp", .5, .5)])
card("02.jpg", "02", "LÈ BAUS", "男装店里藏着咖啡吧和黑胶",
     [("lb00.jpg", .45, .5), ("lb01.jpg", .5, .5), ("lb02.jpg", .5, .5), ("lb06.jpg", .5, .5)])
card("03.jpg", "03", "SONDER", "Five Ways街角的老排屋",
     [("sw_court.jpg", .5, .5), ("sw_avo.jpg", .5, .5), ("son_sit.jpg", .5, .5), ("sw_brunch.jpg", .5, .5)])
card("04.jpg", "04", "JACOB THE ANGEL", "从伦敦来，店里卖Lune可颂",
     [("jf0.jpg", .3, .5), ("jac02.jpg", .5, .5), ("jf2.jpg", .5, .45), ("jf1.jpg", .5, .5)])
card("05.jpg", "05", "AMPERSAND", "三层楼，三万本二手书",
     [("ampcp2.jpg", .5, .5), ("amp00.jpg", .4, .5), ("ampcp5.jpg", .5, .5), ("ampss3.jpg", .5, .5)])
card("06.jpg", "06", "MECCA COFFEE", "悉尼老牌烘焙商的Paddington店",
     [("mec04.jpg", .5, .5), ("mec01.jpg", .5, .5), ("mec05.jpg", .5, .5), ("mec02.jpg", .5, .4)])
print("ok")
