"""悉尼真正订不到的餐厅：首页三选一，每家一张卡（上方照片，下方店名价格、介绍、实测、怎么订）。
用法：python3 tools/hardbook_cards.py 图片目录 老杨图标目录 输出目录"""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
Image.MAX_IMAGE_PIXELS = None
W, H = 1080, 1440
SRC, ICONS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
CREAM = (248, 244, 236); INK = (26, 28, 36); RED = (190, 40, 36); GREY = (60, 56, 50)
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
    im = im.crop((round(x), round(y), round(x) + w, round(y) + h)).filter(ImageFilter.UnsharpMask(1.5, 30, 2))
    return ImageEnhance.Color(im).enhance(1.06)

def icon(img, pose, x, y, h):
    ic = Image.open(f"{ICONS}/{pose}.png").convert("RGBA")
    ic = ic.resize((round(ic.width * h / ic.height), h), Image.LANCZOS)
    img = img.convert("RGBA"); sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 255), (x + 4, y + 6), ic.split()[3].point(lambda v: int(v * .3)))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8))); img.alpha_composite(ic, (x, y))
    return img.convert("RGB")

def wrap(text, font, width):
    toks = re.findall(r"[A-Za-z0-9&'.$,:]+|.", text)
    lines, cur = [], ""
    for t in toks:
        if font.getlength(cur + t) > width and cur and t not in "，。、！？）：；":
            lines.append(cur); cur = t.lstrip()
        else: cur += t
    if cur: lines.append(cur)
    return lines

