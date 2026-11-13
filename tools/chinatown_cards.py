"""悉尼唐人街搬家史：档案风今昔对比。首页、路线图、四张今昔卡。
用法：python3 tools/chinatown_cards.py 图片目录 老杨图标目录 输出目录"""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
Image.MAX_IMAGE_PIXELS = None
W, H = 1080, 1440
SRC, ICONS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
PAPER = (236, 229, 214); INK = (32, 28, 24); SEP = (120, 92, 60); RED = (150, 36, 30)
def serif(s): return ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", s, index=2)
def serifr(s): return ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc", s, index=2)

def crop(spec, w, h, old=False):
    spec = list(spec) if isinstance(spec, tuple) else [spec]
    name, fx, fy, z = spec + [.5, .5, 1.0][len(spec) - 1:]
    im = ImageOps.exif_transpose(Image.open(f"{SRC}/{name}")).convert("RGB")
    s = max(w / im.width, h / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    im = im.crop((round(x), round(y), round(x) + w, round(y) + h))
    return im.filter(ImageFilter.UnsharpMask(1.2, 40, 2)) if old else ImageEnhance.Color(im.filter(ImageFilter.UnsharpMask(1.5, 30, 2))).enhance(1.05)

def icon(img, pose, x, y, h):
    ic = Image.open(f"{ICONS}/{pose}.png").convert("RGBA"); ic = ic.resize((round(ic.width * h / ic.height), h), Image.LANCZOS)
    img = img.convert("RGBA"); sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 255), (x + 4, y + 6), ic.split()[3].point(lambda v: int(v * .3)))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8))); img.alpha_composite(ic, (x, y)); return img.convert("RGB")

def wrap(text, font, width):
    toks = re.findall(r"[A-Za-z0-9&'.$,:]+|.", text); lines, cur = [], ""
    for t in toks:
        if font.getlength(cur + t) > width and cur and t not in "，。、！？）：；": lines.append(cur); cur = t.lstrip()
        else: cur += t
    if cur: lines.append(cur)
    return lines

def stamp(d, x, y, text, size=56):
    f = serif(size); w = f.getlength(text)
    d.rectangle((x, y, x + w + 36, y + size + 26), fill=PAPER); d.text((x + 18, y + 6), text, font=f, fill=INK)

def framed(img, photo, box, label, old):
    x0, y0, x1, y1 = box; pad = 14
    ImageDraw.Draw(img).rectangle(box, fill="white")
    im = crop(photo, x1 - x0 - 2 * pad, y1 - y0 - 2 * pad, old); img.paste(im, (x0 + pad, y0 + pad))
    stamp(ImageDraw.Draw(img), x0 + pad, y1 - pad - 82, label, 48)

def card(fn, head, sub, olds, new, text):
    img = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(img)
    d.text((60, 46), head, font=serif(70), fill=INK); d.text((62, 140), sub, font=serifr(38), fill=SEP)
    d.line((60, 205, W - 60, 205), fill=INK, width=3)
    top, mid = 230, 690
    if len(olds) == 2:
        framed(img, olds[0][0], (60, top, 535, mid), olds[0][1], True); framed(img, olds[1][0], (545, top, W - 60, mid), olds[1][1], True)
    else:
        framed(img, olds[0][0], (60, top, W - 60, mid), olds[0][1], True)
    framed(img, new[0], (60, mid + 14, W - 60, 1130), new[1], False)
    f = serifr(33); y = 1158
    for ln in wrap(text, f, 960): d.text((60, y), ln, font=f, fill=INK); y += 50
    assert y < H - 10, (fn, y)
    img.save(f"{OUT}/{fn}", quality=93)

