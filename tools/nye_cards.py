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

def card(fn, name, price, intro, menu, photos):
    img = Image.new("RGB", (W, H), CREAM); cw, ch = W // 3, 400
    for i, p in enumerate(photos): img.paste(crop(p, cw + 1, ch), ((i % 3) * cw, (i // 3) * ch))
    d = ImageDraw.Draw(img)
    fn_ = serif(58) if re.search(r"[\u4e00-\u9fff]", name) else en(58)
    fp = zh(42, "Bold"); fi = zh(34); fl = zh(34, "Bold")
    il = wrap(intro, fi, 940); ml = wrap(menu, fi, 940) if menu else []
    block = 76 + len(il) * 52 + ((30 + 52 + len(ml) * 52) if ml else 0)
    y = 800 + (640 - block) // 2
    d.text((70, y), name, font=fn_, fill=INK)
    w = fn_.getlength(name); d.text((70 + w + 28, y + 10), price, font=fp, fill=GOLD)
    y += 76
    for ln in il: d.text((72, y), ln, font=fi, fill=(60, 56, 50)); y += 52
    if ml:
        y += 30; d.text((72, y), "菜单", font=fl, fill=GOLD); y += 52
        for ln in ml: d.text((72, y), ln, font=fi, fill=(60, 56, 50)); y += 52
    img.save(f"{OUT}/{fn}", quality=93)

V = [
 ("01.jpg", "BENNELONG", "$2,250到$3,250",
  "在歌剧院的帆形屋顶下面，窗外就是海港，晚上7点开始。吧台和长桌$2,250，主餐厅$2,750，楼上Dress Circle $3,250，能看到海港大桥。都含小食、四道菜和配酒，楼上是五道菜配更高级的酒，香槟到店和零点各一杯。订位要全额付款，12月15日之后取消不退。",
  None, ["bn_t105455397.jpg", "bn_b13.webp", "bn_t105455388.jpg", "bn_nye.jpg", "bn_t105455402.jpg", "bn_t105455385.jpg"]),
 ("02.jpg", "ALTITUDE", "$1,750到$2,500",
  "香格里拉酒店36楼，从高处看整个海港和零点烟花。晚上7点半开始入座，最长可以坐5小时。八道菜品鉴套餐，每道配酒。$1,750是普通座位，$2,500保证靠窗，正对歌剧院和海港大桥。",
  None, [("al_rk1.jpg", .5, .5), "al_wl0.jpg", "al_nye.jpg", ("al_rk2.jpg", .5, .5), "al_wl2.jpg", "al_wl1.jpg"]),
 ("03.jpg", "ARIA", "$1,950",
  "Circular Quay，正对歌剧院和海港大桥。晚上8点场，香槟到店和零点各一杯，六道菜配六款酒。同一家还有更便宜的选法：5点早场三道菜$350，9点开始的站立酒会$795。",
  "芦笋配水牛奶酪和鱼子酱、西澳黑马龙虾、乳鸽配樱桃、M9+和牛配牛尾、芒果香槟甜品、黑松露巧克力",
  ["ar_t105913818.jpg", "ar_b6.jpg", "ar_b8.jpg", "ar_b16.jpg", "ar_b1.jpg", "ar_b9.jpg"]),
 ("04.jpg", "WHALEBRIDGE", "$1,200到$1,500",
  "Circular Quay East，全露天，对着海港大桥和歌剧院，晚上6点半开始。香槟整晚无限量供应。$1,500是水边第一排，$1,200是海港景观座位。",
  "鱼子酱挞、生蚝虎虾扇贝拼盘、松露鹅肝肉冻，主菜烤珊瑚鳟和安格斯牛柳配薯条沙拉，最后是法国奶酪和朗姆酒蛋糕",
  ["wb25_mia.jpg", "wb25_v1.jpg", "wb25_menu.jpg", "wb25_v3.jpg", "wb25_bev.jpg", "wb26_s113.jpg"]),
 ("05.jpg", "SAILS", "$1,495",
  "Lavender Bay水边，就在海港大桥旁边。晚上7点只有一场，六道菜品鉴套餐，含整晚酒水。",
  "蛙蟹挞配鱼子酱、珊瑚鳟刺身、大虾扇贝卷配海胆、干式熟成鸭胸、M9+西冷配羊肚菌、黄桃香槟慕斯",
  ["sa_nye.jpg", "sa_nye3.jpg", "sa_g02.jpg", "sa_to2.jpg", "sa_h.jpg", "sa_nye2.jpg"]),
 ("06.jpg", "几百块的选择", "$295到$395",
  "同样在海港边，价格少一个零。Akti在Woolloomooloo码头，晚场$295含分享套餐和一杯香槟；Ripples在Chowder Bay，$335五道菜含酒水；Riva在Rose Bay，晚场$395五道菜。",
  "Akti：皮塔饼、和牛肉丸、红酒炖牛肉、小羊肩、希腊新年蛋糕。Ripples：生蚝、龙虾卷、炸鹌鹑、T骨牛排。Riva：蛙蟹配海胆、龙虾意面、罗西尼牛柳",
  ["ak_to0.jpg", "ak_nye.png", "rc_7.jpg", "rc_3.jpg", "rv_0.jpg", "rv_5.jpg"]),
]
for fn, name, price, intro, menu, ph in V: card(fn, name, price, intro, menu, ph)


# 首页：模仿手机里直接编辑的样子，不做精修排版
L1, L2 = "悉尼最贵的跨年晚餐", "一位要$3,250"
fc = zh(84, "Black")
# A：举杯对着海港大桥，白底黑字条（像在app里打字加的标签）
a = crop(("wb25_mia.jpg", .5, .5, 1.15), W, H); d = ImageDraw.Draw(a)
y = 170
for t in (L1, L2):
    w = fc.getlength(t); d.rectangle((60, y - 6, 60 + w + 40, y + 108), fill="white")
    d.text((80, y), t, font=fc, fill=INK); y += 128
icon(a, "01_看菜单", W - 250, H - 270, 210).save(f"{OUT}/cover_A.jpg", quality=93)
# B：四宫格，中间一个白框黑字（和账号以前的封面一个路子）
b = Image.new("RGB", (W, H)); cw, ch = W // 2, H // 2
for i, p in enumerate(["bn_t105455397.jpg", "al_nye.jpg", "wb25_v1.jpg", "ar_t105913818.jpg"]):
    b.paste(crop(p, cw, ch), ((i % 2) * cw, (i // 2) * ch))
d = ImageDraw.Draw(b); bw = max(fc.getlength(L1), fc.getlength(L2)) + 90
d.rectangle(((W - bw) / 2, ch - 140, (W + bw) / 2, ch + 140), fill=(250, 247, 240))
for i, t in enumerate((L1, L2)): d.text(((W - fc.getlength(t)) / 2, ch - 116 + i * 120), t, font=fc, fill=INK)
icon(b, "01_看菜单", 30, 30, 190).save(f"{OUT}/cover_B.jpg", quality=93)
# C：Bennelong跨年官方照，黄字黑描边
c = crop(("bn_nye.jpg", .5, .5), W, H); d = ImageDraw.Draw(c)
for i, t in enumerate((L1, L2)):
    d.text((70, 150 + i * 125), t, font=fc, fill=(255, 222, 60), stroke_width=7, stroke_fill=(20, 20, 20))
icon(c, "01_看菜单", W - 250, H - 270, 210).save(f"{OUT}/cover_C.jpg", quality=93)
print("ok")
