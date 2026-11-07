"""悉尼芒果甜品帖：首页选项、班戟来历卡、4家店卡片（2x2拼图，店名压中线）。
用法：python3 tools/mango_cards.py 图片目录 老杨图标目录 输出目录"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps

W, H = 1080, 1440
SRC, ICONS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
CREAM = (250, 244, 230); INK = (34, 28, 20); MANGO = (250, 170, 30); DEEP = (214, 110, 20)
def en(s): return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", s)
def zh(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)

def warm(img):
    img = img.filter(ImageFilter.UnsharpMask(2, 40, 2))
    img = ImageEnhance.Color(ImageEnhance.Contrast(img).enhance(1.05)).enhance(1.12)
    r, g, b = img.split()
    r = r.point(lambda v: min(255, int(v * 1.03))); b = b.point(lambda v: int(v * .96))
    return Image.merge("RGB", (r, g, b))

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

def fade(img, color, top=True, depth=.55, power=1.2, alpha=210):
    ov = Image.new("L", (1, H))
    for yy in range(H):
        t = (1 - yy / (H * depth)) if top else (yy - H * (1 - depth)) / (H * depth)
        ov.putpixel((0, yy), int(max(0, t) ** power * alpha))
    return Image.composite(Image.new("RGB", (W, H), color), img, ov.resize((W, H)))

def card(fn, no, name, tag, photos):
    img = Image.new("RGB", (W, H)); cw, ch = W // 2, H // 2
    for i, p in enumerate(photos): img.paste(crop(p, cw, ch), ((i % 2) * cw, (i // 2) * ch))
    f = en(92)
    while f.getlength(name) > 980: f = en(f.size - 4)
    shadow_text(img, [(W / 2, ch - 106, f"( {no} )", en(36), "m"), (W / 2, ch - 46, name, f, "m"), (W / 2, ch + 64, tag, zh(40), "m")], alpha=.75)
    img.save(f"{OUT}/{fn}", quality=93)

PANCAKE = ("pal_mango.webp", .5, .5)
STICKY = ("mc_4.jpg", .5, .55)
FERRY = ("ap_9.webp", .45, .5)
CAKE = ("enze_3094.jpg", .5, .5)

# ---------- 首页 ----------
# A：芒果班戟铺满，讲来历
a = fade(crop(("pal_mango.webp", .5, .55, 1.0), W, H), (40, 20, 4), True, .55, 1.1, 200)
shadow_text(a, [(76, 150, "悉尼卖芒果班戟", zh(96, "Black"), "l"), (70, 280, "比满记还早", zh(150, "Black"), "l"),
                (80, 480, "芒果季，这4家芒果甜品现在去吃", zh(46, "Bold"), "l")], alpha=.55)
icon(a, "09_吃甜品", W - 280, H - 300, 240).save(f"{OUT}/cover_A.jpg", quality=93)

# B：四宫格，中间芒果色标题带
b = Image.new("RGB", (W, H)); cw, ch = W // 2, H // 2
for i, p in enumerate([PANCAKE, STICKY, FERRY, CAKE]): b.paste(crop(p, cw, ch), ((i % 2) * cw, (i // 2) * ch))
d = ImageDraw.Draw(b, "RGBA")
d.rectangle((0, ch - 170, W, ch + 170), fill=(*MANGO, 245))
f1 = zh(118, "Black"); t = "悉尼芒果季"; d.text(((W - f1.getlength(t)) / 2, ch - 150), t, font=f1, fill=INK)
f2 = zh(52, "Bold"); t = "这4样芒果甜品，现在吃"; d.text(((W - f2.getlength(t)) / 2, ch + 40), t, font=f2, fill=INK)
icon(b, "05_品尝", 30, 30, 200).save(f"{OUT}/cover_B.jpg", quality=93)

# C：AP芒果酥特写，文字在下
c = fade(crop(("ap_9.webp", .5, .5, 1.0), W, H), (40, 22, 6), False, .5, 1.1, 215)
shadow_text(c, [(70, 980, "悉尼芒果季", zh(150, "Black"), "l"), (76, 1180, "班戟、糯米饭、芒果酥、奶油蛋糕", zh(46, "Bold"), "l")], alpha=.5)
icon(c, "04_开吃", 50, 50, 200).save(f"{OUT}/cover_C.jpg", quality=93)

# D：芒果黄底，大字加四个圆
dd = Image.new("RGB", (W, H), (255, 214, 90)); d = ImageDraw.Draw(dd)
d.text((70, 110), "悉尼", font=zh(110, "Black"), fill=INK)
d.text((70, 240), "芒果甜品", font=zh(170, "Black"), fill=INK)
d.text((76, 450), "芒果季，趁现在去吃", font=zh(50, "Bold"), fill=(120, 70, 10))
r = 175
for i, (p, lab) in enumerate([(PANCAKE, "芒果班戟"), (STICKY, "芒果糯米饭"), (FERRY, "芒果奶油酥"), (CAKE, "芒果奶油蛋糕")]):
    cx, cy = 290 + (i % 2) * 500, 725 + (i // 2) * 420
    ph = crop(p, 2 * r, 2 * r); m = Image.new("L", (2 * r, 2 * r), 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
    d.ellipse((cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10), fill="white")
    dd.paste(ph, (cx - r, cy - r), m); d = ImageDraw.Draw(dd)
    f = zh(36, "Black"); tw = f.getlength(lab)
    d.rounded_rectangle((cx - tw / 2 - 20, cy + r + 2, cx + tw / 2 + 20, cy + r + 62), 28, fill=INK)
    d.text((cx - tw / 2, cy + r + 6), lab, font=f, fill="white")
icon(dd, "09_吃甜品", W - 260, 60, 210).save(f"{OUT}/cover_D.jpg", quality=93)

# ---------- 01 班戟来历 ----------
s = Image.new("RGB", (W, H), CREAM)
s.paste(crop(("pal_mango.webp", .5, .5, 1.0), W, 700), (0, 0))
d = ImageDraw.Draw(s)
d.text((70, 760), "芒果班戟", font=zh(110, "Black"), fill=INK)
d.text((70, 890), "悉尼比香港先卖", font=zh(110, "Black"), fill=DEEP)
rows = [("1991年左右", "悉尼唐人街的Marigold酒楼开始卖芒果班戟"), ("1995年", "香港满记甜品才开第一家店"),
        ("现在", "Marigold已经关门，最早是谁发明的没有定论")]
y = 1060
for k, v in rows:
    d.text((74, y), k, font=zh(36, "Black"), fill=DEEP)
    d.text((300, y), v, font=zh(34), fill=INK); y += 74
s.save(f"{OUT}/01.jpg", quality=93)

# ---------- 店卡 ----------
card("02.jpg", "01", "PALACE CHINESE", "大厨推荐的芒果班戟，配推车早茶",
     [PANCAKE, ("pal_a.webp", .5, .45), ("pal_c.webp", .45, .45), ("palc_9.jpg", .5, .5)])
card("03.jpg", "02", "MANGO COCO", "泰式甜品店，招牌是芒果糯米饭",
     [STICKY, ("mc_9.jpg", .55, .55), ("mc_5.jpg", .5, .5), ("mc_7.jpg", .5, .45)])
card("04.jpg", "03", "AP BAKERY MANLY", "限定芒果奶油酥，$15一个",
     [FERRY, ("ap_7.webp", .5, .5), ("ap_3.webp", .5, .5), ("ap_0.webp", .5, .5)])
card("05.jpg", "04", "ENZE", "戚风芒果奶油蛋糕，6寸$71",
     [CAKE, ("enze_3096.jpg", .5, .5), ("enze_3098.jpg", .5, .5), ("enze_3100.jpg", .5, .5)])
print("ok")
