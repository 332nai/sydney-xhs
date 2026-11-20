"""你最爱的悉尼咖啡店说明你是谁：四象限图。店名用文字排版，不用品牌标志。
用法：python3 tools/coffee_quadrant.py 输出目录"""
import sys, os, random
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1440; INK = (22, 22, 24)
def f(kind, s):
    p = {"sb": "NotoSansCJK-Black", "sm": "NotoSansCJK-Medium", "sl": "NotoSansCJK-Light", "rb": "NotoSerifCJK-Black", "rr": "NotoSerifCJK-Regular"}[kind]
    d = "/usr/share/fonts/opentype/noto/"; return ImageFont.truetype(d + p + ".ttc", s, index=2)

Q = {
 "tl": ["Single O", "Reuben Hills", "Toby's Estate", "Paramount Coffee Project", "Campos", "ONA Coffee", "Double Roasters", "Padre Coffee"],
 "tr": ["Only Coffee Project", "Beta Coffee", "Sample Coffee", "Mecca", "Skittle Lane", "Coffee Alchemy", "Primary", "Gypsy Espresso"],
 "bl": ["The Grounds of Alexandria", "bills", "Speedos Cafe", "The Boathouse", "Superfreak", "Promenade Bondi", "Harry's Bondi", "Sea Salt Clovelly"],
 "br": ["Starbucks", "Gloria Jean's", "Muffin Break", "% Arabica", "Black Star Pastry", "Bourke Street Bakery"],
}
STY = [("sb", False, 0), ("rb", False, 0), ("sl", True, 6), ("sm", True, 3), ("rr", True, 4), ("sb", True, 2)]

def wordmark(d, cx, cy, name, maxw, k):
    kind, upper, sp = STY[k % len(STY)]
    t = name.upper() if upper else name
    words = t.split(" "); lines = [t]
    if len(t) > 13 and len(words) > 1:
        mid = len(words) // 2 if len(words) > 2 else 1; lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    size = 54
    def width(fn, s): return max(sum(fn.getlength(c) + s for c in ln) - s for ln in lines)
    while size > 20 and width(f(kind, size), sp) > maxw: size -= 2
    fn = f(kind, size); lh = size * 1.12; y = cy - lh * len(lines) / 2
    for ln in lines:
        w = sum(fn.getlength(c) + sp for c in ln) - sp; x = cx - w / 2
        for c in ln: d.text((x, y), c, font=fn, fill=INK); x += fn.getlength(c) + sp
        y += lh

def make(fn, bg):
    img = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(img)
    t = "你最爱的悉尼咖啡店，说明你是谁"; ft = f("sb", 62); d.text(((W - ft.getlength(t)) / 2, 40), t, font=ft, fill=INK)
    s = "by 老杨的悉尼地图"; fs = f("sm", 28); d.text(((W - fs.getlength(s)) / 2, 122), s, font=fs, fill=(110, 110, 110))
    cx, cy = W // 2, 790; top, bot, l, r = 230, 1370, 40, W - 40
    d.line((cx, top, cx, bot), fill=INK, width=4); d.line((l, cy, r, cy), fill=INK, width=4)
    for (x, y, dx, dy) in ((cx, top, 0, 1), (cx, bot, 0, -1), (l, cy, 1, 0), (r, cy, -1, 0)):
        d.polygon([(x, y), (x + dx * 22 - dy * 12, y + dy * 22 - dx * 12), (x + dx * 22 + dy * 12, y + dy * 22 + dx * 12)], fill=INK)
    fa = f("sb", 34)
    def lab(t, x, y, anchor="mm"): d.text((x, y), t, font=fa, fill=INK, anchor=anchor)
    lab("咖啡懂王", cx, top - 28); lab("来拍照的", cx, bot + 30)
    lab("和朋友来", l + 4, cy + 34, "lm"); lab("一个人来", r - 4, cy + 34, "rm")
    boxes = {"tl": (l + 10, top + 30, cx - 20, cy - 50), "tr": (cx + 20, top + 30, r - 10, cy - 50),
             "bl": (l + 10, cy + 70, cx - 20, bot - 20), "br": (cx + 20, cy + 70, r - 10, bot - 20)}
    random.seed(4); k = 0
    for q, names in Q.items():
        x0, y0, x1, y1 = boxes[q]; rows = (len(names) + 1) // 2; rh = (y1 - y0) / rows; cw = (x1 - x0) / 2
        for i, n in enumerate(names):
            col = i % 2; row = i // 2; jx = random.uniform(-8, 8); jy = random.uniform(-10, 10)
            ccx = x0 + cw * col + cw / 2 + jx
            wordmark(d, ccx, y0 + rh * row + rh / 2 + jy, n, cw - 44, k); k += 1
    img.save(f"{OUT}/{fn}", quality=94)

make("coffee_white.jpg", (255, 255, 255)); make("coffee_cream.jpg", (247, 241, 228))
print("ok")

# ===== 精致版：统一视觉的原创色块，不模仿任何真标志；以及留空框模板 =====
PAL = {"tl": [(194, 92, 60), (226, 150, 100), (150, 70, 50)], "tr": [(30, 52, 92), (70, 100, 150), (20, 30, 50)],
       "bl": [(236, 140, 150), (246, 196, 160), (200, 100, 120)], "br": [(110, 150, 120), (170, 200, 160), (70, 110, 90)]}
