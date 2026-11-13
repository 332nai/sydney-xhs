"""悉尼周末活动帖：首页三选一，每个活动一张卡（上方照片，下方名称、价格、介绍）。
用法：python3 tools/weekend_cards.py 图片目录 老杨图标目录 输出目录"""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
Image.MAX_IMAGE_PIXELS = None
W, H = 1080, 1440
SRC, ICONS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
CREAM = (248, 244, 236); INK = (26, 28, 36); ACC = (178, 84, 48)
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
    toks = re.findall(r"[A-Za-z0-9&'.$,]+|.", text)
    lines, cur = [], ""
    for t in toks:
        if font.getlength(cur + t) > width and cur and t not in "，。、！？）：；":
            lines.append(cur); cur = t.lstrip()
        else: cur += t
    if cur: lines.append(cur)
    return lines

# 照片区高800，按张数排版：每行的张数
ROWS = {1: [1], 2: [1, 1], 3: [1, 2], 4: [2, 2], 5: [2, 3], 6: [3, 3]}
def card(fn, name, price, when, intro, photos):
    img = Image.new("RGB", (W, H), CREAM); rows = ROWS[len(photos)]; rh = 800 // len(rows); k = 0
    for r, n in enumerate(rows):
        cw = W // n
        for c in range(n):
            img.paste(crop(photos[k], cw + 1, rh + 1), (c * cw, r * rh)); k += 1
    d = ImageDraw.Draw(img)
    fn_ = serif(58); fp = zh(40, "Bold"); fw = zh(34, "Bold"); fi = zh(34)
    il = wrap(intro, fi, 940)
    block = 80 + 56 + len(il) * 52
    y = 800 + (640 - block) // 2
    d.text((70, y), name, font=fn_, fill=INK)
    d.text((70 + fn_.getlength(name) + 28, y + 12), price, font=fp, fill=ACC)
    y += 80; d.text((72, y), when, font=fw, fill=ACC); y += 56
    for ln in il: d.text((72, y), ln, font=fi, fill=(60, 56, 50)); y += 52
    img.save(f"{OUT}/{fn}", quality=93)

V = [
 ("01.jpg", "Burwood希腊街头节", "免费", "周六 中午12点到晚上9点",
  "Burwood火车站旁边几条街封路，摆满烤肉串souvlaki、希腊甜点和小吃摊，街上有现场音乐和民族舞，每年来两万多人。下午2点、3点、4点半有希腊东正教堂导览。路封了，坐火车最方便。",
  [("to_106058891.jpg", .5, .15), "to_106058890.jpg", "to_106058892.jpg"]),
 ("02.jpg", "Finders Keepers设计市集", "$7", "周五下午4点起 周六周日10点到5点",
  "Carriageworks老火车厂里一大片本地设计师摊位，陶瓷、首饰、衣服、文具、插画都有，现在去买圣诞礼物正好。单日$7，周末通票$10，13岁以下免费。",
  ["fk_cpOverhead.jpg", "fk_241.jpg", ("fk_242.jpg", .5, .35), "fk_cpStall.jpg", "fk_p2-2.png", "fk_cpMural.jpg"]),
 ("03.jpg", "Bondi户外电影", "免费", "周五到周日 晚上7点半",
  "就在Bondi Pavilion旁边，离沙滩几步路。Waverley市政府办的，免费入场还送爆米花，片单有侏罗纪公园、真爱至上、芭比这类老少都能看的。带块野餐垫，吃完晚饭散步过去。下周四到周日还有一轮。",
  [("to_106465311.jpg", .5, .5)]),
 ("04.jpg", "Inner West精酿节", "免费入场", "这周末是最后三天",
  "Inner West 13家精酿酒厂一起办，每家搭一家本地小店，比如Grifter配AP面包，Heaps Normal配Mapo意式冰淇淋。在酒厂买酒盖章，集满10个章换一个限量帆布袋。",
  ["to_106459958.jpg", "to_106459957.jpg", "to_106459956.jpg", "to_106459959.jpg", "to_106466668.jpg"]),
 ("05.jpg", "Huge Moves自然酒节", "$40起", "周六 下午1点到4点",
  "Surry Hills的Ace Hotel，一百多款自然酒可以慢慢试，配Studd兄妹的奶酪，3点开始有DJ。结束后还有after party，$10随机抽一杯。",
  ["hm_b.webp", "hm_a.webp", "hm_to106278662.jpg", "hm_to106278661.jpg"]),
]
for fn, *a in V: card(fn, *a)

