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

def half(img, y0, hh, photo, name, price, intro, book):
    ph = 330; img.paste(crop(photo, W, ph), (0, y0)); d = ImageDraw.Draw(img)
    fn_ = serif(56); fp = zh(48, "Black"); fi = zh(34); lh = 50
    y = y0 + ph + 26
    d.text((60, y), name, font=fn_, fill=INK); d.text((W - 60 - fp.getlength(price), y + 4), price, font=fp, fill=INK)
    y += 80
    for ln in wrap(intro, fi, 960): d.text((62, y), ln, font=fi, fill=GREY); y += lh
    y += 10
    for ln in wrap(book, fi, 960): d.text((62, y), ln, font=fi, fill=INK); y += lh
    assert y < y0 + hh, (name, y - y0)
def page(fn, a, b=None):
    img = Image.new("RGB", (W, H), CREAM)
    if b:
        half(img, 0, 720, *a); half(img, 720, 720, *b)
        ImageDraw.Draw(img).rectangle((0, 716, W, 724), fill=CREAM)
    else:
        half(img, 200, 1240, *a)
    img.save(f"{OUT}/{fn}", quality=93)

V = [
 (("kisuke_3.jpg", .5, .22), "Kisuke", "$220",
  "Potts Point的小店，Morita夫妇两个人打理，只有6个座位。浅色木头吧台，安静得像日本街坊里的寿司店，菜单每天看当天的鱼。",
  "订位：每月1号下午1点在官网放下个月的位，只接2人、4人、6人。周二到周六晚上营业。"),
 ("ora_2.jpg", "Ora", "$260",
  "Waterloo，Nobuyuki Ura主厨做怀石风格的omakase，9道，10个座位的主厨吧台。店里的设计取材自日本民间故事，空间很大，跟一般小寿司店不一样。",
  "订位：官网选晚上6点半的Omakase，建议提前四周。周三到周六营业，$260只含食物，4天内取消收全额。"),
 ("moku_1.jpg", "Moku", "$268",
  "Darlinghurst的两层小店，主厨来自Sokyo，吧台还有一位很有名的调酒师。日本菜里加了澳洲本地食材，还有水果highball。",
  "订位：omakase只在周三周四晚上，每场6个人，5点半或8点15两场，官网订。"),
 ("bes_105869422.jpg", "Besuto", "$280",
  "Circular Quay，Bondi's Best的老板Joel Best开的8座寿司吧台，以海鲜握寿司为主，大约12到13道，日本威士忌有一百多款。",
  "订位：OpenTable或官网，清酒配酒另加$185。18岁以上，4天内取消收全额。"),
 ("kuon_1.jpg", "Kuon Omakase", "$280",
  "Surry Hills的Fracks Lane小巷里，做现代江户前寿司，把新鲜鱼和熟成鱼搭在一起，配清酒吃，是悉尼少见主打熟成寿司的店。",
  "订位：官网订，每人先付$50订金。周二到周日晚上营业。"),
 ("raita_0.jpg", "R by Raita Noda", "$290",
  "Raita Noda是悉尼最早自立门户做omakase的日本主厨之一，新店开在Redfern的Wunderlich Lane，十道菜，像看一场厨师的表演。",
  "订位：一定要提前订，官网或打电话发短信0451 068 815。周一到周六晚上7点开始。"),
 ("gs_3.jpg", "Green Shiso", "$298",
  "CBD的Quay Quarter Lanes里，菜单每三个月换一次，跟着季节走。4月起涨到$298。",
  "订位：OpenTable。周二周三晚上6点半一场，周四到周六5点半和8点半两场。10人以上可以通过Instagram或微信联系。"),
 ("sokyo_1.jpg", "Sokyo", "$300",
  "The Star里Chase Kojima的日料店，离鱼市场开车五分钟。omakase吧台每晚只接一桌6个人，最多23道，从扇贝饺子到炭烤和牛。",
  "订位：每月1号上午10点放未来三个月的位，只开周一到周四，6点准时开始。48小时内取消每人收$300。"),
 ("sa_luxurious-otoro-nigiri-sushi.jpg", "Sano Omakase", "$300",
  "藏在CBD日料店Azuma里，7个座位。Sano师傅做了三十多年寿司，喜欢边做边讲每道菜。请客人别喷香水、少用手机。",
  "订位：现在只能在Azuma官网填等位表，有位了才发邮件，周六等得最久。周二到周六晚上6点半入座，旁边酒吧6点开。"),
 ("oe_7.webp", "Sushi Oe", "$350",
  "Oe师傅的寿司店，搬到新悉尼鱼市场后变成10个座位，一晚一场，大约30道，菜单每天跟着当天进的鱼变。",
  "订位：OpenTable上选SUSHI OMAKASE 10Seat。周二到周六晚上营业。"),
 ("taka_1.jpg", "Taka's Omakase", "$365",
  "Prefecture 48二楼，主厨Takashi Yamamoto做了二十多年烧肉、怀石和炉端烧。大约22道：A5和牛寿喜烧、北海道海胆、大腹、星鳗，最后是龙虾头味噌汤。",
  "订位：Prefecture 48官网，或发邮件到reservations@p48.com.au。"),
 ("yo_26.jpg", "Yoshii's Omakase", "$380",
  "Crown Sydney里的10座吧台，Ryuichi Yoshii师傅做了将近四十年寿司，十道omakase。周五周六分6点和8点45两场，周二到周四也开。",
  "订位：每月1号在官网放下个月的位，也可以打电话或发邮件。周六另收10%，12月24到31日涨到$500。"),
]
for i in range(0, len(V), 2):
    page(f"{i // 2 + 2:02d}.jpg", V[i], V[i + 1] if i + 1 < len(V) else None)

