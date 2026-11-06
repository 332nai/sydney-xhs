"""Southwest Metro吃饭帖：五个首页方案，每个都带老杨动作包人物图标。
用法：python3 tools/swm_covers.py 图片目录 图标目录 输出目录"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps

W, H = 1080, 1440
SRC, AVATAR, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
TEAL = (22, 131, 136); TEAL_D = (12, 70, 74); CREAM = (247, 242, 233)
STOPS = [("Marrickville", "秘鲁小酒馆", "pep_06.jpg"), ("Dulwich Hill", "炭火希腊烤肉", "om_04.webp"),
         ("Hurlstone Park", "48小时发酵披萨", "fnq_04.jpg"), ("Canterbury", "毛里求斯菜", "dodo_09.jpg"),
         ("Lakemba", "也门mandi", "lak_09.webp"), ("Bankstown", "牛肉河粉和越南面包", "anto0.jpg")]

def zh(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def en(s): return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", s)

def warm(img):
    img = img.filter(ImageFilter.UnsharpMask(2, 50, 2))
    img = ImageEnhance.Color(ImageEnhance.Contrast(img).enhance(1.06)).enhance(1.12)
    r, g, b = img.split()
    r = r.point(lambda v: min(255, int(v * 1.04))); b = b.point(lambda v: int(v * .95))
    return Image.merge("RGB", (r, g, b))

def crop(name, w, h, fx=.5, fy=.5, z=1.0):
    im = ImageOps.exif_transpose(Image.open(f"{SRC}/{name}")).convert("RGB")
    s = max(w / im.width, h / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    return warm(im.crop((round(x), round(y), round(x) + w, round(y) + h)))

def shadow_text(img, items, alpha=.75, blur=14):
    """items: (x, y, text, font, anchor) anchor 'm'=居中 'l'=左对齐"""
    sh = Image.new("L", img.size, 0); d = ImageDraw.Draw(sh)
    pos = []
    for x, y, t, f, a in items:
        px = x - f.getlength(t) / 2 if a == "m" else x
        pos.append((px, y, t, f)); d.text((px, y), t, font=f, fill=200, stroke_width=4, stroke_fill=200)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    img.paste(Image.new("RGB", img.size, (0, 0, 0)), (0, 0), sh.point(lambda v: int(v * alpha)))
    d = ImageDraw.Draw(img)
    for px, y, t, f in pos: d.text((px, y), t, font=f, fill="white")

ICON_DIR = AVATAR  # 老杨动作包透明图标所在目录
def logo(img, x, y, pose="04_开吃", height=190, dark=False):
    """只放老杨的人物图标：不加圆框，不写名字，带一点柔和投影"""
    img = img.convert("RGBA")
    ic = Image.open(f"{ICON_DIR}/{pose}.png").convert("RGBA")
    ic = ic.resize((round(ic.width * height / ic.height), height), Image.LANCZOS)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    a = ic.split()[3].point(lambda v: int(v * .35))
    sh.paste((0, 0, 0, 255), (x + 4, y + 6), a)
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8)))
    img.alpha_composite(ic, (x, y))
    return img.convert("RGB")

def line_strip(img, box, label_color=(30, 30, 30), bg=(255, 255, 255, 235)):
    x0b, y0b, x1b, y1b = box
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.rounded_rectangle(box, 28, fill=bg)
    x0, x1, y = x0b + 110, x1b - 110, y0b + 85
    d.line((x0, y, x1, y), fill=TEAL, width=14)
    f = zh(26)
    for i, (s, _, _) in enumerate(STOPS):
        x = x0 + (x1 - x0) * i / (len(STOPS) - 1)
        d.ellipse((x - 20, y - 20, x + 20, y + 20), fill="white", outline=TEAL, width=8)
        for j, ln in enumerate(s.split(" ")):
            d.text((x - f.getlength(ln) / 2, y + 36 + j * 32), ln, font=f, fill=label_color)
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

# A：俯拍河粉，大字居中，底部地铁线
a = crop("ancp0.jpg", W, H, .55, .5)
shadow_text(a, [(W / 2, 290, "Southwest Metro通车了", zh(54, "Bold"), "m"),
                (W / 2, 380, "坐新地铁", zh(170, "Black"), "m"), (W / 2, 580, "去吃饭", zh(170, "Black"), "m"),
                (W / 2, 800, "从Marrickville到Bankstown，每站吃一家", zh(46), "m")])
a = line_strip(a, (40, 1150, W - 40, 1400))
logo(a, 50, 50, "04_开吃").save(f"{OUT}/cover_A.jpg", quality=93)

# B：越南面包特写，文字压在下半部，地铁线在上
b = crop("bmbn0.jpg", W, H, .62, .5)
ov = Image.new("L", (1, H))
for yy in range(H): ov.putpixel((0, yy), int(max(0, (yy - H * .45) / (H * .55)) ** 1.2 * 225))
b = Image.composite(Image.new("RGB", (W, H), (10, 8, 6)), b, ov.resize((W, H)))
shadow_text(b, [(80, 900, "悉尼新地铁通车", zh(60, "Bold"), "l"),
                (72, 980, "每站下车吃一家", zh(124, "Black"), "l"),
                (80, 1160, "Marrickville到Bankstown，6站6家店", zh(44), "l")], alpha=.5)
b = line_strip(b, (40, 210, W - 40, 460))
logo(b, 50, 40, "15_美食推荐").save(f"{OUT}/cover_B.jpg", quality=93)

# C：六宫格，每站一张图，中间一条青绿色标题带
c = Image.new("RGB", (W, H), TEAL_D)
cw, chh = W // 2, H // 3
fs = zh(28, "Bold")
d = ImageDraw.Draw(c, "RGBA")
for k, (s_, _, img_) in enumerate(STOPS):
    x, y = (k % 2) * cw, (k // 2) * chh
    c.paste(crop(img_, cw, chh, .5, .55), (x, y))
d = ImageDraw.Draw(c, "RGBA")
d.rectangle((0, 560, W, 880), fill=(*TEAL, 240))
t1, t2 = "坐新地铁去吃饭", "Southwest Metro沿线，每站一家"
f1, f2 = zh(120, "Black"), zh(44, "Medium")
d.text(((W - f1.getlength(t1)) / 2, 588), t1, font=f1, fill="white")
d.text(((W - f2.getlength(t2)) / 2, 790), t2, font=f2, fill=(220, 240, 238))
for k, (s_, _, _) in enumerate(STOPS):
    x, y = (k % 2) * cw + 24, (k // 2) * chh + chh - 62
    if k in (2, 3): y = 900
    tw = fs.getlength(s_)
    d.rounded_rectangle((x, y - 6, x + tw + 28, y + 42), 20, fill=(255, 255, 255, 225))
    d.text((x + 14, y - 2), s_, font=fs, fill=(30, 30, 30))
logo(c, 30, 30, "13_探店").save(f"{OUT}/cover_C.jpg", quality=93)

# D：青绿底的竖向线路图，每站一个圆形食物图
dd = Image.new("RGB", (W, H), CREAM)
dr = ImageDraw.Draw(dd)
dr.rectangle((0, 0, W, 330), fill=TEAL)
dr.text((70, 70), "坐新地铁去吃饭", font=zh(110, "Black"), fill="white")
dr.text((74, 230), "Southwest Metro沿线 每站一家", font=zh(44, "Medium"), fill=(215, 240, 238))
lx, y0, y1 = 250, 420, 1340
dr.line((lx, y0, lx, y1), fill=TEAL, width=18)
for i, (s, dish, img) in enumerate(STOPS):
    y = y0 + (y1 - y0) * i / (len(STOPS) - 1)
    r = 72
    ph = crop(img, 2 * r, 2 * r).convert("RGBA")
    m = Image.new("L", (2 * r, 2 * r), 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
    dr.ellipse((lx - r - 8, y - r - 8, lx + r + 8, y + r + 8), fill=TEAL)
    dd.paste(ph, (int(lx - r), int(y - r)), m)
    dr.text((lx + 120, y - 52), s, font=zh(50, "Black"), fill=(28, 28, 28))
    dr.text((lx + 122, y + 10), dish, font=zh(36), fill=(90, 84, 76))
dr.text((70, y0 - 20), "M", font=en(56), fill=TEAL)
logo(dd, W - 300, 1200, "08_吃面", 200).save(f"{OUT}/cover_D.jpg", quality=93)

# E：大数字12分钟，披萨铺满
e = crop("fnq_04.jpg", W, H, .45, .42, 1.18)
ov = Image.new("L", (1, H))
for yy in range(H): ov.putpixel((0, yy), int(max(0, 1 - yy / (H * .62)) ** 1.1 * 205))
e = Image.composite(Image.new("RGB", (W, H), (12, 8, 6)), e, ov.resize((W, H)))
shadow_text(e, [(80, 220, "Marrickville到市中心", zh(56, "Bold"), "l"),
                (70, 290, "12分钟", zh(230, "Black"), "l"),
                (80, 590, "悉尼新地铁通车了", zh(64, "Bold"), "l"),
                (80, 680, "沿线6站，每站下车吃一家", zh(48), "l")], alpha=.5)
logo(e, 50, 40, "04_开吃").save(f"{OUT}/cover_E.jpg", quality=93)
print("ok")
