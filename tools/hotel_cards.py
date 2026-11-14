"""悉尼高端酒店一晚多少钱：深蓝金色版式。价格区间图、结论页、两家一页介绍、多个首页。
价格来自 tools/agoda_hotel_prices.py 抓的同一晚（2027年2月6日周六，两人一间，含税），美元按1.476换成澳元。
用法：python3 tools/hotel_cards.py 图片目录 输出目录"""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
W, H = 1080, 1440
SRC, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
NAVY = (16, 26, 42); NAVY2 = (26, 38, 58); GOLD = (201, 168, 106); IVORY = (244, 238, 226); MUTED = (150, 158, 174)
def zh(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def serif(s, w="Bold"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSerifCJK-{w}.ttc", s, index=2)

def crop(spec, w, h):
    spec = list(spec) if isinstance(spec, tuple) else [spec]
    name, fx, fy, z = spec + [.5, .5, 1.0][len(spec) - 1:]
    im = ImageOps.exif_transpose(Image.open(f"{SRC}/{name}")).convert("RGB")
    s = max(w / im.width, h / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    return ImageEnhance.Contrast(im.crop((round(x), round(y), round(x) + w, round(y) + h)).filter(ImageFilter.UnsharpMask(1.2, 25, 2))).enhance(1.04)

def wrap(text, font, width):
    toks = re.findall(r"[A-Za-z0-9&'.$,:]+|.", text); lines, cur = [], ""
    for t in toks:
        if font.getlength(cur + t) > width and cur and t not in "，。、！？）：；": lines.append(cur); cur = t.lstrip()
        else: cur += t
    if cur: lines.append(cur)
    return lines

# 名字, 标签, 入门房, 看景房(名称,价), 套房, 照片, 介绍, 一句话
HOTELS = [
 ("Kimpton Margot", "最便宜", 596, None, 805, ("ki1.jpg", .5, .55),
  "Pitt Street一栋1930年代的Art Deco老楼改的，大堂是挑高的中庭，屋顶有泳池。看不到海，但房间大，设计感强。",
  "$805就能住套房，是这12家里最便宜的套房。"),
 ("Sofitel Darling Harbour", "泳池", 684, ("达令港景", 951), 1339, ("so1.jpg", .5, .5),
  "达令港边上，高层的无边泳池正对港湾和城市天际线，是悉尼最上镜的酒店泳池之一。",
  "看达令港只比入门房多$267，泳池本身就值回票价。"),
 ("Four Seasons", "看海最值", 688, ("全海港景", 869), 1345, ("fs1.jpg", .5, .5),
  "环形码头旁边，高层房间一边是海港大桥，一边是歌剧院。酒店老，但位置和景色没得挑。",
  "$869的全海港景房，是悉尼看歌剧院最便宜的方式。"),
 ("QT Sydney", "最有个性", 690, None, 830, ("qt1.jpg", .5, .5),
  "藏在State Theatre所在的老楼里，房间是浓烈的复古风，红色、豹纹、皮革都敢用。",
  "不看海，要的是风格和CBD中心的位置。"),
 ("The Fullerton", "老邮局", 700, None, 1182, ("fu1.jpg", .5, .45),
  "Martin Place的老邮政总局，钟楼和砂岩立面是悉尼最有名的老建筑之一。大部分房间在后面的塔楼里，老楼里也有Heritage房。",
  "$973就能住含行政酒廊的房间，这个价位很少见。"),
 ("InterContinental Coogee", "海边", 778, ("海景", 901), 1292, ("co1.jpg", .5, .5),
  "Coogee海滩正对面，刚翻新改成InterContinental，泳池边是条纹遮阳伞，很有度假感。",
  "不想住城里就选它，海景只比入门房多$123。"),
 ("The Langham", "最英式", 917, ("海港景", 984), 1219, ("la1.jpg", .5, .5),
  "The Rocks的山坡上，水晶灯、线条墙板、古典家具，室内泳池顶上是星空灯。",
  "看海港只多$67，这12家里加价最少。"),
 ("W Sydney", "最潮", 927, ("达令港景", 1018), 1063, ("w1.jpg", .5, .5),
  "2023年开的新酒店，玻璃屋顶下的泳池带私人卡座，酒吧和餐厅都是年轻人的场子。",
  "套房只比入门房贵$136，想住大一点就直接订套房。"),
 ("Pullman Quay Grand", "带家人", 981, ("海港景", 1112), None, ("pu1.jpg", .5, .5),
  "环形码头东边，每一间都是带厨房和客厅的公寓，走路去歌剧院两分钟。",
  "带爸妈或小孩最方便，两房公寓$1452一晚。"),
 ("Crown Towers", "最高", 1154, ("海港景", 1222), 1969, ("cr1.jpg", .5, .5),
  "Barangaroo最高的那栋楼，落地窗直接看海港大桥，无边泳池正对着海港。",
  "看海港大桥只比入门房多$68，订就订景观房。"),
 ("Capella", "最有格调", 1355, None, 3124, ("ca1.jpg", .5, .5),
  "百年砂岩政府大楼改的，被叫做悉尼第一家六星酒店。服务细，房间安静，但看不到海。",
  "不看海的酒店里它最贵，你买的是建筑和服务。"),
 ("Park Hyatt", "最贵", 2421, ("歌剧院景", 3456), None, ("ph1.jpg", .5, .5),
  "环形码头对岸，歌剧院就在窗外。全酒店只有150多间房，是离歌剧院最近的酒店。",
  "入门就要$2421，看歌剧院的房间$3456，是Four Seasons的4倍。"),
]
SUB = "2027年2月6日周六一晚，两个人一间，含税"
SHORT = {"Sofitel Darling Harbour": "Sofitel达令港", "InterContinental Coogee": "Coogee洲际", "Pullman Quay Grand": "Pullman"}
def money(v): return f"${v:,}"

# ===== 01 价格区间图 =====
def chart():
    img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
    d.text((60, 56), "悉尼高端酒店一晚多少钱", font=serif(68), fill=IVORY)
    d.text((62, 150), SUB, font=zh(30), fill=MUTED)
    lx = 60; ly = 214; f = zh(28)
    for lab, kind in (("入门房", 0), ("看海看景", 1), ("套房", 2)):
        cx = lx + 14; cy = ly + 18
        if kind == 0: d.ellipse((cx - 11, cy - 11, cx + 11, cy + 11), fill=IVORY)
        elif kind == 1: d.ellipse((cx - 11, cy - 11, cx + 11, cy + 11), fill=GOLD)
        else: d.ellipse((cx - 11, cy - 11, cx + 11, cy + 11), outline=GOLD, width=4)
        d.text((lx + 36, ly), lab, font=f, fill=IVORY); lx += 36 + f.getlength(lab) + 48
    x0, x1 = 400, W - 150; v0, v1 = 500, 3500
    X = lambda v: x0 + (min(v, v1) - v0) / (v1 - v0) * (x1 - x0)
    top = 300; rh = (H - top - 90) // len(HOTELS)
    for v in (500, 1000, 1500, 2000, 2500, 3000, 3500):
        d.line((X(v), top - 10, X(v), top + rh * len(HOTELS)), fill=NAVY2, width=2)
        t = money(v); d.text((X(v) - zh(24).getlength(t) / 2, top + rh * len(HOTELS) + 10), t, font=zh(24), fill=MUTED)
    for i, (n, tag, a, view, suite, *_r) in enumerate(HOTELS):
        y = top + i * rh + rh // 2
        d.text((60, y - 22), SHORT.get(n, n), font=zh(32, "Bold"), fill=IVORY)
        vals = [a] + ([view[1]] if view else []) + ([suite] if suite else [])
        lo, hi = min(vals), max(vals)
        d.line((X(lo), y, X(hi), y), fill=GOLD, width=4)
        if suite: d.ellipse((X(suite) - 12, y - 12, X(suite) + 12, y + 12), fill=NAVY, outline=GOLD, width=4)
        if view: d.ellipse((X(view[1]) - 12, y - 12, X(view[1]) + 12, y + 12), fill=GOLD)
        d.ellipse((X(a) - 12, y - 12, X(a) + 12, y + 12), fill=IVORY)
        fl = zh(27, "Bold"); t = money(lo); d.text((X(lo) - fl.getlength(t) / 2, y - 50), t, font=fl, fill=IVORY)
        if hi != lo:
            t = money(hi); d.text((X(hi) + 20, y - 18), t, font=fl, fill=GOLD)
    img.save(f"{OUT}/01.jpg", quality=93)

# ===== 02 老杨结论 =====
def verdict():
    img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
    d.text((60, 56), "老杨的结论", font=serif(72), fill=IVORY)
    C = [("看歌剧院", "Four Seasons", "$869的全海港景房，同样的景在Park Hyatt要$3456。"),
         ("最便宜", "Kimpton Margot", "$596起，$805住套房，不看海的话性价比最高。"),
         ("海边度假", "InterContinental Coogee", "刚翻新，海景只加$123，不用挤在城里。"),
         ("带家人", "Pullman Quay Grand", "每间都是公寓，有厨房有客厅，走路去歌剧院。"),
         ("纪念日", "Park Hyatt", "贵是真的贵，但歌剧院就在窗外，一辈子住一次。"),
         ("最不值", "Capella", "不看海却卖到$1355起，除非你就是冲着这栋楼去。")]
    y = 200
    for tag, n, s in C:
        d.text((60, y), tag, font=zh(30, "Bold"), fill=GOLD)
        d.text((60, y + 44), n, font=serif(50), fill=IVORY); y += 116
        for ln in wrap(s, zh(32), 960): d.text((62, y), ln, font=zh(32), fill=MUTED); y += 48
        y += 30
        d.line((60, y - 16, W - 60, y - 16), fill=NAVY2, width=2)
    assert y < H, y
    img.save(f"{OUT}/02.jpg", quality=93)

# ===== 两家一页 =====
def chip(d, x, y, lab, val, on):
    fl = zh(24); fv = zh(40, "Black")
    w = max(fl.getlength(lab), fv.getlength(val)) + 40
    d.rounded_rectangle((x, y, x + w, y + 100), radius=12, fill=NAVY2 if on else NAVY, outline=GOLD if on else NAVY2, width=2)
    d.text((x + 20, y + 10), lab, font=fl, fill=MUTED); d.text((x + 20, y + 40), val, font=fv, fill=IVORY if on else MUTED)
    return x + w + 16
def half(img, y0, hh, h):
    n, tag, a, view, suite, photo, intro, line = h
    ph = 300; img.paste(crop(photo, W, ph), (0, y0)); d = ImageDraw.Draw(img)
    y = y0 + ph + 24
    d.text((60, y), n, font=serif(50), fill=IVORY); fs_ = zh(30, "Bold")
    d.text((W - 60 - fs_.getlength(tag), y + 14), tag, font=fs_, fill=GOLD)
    y += 80; x = 60
    x = chip(d, x, y, "入门房", money(a), True)
    if view: x = chip(d, x, y, view[0], money(view[1]), True)
    if suite: x = chip(d, x, y, "套房", money(suite), True)
    y += 122
    for ln in wrap(intro, zh(30), 960): d.text((62, y), ln, font=zh(30), fill=MUTED); y += 44
    y += 6
    for ln in wrap(line, zh(30, "Bold"), 960): d.text((62, y), ln, font=zh(30, "Bold"), fill=IVORY); y += 44
    assert y < y0 + hh - 6, (n, y - y0)
def pages():
    for i in range(0, 12, 2):
        img = Image.new("RGB", (W, H), NAVY)
        half(img, 0, 720, HOTELS[i]); half(img, 720, 720, HOTELS[i + 1])
        ImageDraw.Draw(img).rectangle((0, 718, W, 722), fill=GOLD)
        img.save(f"{OUT}/{i // 2 + 3:02d}.jpg", quality=93)

# ===== 首页 =====
CRM = (255, 246, 226); BRN = (20, 24, 34)
def outlined(d, xy, text, f, sw): d.text(xy, text, font=f, fill=CRM, stroke_width=sw, stroke_fill=BRN)
def blur_name(t, text, f, cx, y, r=8):
    lay = Image.new("RGBA", t.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); w = f.getlength(text); x = cx - w / 2
    d.rounded_rectangle((x - 16, y - 6, x + w + 16, y + f.size + 14), radius=10, fill=(0, 0, 0, 140))
    d.text((x, y), text, font=f, fill=(255, 255, 255, 255))
    box = (int(x - 22), int(y - 12), int(x + w + 22), int(y + f.size + 20))
    lay.paste(lay.crop(box).filter(ImageFilter.GaussianBlur(r)), box)
    b = t.convert("RGBA"); b.alpha_composite(lay); return b.convert("RGB")
BY = {h[0]: h for h in HOTELS}
def cover_grid(fn):
    pick = [("Four Seasons", "看歌剧院", 869), ("Park Hyatt", "最贵", 2421), ("Kimpton Margot", "最便宜", 596),
            ("InterContinental Coogee", "海边", 778), ("Crown Towers", "最高", 1154), ("Sofitel Darling Harbour", "泳池", 684)]
    img = Image.new("RGB", (W, H), NAVY); cw, ch = W // 2, H // 3
    for i, (n, tag, v) in enumerate(pick):
        t = crop(BY[n][5], cw - 4, ch - 4); d = ImageDraw.Draw(t); tw = cw - 4
        outlined(d, ((tw - zh(64, "Black").getlength(tag)) / 2, 24), tag, zh(64, "Black"), 7)
        p = money(v); fp = zh(120, "Black"); outlined(d, ((tw - fp.getlength(p)) / 2, ch / 2 - 70), p, fp, 10)
        t = blur_name(t, n, zh(36, "Black"), tw / 2, ch - 80)
        img.paste(t, ((i % 2) * cw + 2, (i // 2) * ch + 2))
    img.save(f"{OUT}/{fn}", quality=93)
def cover_hero(fn):
    img = Image.new("RGB", (W, H), NAVY); ph = 900
    img.paste(crop(("ph1.jpg", .55, .5), W, ph), (0, 0)); d = ImageDraw.Draw(img)
    d.text((60, ph + 50), "悉尼高端酒店", font=serif(104), fill=IVORY)
    d.text((60, ph + 190), "一晚多少钱", font=serif(104), fill=IVORY)
    f = zh(92, "Black"); s = "$596"; d.text((60, ph + 340), s, font=f, fill=GOLD)
    x = 60 + f.getlength(s) + 24; d.text((x, ph + 362), "到", font=zh(64, "Black"), fill=IVORY); x += zh(64, "Black").getlength("到") + 24
    d.text((x, ph + 340), "$3,456", font=f, fill=GOLD)
    img.save(f"{OUT}/{fn}", quality=93)
def cover_versus(fn):
    img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
    d.text((60, 50), "同样看歌剧院", font=serif(96), fill=IVORY); d.text((60, 180), "差了4倍", font=serif(96), fill=GOLD)
    hh = (H - 330) // 2
    for k, (n, v, ph) in enumerate([("Four Seasons", 869, ("fs1.jpg", .5, .5)), ("Park Hyatt", 3456, ("ph1.jpg", .55, .5))]):
        t = crop(ph, W, hh - 6); dd = ImageDraw.Draw(t); p = money(v); fp = zh(150, "Black")
        outlined(dd, (W - 60 - fp.getlength(p), hh - 230), p, fp, 11)
        t = blur_name(t, n, zh(44, "Black"), 200, hh - 90, r=9)
        img.paste(t, (0, 330 + k * hh + 3))
    img.save(f"{OUT}/{fn}", quality=93)

chart(); verdict(); pages(); cover_grid("cover_A.jpg"); cover_hero("cover_B.jpg"); cover_versus("cover_C.jpg")
print("ok")
