"""悉尼水果日历帖：季节卡（2x2照片，每格写水果名和月份）和首页选项。
用法：python3 tools/fruit_cards.py 照片目录 老杨图标目录 输出目录
照片目录下按 水果英文名/编号.jpg 存放，PICK 里写选用哪张和裁切参数。"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps

W, H = 1080, 1440
SRC, ICONS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
CREAM = (248, 243, 234); INK = (34, 32, 30)
def zh(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)

def warm(img):
    img = img.filter(ImageFilter.UnsharpMask(2, 40, 2))
    img = ImageEnhance.Color(ImageEnhance.Contrast(img).enhance(1.05)).enhance(1.12)
    r, g, b = img.split()
    r = r.point(lambda v: min(255, int(v * 1.03))); b = b.point(lambda v: int(v * .96))
    return Image.merge("RGB", (r, g, b))

def crop(spec, w, h):
    name, fx, fy, z = (list(spec) + [.5, .5, 1.0])[:4] if isinstance(spec, tuple) else (spec, .5, .5, 1.0)
    im = ImageOps.exif_transpose(Image.open(f"{SRC}/{name}")).convert("RGB")
    s = max(w / im.width, h / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    return warm(im.crop((round(x), round(y), round(x) + w, round(y) + h)))

def icon(img, pose, x, y, h):
    ic = Image.open(f"{ICONS}/{pose}.png").convert("RGBA")
    ic = ic.resize((round(ic.width * h / ic.height), h), Image.LANCZOS)
    img = img.convert("RGBA"); sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 255), (x + 4, y + 6), ic.split()[3].point(lambda v: int(v * .3)))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8))); img.alpha_composite(ic, (x, y))
    return img.convert("RGB")

def season(fn, title, months, col, items):
    """items: [(照片spec, 水果名, 月份)] 四个"""
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 200), fill=col)
    d.text((64, 46), title, font=zh(96, "Black"), fill="white")
    f = zh(44, "Bold"); d.text((W - 64 - f.getlength(months), 88), months, font=f, fill="white")
    cw, ch = W // 2, (H - 200) // 2
    for i, (spec, name, m) in enumerate(items):
        x, y = (i % 2) * cw, 200 + (i // 2) * ch
        img.paste(crop(spec, cw, ch), (x, y))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        f1, f2 = zh(52, "Black"), zh(32, "Bold")
        bw = max(f1.getlength(name), f2.getlength(m)) + 52
        od.rounded_rectangle((x + 28, y + ch - 168, x + 28 + bw, y + ch - 28), 26, fill=(255, 255, 255, 236))
        od.text((x + 54, y + ch - 158), name, font=f1, fill=INK)
        od.text((x + 54, y + ch - 82), m, font=f2, fill=col)
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(img)
    d.line((cw, 200, cw, H), fill=CREAM, width=6); d.line((0, 200 + ch, W, 200 + ch), fill=CREAM, width=6)
    img.save(f"{OUT}/{fn}", quality=93)
