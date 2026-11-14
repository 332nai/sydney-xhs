"""悉尼海景早午餐：人均 = 一份早午餐（菜单中位价）加一杯咖啡（统一按$6）。
每家一张卡：一张大海景，三张菜，两张环境。
用法：python3 tools/cafe_cards.py 图片目录 输出目录"""
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

# (店名, 人均, 标签, 结论, 介绍, 必点, 大图, [菜], [环境])
V = [
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
 ("The Boathouse Shelly Beach", "$26", "坐在沙滩上", "桌子直接摆在沙滩上，悉尼最像度假的早餐。",
  "从Manly码头沿海边走15分钟，Shelly Beach是个安静的小海湾，水很清，能看到鱼。早餐7点到11点半，不订位，周末要排队。",
  "必点：蟹肉炒蛋$28，法式吐司$21，牛油果吐司$20。",
  ("shelly2/1559_Shelly-Beach_Beach-Shot.png", .5, .5),
  [("shelly2/1286_corporate-events-shelly-beach-5.png", .5, .5), ("shelly/bs_6db2dc9381f5853687f4bb9672b1214e.jpg", .5, .5), ("shelly/bs_107f209c09472ba6aa3ade5d82c1d46b.jpg", .5, .5)],
  [("shelly/bs_989ee41ccfc4697b70cff89099f25bfd.jpg", .5, .5), ("shelly/bs_732e6eaf2d60978ecfa4d9847c38aacb.jpg", .5, .5)]),
 ("Next Door", "$28", "坐火车到", "坐火车就能到的海景早午餐，菜单最全。",
  "Cronulla海滩边，早上6点半开门，窗外就是North Cronulla的沙滩。从早餐到午餐都有，带爸妈和小孩都好点。",
  "必点：班戟$27，辣炒蛋$26，墨西哥早餐卷$22。",
  ("nextdoor/0c00d19d77.jpg", .5, .5),
  [("nextdoor/16f7d2e880.jpg", .5, .5), ("nextdoor/34f453fe78.jpg", .5, .5), ("nextdoor/b2e484f72e.jpg", .5, .5)],
  [("nextdoor/f3f46dce11.jpg", .5, .5), ("nextdoor/5dfb54d369.jpg", .5, .4)]),
 ("Bianchini's", "$31", "落地窗", "一整排落地窗对着Elouera海滩，傍晚的光最好看。",
  "Cronulla旁边Elouera海滩上，人少很多，停车也容易。不订位，早餐一直供应到下午2点半。",
  "必点：日式松饼$26，土耳其鸡蛋$28，班尼迪克蛋$26。",
  ("bianchinis/27d4d6_62f57d7db6ad4f67903e0799da1bc9b2~mv2.jpeg", .5, .5),
  [("bianchinis/27d4d6_bd56545ecd234c988328d95312350c1c~mv2.jpg", .5, .5), ("bianchinis/27d4d6_f3db62337c4a444abf07c307c40e52eb~mv2.jpg", .5, .5), ("bianchinis/27d4d6_04be3b1f945c47d3857423b3c18e493a~mv2.jpeg", .5, .5)],
  [("bianchinis/27d4d6_c1b2dcf787a24839ac3084ce83825543~mv2.jpg", .5, .5), ("bianchinis/27d4d6_b5d6d4c148c748178834c660558b5af7~mv2.jpeg", .5, .5)]),
]
NAMES = [v[0] for v in V]; PR = {v[0]: v[1] for v in V}; TAG = {v[0]: v[2] for v in V}

