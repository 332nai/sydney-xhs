"""Bondi咖啡店卡片（沿用Paddington版式）：封面单图大字，内页2x2拼图，店名压在中线。
用法：python3 tools/pad_cards.py 图片目录 输出目录"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps

W, H = 1080, 1440
SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
EN = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
def en(s): return ImageFont.truetype(EN, s)
def zh(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)

def warm(img):
    img = img.filter(ImageFilter.UnsharpMask(2, 50, 2))
    img = ImageEnhance.Color(ImageEnhance.Contrast(img).enhance(1.06)).enhance(1.12)
    r, g, b = img.split()
    r = r.point(lambda v: min(255, int(v * 1.04))); b = b.point(lambda v: int(v * .95))
    return Image.merge("RGB", (r, g, b))

def crop(spec, w, h):
    spec = list(spec) if isinstance(spec, tuple) else [spec]
    name, fx, fy, z = spec + [.5, .5, 1.0][len(spec) - 1:]
    im = ImageOps.exif_transpose(Image.open(f"{SRC}/{name}")).convert("RGB")
    s = max(w / im.width, h / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    return warm(im.crop((round(x), round(y), round(x) + w, round(y) + h)))

def shadow_text(img, items):
    """items: (x_center, y, text, font). 先画模糊阴影再画白字。"""
    sh = Image.new("L", img.size, 0); d = ImageDraw.Draw(sh)
    for cx, y, t, f in items:
        d.text((cx - f.getlength(t) / 2, y), t, font=f, fill=200, stroke_width=4, stroke_fill=200)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    img.paste(Image.new("RGB", img.size, (0, 0, 0)), (0, 0), sh.point(lambda v: int(v * .75)))
    d = ImageDraw.Draw(img)
    for cx, y, t, f in items:
        d.text((cx - f.getlength(t) / 2, y), t, font=f, fill="white")

def card(fn, no, name, tag, photos):
    img = Image.new("RGB", (W, H))
    cw, ch = W // 2, H // 2
    for i, p in enumerate(photos):
        img.paste(crop(p, cw, ch), ((i % 2) * cw, (i // 2) * ch))
    f = en(92)
    while f.getlength(name) > 980: f = en(f.size - 4)
    shadow_text(img, [(W / 2, ch - 106, f"( {no} )", en(36)), (W / 2, ch - 46, name, f), (W / 2, ch + 64, tag, zh(40))])
    img.save(f"{OUT}/{fn}", quality=93)

# 封面
c = crop(("gd_sp12.jpg", .5, .5, 1.0), W, H)
shadow_text(c, [(W / 2, 440, "A Little Cafe Guide To", en(50)), (W / 2, 520, "BONDI", en(170)), (W / 2, 720, "悉尼Bondi咖啡小指南", zh(48))])
c.save(f"{OUT}/00.jpg", quality=93)

card("01.jpg", "01", "JACKS NORTH BONDI", "自己种豆子的澳洲咖啡",
     [("jk_site11.jpg", .5, .5), ("jk_site18.jpg", .5, .5), ("jk_site09.jpg", .5, .5), ("jk_wl0.jpg", .45, .5)])
card("02.jpg", "02", "PORCH AND PARLOUR", "North Bondi泳前咖啡老店",
     [("pp00.jpg", .5, .5), ("pp01.jpg", .5, .5), ("pp06.jpg", .5, .5), ("pp03.jpg", .5, .5)])
card("03.jpg", "03", "GLORY DAYS", "Bondi Pavilion里的海景早午餐",
     [("gd_cp32.jpg", .5, .5), ("gd_cp25.jpg", .5, .5), ("gd_to5.jpg", .5, .5), ("gd_to2.jpg", .5, .5)])
card("04.jpg", "04", "WILL & CO", "本地烘焙商的品鉴吧台",
     [("wc_wl2.jpg", .45, .5), ("wc_s01.jpg", .3, .5), ("wc_wl0.jpg", .5, .5), ("wc_wl1.jpg", .6, .5)])
card("05.jpg", "05", "SKITTLE LANE", "店里自己烘豆，还有手冲吧台",
     [("sk_site3.jpg", .5, .5), ("sk_wl0.jpg", .5, .5), ("sk_wl2.jpg", .5, .5), ("sk_lc0.jpg", .5, .5)])
card("06.jpg", "06", "BLACKWOOD", "从Cronulla开过来的人气早午餐",
     [("bw_to01.jpg", .5, .5), ("bw_to04.jpg", .5, .5), ("bw_to00.jpg", .5, .5), ("bw_cp1.jpg", .5, .5)])
card("07.jpg", "07", "LOX STOCK AND BARREL", "每天现煮的手工贝果",
     [("lx05.jpg", .5, .5), ("lx07.jpg", .5, .5), ("lx01.jpg", .5, .5), ("lx10.jpg", .5, .5)])
card("08.jpg", "08", "BENNETT STREET DAIRY", "咖啡像啤酒一样从龙头里打",
     [("bsd04.jpg", .55, .5), ("bsd02.jpg", .5, .5), ("bsd01.jpg", .5, .5), ("bsd11.jpg", .5, .5)])
card("09.jpg", "09", "THE CRABBE HOLE", "藏在Icebergs泳池边",
     [("ch04.jpg", .6, .5), ("ch02.jpg", .5, .5), ("ch05.jpg", .5, .5), ("ch01.jpg", .5, .5)])
card("10.jpg", "10", "MYFLOWERMAN", "花店和咖啡窗开在一起",
     [("mf_al0.jpg", .22, .5), ("mf_al2.jpg", .8, .5), ("mf_al1.jpg", .5, .5), ("mf_al2.jpg", .22, .5)])
print("ok")
