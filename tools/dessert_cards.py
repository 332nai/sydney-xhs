"""悉尼超市雪糕：营养师推荐的低卡低糖款。每款一张卡，首页、排行、怎么挑。
数字用Coles营养标签（每份），没有上架Coles的用包装和营养师给的数字。
用法：python3 tools/dessert_cards.py 图片目录 输出目录"""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
W, H = 1080, 1440
SRC, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
INK = (40, 30, 48); GREY = (92, 84, 96)
def zh(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def serif(s): return ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", s, index=2)
def wrap(text, font, width):
    toks = re.findall(r"[A-Za-z0-9&'.$,:%]+|.", text); lines, cur = [], ""
    for t in toks:
        if font.getlength(cur + t) > width and cur and t not in "，。、！？）：；": lines.append(cur); cur = t.lstrip()
        else: cur += t
    if cur: lines.append(cur)
    return lines

def pack(name, w, h):
    im = Image.open(f"{SRC}/{name}").convert("RGB")
    # 裁掉白边
    bg = Image.new("RGB", im.size, (255, 255, 255)); diff = ImageOps.invert(ImageOps.grayscale(Image.composite(im, bg, Image.new("L", im.size, 255))))
    box = diff.point(lambda v: 255 if v > 18 else 0).getbbox() or (0, 0, *im.size); im = im.crop(box)
    s = min(w / im.width, h / im.height); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    out = Image.new("RGB", (w, h), (255, 255, 255)); out.paste(im, ((w - im.width) // 2, (h - im.height) // 2)); return out

# (名字, 中文名, 标签, 卡, 糖, 额外, 底色, 结论, 介绍, 价格, 图)
P = [
 ("Bulla Frozen Yoghurt Mini", "Bulla迷你冻酸奶条", "最低卡", "45卡", "糖6.5g", "", (255, 228, 214),
  "8款里热量最低，一支刚好解馋。", "酸奶做底，澳洲产，没有人工色素和香精。芒果、草莓、百香果、野莓四种口味，一支36克。", "Coles $10一盒14支", "c_6043866.jpg"),
 ("Streets Solero Mini", "Solero迷你", "水果最多", "55卡", "糖一茶匙多", "", (255, 236, 200),
  "22%是真水果，糖只有一茶匙多一点。", "牛奶做底，外面一层果味冰。Exotic是芒果百香果，Berry Bliss是莓果，小小一支不怕吃多。", "", "solero.png"),
 ("Peters Frosty Fruits 少糖版", "Frosty Fruits少糖版", "给小孩", "66卡", "糖7.2g", "", (226, 244, 200),
  "比原版少一半糖，给小孩最放心。", "39%是果汁，用甜菊糖代替一半的糖，热带水果味。就是一根水果冰棒，没有奶。", "Coles $6一盒8支", "c_8739282.jpg"),
 ("Twisted Minis", "Twisted迷你冻酸奶杯", "冻酸奶杯", "83卡", "糖9.9g", "", (214, 240, 234),
  "一小杯够分量，还有益生菌酸奶。", "草莓香草和巧克力香草两种，一杯120毫升，用勺子吃，比冰棒更有满足感。", "Coles $5.95一盒4杯", "c_3147027.jpg"),
 ("Peters Lil' Pops", "Peters Lil' Pops", "巧克力脆皮", "90卡", "糖9.3g", "", (214, 228, 250),
  "有巧克力脆皮，还不到100卡。", "牛奶做底的香草小雪糕，外面一层巧克力，一口一个，小孩大人都爱。", "Coles $5.9一盒9支", "c_1490572.jpg"),
 ("Bulla Creamy Classics", "Bulla经典香草", "真冰淇淋", "92卡", "糖9.1g", "一勺46克", (250, 222, 226),
  "真正的冰淇淋里，脂肪和糖都偏低的一款。", "澳洲老牌，用鲜奶和奶油做，口感还是很浓。2升一大桶，每次挖一勺46克就是92卡。", "Coles $6.9两升", "c_9486590.jpg"),
 ("Twisted Protein Pint", "Twisted高蛋白冰淇淋", "高蛋白", "102卡", "蛋白10g", "一份是三分之一杯", (232, 224, 214),
  "一份10克蛋白质，零添加糖。", "双重巧克力口味，用赤藓糖醇代糖，饱和脂肪也低。一整杯306卡，有30克蛋白质，健身的人可以当加餐。", "", "protein.png"),
 ("Coles Irresistible Vanilla Bean", "Coles香草豆冰淇淋", "超市自有牌", "153卡", "糖11.3g", "一份100毫升", (236, 228, 250),
  "超市自己的牌子，按克算糖比Bulla还少。", "真冰淇淋，有香草籽。每100克糖16.6克，Bulla是19.9克。一份100毫升比较大，挖小一点就好。", "Coles $6.5一升", "c_2426251.jpg"),
]

def card(fn, p):
    name, cn, tag, cal, sug, note, bg, verdict, intro, price, img = p
    im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)
    ft = zh(64, "Black"); d.text((60, 52), tag, font=ft, fill=INK)
    # 产品
    panel = Image.new("RGB", (W - 120, 640), "white"); panel.paste(pack(img, W - 220, 580), (50, 30))
    m = Image.new("L", panel.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *panel.size), radius=36, fill=255)
    im.paste(panel, (60, 160), m)
    y = 830; d = ImageDraw.Draw(im)
    fc = zh(120, "Black"); d.text((60, y), cal, font=fc, fill=INK); x = 60 + fc.getlength(cal) + 40
    fs = zh(64, "Black"); d.text((x, y + 44), sug, font=fs, fill=(196, 70, 60))
    y += 160
    if note: d.text((62, y - 12), note, font=zh(32), fill=GREY); y += 40
    d.text((60, y + 6), cn, font=serif(48), fill=INK); y += 78
    for ln in wrap(verdict, zh(36, "Bold"), 960): d.text((62, y), ln, font=zh(36, "Bold"), fill=INK); y += 50
    y += 4
    for ln in wrap(intro, zh(32), 960): d.text((62, y), ln, font=zh(32), fill=GREY); y += 46
    if price: y += 6; d.text((62, y), price, font=zh(32, "Bold"), fill=INK); y += 46
    assert y < H - 10, (name, y)
    im.save(f"{OUT}/{fn}", quality=93)

for k, p in enumerate(P): card(f"{k + 3:02d}.jpg", p)

# 01 排行
im = Image.new("RGB", (W, H), (252, 246, 240)); d = ImageDraw.Draw(im)
d.text((60, 60), "悉尼超市雪糕热量排行", font=serif(76), fill=INK)
d.text((62, 168), "按每支或每份算，从低到高", font=zh(34), fill=GREY)
y = 280; fn_ = zh(48, "Medium"); fp = zh(52, "Black"); ft = zh(32, "Bold")
for i, p in enumerate(P):
    d.text((60, y), f"{i + 1}", font=fp, fill=GREY); d.text((115, y), p[1], font=fn_, fill=INK)
    d.text((117, y + 64), p[2] + "，" + p[4], font=ft, fill=(196, 70, 60))
    pw = fp.getlength(p[3]); x0 = 115 + fn_.getlength(p[1]) + 20; x1 = W - 60 - pw - 20
    for xx in range(int(x0), int(x1), 14): d.ellipse((xx, y + 32, xx + 4, y + 36), fill=(214, 204, 196))
    d.text((W - 60 - pw, y), p[3], font=fp, fill=INK); y += 140
im.save(f"{OUT}/01.jpg", quality=93)

# 02 怎么挑
im = Image.new("RGB", (W, H), (252, 246, 240)); d = ImageDraw.Draw(im)
d.text((60, 60), "超市雪糕怎么挑", font=serif(84), fill=INK)
T = [("真冰淇淋看乳脂", "按规定，真正的冰淇淋要有至少10%的乳脂。很多叫雪糕的其实是冰淇淋风味甜品，超市里真冰淇淋只有几款。"),
     ("水果冰棒看糖", "冰棒热量低，但一支最多能有5茶匙糖，还常加色素。翻到背面看配料表，越短越好。"),
     ("迷你装最好控制", "大支巧克力雪糕一支能到300卡，迷你装和冻酸奶一支只有四五十卡，想吃就吃一支。"),
     ("少糖款多用代糖", "标着少糖、零添加糖的，大多用甜菊糖或赤藓糖醇代替，热量低，但吃多了有人会肚子胀。")]
y = 240
for h_, t in T:
    d.text((60, y), h_, font=zh(56, "Black"), fill=(196, 70, 60)); y += 86
    for ln in wrap(t, zh(40), 960): d.text((62, y), ln, font=zh(40), fill=INK); y += 62
    y += 60
assert y < H, y
im.save(f"{OUT}/02.jpg", quality=93)

# 首页：8格产品，卡数最大，标签
def cover(fn, title, sub):
    im = Image.new("RGB", (W, H), (252, 246, 240)); d = ImageDraw.Draw(im)
    d.text((50, 30), title, font=zh(96, "Black"), fill=INK)
    f2 = zh(60, "Black"); f3 = zh(84, "Black")
    d.text((52, 160), sub[0], font=f2, fill=INK); x = 52 + f2.getlength(sub[0]) + 12
    d.text((x, 144), sub[1], font=f3, fill=(196, 70, 60)); x += f3.getlength(sub[1]) + 12
    d.text((x, 160), sub[2], font=f2, fill=INK)
    cw, ch = (W - 60) // 2, (H - 280 - 40) // 4; g = 14
    for i, p in enumerate(P):
        x0 = 30 + (i % 2) * (cw + g // 2); y0 = 270 + (i // 2) * (ch + 4)
        tile = Image.new("RGB", (cw - g // 2, ch - 10), p[6]); td = ImageDraw.Draw(tile)
        pk = pack(p[10], 200, ch - 40); tile.paste(pk, (16, 15))
        fc = zh(78, "Black"); td.text((236, 30), p[3], font=fc, fill=INK)
        td.text((238, 140), p[2], font=zh(40, "Black"), fill=(196, 70, 60))
        m = Image.new("L", tile.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *tile.size), radius=28, fill=255)
        im.paste(tile, (x0, y0), m)
    im.save(f"{OUT}/{fn}", quality=93)

cover("cover_A.jpg", "悉尼超市雪糕", ("营养师推荐，最低", "45卡", ""))
cover("cover_B.jpg", "夏天吃雪糕不胖", ("悉尼超市这8款，最低", "45卡", ""))
print("ok")
