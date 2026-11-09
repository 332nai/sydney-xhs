"""悉尼地中海海边餐厅帖：首页选项和6张店卡（2x2拼图，店名压中线；Club Amalfi用三图版式）。
用法：python3 tools/med_cards.py 图片目录 老杨图标目录 输出目录"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
Image.MAX_IMAGE_PIXELS = None
W, H = 1080, 1440
SRC, ICONS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
SEA = (32, 92, 150); CREAM = (250, 245, 234); INK = (24, 30, 40); SUN = (246, 196, 70)
def en(s): return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", s)
def zh(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)

def warm(img):
    img = img.filter(ImageFilter.UnsharpMask(2, 40, 2))
    return ImageEnhance.Color(ImageEnhance.Contrast(img).enhance(1.04)).enhance(1.10)

def crop(spec, w, h):
    spec = list(spec) if isinstance(spec, tuple) else [spec]
    name, fx, fy, z = spec + [.5, .5, 1.0][len(spec) - 1:]
    im = ImageOps.exif_transpose(Image.open(f"{SRC}/{name}")).convert("RGB")
    s = max(w / im.width, h / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    return warm(im.crop((round(x), round(y), round(x) + w, round(y) + h)))

def shadow_text(img, items, alpha=.7, blur=14):
    sh = Image.new("L", img.size, 0); d = ImageDraw.Draw(sh)
    for x, y, t, f, a in items:
        px = x - f.getlength(t) / 2 if a == "m" else x
        d.text((px, y), t, font=f, fill=200, stroke_width=4, stroke_fill=200)
    img.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha)))
    d = ImageDraw.Draw(img)
    for x, y, t, f, a in items:
        d.text((x - f.getlength(t) / 2 if a == "m" else x, y), t, font=f, fill="white")

def icon(img, pose, x, y, h):
    ic = Image.open(f"{ICONS}/{pose}.png").convert("RGBA")
    ic = ic.resize((round(ic.width * h / ic.height), h), Image.LANCZOS)
    img = img.convert("RGBA"); sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 255), (x + 4, y + 6), ic.split()[3].point(lambda v: int(v * .3)))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8))); img.alpha_composite(ic, (x, y))
    return img.convert("RGB")

def fade(img, color, top=True, depth=.55, power=1.2, alpha=200):
    ov = Image.new("L", (1, H))
    for yy in range(H):
        t = (1 - yy / (H * depth)) if top else (yy - H * (1 - depth)) / (H * depth)
        ov.putpixel((0, yy), int(max(0, t) ** power * alpha))
    return Image.composite(Image.new("RGB", (W, H), color), img, ov.resize((W, H)))

def card(fn, no, name, tag, photos, three=False):
    img = Image.new("RGB", (W, H)); cw, ch = W // 2, H // 2
    if three:
        img.paste(crop(photos[0], W, ch), (0, 0))
        for i, p in enumerate(photos[1:3]): img.paste(crop(p, cw, ch), (i * cw, ch))
    else:
        for i, p in enumerate(photos): img.paste(crop(p, cw, ch), ((i % 2) * cw, (i // 2) * ch))
    f = en(92)
    while f.getlength(name) > 980: f = en(f.size - 4)
    shadow_text(img, [(W / 2, ch - 106, f"( {no} )", en(36), "m"), (W / 2, ch - 46, name, f, "m"), (W / 2, ch + 64, tag, zh(40), "m")], alpha=.75)
    img.save(f"{OUT}/{fn}", quality=93)

# ---------- 店卡 ----------
card("01.jpg", "01", "ST SIANDRA", "阿马尔菲海岸风，门口就是海滩",
     [("ss_to2.jpg", .5, .6), ("ss_cp6.jpg", .5, .5), ("ss_cp7.jpg", .5, .5), ("ss_cp0.jpg", .5, .5)])
card("02.jpg", "02", "AKTI", "爱琴海日落色，白伞下吃希腊菜",
     [("ak_to0.jpg", .5, .6), ("ak_c10.jpg", .5, .5), ("ak_med.jpg", .5, .5), ("ak_c7.jpg", .5, .5)])
card("03.jpg", "03", "SAILS ON LAVENDER BAY", "蔚蓝海岸风装修，正对海港大桥",
     [("sa_to0.jpg", .5, .5), ("sa_to3.jpg", .5, .5), ("sa_to2.jpg", .5, .5), ("sa_to1.jpg", .5, .5)])
card("04.jpg", "04", "MARTINEZ", "戛纳酒店风，楼顶露台看大桥",
     [("ma_sq0.jpg", .45, .5), ("ma_b12.webp", .5, .5), ("ma_sq2.jpg", .5, .5), ("ma_b3.webp", .5, .5)])
card("05.jpg", "05", "WHALEBRIDGE", "全露天，对着歌剧院吃海鲜塔",
     [("wh_b15.jpg", .5, .5), ("wh_b6.jpg", .5, .5), ("wh_b11.jpg", .5, .5), ("wh_b1.jpg", .5, .5)])
card("06.jpg", "06", "CLUB AMALFI", "Watsons Bay每月一次的海滩派对",
     [("wb_ca1.jpg", .5, .5), ("wb_ca0.jpg", .5, .5), ("wb_ca2.jpg", .5, .5)], three=True)

# ---------- 首页 ----------
T1, T2, T3 = "不用飞欧洲", "悉尼的地中海夏天", "6家海边餐厅，阿马尔菲、蔚蓝海岸、爱琴海"
# A：St Siandra沙滩椅铺满，大字在上
a = fade(crop(("ss_cp6.jpg", .42, .5, 1.0), W, H), (10, 30, 60), True, .5, 1.1, 190)
shadow_text(a, [(76, 140, T1, zh(84, "Black"), "l"), (70, 250, T2, zh(118, "Black"), "l"), (80, 420, T3, zh(40, "Bold"), "l")], alpha=.5)
icon(a, "06_拍照打卡", W - 290, H - 300, 240).save(f"{OUT}/cover_A.jpg", quality=93)

# B：六宫格，中间海蓝标题带
b = Image.new("RGB", (W, H)); cw, ch = W // 2, H // 3
for i, p in enumerate([("ss_to2.jpg", .5, .6), ("ak_c10.jpg", .5, .5), ("sa_to3.jpg", .5, .5), ("ma_sq0.jpg", .45, .5), ("wh_b15.jpg", .5, .5), ("wb_ca1.jpg", .5, .5)]):
    b.paste(crop(p, cw, ch), ((i % 2) * cw, (i // 2) * ch))
d = ImageDraw.Draw(b, "RGBA")
d.rectangle((0, 560, W, 880), fill=(*SEA, 242))
f1 = zh(112, "Black"); d.text(((W - f1.getlength(T2)) / 2, 585), T2, font=f1, fill="white")
f2 = zh(46, "Bold"); t = "不用飞欧洲，这6家海边餐厅就够"; d.text(((W - f2.getlength(t)) / 2, 780), t, font=f2, fill=(220, 236, 250))
icon(b, "06_拍照打卡", 30, 30, 190).save(f"{OUT}/cover_B.jpg", quality=93)

# C：Akti粉色沙滩椅，文字在下
c = fade(crop(("ak_c10.jpg", .5, .45, 1.0), W, H), (60, 26, 20), False, .5, 1.1, 200)
shadow_text(c, [(70, 960, T2, zh(118, "Black"), "l"), (76, 1130, T1 + "，这6家就够", zh(50, "Bold"), "l")], alpha=.5)
icon(c, "12_聚餐", 40, 40, 190).save(f"{OUT}/cover_C.jpg", quality=93)

# D：奶油底，蓝色大字，三张拱形图
dd = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(dd)
d.text((70, 90), T1, font=zh(80, "Black"), fill=SEA)
d.text((70, 200), T2, font=zh(118, "Black"), fill=INK)
d.text((76, 360), T3, font=zh(38, "Bold"), fill=(120, 110, 96))
aw, ah, gap = 300, 860, 30; x0 = (W - 3 * aw - 2 * gap) // 2
for i, p in enumerate([("ss_to2.jpg", .5, .6), ("ak_c10.jpg", .5, .5), ("wh_b15.jpg", .5, .5)]):
    ph = crop(p, aw, ah); m = Image.new("L", (aw, ah), 0); md = ImageDraw.Draw(m)
    md.rectangle((0, aw // 2, aw, ah), fill=255); md.ellipse((0, 0, aw - 1, aw), fill=255)
    dd.paste(ph, (x0 + i * (aw + gap), 480), m)
icon(dd, "06_拍照打卡", W - 270, 60, 200).save(f"{OUT}/cover_D.jpg", quality=93)
print("ok")
