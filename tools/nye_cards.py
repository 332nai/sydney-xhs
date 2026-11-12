"""悉尼跨年饭价格帖：首页三选一，每家一张卡（上方6张图，下方店名、价格、介绍）。
用法：python3 tools/nye_cards.py 图片目录 老杨图标目录 输出目录"""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
Image.MAX_IMAGE_PIXELS = None
W, H = 1080, 1440
SRC, ICONS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
CREAM = (248, 244, 236); INK = (26, 28, 36); GOLD = (168, 120, 40)
def en(s): return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", s)
def zh(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def serif(s): return ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", s, index=2)

def crop(spec, w, h):
    spec = list(spec) if isinstance(spec, tuple) else [spec]
    name, fx, fy, z = spec + [.5, .5, 1.0][len(spec) - 1:]
    im = ImageOps.exif_transpose(Image.open(f"{SRC}/{name}")).convert("RGB")
    s = max(w / im.width, h / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    im = im.crop((round(x), round(y), round(x) + w, round(y) + h)).filter(ImageFilter.UnsharpMask(2, 40, 2))
    return ImageEnhance.Color(im).enhance(1.08)

def icon(img, pose, x, y, h):
    ic = Image.open(f"{ICONS}/{pose}.png").convert("RGBA")
    ic = ic.resize((round(ic.width * h / ic.height), h), Image.LANCZOS)
    img = img.convert("RGBA"); sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 255), (x + 4, y + 6), ic.split()[3].point(lambda v: int(v * .3)))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8))); img.alpha_composite(ic, (x, y))
    return img.convert("RGB")

def wrap(text, font, width):
    toks = re.findall(r"[A-Za-z0-9&'.$,ôé]+|.", text)
    lines, cur = [], ""
    for t in toks:
        if font.getlength(cur + t) > width and cur and t not in "，。、！？）：；":
            lines.append(cur); cur = t.lstrip()
        else: cur += t
    if cur: lines.append(cur)
    return lines

