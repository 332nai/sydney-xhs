"""悉尼周边一小时内的一线海景餐厅，人均从低到高：首页多选项、排行、结论、介绍。
人均 = 一个前菜加一个主菜（取菜单中位价），不算饮料；只有套餐的按套餐。
用法：python3 tools/beach_cards.py 图片目录 输出目录"""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
Image.MAX_IMAGE_PIXELS = None
W, H = 1080, 1440
SRC, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
CREAM = (246, 244, 238); INK = (18, 32, 46); GREY = (70, 76, 82); LINE = (204, 210, 212); SEA = (22, 92, 120)
CRM = (255, 244, 214); BRN = (20, 34, 44); GOLD = (255, 200, 70)
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

def wrap(text, font, width):
    toks = re.findall(r"[A-Za-z0-9&'.$,:]+|.", text); lines, cur = [], ""
    for t in toks:
        if font.getlength(cur + t) > width and cur and t not in "，。、！？）：；": lines.append(cur); cur = t.lstrip()
        else: cur += t
    if cur: lines.append(cur)
    return lines

def outlined(d, xy, text, f, sw, fill=CRM):
    d.text(xy, text, font=f, fill=fill, stroke_width=sw, stroke_fill=BRN)

def blur_name(t, text, f, cx, y, r=6.5):
    """店名写上再糊掉：看得出是店名，认不出是哪家"""
    lay = Image.new("RGBA", t.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    w = f.getlength(text); x = cx - w / 2
    d.text((x, y), text, font=f, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 200))
    box = (int(x - 24), int(y - 14), int(x + w + 24), int(y + f.size + 24))
    reg = lay.crop(box).filter(ImageFilter.GaussianBlur(r)); lay.paste(reg, box)
    base = t.convert("RGBA"); base.alpha_composite(lay); return base.convert("RGB")

# (店名, 人均, 标签, 结论, 介绍, 怎么点, 照片[菜, 景])
V = [
 ("North Bondi RSL", "$46", "最划算", "全悉尼最便宜的邦迪海景，和Icebergs看的是同一片海。",
  "邦迪海滩北头的退伍军人俱乐部，露台正对整个海湾。不是会员也能进，门口登记一下证件就行。在吧台点餐，自己找位子。",
  "怎么点：炸鱼薯条$28，椒盐鱿鱼$20，下午去坐露台。",
  [("rsl/s_492365243_1502904180693855_6526830898225430598_n.jpg", .5, .45), ("rsl/s_Nth_Bondi_RSL_Interiors_0271_paul.jpg", .5, .5)]),
 ("Scarborough Hotel", "$46", "自驾一日游", "开车一小时，悬崖上的大草坪对着太平洋。",
  "Wollongong北边的老酒店，就在海边悬崖上，离Sea Cliff Bridge几分钟车程。草坪上摆满遮阳伞，扫码点餐，带小孩和老人都方便。",
  "怎么点：炸鱼薯条$30，海鲜篮$36，顺路去Sea Cliff Bridge拍照。",
  [("scar/s_20251203-scarborough+hotel+030_1.jpg", .5, .5), ("scar/a_1780907752595.jpg", .5, .45)]),
 ("Bobbys", "$62", "坐火车到", "坐火车就能到的沙滩海景，海鲜做得比价格好。",
  "Cronulla海滩边，整面落地窗，窗外就是冲浪的人。地中海风格的海鲜，意面和烤虾都不错，周末午餐最热闹。",
  "怎么点：大虾墨鱼宽面$34，整条鲷鱼$48两个人分。",
  [("bobbys/s_G8oqEJXsouGkOqEaUhDGjFSs.png", .5, .55), ("bobbys/s_GesUDh3esVPeiX36SM3XPNtE4c.jpg", .5, .5)]),
 ("Rick Stein", "$90", "最不值", "名气最大，但炸鱼薯条$45，海景只看得到一角。",
  "英国名厨Rick Stein去年底在Coogee开的店，在InterContinental一楼，隔一条马路是Coogee海滩。室内座位多，想看海要坐户外露台。",
  "怎么点：新加坡辣椒蟹$63是招牌，炸鱼薯条$45。",
  [("rick/to_106349876.jpg", .5, .5), ("rick/to_106335075.jpg", .5, .5)]),
 ("Pilu", "$99", "约会", "真正建在沙滩上的餐厅，约会最合适。",
  "Freshwater海滩上的一栋白色老房子，三面都是窗，下面就是沙滩和冲浪的人。主厨Giovanni Pilu做撒丁岛菜，招牌是烤乳猪。",
  "怎么点：金枪鱼$45，烤乳猪$75。周末要点三道菜。",
  [("pilu/s_7-Pilu-at-Freshwater-139-scaled.jpg", .5, .5), ("pilu/s_IMG001-scaled.jpg", .5, .5)]),
 ("Sean's", "$140", "本地人的店", "开了三十多年的邦迪老店，本地人庆祝都来这里。",
  "North Bondi街角的小餐厅，只有45个座位，墙上挂满画和贝壳。菜单每天换，三道菜$140，每道有三个选择。",
  "怎么点：三道菜$140，提早订窗边的位子。",
  [("seans/to_106155434.jpg", .5, .5), ("seans/to_106155430.jpg", .55, .5)]),
 ("Jonah's", "$145", "看鲸鱼", "每张桌子都对着太平洋，冬天和春天能看到鲸鱼。",
  "Whale Beach的悬崖顶上，开车一小时，也可以从Rose Bay坐水上飞机过去。餐厅是一整排落地窗，下面是整片海滩和海岬。晚餐三道菜$145，海鲜塔两个人$295。",
  "怎么点：三道菜$145，6月到11月去，带上望远镜看鲸鱼。",
  [("jonahs/s_mo_main.jpg", .5, .45), ("jonahs/s_IMG_3574-Copy-scaled.jpg", .5, .5)]),
]
NAMES = [v[0] for v in V]; PR = {v[0]: v[1] for v in V}; TAG = {v[0]: v[2] for v in V}

