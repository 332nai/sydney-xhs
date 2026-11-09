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

# ---------- 店卡：每家两张，A是2x2拼图，B是三图加简介 ----------
def wrap(text, font, width):
    import re
    toks = re.findall(r"[A-Za-z0-9&'.$ôé]+|.", text)
    lines, cur = [], ""
    for t in toks:
        if font.getlength(cur + t) > width and cur and t not in "，。、！？）：；":
            lines.append(cur); cur = t.lstrip()
        else: cur += t
    if cur: lines.append(cur)
    return lines

def info(fn, no, name, style, intro, chips, photos, accent):
    img = Image.new("RGB", (W, H), CREAM)
    img.paste(crop(photos[0], 640, 780), (0, 0))
    img.paste(crop(photos[1], 434, 387), (646, 0)); img.paste(crop(photos[2], 434, 387), (646, 393))
    d = ImageDraw.Draw(img)
    y = 830
    d.text((70, y), f"( {no} )", font=en(34), fill=accent)
    f = en(70)
    while f.getlength(name) > 940: f = en(f.size - 2)
    d.text((70, y + 52), name, font=f, fill=INK)
    d.text((72, y + 150), style, font=zh(50, "Black"), fill=accent)
    fy = y + 240
    for ln in wrap(intro, zh(40), 940):
        d.text((72, fy), ln, font=zh(40), fill=(70, 66, 60)); fy += 62
    cx, fc = 72, zh(32, "Bold")
    cy = fy + 30
    for c in chips:
        tw = fc.getlength(c)
        if cx + tw + 40 > W - 60: cx = 72; cy += 66
        d.rounded_rectangle((cx, cy, cx + tw + 40, cy + 54), 27, fill=accent)
        d.text((cx + 20, cy + 6), c, font=fc, fill="white"); cx += tw + 56
    img.save(f"{OUT}/{fn}", quality=93)

V = [
 ("01", "ST SIANDRA", "阿马尔菲海岸风，门口就是海滩", "阿马尔菲海岸风",
  "在The Spit的海滩边，金黄墙面、陶土地砖、白色大理石吧台。夏天沙滩上摆满条纹沙滩椅和阳伞，还可以坐船直接到。",
  ["Mosman · The Spit", "周一周二休息"],
  [("ss25_0.jpg", .5, .5), ("ss26_b.jpg", .5, .5), ("ss25_1.jpg", .45, .5), ("ss26_c.jpg", .6, .5)],
  [("ss_r3.jpg", .6, .5), ("ss26_a.jpg", .5, .5), ("ss_ft2.jpg", .5, .6)], (196, 140, 40)),
 ("02", "AKTI", "爱琴海日落色，白伞下吃希腊菜", "爱琴海日落色",
  "Woolloomooloo码头上的希腊餐厅，整间店是蜜桃粉加暖黄，户外一排白色阳伞。现烤皮塔饼配蘸酱，小羊肩冒着烟端上桌。",
  ["Woolloomooloo码头", "Happy hour每天4点到6点"],
  [("ak_to0.jpg", .5, .6), ("ak_c10.jpg", .5, .5), ("ak_med.jpg", .5, .5), ("ak_c7.jpg", .5, .5)],
  [("ak_baraki.jpg", .5, .5), ("ak_hh.jpg", .5, .5), ("ak_c3.jpg", .5, .5)], (214, 110, 100)),
 ("04", "MARTINEZ", "戛纳酒店风，楼顶露台看大桥", "戛纳酒店风",
  "名字来自戛纳的Hôtel Martinez。楼顶露台是蓝白花纹卡座配红色桌子，能看到海港大桥，傍晚上来喝一杯spritz正好。",
  ["Circular Quay楼顶", "Young St专用电梯上楼"],
  [("ma_sw13.jpg", .5, .5), ("ma_sq1.jpg", .5, .5), ("ma_sq2.jpg", .5, .5), ("ma_es.jpg", .5, .5)],
  [("ma_sw10.jpg", .5, .5), ("ma_y48.jpg", .5, .5), ("ma_sw11.jpg", .5, .5)], (40, 80, 150)),
 ("05", "WHALEBRIDGE", "全露天，对着海港吃海鲜塔", "地中海海边小馆",
  "全露天，几乎每桌都对着海港大桥和歌剧院。招牌是马赛鱼汤，海鲜塔可以自己挑龙虾、生蚝、鱼子酱，再配一桶香槟。",
  ["Circular Quay East", "没有室内座位，看天气"],
  [("wb25_mia.jpg", .5, .5), ("wb25_menu.jpg", .5, .5), ("wb25_bev.jpg", .5, .5), ("wb26_s113.jpg", .5, .5)],
  [("wb25_v1.jpg", .5, .5), ("wb26_platter.jpg", .5, .5), ("wb26_spritz.jpg", .5, .5)], (30, 110, 140)),
 ("06", "CLUB AMALFI", "Watsons Bay每月一次的海滩派对", "海滩俱乐部周日派对",
  "Watsons Bay Hotel翻新后的顶层平台，每月一个周日变成地中海海滩俱乐部，有分享套餐、Hugo Spritz和DJ，一玩就是4个小时。",
  ["Watsons Bay", "$89一位", "下一场11月15日"],
  [("wbh_ext.jpg", .5, .5), ("wb_ca1.jpg", .5, .5), ("wbh_fr.jpg", .5, .5), ("wb_ca0.jpg", .5, .5)],
  [("wbh_top2.jpg", .5, .5), ("wb_ca2.jpg", .5, .5), ("wbh_sun.jpg", .5, .5)], (30, 70, 130)),
]
for no, name, tag, style, intro, chips, pa, pb, acc in V:
    card(f"{no}a.jpg", no, name, tag, pa)
    info(f"{no}b.jpg", no, name, style, intro, chips, pb, acc)

# ---------- 首页 ----------
T1, T2, T3 = "不用飞欧洲", "悉尼的地中海夏天", "6家海边餐厅，阿马尔菲、蔚蓝海岸、爱琴海"
# A：St Siandra沙滩椅铺满，大字在上
a = fade(crop(("ss25_0.jpg", .5, .5, 1.0), W, H), (10, 30, 60), True, .5, 1.1, 190)
shadow_text(a, [(76, 140, T1, zh(84, "Black"), "l"), (70, 250, T2, zh(118, "Black"), "l"), (80, 420, T3, zh(40, "Bold"), "l")], alpha=.5)
icon(a, "06_拍照打卡", W - 290, H - 300, 240).save(f"{OUT}/cover_A.jpg", quality=93)

# B：六宫格，中间海蓝标题带
b = Image.new("RGB", (W, H)); cw, ch = W // 2, H // 3
for i, p in enumerate([("ss25_0.jpg", .5, .5), ("ak_c10.jpg", .5, .5), ("ak_c7.jpg", .5, .5), ("ma_sw13.jpg", .5, .5), ("wb25_mia.jpg", .5, .5), ("wb_ca1.jpg", .5, .5)]):
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
for i, p in enumerate([("ss25_0.jpg", .5, .5), ("ak_c10.jpg", .5, .5), ("wb25_mia.jpg", .5, .5)]):
    ph = crop(p, aw, ah); m = Image.new("L", (aw, ah), 0); md = ImageDraw.Draw(m)
    md.rectangle((0, aw // 2, aw, ah), fill=255); md.ellipse((0, 0, aw - 1, aw), fill=255)
    dd.paste(ph, (x0 + i * (aw + gap), 480), m)
icon(dd, "06_拍照打卡", W - 270, 60, 200).save(f"{OUT}/cover_D.jpg", quality=93)
print("ok")
