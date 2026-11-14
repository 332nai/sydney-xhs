"""悉尼海景早午餐：人均 = 一份早午餐（菜单中位价）加一杯咖啡（统一按$6）。
每家一张卡：一张大海景，三张菜，两张环境。
用法：python3 tools/cafe_cards.py 图片目录 输出目录"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sydney_minimap import minimap, paste_map
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

# (店名, 人均, 标签, 结论, 介绍, 必点, 大图, [菜], [环境])
V = [
 ("Gusto on the Beach", "$23", "带狗来", "冲浪救生俱乐部楼上，坐在窗边看海，咖啡$5。",
  "South Curl Curl海滩边，一整排窗户正对大海，阳台上也能坐。可以带狗，本地人遛狗顺路来吃早餐。",
  "必点：牛油果吐司$18，红薯饼$17，蔬菜碗$20。",
  ("gusto/bs_17d411288dca52ecb5b2cba5ea4ddb9e.jpg", .5, .5),
  [("gusto2/to_103101399.jpg", .5, .5), ("gusto2/to_103101401.jpg", .5, .5), ("gusto2/flatwhite.jpg", .5, .5)],
  [("gusto/bs_2c27ef579a61450ab8a0a6d8a48d35b7.jpg", .5, .5), ("gusto2/to_103101400.jpg", .5, .5)]),
 ("Promenade Bondi", "$24", "看邦迪", "邦迪海滩正中间吃早餐，比旁边很多咖啡店还便宜。",
  "Bondi Pavilion里的海滩吧，红白遮阳伞对着整片沙滩。早餐只有周末早上7点到11点半，不订位，早点去占海边的桌子。",
  "必点：牛油果吐司$24，蘑菇吐司$27，培根蛋卷$16。",
  ("promenade/7a969f17cf.jpg", .5, .55),
  [("promenade/69fc4b779b.jpg", .5, .5), ("promenade/3eb5dc7e24.jpg", .5, .5)],
  [("promenade/0c7b0a4b9d.jpg", .5, .5), ("promenade/3a3388c3d4.jpg", .5, .5)]),
 ("Pilu Baretto", "$24", "冲浪看早餐", "Pilu楼下的小咖啡店，同一片海，早餐价钱。",
  "Freshwater海滩上，早上6点半开门，一边吃一边看冲浪的人。不订位，坐长凳就能看到整个海湾。咖啡只要$5。",
  "必点：鸡蛋意式培根卷$18，牛油果吐司$18，西葫芦吐司$20。",
  ("baretto/Baretto-Nights-outlook-scaled.jpg", .5, .5),
  [("baretto/Pilu_at_Freshwater_Andrea_Paez_October_2026-126.jpg", .5, .5), ("baretto/old_eggroll.jpg", .5, .5)],
  [("baretto/Baretto-Bench-scaled.jpg", .5, .5), ("baretto/Baretto-view-to-register-scaled.jpg", .5, .5)]),
 ("The Boathouse Balmoral", "$25", "东南亚早餐", "海景早餐里唯一能吃到炒饭和泰式蛋的，中国胃最喜欢。",
  "Balmoral海湾的老码头边，房子一半建在水上。早餐有泰式女婿蛋、炒饭和印度煎饼，也有西式大早餐，适合带爸妈。",
  "必点：泰式女婿蛋$16，炒饭$18，蟹肉蛋卷$32。",
  ("balm/372_venue-balmoral-beach.jpg", .5, .5),
  [("balm/2279_IMG_0702.jpg", .5, .5), ("balm/2276_IMG_0369.jpg", .5, .5), ("balm/2303_IMG_0249.jpg", .5, .5)],
  [("balm/2404_IMG_1761.jpg", .5, .5), ("balm/2454_IMG_1779.jpg", .5, .5)]),
 ("The Boathouse Shelly Beach", "$26", "坐在沙滩上", "桌子直接摆在沙滩上，悉尼最像度假的早餐。",
  "从Manly码头沿海边走15分钟，Shelly Beach是个安静的小海湾，水很清，能看到鱼。早餐7点到11点半，不订位，周末要排队。",
  "必点：蟹肉炒蛋$28，法式吐司$21，牛油果吐司$20。",
  ("shel3/277_5e03127827a7baa664fc98a56ca9ec3d.jpg", .5, .5),
  [("shel3/2559_IMG_0162.jpg", .5, .6), ("shel3/2607_20261004_FoH_Boatshed-Shelley-Beach_TomoO_High-100.jpg", .5, .5), ("shel3/2610_20261004_FoH_Boatshed-Shelley-Beach_TomoO_High-111.jpg", .5, .6)],
  [("shel3/2457_SB-Upper-Level-Seated-view-.jpg", .5, .5), ("shel3/1558_carousel-5.jpg", .5, .5)]),
 ("Sea Salt Clovelly", "", "最好拍", "绿白条纹遮阳伞对着Clovelly海湾，这几家里最好拍照。",
  "Clovelly海湾正对面，海水很平静，吃完可以下去浮潜。早餐8点到11点半，周末人很多。",
  "必点：昆士兰蟹肉蛋卷，松露炒蛋，牛油果吐司。",
  ("seasalt/0Y6A6332.jpg", .5, .5),
  [("seasalt/0Y6A6613.jpg", .5, .5), ("seasalt/0Y6A6381.jpg", .5, .45), ("seasalt/0Y6A6485.jpg", .5, .5)],
  [("seasalt/0Y6A6245.jpg", .5, .45), ("seasalt/0Y6A6306.jpg", .5, .5)]),
]
LOC = {"Dunes Kiosk": (-33.588, 151.323, "Palm Beach"), "Gusto on the Beach": (-33.773, 151.296, "South Curl Curl"),
       "Promenade Bondi": (-33.891, 151.278, "Bondi Beach"), "Pilu Baretto": (-33.780, 151.292, "Freshwater"),
       "The Boathouse Balmoral": (-33.826, 151.253, "Balmoral"), "The Boathouse Shelly Beach": (-33.800, 151.297, "Manly"),
       "Next Door": (-34.048, 151.157, "Cronulla"), "Bianchini's": (-34.040, 151.160, "Elouera"),
       "Sea Salt Clovelly": (-33.913, 151.267, "Clovelly")}
NAMES = [v[0] for v in V]; PR = {v[0]: v[1] for v in V}; TAG = {v[0]: v[2] for v in V}

def card(fn, v):
    name, price, tag, verdict, intro, order, hero, dishes, env = v
    img = Image.new("RGB", (W, H), CREAM); g = 4
    img.paste(crop(hero, W, 480), (0, 0)); y0 = 480 + g
    la, lo, lab = LOC[name]; img = paste_map(img, minimap(la, lo, lab, zh(30 if len(lab) > 12 else 34, "Black"), bounds=(-33.715, -33.95, 151.13, 151.34)), W - 250 - 26, 22)
    n = len(dishes); cw = (W - g * (n - 1)) // n
    for i, p in enumerate(dishes): img.paste(crop(p, cw, 300), (i * (cw + g), y0))
    y0 += 300 + g; cw = (W - g) // 2
    for i, p in enumerate(env): img.paste(crop(p, cw, 260), (i * (cw + g), y0))
    y = y0 + 260 + 20
    d = ImageDraw.Draw(img); fn_ = serif(52); fp = zh(46, "Black"); fv = zh(34, "Bold"); fi = zh(31); lh = 44
    d.text((60, y), name, font=fn_, fill=INK); t = "人均" + price
    if price: d.text((W - 60 - fp.getlength(t), y + 4), t, font=fp, fill=INK)
    y += 74
    for ln in wrap(verdict, fv, 960): d.text((62, y), ln, font=fv, fill=SEA); y += 48
    y += 4
    for ln in wrap(intro, fi, 960): d.text((62, y), ln, font=fi, fill=GREY); y += lh
    y += 6
    for ln in wrap(order, fi, 960): d.text((62, y), ln, font=fi, fill=INK); y += lh
    assert y < H - 8, (name, y)
    img.save(f"{OUT}/{fn}", quality=93)

for k, v in enumerate(V): card(f"{k + 2:02d}.jpg", v)

# 01 排行
img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
d.text((60, 64), "悉尼海景早午餐人均", font=serif(80), fill=INK)
d.text((62, 182), "一份早午餐加一杯咖啡，咖啡统一按$6算", font=zh(34), fill=GREY)
fn_ = zh(46, "Medium"); fp = zh(46, "Bold"); ft = zh(32, "Bold"); y = 300; lh = 170
for i, n in enumerate(NAMES):
    d.text((60, y), f"{i + 1}", font=fp, fill=GREY); d.text((120, y), n, font=fn_, fill=INK)
    d.text((122, y + 58), TAG[n], font=ft, fill=SEA)
    if not PR[n]: y += lh; continue
    pw = fp.getlength(PR[n]); x0 = 120 + fn_.getlength(n) + 20; x1 = W - 60 - pw - 20
    for xx in range(int(x0), int(x1), 14): d.ellipse((xx, y + 32, xx + 4, y + 36), fill=LINE)
    d.text((W - 60 - pw, y), PR[n], font=fp, fill=INK); y += lh
d.text((62, y + 20), "很多店周末和公众假期有附加费，大多不订位，早点去。", font=zh(32), fill=GREY)
img.save(f"{OUT}/01.jpg", quality=93)

# ===== 首页 =====
SHORT = {"The Boathouse Shelly Beach": "Boathouse", "The Boathouse Balmoral": "Boathouse", "Promenade Bondi": "Promenade", "Gusto on the Beach": "Gusto", "Sea Salt Clovelly": "Sea Salt"}
CP = {v[0]: v[6] for v in V}

def tile(n, w, h, ftag, fp, fname, tagy=18):
    t = crop(CP[n], w, h); d = ImageDraw.Draw(t)
    outlined(d, ((w - ftag.getlength(TAG[n])) / 2, tagy), TAG[n], ftag, max(5, ftag.size // 12))
    outlined(d, ((w - fp.getlength(PR[n])) / 2, h / 2 - fp.size / 2), PR[n], fp, 8)
    return blur_name(t, SHORT.get(n, n), fname, w / 2, h - fname.size - 34)

def cov_five(fn, top, sub, pick):
    img = Image.new("RGB", (W, H), (14, 26, 36)); d = ImageDraw.Draw(img)
    d.text((60, 36), top, font=zh(100, "Black"), fill=CRM)
    f2 = zh(64, "Black"); f3 = zh(88, "Black"); yy = 168
    d.text((60, yy + 15), sub[0], font=f2, fill=CRM); x = 60 + f2.getlength(sub[0]) + 16
    d.text((x, yy), sub[1], font=f3, fill=GOLD); x += f3.getlength(sub[1]) + 12
    d.text((x, yy + 15), sub[2], font=f2, fill=CRM)
    top_h = 300; hh = 470
    img.paste(tile(pick[0], W - 6, hh - 6, zh(72, "Black"), zh(120, "Black"), zh(50, "Black")), (3, top_h + 3))
    cw, ch = (W - 6) // 2, (H - top_h - hh - 6) // 2
    for i, n in enumerate(pick[1:]):
        img.paste(tile(n, cw - 6, ch - 6, zh(60, "Black"), zh(92, "Black"), zh(44, "Black")), (3 + (i % 2) * cw + 3, top_h + hh + (i // 2) * ch + 3))
    img.save(f"{OUT}/{fn}", quality=93)

def cov_four(fn, pick):
    img = Image.new("RGB", (W, H), (14, 26, 36)); cw, ch = W // 2, H // 2
    for i, n in enumerate(pick):
        img.paste(tile(n, cw - 4, ch - 4, zh(80, "Black"), zh(132, "Black"), zh(50, "Black"), tagy=30), ((i % 2) * cw + 2, (i // 2) * ch + 2))
    img.save(f"{OUT}/{fn}", quality=93)

cov_five("cover_A.jpg", "悉尼海景早午餐", ("人均", "$23", "起"), ["The Boathouse Shelly Beach", "Gusto on the Beach", "Promenade Bondi", "The Boathouse Balmoral", "Pilu Baretto"])
cov_five("cover_B.jpg", "悉尼看海吃早餐", ("人均", "$23", "起，坐沙滩上"), ["Promenade Bondi", "Pilu Baretto", "The Boathouse Shelly Beach", "The Boathouse Balmoral", "Gusto on the Beach"])
cov_four("cover_C.jpg", ["Promenade Bondi", "The Boathouse Shelly Beach", "The Boathouse Balmoral", "Pilu Baretto"])
print("ok")

# ===== 首页新风格 =====
import math, random
from sydney_minimap import COAST, HARBOUR, MIDDLE, BOTANY, CBD
BND = (-33.73, -33.94, 151.08, 151.42)

def cov_map(fn):
    """大卡通地图，6个照片气泡连到图钉"""
    img = Image.new("RGB", (W, H), (158, 212, 232)); d = ImageDraw.Draw(img)
    S = 2; big = Image.new("RGB", (W * S, H * S), (158, 212, 232)); bd = ImageDraw.Draw(big)
    la0, la1, lo0, lo1 = BND; top, bot = 300, H - 40
    def xy(la, lo, s=S):
        return ((lo - lo0) / (lo1 - lo0) * W * s, (top + (la - la0) / (la1 - la0) * (bot - top)) * s)
    land = (246, 232, 196); edge = (30, 52, 70); sea = (158, 212, 232)
    poly = [xy(la, lo) for la, lo in COAST]
    bd.polygon([(0, top * S - 400)] + poly + [(0, H * S + 400)], fill=land)
    for line, wd in ((HARBOUR, 26), (MIDDLE, 16)):
        bd.line([xy(*p) for p in line], fill=sea, width=wd * S, joint="curve")
    bd.polygon([xy(*p) for p in BOTANY], fill=sea)
    bd.line(poly, fill=edge, width=5 * S, joint="curve")
    for (la, lo) in ((-33.76, 151.325), (-33.86, 151.33), (-33.93, 151.32)):
        x, y = xy(la, lo)
        for k in range(3): bd.arc((x - 30 * S + k * 26 * S, y - 10 * S, x - 4 * S + k * 26 * S, y + 10 * S), 200, 340, fill=(255, 255, 255), width=5 * S)
    cx, cy = xy(*CBD)
    for i, r in enumerate((34, 25, 17)):
        ox = cx - 28 * S + i * 22 * S; r *= S
        bd.pieslice((ox - r, cy - r, ox + r, cy + r), 180, 270, fill=(255, 255, 255), outline=edge, width=4 * S)
    img = big.resize((W, H), Image.LANCZOS); d = ImageDraw.Draw(img)
    # 标题
    d.rectangle((0, 0, W, 285), fill=(14, 26, 36))
    d.text((60, 30), "悉尼海景早午餐", font=zh(104, "Black"), fill=CRM)
    f2 = zh(64, "Black"); f3 = zh(92, "Black")
    d.text((60, 182), "人均", font=f2, fill=CRM); x = 60 + f2.getlength("人均") + 16
    d.text((x, 166), "$23", font=f3, fill=GOLD); x += f3.getlength("$23") + 12
    d.text((x, 182), "起，坐着就能看海", font=f2, fill=CRM)
    # 气泡：名字, 气泡中心
    B = [("Gusto on the Beach", (915, 410)), ("Pilu Baretto", (330, 430)), ("The Boathouse Shelly Beach", (915, 700)),
         ("The Boathouse Balmoral", (250, 760)), ("Promenade Bondi", (915, 1010)), ("Sea Salt Clovelly", (300, 1200))]
    bs = 230; pins = []
    for n, (bx, by) in B:
        la, lo, _ = LOC[n]; px, py = xy(la, lo, 1); pins.append((px, py))
        for t in range(0, 100, 4):
            a = t / 100; b = (t + 2) / 100
            d.line((bx + (px - bx) * a, by + (py - by) * a, bx + (px - bx) * b, by + (py - by) * b), fill=edge, width=4)
    for n, (bx, by) in B:
        t = crop(CP[n], bs, bs); td = ImageDraw.Draw(t)
        ftag = zh(42, "Black"); outlined(td, ((bs - ftag.getlength(TAG[n])) / 2, 10), TAG[n], ftag, 5)
        if PR[n]:
            fp = zh(76, "Black"); outlined(td, ((bs - fp.getlength(PR[n])) / 2, bs / 2 - 36), PR[n], fp, 7)
        t = blur_name(t, SHORT.get(n, n), zh(30, "Black"), bs / 2, bs - 52)
        frame = Image.new("RGB", (bs + 16, bs + 16), "white"); frame.paste(t, (8, 8))
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((bx - bs / 2 + 4, by - bs / 2 + 10, bx + bs / 2 + 20, by + bs / 2 + 26), fill=(0, 0, 0, 90))
        img = Image.alpha_composite(img.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(10))).convert("RGB")
        img.paste(frame, (int(bx - bs / 2 - 8), int(by - bs / 2 - 8)))
    d = ImageDraw.Draw(img)
    for px, py in pins:
        r = 17; d.ellipse((px - r, py - 2.6 * r, px + r, py - 0.6 * r), fill=(226, 64, 52), outline="white", width=3)
        d.polygon([(px - .75 * r, py - 1.25 * r), (px + .75 * r, py - 1.25 * r), (px, py)], fill=(226, 64, 52))
        d.ellipse((px - 6, py - 1.98 * r, px + 6, py - 1.98 * r + 12), fill="white")
    img.save(f"{OUT}/{fn}", quality=93)

def cov_polaroid(fn):
    """沙色背景，拍立得照片散放，底部白边写标签和价格"""
    random.seed(7)
    img = Image.new("RGB", (W, H), (240, 230, 210)).convert("RGBA")
    nz = Image.effect_noise((W, H), 18).convert("L"); img = Image.blend(img, Image.merge("RGBA", (nz, nz, nz, Image.new("L", (W, H), 255))), .06)
    d = ImageDraw.Draw(img)
    d.text((60, 46), "悉尼海景早午餐", font=serif(108), fill=INK)
    f2 = zh(60, "Black"); f3 = zh(88, "Black")
    d.text((62, 196), "人均", font=f2, fill=INK); x = 62 + f2.getlength("人均") + 14
    d.text((x, 180), "$23", font=f3, fill=(214, 92, 50)); x += f3.getlength("$23") + 12
    d.text((x, 196), "起，坐着看海", font=f2, fill=INK)
    P = [("The Boathouse Shelly Beach", (40, 300), -4), ("Promenade Bondi", (560, 310), 4), ("The Boathouse Balmoral", (50, 850), 3),
         ("Gusto on the Beach", (565, 845), -3)]
    pw, ph = 440, 360
    for n, (x, y), ang in P:
        card = Image.new("RGBA", (pw + 40, ph + 150), (255, 255, 255, 255)); cd = ImageDraw.Draw(card)
        card.paste(crop(CP[n], pw, ph), (20, 20))
        ft = zh(52, "Black"); fp = zh(66, "Black")
        cd.text((26, ph + 46), TAG[n], font=ft, fill=INK)
        if PR[n]: cd.text((pw + 14 - fp.getlength(PR[n]), ph + 36), PR[n], font=fp, fill=(214, 92, 50))
        card = card.rotate(ang, resample=Image.BICUBIC, expand=True)
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); sh.paste((0, 0, 0, 80), (x + 10, y + 16), card.split()[3])
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(10))); img.alpha_composite(card, (x, y))
    img.convert("RGB").save(f"{OUT}/{fn}", quality=93)

def cov_full(fn):
    """一张满版海景，标题加六行标签价格"""
    img = crop(("shel3/277_5e03127827a7baa664fc98a56ca9ec3d.jpg", .45, .5), W, H).convert("RGBA")
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(H):
        a = int(max(0, (y - 520) / (H - 520)) * 150); gd.line((0, y, W, y), fill=(10, 30, 40, a))
    img = Image.alpha_composite(img, g); d = ImageDraw.Draw(img)
    outlined(d, (60, 70), "悉尼海景", zh(150, "Black"), 10); outlined(d, (60, 240), "早午餐", zh(150, "Black"), 10)
    outlined(d, (64, 420), "人均$23起", zh(90, "Black"), 8, fill=GOLD)
    y = 680; ft = zh(64, "Black"); fp = zh(72, "Black")
    for n in NAMES:
        outlined(d, (80, y), TAG[n], ft, 6)
        if PR[n]: outlined(d, (W - 80 - fp.getlength(PR[n]), y - 4), PR[n], fp, 6, fill=GOLD)
        y += 118
    img.convert("RGB").save(f"{OUT}/{fn}", quality=93)

cov_map("cover_D.jpg"); cov_polaroid("cover_E.jpg"); cov_full("cover_F.jpg")
print("new covers ok")