def half(img, y0, hh, v, ph=300):
    name, price, tag, verdict, intro, order, pics = v
    pw = W // 2
    img.paste(crop(pics[0], pw - 2, ph), (0, y0)); img.paste(crop(pics[1], pw - 2, ph), (pw + 2, y0))
    d = ImageDraw.Draw(img); fn_ = serif(54); fp = zh(46, "Black"); fv = zh(36, "Bold"); fi = zh(32); lh = 46
    y = y0 + ph + 22
    d.text((60, y), name, font=fn_, fill=INK); t = "人均" + price
    d.text((W - 60 - fp.getlength(t), y + 4), t, font=fp, fill=INK)
    y += 78
    for ln in wrap(verdict, fv, 960): d.text((62, y), ln, font=fv, fill=SEA); y += 52
    y += 4
    for ln in wrap(intro, fi, 960): d.text((62, y), ln, font=fi, fill=GREY); y += lh
    y += 6
    for ln in wrap(order, fi, 960): d.text((62, y), ln, font=fi, fill=INK); y += lh
    assert y < y0 + hh - 6, (name, y - y0)

# 每家一张卡：第一张是大图海景，其余至少三张环境图
PICS = {
 "North Bondi RSL": [("rsl/s_Nth_Bondi_RSL_Interiors_0271_paul.jpg", .5, .5), ("rsl/s_Nth_Bondi_RSL_Interiors_0121_paul-scaled.jpg", .5, .5),
                     ("rsl/s_DAE460DF-DC77-4A3C-A6AB-C99EA14272DF_1_201_a-scaled.jpeg", .5, .5), ("rsl/s_Nth_Bondi_RSL_Interiors_0251_paul-scaled.jpg", .5, .5),
                     ("rsl/s_492365243_1502904180693855_6526830898225430598_n.jpg", .5, .45)],
 "Scarborough Hotel": [("scar/a_1780907752595.jpg", .3, .35, 1.2), ("scar2/0c0217b4.jpg", .5, .25), ("scar2/9306a803.jpg", .5, .5),
                       ("scar/a_1781251328494.jpg", .5, .35), ("scar/s_20251203-scarborough+hotel+030_1.jpg", .5, .5)],
 "Bobbys": [("bobbys3/98bfed635fcc8b9b5dea6110b82c8a65.webp", .5, .5), ("bobbys3/2b2b88919bc786d73bf4016398456abc.webp", .5, .5),
            ("bobbys3/915f0cbd2201b3c46099fb4230ac1d19.webp", .5, .5), ("bobbys/s_GesUDh3esVPeiX36SM3XPNtE4c.jpg", .5, .5),
            ("bobbys3/5f3be81e0b7fb602c14e9bdfa79d0530.webp", .5, .5)],
 "Rick Stein": [("rick/to_106335075.jpg", .5, .45), ("rick2/cp_10-1.jpg", .5, .5), ("rick2/cp_11-2.jpg", .5, .5),
                ("rick2/cp_14.jpg", .5, .5), ("rick/to_106349876.jpg", .5, .5)],
 "Pilu": [("pilu/s_IMG001-scaled.jpg", .5, .5), ("pilu/s_7-Pilu-at-Freshwater-173-scaled.jpg", .5, .5), ("pilu/s_WH0004-scaled.jpg", .5, .5),
          ("pilu/s_dn3ulNkA-scaled.jpg", .5, .5), ("pilu/s_7-Pilu-at-Freshwater-139-scaled.jpg", .5, .5)],
 "Sean's": [("seans2/f1d5f6188bf147588c16143ffc2b2e6c.webp", .5, .5), ("seans2/f4b7826c6597b35667d1aa19cd1845f7.webp", .5, .5),
            ("seans2/fda023f0cae7ffd8037057cad46805ed.webp", .5, .5), ("seans/to_106155430.jpg", .55, .5),
            ("seans/to_106155434.jpg", .5, .5)],
 "Jonah's": [("jonahs/s_mo_main.jpg", .5, .3), ("jonahs/s_Header-V2-scaled.jpg", .55, .8, 1.5), ("jonahs/s_IMG_3574-Copy-scaled.jpg", .5, .5),
             ("jonahs/s_CN_PRINT_407-scaled.jpg", .5, .5)],
}

