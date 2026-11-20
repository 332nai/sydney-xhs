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
