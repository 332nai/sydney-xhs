"""Lane Cove封面：上面10家店的招牌菜照片拼图，每张图标店名；下面深色标题条。"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"b": "NotoSansCJK-Bold.ttc", "k": "NotoSansCJK-Black.ttc"}[w], s, index=2)
P = "data/post_img/"
# 每行：[(图片, 店名, 焦点x, 焦点y)]
CELLS = [  # 9家店，每家只出现一次
    ("lh_tk_12.jpg", "Tashkent", .5, .5), ("lh_dp_04.jpg", "Dom Panino", .5, .5), ("lh_ap_05.jpg", "Aperitivo", .5, .5),
    ("lh_sb_09.jpg", "Sébastien", .5, .5), ("lh_lb_01.jpg", "La Botte D'Oro", .5, .5), ("lh_cp_08.jpg", "Capriccio", .5, .5),
    ("lh_sp_17.jpg", "Spicetown", .45, .55), ("lh_cc_02.jpg", "Creek & Cella", .5, .5), ("lh_ry_19.jpg", "The Royal", .5, .5),
]
ROWS = [CELLS[i:i + 3] for i in range(0, 9, 3)]
BAND, GAP = 290, 4
DARK = (24, 24, 26)
img = Image.new("RGB", (W, H), DARK)
d = ImageDraw.Draw(img)
rh = (H - BAND - GAP * (len(ROWS) - 1)) / len(ROWS)
fl = F("k", 46)
def fill(src, w, h, fx, fy):
    im = Image.open(P + src).convert("RGB")
    s = max(w / im.width, h / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    return im.crop((round(x), round(y), round(x) + w, round(y) + h))
y = 0
for row in ROWS:
    n = len(row); cw = (W - GAP * (n - 1)) / n; x = 0
    for src, name, fx, fy in row:
        w, h = round(cw), round(rh)
        tile = fill(src, w, h, fx, fy)
        # 底部渐暗，方便看清店名
        grad = Image.new("L", (1, h)); [grad.putpixel((0, i), int(max(0, (i - h * .5) / (h * .5)) * 170)) for i in range(h)]
        tile.paste(Image.new("RGB", (w, h), (0, 0, 0)), (0, 0), grad.resize((w, h)))
        img.paste(tile, (round(x), round(y)))
        fs_ = 56
        while F("k", fs_).getlength(name) > w - 26: fs_ -= 2
        fl = F("k", fs_)
        d.text((round(x) + 14, round(y) + h - 18 - fs_), name, font=fl, fill="white", stroke_width=3, stroke_fill=(0, 0, 0))
        x += cw + GAP
    y += rh + GAP
f1 = F("k", 100)
d.text((70, H - BAND + 30), "悉尼Leichhardt附近", font=f1, fill="white")
d.text((70, H - BAND + 152), "吃什么？", font=f1, fill=(255, 140, 60))
img.save(sys.argv[1] if len(sys.argv) > 1 else "lc_cover.png")