# 首页：一张现场照片，宋体白字在下，像手机里直接加字
L1, L2 = "悉尼这周末", "别在家躺着了"
def cover(fn, spec):
    c = crop(spec, W, H)
    ov = Image.new("L", (1, H))
    for yy in range(H): ov.putpixel((0, yy), int(max(0, (yy - H * .5) / (H * .5)) ** 1.1 * 200))
    c = Image.composite(Image.new("RGB", (W, H), (10, 8, 6)), c, ov.resize((W, H)))
    d = ImageDraw.Draw(c); fs_ = serif(110)
    d.text((70, 1050), L1, font=fs_, fill="white"); d.text((70, 1190), L2, font=fs_, fill="white")
    icon(c, "06_拍照打卡", 50, 50, 200).save(f"{OUT}/{fn}", quality=93)
cover("cover_A.jpg", ("to_106058891.jpg", .45, .5))
cover("cover_B.jpg", ("fk_cpOverhead.jpg", .5, .5))
cover("cover_C.jpg", ("to_106465311.jpg", .5, .5))
print("ok")

# 四宫格首页：四个活动各一格，格子上写活动名，中间写标题
G = [(("to_106058891.jpg", .5, .2), "希腊美食街"), (("fk_cpOverhead.jpg", .5, .5), "设计师市集"),
     (("to_106465311.jpg", .5, .5), "海边露天电影"), (("po_gallery-c2uqg0.webp", .5, .5), "草地马球日")]
