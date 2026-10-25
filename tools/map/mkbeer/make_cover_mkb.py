"""Lane Cove封面：上面10家店的招牌菜照片拼图，每张图标店名；下面深色标题条。"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"b": "NotoSansCJK-Bold.ttc", "k": "NotoSansCJK-Black.ttc"}[w], s, index=2)
P = "data/post_img/"
# 每行：[(图片, 店名, 焦点x, 焦点y)]
CELLS = [  # 16家店，每家只出现一次
    ("mb_bh_05.jpg", "Bob Hawke", .5, .5), ("mb_es_08.jpg", "Ester", .5, .5), ("mb_gr_14.jpg", "Grifter", .45, .5), ("mb_ph_11.jpg", "Philter", .4, .5),
    ("mb_ug_06.jpg", "Unexpected Guest", .3, .5), ("mb_sc_01.jpg", "Sauce", .5, .6), ("mb_w3_02.jpg", "We Three", .55, .5), ("mb_mx_02.jpg", "Mixtape", .5, .5),
    ("mb_tj_08.jpg", "Titus Jones", .5, .6), ("mb_kk_05.jpg", "Kicks", .5, .5), ("mb_ms_06.jpg", "Moonshiner", .5, .6), ("mb_hn_08.jpg", "Heaps Normal", .5, .5),
    ("mb_mh_08.jpg", "Marrickville Hotel", .5, .5), ("mb_bt_09.jpg", "Batch", .6, .5), ("mb_gp_08.jpg", "Gasoline Pony", .5, .5), ("mb_wn_02.jpg", "Where's Nick", .5, .6),
]
ROWS = [CELLS[i:i + 4] for i in range(0, 16, 4)]
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
        fs_ = 46
        while F("k", fs_).getlength(name) > w - 26: fs_ -= 2
        fl = F("k", fs_)
        d.text((round(x) + 14, round(y) + h - 18 - fs_), name, font=fl, fill="white", stroke_width=3, stroke_fill=(0, 0, 0))
        x += cw + GAP
    y += rh + GAP
f1 = F("k", 86)
d.text((70, H - BAND + 30), "悉尼精酿，来这就够了", font=f1, fill="white")
d.text((70, H - BAND + 152), "Marrickville最全攻略", font=f1, fill=(255, 140, 60))
img.save(sys.argv[1] if len(sys.argv) > 1 else "lc_cover.png")