def card(fn, v):
    name, price, tag, verdict, intro, order, _ = v
    img = Image.new("RGB", (W, H), CREAM); ps = PICS[name]; g = 4
    hh = 580; img.paste(crop(ps[0], W, hh), (0, 0)); rest = ps[1:]; y0 = hh + g
    if len(rest) == 4:
        cw, ch = (W - g) // 2, 270
        for i, p in enumerate(rest): img.paste(crop(p, cw, ch), ((i % 2) * (cw + g), y0 + (i // 2) * (ch + g)))
        y = y0 + 2 * ch + g
    else:
        n = len(rest); cw, ch = (W - g * (n - 1)) // n, 480
        for i, p in enumerate(rest): img.paste(crop(p, cw, ch), (i * (cw + g), y0))
        y = y0 + ch
    d = ImageDraw.Draw(img); fn_ = serif(54); fp = zh(46, "Black"); fv = zh(34, "Bold"); fi = zh(31); lh = 44
    y += 20
    d.text((60, y), name, font=fn_, fill=INK); t = "人均" + price
    d.text((W - 60 - fp.getlength(t), y + 4), t, font=fp, fill=INK); y += 76
    for ln in wrap(verdict, fv, 960): d.text((62, y), ln, font=fv, fill=SEA); y += 50
    y += 4
    for ln in wrap(intro, fi, 960): d.text((62, y), ln, font=fi, fill=GREY); y += lh
    y += 6
    for ln in wrap(order, fi, 960): d.text((62, y), ln, font=fi, fill=INK); y += lh
    assert y < H - 10, (name, y)
    img.save(f"{OUT}/{fn}", quality=93)

for k, v in enumerate(V): card(f"{k + 3:02d}.jpg", v)

# 01 排行
img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
d.text((60, 64), "悉尼一线海景餐厅人均", font=serif(80), fill=INK)
d.text((62, 182), "开车一小时内，一个前菜加一个主菜，不算饮料", font=zh(34), fill=GREY)
fn_ = zh(46, "Medium"); fp = zh(46, "Bold"); ft = zh(32, "Bold"); y = 300; lh = (H - 360) // 7
for i, n in enumerate(NAMES):
    d.text((60, y), f"{i + 1}", font=fp, fill=GREY); d.text((120, y), n, font=fn_, fill=INK)
    d.text((122, y + 64), TAG[n], font=ft, fill=SEA)
    pw = fp.getlength(PR[n]); x0 = 120 + fn_.getlength(n) + 20; x1 = W - 60 - pw - 20
    for xx in range(int(x0), int(x1), 14): d.ellipse((xx, y + 32, xx + 4, y + 36), fill=LINE)
    d.text((W - 60 - pw, y), PR[n], font=fp, fill=INK); y += lh
img.save(f"{OUT}/01.jpg", quality=93)

# 02 老杨的结论
img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
d.text((60, 64), "老杨的结论", font=serif(84), fill=INK)
C = [("最划算", "North Bondi RSL", "$46看邦迪，和Icebergs同一片海，差价能再吃三顿。"),
     ("自驾", "Scarborough Hotel", "开车一小时，悬崖草坪对着太平洋，顺路去Sea Cliff Bridge。"),
     ("约会", "Pilu", "整栋房子建在沙滩上，窗外就是Freshwater的浪。"),
     ("看鲸鱼", "Jonah's", "6月到11月坐窗边，带上望远镜真能看到鲸鱼。"),
     ("最不值", "Rick Stein", "炸鱼薯条$45，比RSL贵一半，海景还没它好。")]
y = 220; f1 = zh(36, "Bold")
for tag, n, s_ in C:
    d.text((60, y + 10), tag, font=f1, fill=SEA)
    d.text((60 + f1.getlength(tag) + 28, y), n, font=serif(52), fill=INK); y += 82
    for ln in wrap(s_, zh(34), 960): d.text((62, y), ln, font=zh(34), fill=GREY); y += 50
    y += 40
assert y < H, y
img.save(f"{OUT}/02.jpg", quality=93)

# ===== 首页 =====
CT = dict(TAG)
CP = {"North Bondi RSL": ("rsl/s_492365243_1502904180693855_6526830898225430598_n.jpg", .5, .45),
      "Scarborough Hotel": ("scar/a_1780907752595.jpg", .3, .3, 1.25),
      "Bobbys": ("bobbys/s_GesUDh3esVPeiX36SM3XPNtE4c.jpg", .5, .5),
      "Rick Stein": ("rick/to_106349876.jpg", .5, .5),
      "Pilu": ("pilu/s_IMG001-scaled.jpg", .5, .5),
      "Sean's": ("seans/to_106155430.jpg", .55, .5),
      "Jonah's": ("jonahs/s_mo_main.jpg", .5, .4)}
SHORT = {"North Bondi RSL": "North Bondi", "Scarborough Hotel": "Scarborough"}

def title(d, top, y=40):
    f1 = zh(100, "Black"); f2 = zh(64, "Black"); f3 = zh(88, "Black")
    d.text((60, y), top, font=f1, fill=CRM)
    yy = y + 135; d.text((60, yy + 15), "人均", font=f2, fill=CRM); x = 60 + f2.getlength("人均") + 16
    d.text((x, yy), "$46", font=f3, fill=GOLD); x += f3.getlength("$46") + 16
    d.text((x, yy + 15), "到", font=f2, fill=CRM); x += f2.getlength("到") + 16
    d.text((x, yy), "$145", font=f3, fill=GOLD)

def tile(n, w, h, ftag, fp, fname, tagy=18):
    t = crop(CP[n], w, h); d = ImageDraw.Draw(t)
    outlined(d, ((w - ftag.getlength(CT[n])) / 2, tagy), CT[n], ftag, max(5, ftag.size // 12))
    outlined(d, ((w - fp.getlength(PR[n])) / 2, h / 2 - fp.size / 2), PR[n], fp, 8)
    return blur_name(t, SHORT.get(n, n), fname, w / 2, h - fname.size - 34)

def cov_hero(fn, pick, top):
    img = Image.new("RGB", (W, H), (14, 26, 36)); d = ImageDraw.Draw(img); title(d, top)
    cw, ch = (W - 6) // 2, (H - 300 - 6) // 3
    for i, n in enumerate(pick):
        t = tile(n, cw - 6, ch - 6, zh(64, "Black"), zh(96, "Black"), zh(46, "Black"))
        img.paste(t, (3 + (i % 2) * cw + 3, 300 + (i // 2) * ch + 3))
    img.save(f"{OUT}/{fn}", quality=93)

def cov_four(fn, pick):
    img = Image.new("RGB", (W, H), (14, 26, 36)); cw, ch = W // 2, H // 2
    for i, n in enumerate(pick):
        t = tile(n, cw - 4, ch - 4, zh(84, "Black"), zh(132, "Black"), zh(50, "Black"), tagy=30)
        img.paste(t, ((i % 2) * cw + 2, (i // 2) * ch + 2))
    img.save(f"{OUT}/{fn}", quality=93)

def cov_versus(fn):
    img = Image.new("RGB", (W, H), (14, 26, 36)); d = ImageDraw.Draw(img); hh = (H - 260) // 2
    f1 = zh(84, "Black"); d.text((60, 50), "同样看海吃炸鱼薯条", font=f1, fill=CRM); d.text((60, 150), "$28和$45差在哪", font=f1, fill=GOLD)
    for k, (n, spec, p) in enumerate([("North Bondi", ("rsl/s_Nth_Bondi_RSL_Interiors_0271_paul.jpg", .5, .5), "$28"),
                                      ("Rick Stein", ("rick/to_106349877.jpg", .5, .5), "$45")]):
        t = crop(spec, W, hh - 6); dd = ImageDraw.Draw(t); fb = zh(170, "Black")
        outlined(dd, (W - 60 - fb.getlength(p), hh - 250), p, fb, 11)
        t = blur_name(t, n, zh(50, "Black"), 220, hh - 90)
        img.paste(t, (0, 260 + k * hh + 3))
    img.save(f"{OUT}/{fn}", quality=93)

cov_hero("cover_A.jpg", ["North Bondi RSL", "Scarborough Hotel", "Bobbys", "Pilu", "Sean's", "Jonah's"], "悉尼一线海景餐厅")
cov_hero("cover_B.jpg", ["North Bondi RSL", "Scarborough Hotel", "Pilu", "Rick Stein", "Sean's", "Jonah's"], "悉尼一小时海景")
cov_four("cover_C.jpg", ["North Bondi RSL", "Pilu", "Scarborough Hotel", "Jonah's"])
cov_versus("cover_D.jpg")
print("ok")
