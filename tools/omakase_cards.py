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
 ("02.jpg", "$220到268", ["kisuke_3.jpg", "ora_2.jpg", "moku_1.jpg"], [
  ("Kisuke", "$220", "Potts Point，Morita夫妇两个人打理，只有6个座位，最像日本街坊里的寿司店。每月1号下午1点在官网放下个月的位，只接2人、4人、6人。"),
  ("Tsuzumi", "$250", "Barangaroo，菜单每天看鱼市进什么。晚餐$250，午餐有$160的版本，周日周一休息。"),
  ("Ora", "$260", "Waterloo，Nobuyuki Ura主厨的怀石风格omakase，9道，10个座位，周三到周六晚上6点半开始。$260只含食物，建议提前四周订。"),
  ("Moku", "$268", "Darlinghurst的两层小店，主厨来自Sokyo。omakase只在周三周四晚上，每场6个人，5点半或8点15两场。")]),
 ("03.jpg", "$280到290", ["bes_105869422.jpg", "kuon_1.jpg", "raita_0.jpg"], [
  ("Besuto", "$280", "Circular Quay，Joel Best开的。清酒配酒另加$185，日本威士忌很多。18岁以上才能订，4天内取消收全额。"),
  ("Kuon Omakase", "$280", "Surry Hills小巷里，主打熟成寿司配清酒。订位时每人先付$50订金，周二到周日晚上都开。"),
  ("R by Raita Noda", "$290", "Redfern的Wunderlich Lane，Raita Noda主厨的十道菜，周一到周六晚上7点开始，可以打电话或发短信订。")]),
 ("04.jpg", "$298到300", ["gs_3.jpg", "sokyo_1.jpg", "sa_luxurious-otoro-nigiri-sushi.jpg"], [
  ("Green Shiso", "$298", "CBD的Quay Quarter Lanes，4月起涨到$298，菜单每三个月换一次，周四到周六有5点半和8点半两场。"),
  ("Sokyo", "$300", "Pyrmont的The Star，每晚只接一桌6个人，最多23道，只开周一到周四。每月1号上午10点放未来三个月的位，48小时内取消收全额。"),
  ("Sano Omakase", "$300", "CBD日料店Azuma里，7个座位，Sano师傅做了三十多年寿司。请客人别喷香水、少看手机。只能填等位表，周六等得最久。")]),
 ("05.jpg", "$350以上", ["oe_7.webp", "taka_1.jpg", "yo_26.jpg"], [
  ("Sushi Oe", "$350", "搬到新鱼市场后变成10个座位，Oe师傅掌板，一晚一场，现在可以在OpenTable上直接订。"),
  ("Taka's Omakase", "$365", "Prefecture 48二楼，Takashi Yamamoto主厨。大约22道：A5和牛寿喜烧、北海道海胆、大腹、中腹、星鳗，最后用龙虾头煮味噌汤，再来一卷配鱼子酱的寿司。"),
  ("Yoshii's Omakase", "$380", "Crown Sydney里10个座位，十道。每月1号放下个月的位，12月24到31日涨到$500。")]),
]
for fn, title, ph_, items in T: tier(fn, title, ph_, items)

# 价格总览
ALL = [(n, p) for _, _, _, items in T for n, p, _ in items]
img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
d.text((60, 70), "悉尼omakase价格", font=serif(84), fill=INK); d.text((62, 190), "从低到高，一位的价格，11月中查", font=zh(38), fill=GREY)
fn_ = zh(46, "Medium"); fp = zh(46, "Bold"); y = 290; lh = (H - 330) // len(ALL)
for i, (n, p) in enumerate(ALL):
    d.text((60, y), f"{i + 1:>2}", font=fp, fill=GREY); d.text((130, y), n, font=fn_, fill=INK)
    d.text((W - 60 - fp.getlength(p), y), p, font=fp, fill=INK)
    x0 = 130 + fn_.getlength(n) + 20; x1 = W - 60 - fp.getlength(p) - 20
    for xx in range(int(x0), int(x1), 14): d.ellipse((xx, y + 34, xx + 4, y + 38), fill=LINE)
    y += lh
img.save(f"{OUT}/01.jpg", quality=93)

# 首页：12宫格，每格写店名和价格
G = [("kisuke_3.jpg", "Kisuke", "$220"), ("ora_2.jpg", "Ora", "$260"), ("moku_1.jpg", "Moku", "$268"),
     ("bes_105869422.jpg", "Besuto", "$280"), ("kuon_1.jpg", "Kuon", "$280"), ("raita_0.jpg", "Raita Noda", "$290"),
     ("gs_3.jpg", "Green Shiso", "$298"), ("sokyo_1.jpg", "Sokyo", "$300"), ("sa_luxurious-otoro-nigiri-sushi.jpg", "Sano", "$300"),
     ("oe_7.webp", "Sushi Oe", "$350"), ("taka_1.jpg", "Taka's", "$365"), ("yo_26.jpg", "Yoshii's", "$380")]
CRM = (255, 244, 214); BRN = (38, 26, 16)
def fit(text, maxw, start, w="Black"):
    sz = start
    while zh(sz, w).getlength(text) > maxw and sz > 20: sz -= 2
    return zh(sz, w)
def outlined(d, xy, text, f, sw):
    d.text(xy, text, font=f, fill=CRM, stroke_width=sw, stroke_fill=BRN)
def grid12(fn, big_top="price"):
    g = Image.new("RGB", (W, H), (240, 236, 228)); cw, ch = W // 3, H // 4
    for i, (p, n, pr) in enumerate(G):
        t = crop(p, cw - 3, ch - 3); d = ImageDraw.Draw(t)
        top, bot = (pr, n) if big_top == "price" else (n, pr)
        ft = fit(top, cw - 40, 118); fb = fit(bot, cw - 30, 54)
        tw = ft.getlength(top); outlined(d, ((cw - 3 - tw) / 2, 14), top, ft, 9)
        bw = fb.getlength(bot); outlined(d, ((cw - 3 - bw) / 2, ch - 3 - fb.size - 34), bot, fb, 6)
        g.paste(t, ((i % 3) * cw + 1, (i // 3) * ch + 1))
    g.save(f"{OUT}/{fn}", quality=93)
grid12("cover_A.jpg", "price")
grid12("cover_B.jpg", "name")
print("ok")