C = [
 ("02.jpg", "第一站 The Rocks", "1850年代到1900年前后",
  [("old_116.jpg", "华人家具厂"), (("old_176.jpg", .5, .45), "1908 华人商号")], (("now_231george.jpg", .5, .55), "今天的George St，The Rocks"),
  "淘金热之后，华人从各地回到悉尼，先聚在码头边的The Rocks，在Lower George St和后面的Cambridge St开店、开寄宿屋、做家具。1861年悉尼只登记了189个华人，1881年已经有1,321人。"),
 ("03.jpg", "第二站 Haymarket", "1890年代到1906年",
  [(("old_131.jpg", .5, .5), "1906年拆之前的Wexford St")], (("now_wentworth.jpg", .5, .55), "原址，今天的Wentworth Ave"),
  "菜农把菜运到Belmore Markets，常在附近过夜，Campbell St、Goulburn St和Wexford St一带开起寄宿屋、杂货铺和饭馆。1906年市政府拆掉整条Wexford St，724人被迫搬走，原址修成今天的Wentworth Ave。"),
 ("04.jpg", "第三站 Dixon St", "1910年代到今天",
  [(("old_015.jpg", .45, .45, 1.08), "1954 Dixon St"), (("old_089.jpg", .5, .5), "1970年代")], (("now_dixon2.jpg", .5, .6), "2026年的Dixon St"),
  "1909到1915年，新的City Markets在Hay St一带建成，也就是今天的Paddy's Markets。华人跟着市场往西搬，到1930年代，Dixon St已经是唐人街。1942年中国海员工会就在这条街上成立。"),
 ("05.jpg", "牌楼 1980", "Dixon St变成步行街",
  [(("old_097.jpg", .5, .5), "1980年开街"), (("old_062.jpg", .5, .5), "1985")], (("now_dixon1.jpg", .5, .45), "2026年的牌楼"),
  "1979年中秋节起，Dixon St永久封路改成步行街。1980年悉尼市长主持开街，街两头立起华裔建筑师Henry Tsang设计的牌楼。1970年代以后，新移民从中国大陆、台湾、香港和东南亚过来，很多是专业人士。"),
]
for c in C: card(*c)

# 01 路线图：George St从北到南
img = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(img)
d.text((60, 46), "唐人街搬家路线", font=serif(70), fill=INK); d.text((62, 140), "沿着George St，一路往南", font=serifr(38), fill=SEP)
d.line((60, 205, W - 60, 205), fill=INK, width=3)
x = 300; y0, y1 = 300, 1330
d.line((x, y0, x, y1), fill=INK, width=8)
d.text((x - 120, y0 - 70), "Circular Quay", font=serifr(34), fill=SEP); d.text((x - 70, y1 + 16), "Central", font=serifr(34), fill=SEP)
stops = [(390, "1850s", "The Rocks", "码头边，第一个唐人街"),
         (900, "1890s", "Campbell St", "Belmore Markets旁，第二个"),
         (1080, "1930s", "Dixon St", "跟着新市场西移，第三个"),
         (1230, "1980", "牌楼落成", "Dixon St变成步行街")]
for yy, yr, place, note in stops:
    d.ellipse((x - 26, yy - 26, x + 26, yy + 26), fill=RED, outline=INK, width=4)
    d.text((80, yy - 28), yr, font=serif(44), fill=RED)
    d.text((x + 60, yy - 46), place, font=serif(50), fill=INK); d.text((x + 62, yy + 14), note, font=serifr(34), fill=SEP)
img.save(f"{OUT}/01.jpg", quality=93)

# 首页：上旧下新，中间档案纸条写标题
def cover(fn, old, new, oy, ny):
    c = Image.new("RGB", (W, H), PAPER)
    c.paste(crop(old, W, 640, True), (0, 0)); c.paste(crop(new, W, 640), (0, 800))
    d = ImageDraw.Draw(c); f = serif(92)
    d.text((60, 652), "悉尼唐人街搬过三次家", font=f, fill=INK)
    stamp(d, 30, 540, oy, 56); stamp(d, 30, 1330, ny, 56)
    icon(c, "06_拍照打卡", W - 230, 30, 190).save(f"{OUT}/{fn}", quality=93)
cover("cover_A.jpg", ("old_093.jpg", .5, .45), ("now_dixon1.jpg", .5, .45), "1979", "2026")
cover("cover_B.jpg", ("old_015.jpg", .45, .45, 1.08), ("now_dixon2.jpg", .5, .55), "1954", "2026")
print("ok")
