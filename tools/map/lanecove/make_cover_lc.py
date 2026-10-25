"""Lane Cove封面：上面10家店的招牌菜照片拼图，每张图标店名；下面深色标题条。"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"b": "NotoSansCJK-Bold.ttc", "k": "NotoSansCJK-Black.ttc"}[w], s, index=2)
P = "data/post_img/"
# 每行：[(图片, 店名, 焦点x, 焦点y)]
CELLS = [
    ("lc_sho_sashimi.jpg", "Sho Sushi", .45, .35), ("lc_jl_rosti.jpg", "Jules", .5, .5), ("lc_l8_eclair.jpg", "Lamin8", .5, .5), ("lc_vn_pizza.jpg", "Via Napoli", .45, .5),
    ("lc_ko_ramen.jpg", "Kosuke", .7, .55), ("lc_ec_spread.jpg", "Encasa", .3, .55), ("lc_s11_cans.jpg", "11:11 Sweet", .5, .5), ("lc_sho_wagyu.jpg", "Sho Sushi", .5, .35),
    ("lc_jl_prawn.jpg", "Jules", .45, .5), ("lc_sh_octopus.jpg", "Shorties", .55, .6), ("lc_kin_pasta.jpg", "KIN", .5, .6), ("lc_l8_choux.jpg", "Lamin8", .5, .5),
    ("lc_pc_grilled.jpg", "波塞冬", .5, .5), ("lc_sho_uni.jpg", "Sho Sushi", .45, .45), ("lc_ec_jamon.jpg", "Encasa", .45, .5), ("lc_sh_martini.jpg", "Shorties", .45, .5),
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
f1 = F("k", 100)
d.text((70, H - BAND + 30), "悉尼Lane Cove附近", font=f1, fill="white")
d.text((70, H - BAND + 152), "吃什么？", font=f1, fill=(255, 140, 60))
img.save(sys.argv[1] if len(sys.argv) > 1 else "lc_cover.png")
