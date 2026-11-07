"""悉尼房价帖：四个首页方案，每个都带老杨小图标（无圆框、无名字）。
用法：python3 tools/hp_covers.py 老杨图标目录 输出目录"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1440
ICONS, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
CREAM = (244, 239, 230); INK = (28, 33, 45); RED = (201, 90, 74); GREY = (200, 196, 188)

def zh(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def icon(img, pose, x, y, h):
    ic = Image.open(f"{ICONS}/{pose}.png").convert("RGBA")
    ic = ic.resize((round(ic.width * h / ic.height), h), Image.LANCZOS)
    img = img.convert("RGBA"); sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 255), (x + 4, y + 6), ic.split()[3].point(lambda v: int(v * .3)))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8))); img.alpha_composite(ic, (x, y))
    return img.convert("RGB")

# A：深色底，下行折线，大标题
a = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(a)
pts = [(0, 520), (160, 470), (300, 430), (430, 380), (560, 330), (640, 300), (720, 360), (820, 450), (930, 560), (1080, 700)]
for i in range(len(pts) - 1): d.line((pts[i], pts[i + 1]), fill=(60, 70, 88), width=10)
d.line(pts[5:], fill=RED, width=12, joint="curve")
d.ellipse((624, 284, 656, 316), fill=CREAM); d.text((600, 240), "2月高点", font=zh(32, "Bold"), fill=CREAM)
d.text((80, 780), "悉尼房价", font=zh(84), fill=CREAM)
d.text((80, 890), "跌回五年前", font=zh(150), fill=CREAM)
d.text((84, 1100), "比2021年10月还低", font=zh(44, "Medium"), fill=GREY)
icon(a, "01_看菜单", W - 330, H - 300, 250).save(f"{OUT}/cover_A.jpg", quality=93)

# B：米色底，超大“13万”
b = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(b)
d.text((80, 150), "悉尼房价跌回五年前", font=zh(72), fill=INK)
d.text((80, 260), "高点到现在，中位价少了", font=zh(46, "Medium"), fill=(90, 86, 80))
f = zh(360); d.text((50, 360), "13万", font=f, fill=RED)
d.line((80, 900, 1000, 900), fill=(214, 206, 192), width=4)
d.text((80, 940), "$1,311,412", font=zh(64, "Bold"), fill=(150, 146, 138))
d.line((80, 984, 80 + zh(64, "Bold").getlength("$1,311,412"), 984), fill=(150, 146, 138), width=6)
d.text((80, 1040), "$1,178,959", font=zh(96), fill=INK)
icon(b, "07_发朋友圈", W - 320, H - 310, 260).save(f"{OUT}/cover_B.jpg", quality=93)

# C：红底，年份倒退
c = Image.new("RGB", (W, H), RED); d = ImageDraw.Draw(c)
d.text((80, 140), "悉尼房价", font=zh(96), fill=CREAM)
d.text((80, 260), "跌回五年前", font=zh(140), fill=CREAM)
f = zh(250)
d.text((80, 560), "2026", font=f, fill=(235, 170, 158))
d.line((70, 720, 80 + f.getlength("2026") + 10, 720), fill=CREAM, width=14)
d.text((80, 840), "2021", font=f, fill=CREAM)
d.text((84, 1160), "中位价比2021年10月还低1.5%", font=zh(42, "Medium"), fill=CREAM)
icon(c, "13_探店", W - 300, 560, 250).save(f"{OUT}/cover_C.jpg", quality=93)

# D：深色底，标题压上方，下面一根根下降的柱子
dd = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(dd)
d.text((80, 120), "悉尼房价", font=zh(96), fill=CREAM)
d.text((80, 240), "跌回五年前", font=zh(150), fill=CREAM)
bars = [("2016", .877), ("2021", 1.197), ("2025", 1.301), ("高点", 1.311), ("现在", 1.179)]
base, bw, gap, x = 1300, 150, 42, 80
for lab, v in bars:
    h = v / 1.4 * 640; col = RED if lab == "现在" else (70, 82, 104)
    d.rectangle((x, base - h, x + bw, base), fill=col)
    t = f"${v:.2f}m"; ft = zh(36, "Bold"); d.text((x + bw / 2 - ft.getlength(t) / 2, base - h - 52), t, font=ft, fill=CREAM if col == RED else GREY)
    fl = zh(32, "Medium"); d.text((x + bw / 2 - fl.getlength(lab) / 2, base + 16), lab, font=fl, fill=GREY)
    x += bw + gap
d.text((84, 450), "悉尼住宅中位价（百万澳币）", font=zh(40, "Medium"), fill=GREY)
icon(dd, "03_等上菜", W - 300, 400, 230).save(f"{OUT}/cover_D.jpg", quality=93)
print("ok")
