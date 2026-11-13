"""悉尼omakase价格从低到高：首页三选一、价格总览、5张分档卡。
用法：python3 tools/omakase_cards.py 图片目录 老杨图标目录 输出目录"""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
Image.MAX_IMAGE_PIXELS = None
W, H = 1080, 1440
SRC, ICONS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
CREAM = (248, 244, 236); INK = (26, 28, 36); GREY = (70, 66, 60); LINE = (214, 206, 192)
def zh(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def serif(s): return ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", s, index=2)

def crop(spec, w, h):
    spec = list(spec) if isinstance(spec, tuple) else [spec]
    name, fx, fy, z = spec + [.5, .5, 1.0][len(spec) - 1:]
    im = ImageOps.exif_transpose(Image.open(f"{SRC}/{name}")).convert("RGB")
    s = max(w / im.width, h / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    return ImageEnhance.Color(im.crop((round(x), round(y), round(x) + w, round(y) + h)).filter(ImageFilter.UnsharpMask(1.5, 30, 2))).enhance(1.05)

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

def tier(fn, title, photos, items, ph=420):
    img = Image.new("RGB", (W, H), CREAM); n = len(photos); cw = W // n
    for i, p in enumerate(photos): img.paste(crop(p, cw + 1, ph), (i * cw, 0))
    d = ImageDraw.Draw(img); ft = serif(68)
    for k in range(0, 30):  # 从大字号往下试，直到填满又放得下
        sd = 44 - k * .5; sn = sd + 10; lh = sd * 1.42; gap = sd * 1.3
        fn_ = zh(round(sn), "Bold"); fi = zh(round(sd))
        L = [wrap(desc, fi, 960) for _, _, desc in items]
        hgt = 100 + sum(sn * 1.45 + len(l) * lh for l in L) + gap * (len(items) - 1)
        if ph + 40 + hgt < H - 50: break
    y = ph + 40 + max(0, (H - 50 - ph - 40 - hgt) / 3)
    d.text((60, y), title, font=ft, fill=INK); y += 100
    for k, ((name, price, _), l) in enumerate(zip(items, L)):
        d.text((60, y), name, font=fn_, fill=INK); d.text((W - 60 - fn_.getlength(price), y), price, font=fn_, fill=INK)
        y += sn * 1.45
        for ln in l: d.text((62, y), ln, font=fi, fill=GREY); y += lh
        if k < len(items) - 1: y += gap / 2; d.line((60, y - 6, W - 60, y - 6), fill=LINE, width=2); y += gap / 2
    img.save(f"{OUT}/{fn}", quality=93)

T = [
 ("02.jpg", "$100以内", ["kok_1.jpg", "kok_to.jpg", "kok_2.jpg"], [
  ("Sushi e", "$60", "Merivale旗下，在CBD的Establishment楼上。Omakase Express一位$60，想先试试omakase是什么感觉，这个最划算。订位要留信用卡。"),
  ("Kokumai", "$60起", "Barangaroo的寿司店，$60是8贯寿司加一条手卷和味噌汤，另有$80和$100的升级版。价格是2024年的，去之前再确认。"),
  ("Hachioji", "$100以内", "Crows Nest的寿司吧台，把omakase带到北岸，人均$100以内。不想订位也可以直接去点单。")]),
 ("03.jpg", "$160左右", ["haco_105869764.jpg", "haco_105869765.jpg", "haco_105869766.jpg"], [
  ("Gold Class Daruma", "$160", "CBD的Grace酒店里。主厨寿司套餐$160，周一、周五、周六有；11月17日起周二到周六还有$180的寿司怀石。周六另收5%。"),
  ("Tsuzumi", "$160 / $250", "Barangaroo，菜单每天看鱼市进什么。午餐$160，晚餐$250，周日周一休息。"),
 ]),
 ("04.jpg", "$185到200", ["haco_105869765.jpg", "haco_105869766.jpg", "haco_105869764.jpg"], [
  ("Haco", "$185", "Chaco Bar老板Keita Abe开的，12个座位围着厨房，晚餐大约20道，主打天妇罗。午餐有$130的天妇罗套餐，更便宜。"),
  ("Kappo Yama", "$185", "Bridge St上8个座位的桧木吧台，大约12道，90分钟。严格说是割烹，适合一两个人去，建议提前三到五周订。"),
  ("Kuon Sushi Sei", "约$195", "Haymarket的寿司吧台，Kuon旗下。食客分享晚餐omakase大约$195，周四到周日也有午餐。")]),
 ("05.jpg", "$200到270", ["ora_1.jpg", "ora_2.jpg", "moku_1.jpg"], [
  ("Kisuke", "约$220", "Potts Point，Morita夫妇两个人打理，只有6个座位，最像日本街坊里的寿司店。只提前30天开放订位。"),
  ("Ora", "$260", "Waterloo，Nobuyuki Ura主厨的怀石风格omakase，9道，10个座位，周三到周六晚上6点半开始。$260只含食物，建议提前四周订。"),
  ("Moku", "$268", "Darlinghurst的两层小店，主厨来自Sokyo。omakase只在周三周四晚上，每场6个人，5点半或8点15两场。")]),
 ("06.jpg", "$280", ["bes_105869422.jpg", "bes_1.jpg", "bes_2.jpg"], [
  ("Besuto", "$280", "Circular Quay，Joel Best开的。清酒配酒另加$185，日本威士忌很多。18岁以上才能订。"),
  ("Kuon Omakase", "$280", "Surry Hills小巷里，主打熟成寿司配清酒。订位时每人先付$50订金。"),
  ("R by Raita Noda", "约$280", "Redfern，Raita Noda主厨2025年开的新店，15个座位，10道，周二到周六晚上7点开始。"),
 ]),
 ("07.jpg", "$298到300", ["gs_3.jpg", "gs_1.jpg", "sa_luxurious-otoro-nigiri-sushi.jpg"], [
  ("Green Shiso", "$298", "CBD的Quay Quarter Lanes，4月起涨到$298，菜单每三个月换一次。"),
  ("Sokyo", "$300", "Pyrmont的The Star，每晚只接一桌6个人，最多23道。每月1号上午10点放未来三个月的位。"),
  ("Sano Omakase", "$300", "CBD日料店Azuma里，7个座位，Sano师傅做了三十多年寿司。只能填等位表，周六等得最久。")]),
 ("08.jpg", "$350以上", ["oe_7.webp", "oe_10.webp", "yo_26.jpg"], [
  ("Sushi Oe", "$350", "搬到新鱼市场后变成10个座位，Oe师傅掌板，一晚一场。现在可以在OpenTable上直接订。"),
  ("Prefecture 48", "$365", "大约22道：A5和牛寿喜烧、北海道海胆、大腹、中腹、星鳗，最后用龙虾头煮味噌汤，再来一卷配鱼子酱的寿司。"),
  ("Yoshii's Omakase", "$380", "Crown Sydney里10个座位，十道。每月1号放下个月的位。12月24到31日涨到$500。")]),
]
for fn, title, ph_, items in T: tier(fn, title, ph_, items)

# 价格总览
ALL = [(n, p) for _, _, _, items in T for n, p, _ in items]
img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
d.text((60, 60), "悉尼omakase价格", font=serif(72), fill=INK); d.text((60, 160), "从低到高，一位的价格", font=zh(34), fill=GREY)
fn_ = zh(36, "Medium"); fp = zh(36, "Bold"); y = 250; lh = 56
for i, (n, p) in enumerate(ALL):
    d.text((60, y), f"{i + 1:>2}", font=fp, fill=GREY); d.text((130, y), n, font=fn_, fill=INK)
    d.text((W - 60 - fp.getlength(p), y), p, font=fp, fill=INK)
    x0 = 130 + fn_.getlength(n) + 20; x1 = W - 60 - fp.getlength(p) - 20
    for xx in range(int(x0), int(x1), 14): d.ellipse((xx, y + 26, xx + 3, y + 29), fill=LINE)
    y += lh
img.save(f"{OUT}/01.jpg", quality=93)

# 首页
def grad(c, a=.45, k=220):
    ov = Image.new("L", (1, H))
    for yy in range(H): ov.putpixel((0, yy), int(max(0, (yy - H * a) / (H * (1 - a))) ** 1.1 * k))
    return Image.composite(Image.new("RGB", (W, H), (10, 8, 6)), c, ov.resize((W, H)))
L = ["悉尼omakase", "从$60到$380", "20家价格全整理"]
a = grad(crop(("oe_7.webp", .5, .5), W, H), .4); d = ImageDraw.Draw(a); f = serif(104)
for i, t in enumerate(L): d.text((70, 930 + i * 135), t, font=f, fill="white")
icon(a, "13_探店", 50, 50, 200).save(f"{OUT}/cover_A.jpg", quality=93)
b = Image.new("RGB", (W, H)); cw, ch = W // 2, H // 3
for i, p in enumerate(["oe_7.webp", "bes_105869422.jpg", "yo_26.jpg", "gs_3.jpg", "sa_luxurious-otoro-nigiri-sushi.jpg", "ora_2.jpg"]):
    b.paste(crop(p, cw, ch), ((i % 2) * cw, (i // 2) * ch))
d = ImageDraw.Draw(b); f = zh(88, "Black"); lh = 112; y0 = H // 2 - lh * 3 // 2
for i, t in enumerate(L):
    w = f.getlength(t); d.rectangle(((W - w) / 2 - 26, y0 + i * lh - 4, (W + w) / 2 + 26, y0 + i * lh + lh - 10), fill=(255, 214, 64))
    d.text(((W - w) / 2, y0 + i * lh), t, font=f, fill=INK)
icon(b, "13_探店", 30, 30, 180).save(f"{OUT}/cover_B.jpg", quality=93)
c = Image.new("RGB", (W, H), (22, 20, 18)); d = ImageDraw.Draw(c); f = zh(104, "Black")
d.text((70, 110), "悉尼omakase", font=f, fill="white"); d.text((70, 250), "从$60到$380", font=f, fill=(255, 214, 64)); d.text((70, 390), "20家价格全整理", font=f, fill="white")
for i, p in enumerate(["oe_7.webp", "bes_105869422.jpg", "yo_26.jpg", "sa_luxurious-otoro-nigiri-sushi.jpg"]):
    c.paste(crop(p, 470, 400), (60 + (i % 2) * 490, 600 + (i // 2) * 410))
icon(c, "13_探店", W - 250, 90, 210).save(f"{OUT}/cover_C.jpg", quality=93)
print("ok")