ROWS = {3: [1, 2], 4: [2, 2], 5: [2, 3], 6: [3, 3]}
def card(fn, name, price, intro, test, how, photos, ph=640):
    img = Image.new("RGB", (W, H), CREAM); rows = ROWS[len(photos)]; rh = ph // len(rows); k = 0
    for r, n in enumerate(rows):
        cw = W // n
        for c in range(n): img.paste(crop(photos[k], cw + 1, rh + 1), (c * cw, r * rh)); k += 1
    d = ImageDraw.Draw(img)
    fn_ = serif(62); fp = zh(42, "Bold"); fi = zh(36); fl = zh(36, "Bold")
    il = wrap(intro, fi, 940); tl = wrap(test, fi, 800); hl = wrap(how, fi, 800)
    lh = 54; block = 84 + len(il) * lh + 22 + len(tl) * lh + 16 + len(hl) * lh
    y = ph + max(30, (H - ph - block) // 2)
    d.text((70, y), name, font=fn_, fill=INK)
    if price: d.text((70 + fn_.getlength(name) + 26, y + 12), price, font=fp, fill=RED)
    y += 84
    for ln in il: d.text((72, y), ln, font=fi, fill=GREY); y += lh
    y += 22
    for tag, ls in (("实测", tl), ("怎么订", hl)):
        d.text((72, y), tag, font=fl, fill=RED)
        for ln in ls: d.text((230, y), ln, font=fi, fill=INK if tag == "实测" else GREY); y += lh
        y += 16
    img.save(f"{OUT}/{fn}", quality=93)

V = [
 ("01.jpg", "YOSHII'S OMAKASE", "$380",
  "Barangaroo的Crown酒店里，只有10个座位的板前寿司。Yoshii师傅当面捏，十道omakase，周五周六分6点和8点45两场。",
  "未来4周开门20天，只有3天还有位，最早11月26日晚上6点。",
  "每月1号放位，这家是真要定闹钟抢的。",
  ["yo_seat.jpg", "yo_24.jpg", ("yo_sash.jpg", .5, .45), "yo_chef.jpg", "yo_26.jpg"]),
 ("02.jpg", "SUSHI OE", None,
  "新鱼市场里的8座寿司店，Oe师傅一晚只做一场，大约30道，菜单每天跟着当天的鱼变。",
  "不在网上订位系统里，一个月的位几分钟就没了。",
  "关注它的Instagram，每个月公布放位时间，到点马上联系。",
  ["oe_10.webp", "oe_7.webp", "oe_2.webp", "oe_4.webp", "oe_16.webp", "oe_5.webp"]),
 ("03.jpg", "BISTECCA", "按重量点",
  "CBD小巷里推门下楼的地下牛排馆，只做佛罗伦萨T骨牛排，建议600克起点。进门会请你把手机锁进抽屉。",
  "未来4周只有2天能订到晚餐，最早11月16日周一下午5点半。",
  "订不到就早点去前面的酒吧坐着，喝一杯吃点小食等位。",
  ["bi_1.jpg", "bi_3.jpg", "bi_to105294526.jpg", "bi_2.jpg", "bi_to105294529.jpg", "bi_to105294527.jpg"]),
 ("04.jpg", "SAINT PETER", "$395",
  "Josh Niland的鱼料理，搬进Paddington的Grand National酒店后更难订。晚餐十道菜$395，午餐三道菜$195，整条鱼从鱼鳞吃到鱼眼。",
  "订位系统查不到实时空位，靠规则抢。",
  "提前6个月开放，每天往后放一天。吃不到正餐就去酒吧，不接受预订，直接进去点汉堡和马天尼。",
  ["sp_to106185014.jpg", "sp_to106185023.jpg", "sp_to106186949.jpg", "sp_to106186947.jpg", "sp_to106186950.jpg", "sp_to106186948.jpg"]),
 ("05.jpg", "THE GIDLEY", None,
  "King St一扇没招牌的灰门进去，下楼是丝绒卡座的美式牛排馆，跟Bistecca同一个老板。",
  "未来4周一半日子有位，但几乎全是晚上9点半那一场，正常饭点要等到12月以后。",
  "不介意吃晚点，就订9点半当宵夜。",
  ["gi_to105730414.jpg", "gi_to105730412.jpg", "gi_1.jpg", "gi_to105730411.jpg", "gi_to105730415.jpg", "gi_to105730413.jpg"]),
 ("06.jpg", "FIREDOOR", None,
  "Surry Hills，Lennox Hastie的柴火餐厅，没有煤气灶，所有菜都用不同的木头烤。招牌是长时间干式熟成牛排。",
  "未来4周开门20天，12天能订，周末要提前两三周。",
  "提前6个月开放。周三周四最好订，午餐有$155的主厨套餐。",
  ["fd_11.jpg", "fd_1.jpg", "fd_3.jpg", "fd_5.jpg", "fd_10.jpg", "fd_4.jpg"]),
]
for fn, *a in V: card(fn, *a)

# 首页
def grad(c, a=.45, k=215):
    ov = Image.new("L", (1, H))
    for yy in range(H): ov.putpixel((0, yy), int(max(0, (yy - H * a) / (H * (1 - a))) ** 1.1 * k))
    return Image.composite(Image.new("RGB", (W, H), (10, 8, 6)), c, ov.resize((W, H)))
L = ["吐血整理", "悉尼真正订不到的", "6家餐厅"]
# A：一张大图，白色宋体
a = grad(crop(("yo_seat.jpg", .5, .5), W, H), .35); d = ImageDraw.Draw(a); f = serif(104)
for i, t in enumerate(L): d.text((70, 900 + i * 135), t, font=f, fill="white")
icon(a, "13_探店", 50, 50, 200).save(f"{OUT}/cover_A.jpg", quality=93)
# B：六宫格，中间黄底黑字
b = Image.new("RGB", (W, H)); cw, ch = W // 2, H // 3
for i, p in enumerate(["oe_7.webp", "bi_1.jpg", "yo_24.jpg", "fd_11.jpg", "sp_to106185014.jpg", "gi_to105730412.jpg"]):
    b.paste(crop(p, cw, ch), ((i % 2) * cw, (i // 2) * ch))
d = ImageDraw.Draw(b); f = zh(88, "Black"); lh = 112; y0 = H // 2 - lh * 3 // 2
for i, t in enumerate(L):
    w = f.getlength(t); d.rectangle(((W - w) / 2 - 26, y0 + i * lh - 4, (W + w) / 2 + 26, y0 + i * lh + lh - 10), fill=(255, 214, 64))
    d.text(((W - w) / 2, y0 + i * lh), t, font=f, fill=INK)
icon(b, "13_探店", 30, 30, 180).save(f"{OUT}/cover_B.jpg", quality=93)
# C：深色底大字，下面四张小图
c = Image.new("RGB", (W, H), (22, 20, 18)); d = ImageDraw.Draw(c); f = zh(110, "Black")
d.text((70, 110), "吐血整理", font=f, fill=(255, 214, 64))
d.text((70, 250), "悉尼真正订不到的", font=f, fill="white"); d.text((70, 390), "6家餐厅", font=f, fill="white")
for i, p in enumerate(["oe_7.webp", "bi_1.jpg", "yo_26.jpg", "fd_11.jpg"]):
    c.paste(crop(p, 470, 400), (70 + (i % 2) * 470, 600 + (i // 2) * 400 + (i // 2) * 20) if False else (60 + (i % 2) * 490, 600 + (i // 2) * 410))
icon(c, "13_探店", W - 250, 90, 210).save(f"{OUT}/cover_C.jpg", quality=93)
print("ok")
