"""Southwest Metro沿线吃饭卡片（沿用Paddington版式）：封面单图大字，内页2x2拼图，店名压在中线。
用法：python3 tools/pad_cards.py 图片目录 输出目录"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps

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
    im = ImageOps.exif_transpose(Image.open(f"{SRC}/{name}")).convert("RGB")
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

def card(fn, no, name, tag, photos):  # no: 站名标签
    img = Image.new("RGB", (W, H))
    cw, ch = W // 2, H // 2
    for i, p in enumerate(photos):
        img.paste(crop(p, cw, ch), ((i % 2) * cw, (i // 2) * ch))
    f = en(92)
    while f.getlength(name) > 980: f = en(f.size - 4)
    shadow_text(img, [(W / 2, ch - 110, f"( {no} )", zh(34, "Bold")), (W / 2, ch - 46, name, f), (W / 2, ch + 64, tag, zh(40))])
    img.save(f"{OUT}/{fn}", quality=93)

TEAL = (22, 131, 136)
STOPS = ["Marrickville", "Dulwich Hill", "Hurlstone Park", "Canterbury", "Lakemba", "Bankstown"]

# 封面：俯拍一桌越南菜，上方标题，底部一条地铁线
c = crop(("ancp0.jpg", .55, .5, 1.0), W, H)
shadow_text(c, [(W / 2, 250, "Southwest Metro通车了", zh(54, "Bold")),
                (W / 2, 340, "坐新地铁", zh(170, "Black")),
                (W / 2, 540, "去吃饭", zh(170, "Black")),
                (W / 2, 760, "从Marrickville到Bankstown，每站吃一家", zh(46))])
# 地铁线条
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
d.rounded_rectangle((40, 1150, W - 40, 1400), 28, fill=(255, 255, 255, 235))
x0, x1, y = 150, W - 150, 1235
d.line((x0, y, x1, y), fill=TEAL, width=14)
f = zh(26, "Medium")
for i, s in enumerate(STOPS):
    x = x0 + (x1 - x0) * i / (len(STOPS) - 1)
    d.ellipse((x - 20, y - 20, x + 20, y + 20), fill="white", outline=TEAL, width=8)
    lines = s.split(" ") if " " in s else [s]
    for j, ln in enumerate(lines):
        d.text((x - f.getlength(ln) / 2, y + 36 + j * 34), ln, font=f, fill=(30, 30, 30))
d.text((x0 - 10, y - 66), "M", font=en(40), fill=TEAL)
c = Image.alpha_composite(c.convert("RGBA"), ov).convert("RGB")
c.save(f"{OUT}/00.jpg", quality=93)

card("01.jpg", "01 Marrickville站", "PEPITO'S", "站口的秘鲁小酒馆",
     [("pep_01.jpg", .5, .5), ("pep_06.jpg", .5, .5), ("pep_04.jpg", .5, .5), ("pep_07.jpg", .6, .5)])
card("02.jpg", "02 Dulwich Hill站", "OLYMPIC MEATS", "炭火转着烤的希腊肉铺",
     [("om_04.webp", .5, .5), ("om_06.webp", .5, .5), ("om_08.webp", .5, .5), ("om_00.webp", .5, .5)])
card("03.jpg", "03 Hurlstone Park站", "FRANKLY NICK'S", "两个从17岁就开始做披萨的老友",
     [("fn_02.webp", .5, .5), ("fn_00.webp", .45, .5), ("fn_09.webp", .55, .5), ("fn_15.webp", .5, .5)])
card("04.jpg", "04 Canterbury站", "LE DODO AFFAMER", "悉尼唯一一家传统毛里求斯菜",
     [("dodo_01.jpg", .5, .5), ("dodo_09.jpg", .5, .5), ("dodo_11.jpg", .5, .5), ("dodo_19.jpg", .5, .5)])
card("05.jpg", "05 Lakemba站", "HALDON STREET", "也门mandi和阿富汗烤肉",
     [("lak_10.webp", .5, .5), ("lak_09.webp", .5, .5), ("lak_12.webp", .5, .5), ("lak_11.webp", .5, .5)])
card("06.jpg", "06 Bankstown站", "AN & BANH MI BAY NGO", "一碗牛肉河粉，一个越南面包",
     [("anwl1.jpg", .5, .5), ("anto0.jpg", .45, .5), ("bmbn0.jpg", .5, .5), ("ancp0.jpg", .4, .5)])
print("ok")
