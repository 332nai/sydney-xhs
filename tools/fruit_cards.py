"""悉尼水果日历帖：季节卡（2x2照片，每格写水果名和月份）和首页选项。
用法：python3 tools/fruit_cards.py 照片目录 老杨图标目录 输出目录
照片目录下按 水果英文名/编号.jpg 存放，PICK 里写选用哪张和裁切参数。"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps

W, H = 1080, 1440
SRC, ICONS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
CREAM = (248, 243, 234); INK = (34, 32, 30)
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

def icon(img, pose, x, y, h):
    ic = Image.open(f"{ICONS}/{pose}.png").convert("RGBA")
    ic = ic.resize((round(ic.width * h / ic.height), h), Image.LANCZOS)
    img = img.convert("RGBA"); sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 255), (x + 4, y + 6), ic.split()[3].point(lambda v: int(v * .3)))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8))); img.alpha_composite(ic, (x, y))
    return img.convert("RGB")

def season(fn, title, months, col, items):
    """items: [(照片spec, 水果名, 月份)] 四个"""
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 200), fill=col)
    d.text((64, 46), title, font=zh(96, "Black"), fill="white")
    f = zh(44, "Bold"); d.text((W - 64 - f.getlength(months), 88), months, font=f, fill="white")
    cw, ch = W // 2, (H - 200) // 2
    for i, (spec, name, m) in enumerate(items):
        x, y = (i % 2) * cw, 200 + (i // 2) * ch
        img.paste(crop(spec, cw, ch), (x, y))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        f1, f2 = zh(52, "Black"), zh(32, "Bold")
        bw = max(f1.getlength(name), f2.getlength(m)) + 52
        od.rounded_rectangle((x + 28, y + ch - 168, x + 28 + bw, y + ch - 28), 26, fill=(255, 255, 255, 236))
        od.text((x + 54, y + ch - 158), name, font=f1, fill=INK)
        od.text((x + 54, y + ch - 82), m, font=f2, fill=col)
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(img)
    d.line((cw, 200, cw, H), fill=CREAM, width=6); d.line((0, 200 + ch, W, 200 + ch), fill=CREAM, width=6)
    img.save(f"{OUT}/{fn}", quality=93)

GREEN, RED_, BROWN, BLUE = (96, 140, 70), (214, 96, 70), (176, 112, 50), (70, 100, 140)
season("02.jpg", "现在吃什么", "9到11月", GREEN,
       [(("mango2/07.jpg", .22, .62, 1.7), "芒果", "9月到2月"), (("cherry/03.jpg", .5, .5), "樱桃", "11月到1月"),
        (("loquat/16.jpg", .5, .35), "枇杷", "只有11月"), (("blueberry/03.jpg", .5, .5), "蓝莓", "10月到2月")])
season("03.jpg", "夏天", "12到2月", RED_,
       [(("lychee/02.jpg", .5, .5), "荔枝", "12月到2月"), (("peach/11.jpg", .45, .55), "桃子", "12月到2月"),
        (("rambutan/01.jpg", .5, .45), "红毛丹", "1月到2月"), (("mangosteen/02.jpg", .6, .45), "山竹", "2月到3月")])
season("04.jpg", "秋天", "3到5月", BROWN,
       [(("pomegranate/05.jpg", .55, .5), "石榴", "3月到5月"), (("persimmon/12.jpg", .5, .4), "柿子", "只有4到5月"),
        (("grape/14.jpg", .45, .5), "葡萄", "12月到5月"), (("fig/05.jpg", .55, .5), "无花果", "2月到3月")])
season("05.jpg", "冬天", "6到8月", BLUE,
       [(("mandarin/02.jpg", .5, .5), "柑橘", "4月到9月"), (("pomelo/16.jpg", .5, .6), "柚子", "6月到10月"),
        (("strawberry/02.jpg", .5, .5), "草莓", "7月开始"), (("bloodorange/00.jpg", .4, .5), "血橙", "只有8到9月")])
print("ok")

# ---------- 首页选项 ----------
def shadow_text(img, items, alpha=.6, blur=14):
    sh = Image.new("L", img.size, 0); dd = ImageDraw.Draw(sh)
    for x, y, t, f, a in items:
        px = x - f.getlength(t) / 2 if a == "m" else x
        dd.text((px, y), t, font=f, fill=200, stroke_width=4, stroke_fill=200)
    img.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha)))
    dd = ImageDraw.Draw(img)
    for x, y, t, f, a in items:
        dd.text((x - f.getlength(t) / 2 if a == "m" else x, y), t, font=f, fill="white")

# A：九宫格水果，中间一条奶油色标题带
a = Image.new("RGB", (W, H), CREAM)
grid = ["lychee/02.jpg", "cherry/03.jpg", "mangosteen/02.jpg", ("mango2/07.jpg", .22, .62, 1.7), "persimmon/12.jpg",
        "strawberry/02.jpg", "pomegranate/05.jpg", "bloodorange/00.jpg", "peach/11.jpg"]
cw, ch = W // 3, H // 3
for i, sp in enumerate(grid): a.paste(crop(sp, cw + 1, ch + 1), ((i % 3) * cw, (i // 3) * ch))
d = ImageDraw.Draw(a)
d.rectangle((0, 520, W, 900), fill=CREAM)
f1 = zh(150, "Black"); t = "悉尼水果日历"; d.text(((W - f1.getlength(t)) / 2, 560), t, font=f1, fill=INK)
f2 = zh(48, "Bold"); t = "24种水果，几月最当季"; d.text(((W - f2.getlength(t)) / 2, 780), t, font=f2, fill=(214, 96, 70))
icon(a, "09_吃甜品", W - 240, 330, 190).save(f"{OUT}/cover_A.jpg", quality=93)

# B：荔枝铺满，大字讲反季
b = crop(("lychee/02.jpg", .5, .5, 1.0), W, H)
ov = Image.new("L", (1, H))
for yy in range(H): ov.putpixel((0, yy), int(max(0, 1 - yy / (H * .55)) ** 1.2 * 200))
b = Image.composite(Image.new("RGB", (W, H), (40, 12, 16)), b, ov.resize((W, H)))
shadow_text(b, [(76, 140, "在悉尼", zh(90, "Black"), "l"), (70, 260, "荔枝要等到", zh(150, "Black"), "l"),
                (70, 440, "圣诞节", zh(150, "Black"), "l"), (80, 650, "悉尼一年24种水果的应季月份", zh(46, "Bold"), "l")])
icon(b, "05_品尝", W - 280, H - 300, 240).save(f"{OUT}/cover_B.jpg", quality=93)

# C：奶油底，12个月份圆形小图围成一圈
c = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(c)
mon = [(11, "loquat/16.jpg"), (12, "cherry/03.jpg"), (1, "lychee/02.jpg"), (2, "mangosteen/02.jpg"), (3, "fig/05.jpg"),
       (4, "persimmon/12.jpg"), (5, "pomegranate/05.jpg"), (6, "mandarin/02.jpg"), (7, "strawberry/02.jpg"),
       (8, "bloodorange/00.jpg"), (9, ("mango2/07.jpg", .22, .62, 1.7)), (10, "blueberry/03.jpg")]
import math
cx, cy, R, r = W / 2, 820, 400, 92
for i, (m, sp) in enumerate(mon):
    ang = -math.pi / 2 + i * 2 * math.pi / 12
    x, y = cx + R * math.cos(ang), cy + R * math.sin(ang)
    ph = crop(sp, 2 * r, 2 * r); mk = Image.new("L", (2 * r, 2 * r), 0); ImageDraw.Draw(mk).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
    d.ellipse((x - r - 6, y - r - 6, x + r + 6, y + r + 6), fill="white")
    c.paste(ph, (int(x - r), int(y - r)), mk)
    t = f"{m}月"; f = zh(30, "Black"); tw = f.getlength(t)
    d.rounded_rectangle((x - tw / 2 - 14, y + r - 20, x + tw / 2 + 14, y + r + 26), 20, fill=INK)
    d.text((x - tw / 2, y + r - 18), t, font=f, fill="white")
f1 = zh(120, "Black"); t = "悉尼水果"; d.text((cx - f1.getlength(t) / 2, cy - 150), t, font=f1, fill=INK)
t = "日历"; d.text((cx - f1.getlength(t) / 2, cy - 10), t, font=f1, fill=(214, 96, 70))
f2 = zh(46, "Bold"); t = "每个月吃什么"; d.text((cx - f2.getlength(t) / 2, 140), t, font=f2, fill=(110, 104, 96))
icon(c, "15_美食推荐", 40, 40, 200).save(f"{OUT}/cover_C.jpg", quality=93)

# D：芒果特写铺满，标题在下
dd = crop(("mango2/07.jpg", .3, .68, 1.6), W, H)
ov = Image.new("L", (1, H))
for yy in range(H): ov.putpixel((0, yy), int(max(0, (yy - H * .45) / (H * .55)) ** 1.1 * 215))
dd = Image.composite(Image.new("RGB", (W, H), (30, 18, 8)), dd, ov.resize((W, H)))
shadow_text(dd, [(70, 980, "悉尼水果日历", zh(140, "Black"), "l"), (76, 1170, "芒果、荔枝、樱桃，几月最好吃", zh(48, "Bold"), "l")], alpha=.5)
icon(dd, "04_开吃", 50, 50, 200).save(f"{OUT}/cover_D.jpg", quality=93)
print("covers ok")