def icon(d, kind, x, y, s, col):
    w = max(2, s // 10)
    if kind == 0:  # 杯子
        d.rounded_rectangle((x - s * .35, y - s * .3, x + s * .25, y + s * .35), radius=s * .08, outline=col, width=w)
        d.arc((x + s * .12, y - s * .15, x + s * .45, y + s * .18), 270, 90, fill=col, width=w)
        for k in (-.15, .05): d.arc((x + k * s - s * .08, y - s * .7, x + k * s + s * .08, y - s * .38), 90, 270, fill=col, width=w)
    elif kind == 1:  # 咖啡豆
        d.ellipse((x - s * .28, y - s * .4, x + s * .28, y + s * .4), outline=col, width=w)
        d.arc((x - s * .2, y - s * .4, x + s * .2, y + s * .4), 280, 80, fill=col, width=w)
    elif kind == 2:  # 手冲壶
        d.polygon([(x - s * .35, y - s * .3), (x + s * .35, y - s * .3), (x + s * .08, y + s * .1), (x - s * .08, y + s * .1)], outline=col, width=w)
        d.rounded_rectangle((x - s * .25, y + s * .12, x + s * .25, y + s * .42), radius=s * .1, outline=col, width=w)
    else:  # 星点
        for a in range(0, 360, 45):
            import math
            r = s * (.4 if a % 90 == 0 else .2); d.line((x, y, x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a))), fill=col, width=w)

def base(bg):
    img = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(img)
    t = "你最爱的悉尼咖啡店，说明你是谁"; ft = f("sb", 62); d.text(((W - ft.getlength(t)) / 2, 40), t, font=ft, fill=INK)
    s = "by 老杨的悉尼地图"; fs = f("sm", 28); d.text(((W - fs.getlength(s)) / 2, 122), s, font=fs, fill=(110, 110, 110))
    cx, cy = W // 2, 790; top, bot, l, r = 230, 1370, 40, W - 40
    d.line((cx, top, cx, bot), fill=INK, width=4); d.line((l, cy, r, cy), fill=INK, width=4)
    for (x, y, dx, dy) in ((cx, top, 0, 1), (cx, bot, 0, -1), (l, cy, 1, 0), (r, cy, -1, 0)):
        d.polygon([(x, y), (x + dx * 22 - dy * 12, y + dy * 22 - dx * 12), (x + dx * 22 + dy * 12, y + dy * 22 + dx * 12)], fill=INK)
    fa = f("sb", 34)
    d.text((cx, top - 28), "咖啡懂王", font=fa, fill=INK, anchor="mm"); d.text((cx, bot + 30), "来拍照的", font=fa, fill=INK, anchor="mm")
    d.text((l + 4, cy + 34), "和朋友来", font=fa, fill=INK, anchor="lm"); d.text((r - 4, cy + 34), "一个人来", font=fa, fill=INK, anchor="rm")
    boxes = {"tl": (l + 10, top + 30, cx - 20, cy - 50), "tr": (cx + 20, top + 30, r - 10, cy - 50),
             "bl": (l + 10, cy + 70, cx - 20, bot - 20), "br": (cx + 20, cy + 70, r - 10, bot - 20)}
    return img, d, boxes

def slots(boxes):
    for q, names in Q.items():
        x0, y0, x1, y1 = boxes[q]; rows = (len(names) + 1) // 2; rh = (y1 - y0) / rows; cw = (x1 - x0) / 2
        for i, n in enumerate(names):
            yield q, i, n, x0 + cw * (i % 2) + 10, y0 + rh * (i // 2) + 8, cw - 20, rh - 16

def make_badges(fn, bg=(250, 247, 240)):
    img, d, boxes = base(bg)
    for q, i, n, x, y, w, h in slots(boxes):
        col = PAL[q][i % 3]; light = sum(col) > 520; tc = INK if light else (255, 252, 244)
        d.rounded_rectangle((x, y, x + w, y + h), radius=22, fill=col)
        icon(d, i % 4, x + 36, y + h / 2, 42, tc)
        t = n.upper() if i % 2 else n; kind = "sb" if i % 3 != 1 else "rb"
        words = t.split(" "); lines = [t] if len(t) <= 8 or len(words) == 1 else [" ".join(words[:len(words) // 2]), " ".join(words[len(words) // 2:])]
        size = 40
        while size > 16 and max(f(kind, size).getlength(ln) for ln in lines) > w - 84: size -= 2
        fn_ = f(kind, size); lh = size * 1.15; yy = y + h / 2 - lh * len(lines) / 2
        for ln in lines: d.text((x + 70 + (w - 78 - fn_.getlength(ln)) / 2, yy), ln, font=fn_, fill=tc); yy += lh
    img.save(f"{OUT}/{fn}", quality=94)

def make_template(fn):
    img, d, boxes = base((255, 255, 255))
    for q, i, n, x, y, w, h in slots(boxes):
        bx = (x + 20, y, x + w - 20, y + h - 30)
        for k in range(int(bx[0]), int(bx[2]), 16): d.line((k, bx[1], k + 8, bx[1]), fill=(190, 190, 190), width=2); d.line((k, bx[3], k + 8, bx[3]), fill=(190, 190, 190), width=2)
        for k in range(int(bx[1]), int(bx[3]), 16): d.line((bx[0], k, bx[0], k + 8), fill=(190, 190, 190), width=2); d.line((bx[2], k, bx[2], k + 8), fill=(190, 190, 190), width=2)
        fs = f("sm", 20); d.text((x + w / 2, y + h - 12), n, font=fs, fill=(150, 150, 150), anchor="mm")
    img.save(f"{OUT}/{fn}", quality=94)

make_badges("coffee_badges.jpg"); make_template("coffee_template.png")
print("badges ok")