TITLE = "悉尼这周末去哪"
def grid():
    g = Image.new("RGB", (W, H)); cw, ch = W // 2, H // 2
    for i, (p, _) in enumerate(G): g.paste(crop(p, cw, ch), ((i % 2) * cw, (i // 2) * ch))
    return g
def labels(g, f, box):
    d = ImageDraw.Draw(g); cw, ch = W // 2, H // 2
    for i, (_, t) in enumerate(G):
        x0, y0 = (i % 2) * cw, (i // 2) * ch
        y = y0 + ch - 130 if i >= 2 else y0 + 40
        x = x0 + (cw - f.getlength(t)) / 2
        if box: d.rectangle((x - 22, y - 4, x + f.getlength(t) + 22, y + 92), fill=CREAM); d.text((x, y), t, font=f, fill=INK)
        else: d.text((x, y), t, font=f, fill="white", stroke_width=3, stroke_fill=(0, 0, 0))
    return g
# A：米白底黑字，标题一条横在中线
f = serif(76); a = labels(grid(), f, True); d = ImageDraw.Draw(a)
tw = f.getlength(TITLE); d.rectangle(((W - tw) / 2 + 20, H / 2 - 62, (W + tw) / 2 + 100, H / 2 + 62), fill=CREAM)
d.text(((W - tw) / 2 + 60, H / 2 - 50), TITLE, font=f, fill=INK)
icon(a, "06_拍照打卡", 30, H // 2 - 85, 170).save(f"{OUT}/cover_grid_A.jpg", quality=93)
# B：白字黑描边，中线一条深色横带写标题
f = serif(80); b = labels(grid(), f, False); d = ImageDraw.Draw(b)
d.rectangle((0, H / 2 - 70, W, H / 2 + 70), fill=(20, 18, 16))
tw = f.getlength(TITLE); d.text(((W - tw) / 2 + 60, H / 2 - 54), TITLE, font=f, fill="white")
icon(b, "06_拍照打卡", 30, H // 2 - 85, 170).save(f"{OUT}/cover_grid_B.jpg", quality=93)

# 四宫格v2：更亮的现场图，每格写活动和地点，中间写日期
def pop(im): return ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(1.1)).enhance(1.04)
G2 = [(("to_106058892.jpg", .55, .5), "希腊美食街", "Burwood"), (("fk_241.jpg", .45, .5), "设计师市集", "Eveleigh"),
      (("to_106466668.jpg", .5, .35), "精酿啤酒节", "Inner West"), (("to_106465311.jpg", .5, .5), "海边露天电影", "Bondi")]
def grid2(f, style):
    g = Image.new("RGB", (W, H)); cw, ch = W // 2, H // 2
    for i, (p, *_) in enumerate(G2): g.paste(pop(crop(p, cw, ch)), ((i % 2) * cw, (i // 2) * ch))
    d = ImageDraw.Draw(g); lh = f.size + 18
    for i, (_, t, loc) in enumerate(G2):
        x0, y0 = (i % 2) * cw, (i // 2) * ch
        y = y0 + ch - 2 * lh - 40 if i >= 2 else y0 + 40
        for k, s in enumerate((t, loc)):
            x = x0 + (cw - f.getlength(s)) / 2; yy = y + k * lh
            if style == "box":
                d.rectangle((x - 20, yy - 2, x + f.getlength(s) + 20, yy + lh - 4), fill=(255, 226, 64)); d.text((x, yy), s, font=f, fill=INK)
            else: d.text((x, yy), s, font=f, fill="white", stroke_width=5, stroke_fill=(0, 0, 0))
    # 中间：标题和日期
    for k, s in enumerate(("悉尼这周末去哪", "11月13日到15日")):
        tw = f.getlength(s); yy = H / 2 - lh + k * lh
        if style == "box":
            d.rectangle(((W - tw) / 2 - 24, yy - 2, (W + tw) / 2 + 24, yy + lh - 4), fill=(255, 226, 64)); d.text(((W - tw) / 2, yy), s, font=f, fill=INK)
        else: d.text(((W - tw) / 2, yy), s, font=f, fill="white", stroke_width=5, stroke_fill=(0, 0, 0))
    return g
icon(grid2(zh(70, "Black"), "box"), "06_拍照打卡", W - 200, H // 2 - 220, 170).save(f"{OUT}/cover_grid_C.jpg", quality=93)
icon(grid2(zh(70, "Black"), "stroke"), "06_拍照打卡", W - 200, H // 2 - 220, 170).save(f"{OUT}/cover_grid_D.jpg", quality=93)

# 拼贴版首页：纯色底，四张白边照片微微歪着贴，照片下写活动、地点、时间
P = [(("to_106058892.jpg", .55, .5), "希腊美食街", "Burwood 周六"),
     (("fk_cpStall.jpg", .5, .45), "设计师市集", "Eveleigh 周五到周日"),
     (("to_106466668.jpg", .5, .3), "内西精酿啤酒节", "Inner West 周五到周日"),
     (("to_106465311.jpg", .5, .55), "海边露天电影", "Bondi 周五到周日")]
def collage(fn, bg, ink, tag_bg, tag_ink):
    c = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(c)
    ft = zh(118, "Black"); fd = zh(60, "Black"); fc = zh(48, "Black"); fl = zh(36, "Bold")
    d.text((60, 50), "悉尼这周末", font=ft, fill=ink); d.text((60, 190), "去哪玩", font=ft, fill=ink)
    s = "11月13日到15日"; w = fd.getlength(s)
    d.rectangle((60, 350, 60 + w + 40, 440), fill=tag_bg); d.text((80, 360), s, font=fd, fill=tag_ink)
    pw, ph = 445, 300; rots = [-3, 2.5, 2, -2.5]; pos = [(40, 470), (555, 465), (45, 950), (560, 955)]
    for (p, name, where), r, (x, y) in zip(P, rots, pos):
        card_ = Image.new("RGB", (pw + 30, ph + 140), "white")
        card_.paste(pop(crop(p, pw, ph)), (15, 15)); dc = ImageDraw.Draw(card_)
        dc.text((18, ph + 28), name, font=fc, fill=INK); dc.text((20, ph + 92), where, font=fl, fill=(110, 100, 90))
        card_ = card_.convert("RGBA").rotate(r, expand=True, resample=Image.BICUBIC)
        sh = Image.new("RGBA", c.size, (0, 0, 0, 0)); sh.paste((0, 0, 0, 90), (x + 8, y + 12), card_.split()[3])
        c = Image.alpha_composite(c.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(10)))
        c.alpha_composite(card_, (x, y)); c = c.convert("RGB")
    icon(c, "06_拍照打卡", W - 270, 70, 230).save(f"{OUT}/{fn}", quality=94)
collage("cover_E.jpg", (255, 210, 63), INK, INK, (255, 210, 63))
collage("cover_F.jpg", (32, 92, 150), "white", (255, 210, 63), INK)
collage("cover_G.jpg", (226, 98, 62), "white", "white", (226, 98, 62))
