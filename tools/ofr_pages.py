"""Overflow Room（Algorithm新店）图组：封面加6张内页，1080x1440。
用法：python3 tools/ofr_pages.py 图片目录 输出目录"""
import sys, re, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

W, H = 1080, 1440
SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
CREAM = (244, 238, 228); INK = (34, 30, 27); ACC = (176, 92, 52); GREY = (110, 102, 94)

def sans(s, w="Regular"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def serif(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSerifCJK-{w}.ttc", s, index=2)

def warm(img):
    img = img.filter(ImageFilter.UnsharpMask(2, 60, 2))
    img = ImageEnhance.Color(ImageEnhance.Contrast(img).enhance(1.08)).enhance(1.18)
    r, g, b = img.split()
    r = r.point(lambda v: min(255, int(v * 1.05))); b = b.point(lambda v: int(v * .93))
    return Image.merge("RGB", (r, g, b))

def crop(name, w, h, fx=.5, fy=.5, z=1.0):
    im = Image.open(f"{SRC}/{name}.webp").convert("RGB")
    s = max(w / im.width, h / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    return warm(im.crop((round(x), round(y), round(x) + w, round(y) + h)))

NOSTART = "，。、；：！？）」』%"
def wrap(t, f, lim):
    toks = re.findall(r"[A-Za-z0-9@.:,&'’/]+|.", t)
    lines, cur = [], ""
    for tk in toks:
        if f.getlength(cur + tk) > lim and cur:
            if tk in NOSTART: cur += tk; continue
            lines.append(cur); cur = tk.lstrip()
        else: cur += tk
    if cur: lines.append(cur)
    return lines

def panel(img, top, no, head, body):
    d = ImageDraw.Draw(img)
    d.rectangle((0, top, W, H), fill=CREAM)
    y = top + 58
    d.text((80, y), no, font=sans(28, "Bold"), fill=ACC); y += 62
    for ln in wrap(head, serif(66), 920):
        d.text((80, y), ln, font=serif(66), fill=INK); y += 90
    y += 18
    fb = sans(35)
    for ln in wrap(body, fb, 920):
        d.text((80, y), ln, font=fb, fill=(62, 57, 52)); y += 60
    return y

def page_one(fn, name, fx, fy, no, head, body, ph=860, z=1.0):
    img = Image.new("RGB", (W, H), CREAM)
    img.paste(crop(name, W, ph, fx, fy, z), (0, 0))
    y = panel(img, ph, no, head, body)
    assert y < H - 30, (fn, y)
    img.save(f"{OUT}/{fn}", quality=93)

def page_two(fn, a, b, no, head, body, ph=840, split=640):
    img = Image.new("RGB", (W, H), CREAM)
    img.paste(crop(a[0], split, ph, *a[1:]), (0, 0))
    img.paste(crop(b[0], W - split - 8, ph, *b[1:]), (split + 8, 0))
    y = panel(img, ph, no, head, body)
    assert y < H - 30, (fn, y)
    img.save(f"{OUT}/{fn}", quality=93)

# 封面
img = crop("o018", W, H, .52, .5)
ov = Image.new("L", (1, H))
for yy in range(H):
    ov.putpixel((0, yy), int(max(0, 1 - yy / (H * .5)) ** 1.1 * 215))
img = Image.composite(Image.new("RGB", (W, H), (14, 11, 9)), img, ov.resize((W, H)))
d = ImageDraw.Draw(img)
d.text((80, 96), "Algorithm新店", font=sans(44, "Bold"), fill=(240, 200, 170))
d.text((76, 168), "悉尼奶油咖啡", font=serif(128), fill="white")
d.text((76, 318), "又开新店了", font=serif(128), fill="white")
d.text((80, 486), "这次藏在Surry Hills一条小巷里", font=sans(46, "Medium"), fill=(245, 240, 232), stroke_width=3, stroke_fill=(20, 15, 12))
img.save(f"{OUT}/01.jpg", quality=93)

page_one("02.jpg", "o001", .5, .5, "藏在哪",
         "Marys Place这条小巷",
         "巷子一头是Bourke St，另一头通往South Dowling St。店面只有几米宽，一大半给了开放式吧台。位子不多，很多人直接坐在门口的塑料箱上喝。老板Angelina说，这条巷子让她想到日本。")

page_one("03.jpg", "o021", .45, .55, "招牌",
         "还是那杯Rhythm",
         "冷萃咖啡上盖一层很厚的奶油，奶油里有橙皮和香草的味道。豆子是Algorithm和悉尼烘焙商Headlands Coffee一起做的拼配，口感接近蒙布朗。")

page_two("04.jpg", ("o012", .55, .5, 1.0), ("o017", .45, .5, 1.0), "这家店的新菜单",
         "黑芝麻和棉花糖",
         "一杯是黑芝麻奶油，上面放一块曲奇。另一杯是Overflow Room限定的三层冰拿铁，加了棉花糖糖浆。")

page_two("05.jpg", ("o008", .45, .5, 1.0), ("o024", .4, .5, 1.0), "吃的",
         "热的可颂吐司Croloaf",
         "用可颂面团做成吐司，厚切后烤到金黄，上面放一块枫糖黄油。另外有原味可颂、曲奇和巴斯克芝士蛋糕。")

page_two("06.jpg", ("o023", .35, .5, 1.0), ("o019", .58, .5, 1.0), "Algorithm是谁",
         "三年开了三家店",
         "2023年9月在Marrickville开出第一家，2025年9月开到Potts Point，现在是Surry Hills这间。老板Angelina Kartiko在Le Cordon Bleu学厨，在Quay实习过，和丈夫Beryl Leomongga一起经营。")

# 信息页
img = Image.new("RGB", (W, H), CREAM)
img.paste(crop("o032", W, 760, .5, .5), (0, 0))
d = ImageDraw.Draw(img)
y = 760 + 58
d.text((80, y), "怎么去", font=sans(28, "Bold"), fill=ACC); y += 62
d.text((80, y), "Overflow Room", font=serif(72), fill=INK); y += 120
for k, v in [("地址", "1 Marys Place, Surry Hills"), ("营业", "每天7am至2:30pm"), ("Instagram", "@overflowroomsydney")]:
    d.text((80, y), k, font=sans(32, "Bold"), fill=GREY)
    d.text((300, y - 4), v, font=sans(38, "Medium"), fill=INK)
    y += 50; d.line((80, y + 14, W - 80, y + 14), fill=(214, 204, 190), width=2); y += 44
d.text((80, y + 6), "下午两点半就关门，想喝得早点去。", font=sans(35), fill=(62, 57, 52))
img.save(f"{OUT}/07.jpg", quality=93)
print("ok")