# 价格总览
ALL = [(n, p) for _, n, p, _, _ in V]
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
     ("bes_105869422.jpg", "Besuto", "$280"), ("kuon_1.jpg", "Kuon Omakase", "$280"), ("raita_0.jpg", "R by Raita Noda", "$290"),
     ("gs_3.jpg", "Green Shiso", "$298"), ("sokyo_1.jpg", "Sokyo", "$300"), ("sa_luxurious-otoro-nigiri-sushi.jpg", "Sano", "$300"),
     ("oe_7.webp", "Sushi Oe", "$350"), ("taka_1.jpg", "Taka's", "$365"), ("yo_26.jpg", "Yoshii's", "$380")]
CRM = (255, 244, 214); BRN = (38, 26, 16)
def fit(text, maxw, start, w="Black"):
    sz = start
    while zh(sz, w).getlength(text) > maxw and sz > 20: sz -= 2
    return zh(sz, w)
def outlined(d, xy, text, f, sw):
    d.text(xy, text, font=f, fill=CRM, stroke_width=sw, stroke_fill=BRN)
def wrap_words(text, f, maxw):
    lines, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if f.getlength(t) > maxw and cur: lines.append(cur); cur = w
        else: cur = t
    return lines + [cur]
def grid12(fn, big_top="price"):
    g = Image.new("RGB", (W, H), (240, 236, 228)); cw, ch = W // 3, H // 4; tw_ = cw - 3; th_ = ch - 3
    fprice = zh(118, "Black"); fname = zh(62, "Black") if big_top == "price" else zh(68, "Black")
    fsmall = zh(60, "Black")
    for i, (p, n, pr) in enumerate(G):
        t = crop(p, tw_, th_); d = ImageDraw.Draw(t)
        if big_top == "price":
            outlined(d, ((tw_ - fprice.getlength(pr)) / 2, 14), pr, fprice, 9)
            ls = wrap_words(n, fname, tw_ - 30); lh = fname.size + 6
            y = th_ - 30 - lh * len(ls)
            for ln in ls: outlined(d, ((tw_ - fname.getlength(ln)) / 2, y), ln, fname, 7); y += lh
        else:
            ls = wrap_words(n, fname, tw_ - 30); lh = fname.size + 8; y = 14
            for ln in ls: outlined(d, ((tw_ - fname.getlength(ln)) / 2, y), ln, fname, 8); y += lh
            outlined(d, ((tw_ - fsmall.getlength(pr)) / 2, th_ - 30 - fsmall.size - 6), pr, fsmall, 7)
        g.paste(t, ((i % 3) * cw + 1, (i // 3) * ch + 1))
    g.save(f"{OUT}/{fn}", quality=93)
grid12("cover_A.jpg", "price")
grid12("cover_B.jpg", "name")
print("ok")