def card(fn, v):
    name, price, tag, verdict, intro, order, hero, dishes, env = v
    img = Image.new("RGB", (W, H), CREAM); g = 4
    img.paste(crop(hero, W, 480), (0, 0)); y0 = 480 + g
    n = len(dishes); cw = (W - g * (n - 1)) // n
    for i, p in enumerate(dishes): img.paste(crop(p, cw, 300), (i * (cw + g), y0))
    y0 += 300 + g; cw = (W - g) // 2
    for i, p in enumerate(env): img.paste(crop(p, cw, 260), (i * (cw + g), y0))
    y = y0 + 260 + 20
    d = ImageDraw.Draw(img); fn_ = serif(52); fp = zh(46, "Black"); fv = zh(34, "Bold"); fi = zh(31); lh = 44
    d.text((60, y), name, font=fn_, fill=INK); t = "人均" + price
    d.text((W - 60 - fp.getlength(t), y + 4), t, font=fp, fill=INK); y += 74
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
fn_ = zh(46, "Medium"); fp = zh(46, "Bold"); ft = zh(32, "Bold"); y = 320; lh = 190
for i, n in enumerate(NAMES):
    d.text((60, y), f"{i + 1}", font=fp, fill=GREY); d.text((120, y), n, font=fn_, fill=INK)
    d.text((122, y + 66), TAG[n], font=ft, fill=SEA)
    pw = fp.getlength(PR[n]); x0 = 120 + fn_.getlength(n) + 20; x1 = W - 60 - pw - 20
    for xx in range(int(x0), int(x1), 14): d.ellipse((xx, y + 32, xx + 4, y + 36), fill=LINE)
    d.text((W - 60 - pw, y), PR[n], font=fp, fill=INK); y += lh
d.text((62, y + 20), "很多店周末和公众假期有附加费，大多不订位，早点去。", font=zh(32), fill=GREY)
img.save(f"{OUT}/01.jpg", quality=93)

# ===== 首页 =====
SHORT = {"The Boathouse Shelly Beach": "Boathouse", "Promenade Bondi": "Promenade"}
CP = {v[0]: v[6] for v in V}

def tile(n, w, h, ftag, fp, fname, tagy=18):
    t = crop(CP[n], w, h); d = ImageDraw.Draw(t)
    outlined(d, ((w - ftag.getlength(TAG[n])) / 2, tagy), TAG[n], ftag, max(5, ftag.size // 12))
    outlined(d, ((w - fp.getlength(PR[n])) / 2, h / 2 - fp.size / 2), PR[n], fp, 8)
    return blur_name(t, SHORT.get(n, n), fname, w / 2, h - fname.size - 34)

def cov_five(fn, top, sub):
    img = Image.new("RGB", (W, H), (14, 26, 36)); d = ImageDraw.Draw(img)
    d.text((60, 36), top, font=zh(100, "Black"), fill=CRM)
    f2 = zh(64, "Black"); f3 = zh(88, "Black"); yy = 168
    d.text((60, yy + 15), sub[0], font=f2, fill=CRM); x = 60 + f2.getlength(sub[0]) + 16
    d.text((x, yy), sub[1], font=f3, fill=GOLD); x += f3.getlength(sub[1]) + 12
    d.text((x, yy + 15), sub[2], font=f2, fill=CRM)
    top_h = 300; hh = 470
    img.paste(tile(NAMES[0], W - 6, hh - 6, zh(72, "Black"), zh(120, "Black"), zh(50, "Black")), (3, top_h + 3))
    cw, ch = (W - 6) // 2, (H - top_h - hh - 6) // 2
    for i, n in enumerate(NAMES[1:]):
        img.paste(tile(n, cw - 6, ch - 6, zh(60, "Black"), zh(92, "Black"), zh(44, "Black")), (3 + (i % 2) * cw + 3, top_h + hh + (i // 2) * ch + 3))
    img.save(f"{OUT}/{fn}", quality=93)

def cov_four(fn, pick):
    img = Image.new("RGB", (W, H), (14, 26, 36)); cw, ch = W // 2, H // 2
    for i, n in enumerate(pick):
        img.paste(tile(n, cw - 4, ch - 4, zh(80, "Black"), zh(132, "Black"), zh(50, "Black"), tagy=30), ((i % 2) * cw + 2, (i // 2) * ch + 2))
    img.save(f"{OUT}/{fn}", quality=93)

cov_five("cover_A.jpg", "悉尼海景早午餐", ("人均", "$24", "起"))
cov_five("cover_B.jpg", "悉尼看海吃早餐", ("人均", "$24", "起，坐沙滩上"))
cov_four("cover_C.jpg", ["Promenade Bondi", "The Boathouse Shelly Beach", "Pilu Baretto", "Bianchini's"])
print("ok")