def card(fn, name, price, intro, photos):
    img = Image.new("RGB", (W, H), CREAM); cw, ch = W // 3, 470
    for i, p in enumerate(photos): img.paste(crop(p, cw + 1, ch), ((i % 3) * cw, (i // 3) * ch))
    d = ImageDraw.Draw(img)
    fn_ = serif(64) if re.search(r"[一-鿿]", name) else en(64)
    fp = serif(52); fi = zh(38); lines = wrap(intro, fi, 940)
    block = 84 + 78 + len(lines) * 58
    y = 940 + (500 - block) // 2
    d.text((70, y), name, font=fn_, fill=INK)
    d.text((70, y + 84), price, font=fp, fill=GOLD)
    fy = y + 162
    for ln in lines:
        d.text((72, fy), ln, font=fi, fill=(70, 66, 60)); fy += 58
    img.save(f"{OUT}/{fn}", quality=93)

V = [
 ("01.jpg", "BENNELONG", "$2,250到$3,250一位",
  "在歌剧院里面，帆形屋顶下吃饭。四到五道菜配酒，香槟到店和零点各一杯。最贵的是楼上Dress Circle，能看到海港大桥。订位要全额付款。",
  ["bn_t105455397.jpg", "bn_b13.webp", "bn_t105455388.jpg", "bn_nye.jpg", "bn_t105455402.jpg", "bn_t105455385.jpg"]),
 ("02.jpg", "ALTITUDE", "$1,750到$2,500一位",
  "香格里拉酒店36楼，从高处看整个海港的烟花。八道菜品鉴套餐配酒，最长可以坐5小时。$1,750是普通座位，$2,500保证靠窗。",
  [("al_rk1.jpg", .5, .5), "al_wl0.jpg", "al_nye.jpg", ("al_rk2.jpg", .5, .5), "al_wl2.jpg", "al_wl1.jpg"]),
 ("03.jpg", "ARIA", "$1,950一位",
  "Circular Quay，正对歌剧院和海港大桥。晚8点场六道菜配六款酒，香槟到店和零点各一杯。想便宜一点可以选早场$350，或者站着的酒会$795。",
  ["ar_t105913818.jpg", "ar_b6.jpg", "ar_b8.jpg", "ar_b16.jpg", "ar_b1.jpg", "ar_b9.jpg"]),
 ("04.jpg", "WHALEBRIDGE", "$1,200到$1,500一位",
  "Circular Quay East全露天，对着海港大桥。香槟整晚无限量，有鱼子酱、海鲜拼盘和和牛。$1,500是水边座位，$1,200是海港景观座位。",
  ["wb25_mia.jpg", "wb25_v1.jpg", "wb25_menu.jpg", "wb25_v3.jpg", "wb25_bev.jpg", "wb26_s113.jpg"]),
 ("05.jpg", "SAILS", "$1,495一位",
  "Lavender Bay水边，就在海港大桥旁边。晚上7点只有一场，六道菜加酒水套餐。",
  ["sa_nye.jpg", "sa_nye3.jpg", "sa_g02.jpg", "sa_to2.jpg", "sa_h.jpg", "sa_nye2.jpg"]),
 ("06.jpg", "几百块的选择", "$295到$395一位",
  "同样在海港边：Akti晚场分享套餐加一杯香槟$295，Ripples Chowder Bay五道菜含酒水$335，Riva晚场五道菜$395。",
  ["ak_to0.jpg", "ak_nye.png", "rc_7.jpg", "rc_3.jpg", "rv_0.jpg", "rv_5.jpg"]),
]
for fn, name, price, intro, ph in V: card(fn, name, price, intro, ph)

L1, L2 = "悉尼跨年一顿饭", "$3,250值不值"
ft = serif(110)
# A：Altitude烟花俯瞰铺满
a = crop(("al_nye.jpg", .5, .55, 1.0), W, H)
ov = Image.new("L", (1, H))
for yy in range(H): ov.putpixel((0, yy), int(max(0, 1 - yy / (H * .45)) ** 1.2 * 200))
a = Image.composite(Image.new("RGB", (W, H), (6, 8, 20)), a, ov.resize((W, H)))
d = ImageDraw.Draw(a); d.text((70, 110), L1, font=ft, fill="white"); d.text((70, 250), L2, font=ft, fill="white")
icon(a, "01_看菜单", W - 290, H - 300, 240).save(f"{OUT}/cover_A.jpg", quality=93)
# B：米色底，三张拱形图
b = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(b)
fb = serif(100); d.text((70, 100), L1, font=fb, fill=INK); d.text((70, 230), L2, font=fb, fill=INK)
aw, ah, gap = 300, 900, 30; x0 = (W - 3 * aw - 2 * gap) // 2
for i, p in enumerate(["bn_t105455397.jpg", ("al_rk1.jpg", .78, .5), "sa_nye3.jpg"]):
    ph = crop(p, aw, ah); m = Image.new("L", (aw, ah), 0); md = ImageDraw.Draw(m)
    md.rectangle((0, aw // 2, aw, ah), fill=255); md.ellipse((0, 0, aw - 1, aw), fill=255)
    b.paste(ph, (x0 + i * (aw + gap), 450), m)
icon(b, "01_看菜单", W - 230, 70, 180).save(f"{OUT}/cover_B.jpg", quality=93)
# C：Bennelong帆形屋顶下的夜景，字在下
c = crop(("bn_t105455397.jpg", .5, .5, 1.0), W, H)
ov = Image.new("L", (1, H))
for yy in range(H): ov.putpixel((0, yy), int(max(0, (yy - H * .5) / (H * .5)) ** 1.1 * 215))
c = Image.composite(Image.new("RGB", (W, H), (10, 8, 6)), c, ov.resize((W, H)))
d = ImageDraw.Draw(c); d.text((70, 1050), L1, font=ft, fill="white"); d.text((70, 1190), L2, font=ft, fill="white")
icon(c, "01_看菜单", 50, 50, 200).save(f"{OUT}/cover_C.jpg", quality=93)
print("ok")
