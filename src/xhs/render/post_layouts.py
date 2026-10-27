"""单篇模式的版式。每一页用哪个版式，直接写在帖子数据文件的 pages 里。"""
from PIL import Image, ImageDraw, ImageOps

from .. import config
from .base import *  # noqa: F401,F403
from . import layouts

BODY = config.settings()["render"]["body_size"]


def _img(path, size):
    return cover_crop(path, size)


def _shade(img, box, alpha=150):
    ov = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]), (15, 12, 10, alpha))
    img.paste(ov, (box[0], box[1]), ov)


def cover_photo(p, ctx):
    """整版照片，底部深色区只放大标题（封面不写小字）。"""
    img = Image.new("RGB", (W, H), INK)
    ph = 880
    img.paste(_img(p["image"], (W, ph)), (0, 0))
    d = ImageDraw.Draw(img)
    lines = p.get("headline", [])
    fonts = [fit("sans", "black", line, 860, 104, 60) for line in lines]
    size = min(f.size for f in fonts) if fonts else 104
    f = F("sans", "black", size)
    step = int(size * 1.22)
    y = ph + (H - ph - step * len(lines)) // 2 + int(size * 0.05)
    acc = p.get("accent")
    for i, line in enumerate(lines):
        d.text((M, y), line, font=f, fill=CORAL if acc and acc in line and i == 0 else CREAM)
        y += step
    return img


def cover_full(p, ctx):
    """照片铺满整张，底部渐变压暗，只放大标题。"""
    img = _img(p["image"], (W, H)).convert("RGB")
    lines = p.get("headline", [])
    fonts = [fit("sans", "black", line, 860, 108, 60) for line in lines]
    size = min(f.size for f in fonts) if fonts else 108
    f = F("sans", "black", size)
    step = int(size * 1.22)
    top = H - 90 - step * len(lines)
    grad = Image.new("L", (1, H), 0)
    g0 = top - 260
    for yy in range(H):
        t = 0 if yy < g0 else min(1, (yy - g0) / (H - g0) * 1.4)
        grad.putpixel((0, yy), int(215 * t))
    shade = Image.new("RGB", (W, H), (12, 10, 10))
    img = Image.composite(shade, img, grad.resize((W, H)))
    d = ImageDraw.Draw(img)
    if p.get("label"):  # 和原来封面一样：左上角深色小标签
        lf = F("sans", "bold", 26)
        rrect(d, [M - 16, 64, M + tw(lf, p["label"]) + 16, 112], 24, fill=(20, 20, 20))
        d.text((M, 70), p["label"], font=lf, fill=CREAM)
    y = top
    for i, line in enumerate(lines):
        d.text((M, y), line, font=f, fill=(255, 140, 60) if p.get("accent") and i == len(lines) - 1 else WHITE)
        y += step
    return img


def _film_grade(im, seed=7):
    """王家卫式胶片调色：暗部偏青绿，亮部偏暖，加对比和颗粒。"""
    from PIL import ImageEnhance
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Color(im).enhance(1.08)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.04 + 4)))
    g = g.point(lambda v: min(255, int(v * 1.0 + (10 if v < 110 else 0))))
    b = b.point(lambda v: min(255, int(v * 0.9 + (14 if v < 90 else 0))))
    im = Image.merge("RGB", (r, g, b))
    noise = Image.effect_noise(im.size, 26).convert("L")
    return Image.blend(im, Image.merge("RGB", [noise] * 3), 0.07)


def cover_film(p, ctx):
    """电影截图式封面：上下黑边，胶片调色，大标题像字幕一样居中。"""
    img = Image.new("RGB", (W, H), (8, 8, 8))
    top, ph = 150, 760
    img.paste(_film_grade(_img(p["image"], (W, ph)).convert("RGB")), (0, top))
    d = ImageDraw.Draw(img)
    if p.get("label"):
        lf = F("sans", "bold", 26)
        rrect(d, [M - 16, 51, M + tw(lf, p["label"]) + 16, 99], 24, fill=(36, 36, 36))
        d.text((M, 57), p["label"], font=lf, fill=CREAM)
    lines = p.get("headline", [])
    fonts = [fit("serif", "black", line, 880, 92, 52) for line in lines]
    size = min(f.size for f in fonts) if fonts else 92
    f = F("serif", "black", size)
    step = int(size * 1.4)
    band_top = top + ph
    y = band_top + (H - band_top - step * len(lines)) // 2 + int(size * 0.08)
    yellow = (246, 214, 92)
    for line in lines:
        x = (W - f.getlength(line)) / 2
        d.text((x + 3, y + 3), line, font=f, fill=(0, 0, 0))
        d.text((x, y), line, font=f, fill=yellow)
        y += step
    return img


def _pop(im):
    """美食照片增强：放大后锐化，略提对比、饱和和暖度。"""
    from PIL import ImageEnhance, ImageFilter
    im = im.filter(ImageFilter.UnsharpMask(radius=2.2, percent=90, threshold=2))
    im = ImageEnhance.Contrast(im).enhance(1.1)
    im = ImageEnhance.Color(im).enhance(1.15)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.03)))
    return Image.merge("RGB", (r, g, b))


def cover_hero(p, ctx):
    """美食主图封面：照片占上部，底部渐变压暗放大标题。适合分辨率不高的照片。"""
    ph = p.get("photo_h", 1060)
    img = Image.new("RGB", (W, H), (14, 10, 8))
    photo = _pop(_img(p["image"], (W, ph), ).convert("RGB")) if not p.get("focus") else _pop(
        ImageOps.fit(Image.open(p["image"]).convert("RGB"), (W, ph), method=Image.LANCZOS, centering=tuple(p["focus"])))
    img.paste(photo, (0, 0))
    grad = Image.new("L", (1, H), 0)
    g0 = ph - 380
    for yy in range(H):
        t = 0 if yy < g0 else min(1, (yy - g0) / 380)
        grad.putpixel((0, yy), int(255 * t ** 1.3))
    img = Image.composite(Image.new("RGB", (W, H), (14, 10, 8)), img, grad.resize((W, H)))
    d = ImageDraw.Draw(img)
    if p.get("label"):
        lf = F("sans", "bold", 26)
        rrect(d, [M - 16, 64, M + tw(lf, p["label"]) + 16, 112], 24, fill=(20, 20, 20))
        d.text((M, 70), p["label"], font=lf, fill=CREAM)
    lines = p.get("headline", [])
    fonts = [fit("sans", "black", line, 860, 112, 60) for line in lines]
    size = min(f.size for f in fonts) if fonts else 112
    f = F("sans", "black", size)
    step = int(size * 1.2)
    y = H - 100 - step * len(lines)
    acc = p.get("accent")
    for i, line in enumerate(lines):
        d.text((M, y), line, font=f, fill=(255, 140, 60) if acc and i == len(lines) - 1 else WHITE)
        y += step
    return img


def cover_sleeve(p, ctx):
    """唱片封套式封面：照片铺满，四周一圈细框，衬线标题放在顶部。"""
    img = _fit_focus(p["image"], (W, H), p.get("focus")).convert("RGB")
    grad = Image.new("L", (1, H), 0)
    for yy in range(0, 560):
        grad.putpixel((0, yy), int(150 * (1 - yy / 560) ** 1.6))
    img = Image.composite(Image.new("RGB", (W, H), (20, 14, 10)), img, grad.resize((W, H)))
    d = ImageDraw.Draw(img)
    ink = tuple(p.get("ink", CREAM))
    if p.get("frame", True):
        d.rectangle([34, 34, W - 34, H - 34], outline=ink, width=3)
    if p.get("label"):
        lf = F("sans", "bold", 26)
        rrect(d, [M - 16, 76, M + tw(lf, p["label"]) + 16, 124], 24, fill=(20, 20, 20))
        d.text((M, 82), p["label"], font=lf, fill=CREAM)
    y = 168
    for line in p.get("headline", []):
        f = fit("serif", "black", line, 860, 96, 56)
        d.text((M, y), line, font=f, fill=ink)
        y += int(f.size * 1.28)
    return img


def cover_bignum(p, ctx):
    """大数字封面：照片铺满，超大数字压在上面，下面一句话标题，可加三色条。"""
    img = _pop(_fit_focus(p["image"], (W, H), p.get("focus")).convert("RGB"))
    grad = Image.new("L", (1, H), 0)
    for yy in range(H):
        top = max(0, 1 - yy / 520) ** 1.5 * 0.55
        bot = max(0, (yy - (H - 620)) / 620) ** 1.3 * 0.9
        grad.putpixel((0, yy), int(255 * min(1, top + bot)))
    img = Image.composite(Image.new("RGB", (W, H), (12, 10, 10)), img, grad.resize((W, H)))
    d = ImageDraw.Draw(img)
    num, unit = p["big"], p.get("unit", "")
    size = p.get("big_size", 300)
    nf = F("inter", "Black", size)
    uf = F("sans", "black", int(size * 0.42))
    y = H - 140 - int(size * 0.95) - 120 * len(p.get("headline", []))
    x = M - 8
    d.text((x + 6, y + 6), num, font=nf, fill=(0, 0, 0))
    d.text((x, y), num, font=nf, fill=WHITE)
    ux = x + nf.getlength(num) + 14
    d.text((ux + 4, y + size * 0.45 + 4), unit, font=uf, fill=(0, 0, 0))
    d.text((ux, y + size * 0.45), unit, font=uf, fill=WHITE)
    yy = y + int(size * 1.02)
    if p.get("stripe"):
        cols = [tuple(c) for c in p["stripe"]]
        sw = 120
        for i, c in enumerate(cols):
            d.rectangle([M + i * sw, yy, M + (i + 1) * sw - 6, yy + 16], fill=c)
        yy += 46
    for line in p.get("headline", []):
        f = fit("sans", "black", line, 860, 92, 56)
        d.text((M, yy), line, font=f, fill=WHITE)
        yy += int(f.size * 1.25)
    return img


def cover_mosaic(p, ctx):
    """四宫格封面：上面2x2四张照片，下面深色区放大标题。"""
    img = Image.new("RGB", (W, H), (16, 20, 20))
    gap, top_h = 8, p.get("grid_h", 900)
    cw, ch = (W - gap) // 2, (top_h - gap) // 2
    foci = p.get("focus") or [None] * 4
    for i, path in enumerate(p["images"][:4]):
        x, y = (i % 2) * (cw + gap), (i // 2) * (ch + gap)
        img.paste(_pop(_fit_focus(path, (cw, ch), foci[i]).convert("RGB")), (x, y))
    d = ImageDraw.Draw(img)
    lines = p.get("headline", [])
    fonts = [fit("sans", "black", line, 860, 104, 56) for line in lines]
    size = min(f.size for f in fonts) if fonts else 104
    f = F("sans", "black", size)
    step = int(size * 1.22)
    y = top_h + (H - top_h - step * len(lines)) // 2
    for i, line in enumerate(lines):
        d.text((M, y), line, font=f, fill=tuple(p.get("accent_rgb", (0, 190, 180))) if p.get("accent") and i == len(lines) - 1 else WHITE)
        y += step
    return img


def spot(p, ctx):
    """合集里的单店页：上面一到两张照片，下面店名、地址和两三句介绍。"""
    img = Image.new("RGB", (W, H), CREAM)
    imgs = p.get("images", [])
    ph = p.get("photo_h", 760)
    foci = p.get("focus") or [None] * len(imgs)
    if len(imgs) == 1:
        img.paste(_fit_focus(imgs[0], (W, ph), foci[0]), (0, 0))
    elif len(imgs) >= 2:
        gw = (W - 8) // 2
        img.paste(_fit_focus(imgs[0], (gw, ph), foci[0]), (0, 0))
        img.paste(_fit_focus(imgs[1], (W - gw - 8, ph), foci[1]), (gw + 8, 0))
    d = ImageDraw.Draw(img)
    y = (ph if imgs else 120) + 52
    tagc = (214, 69, 65) if p.get("cat", "r") == "r" else (0, 128, 128)
    tf = F("sans", "medium", 30); tag = p.get("tag", "")
    if tag:  # 简单的文字标签，不加底色
        d.text((M, y), tag, font=tf, fill=GREY); y += 58
    nf = fit("sans", "black", p["name"], 860, 84, 52)
    d.text((M, y), p["name"], font=nf, fill=INK); y += int(nf.size * 1.3)
    if p.get("addr"):
        d.text((M, y), p["addr"], font=F("sans", "medium", 31), fill=GREY); y += 64
    else:
        y += 24
    for line in p.get("lines", []):
        y = para(d, (M, y), line, F("sans", "regular", 36), INK, 860, 1.55) + 12
    return img


def spot_clean(p, ctx):
    """极简单店页：照片，店名，一两句话。只用两种字号、一种字色。"""
    img = Image.new("RGB", (W, H), CREAM)
    imgs = p.get("images", [])
    ph = p.get("photo_h", 860)
    foci = p.get("focus") or [None] * len(imgs)
    if len(imgs) == 1:
        img.paste(_fit_focus(imgs[0], (W, ph), foci[0]), (0, 0))
    elif len(imgs) == 2:
        gw = (W - 6) // 2
        img.paste(_fit_focus(imgs[0], (gw, ph), foci[0]), (0, 0))
        img.paste(_fit_focus(imgs[1], (W - gw - 6, ph), foci[1]), (gw + 6, 0))
    elif len(imgs) == 3:
        lw = int(W * 0.58); rh = (ph - 6) // 2
        img.paste(_fit_focus(imgs[0], (lw, ph), foci[0]), (0, 0))
        img.paste(_fit_focus(imgs[1], (W - lw - 6, rh), foci[1]), (lw + 6, 0))
        img.paste(_fit_focus(imgs[2], (W - lw - 6, ph - rh - 6), foci[2]), (lw + 6, rh + 6))
    elif len(imgs) >= 4:
        gw = (W - 6) // 2; gh = (ph - 6) // 2
        for i, (x, y0) in enumerate([(0, 0), (gw + 6, 0), (0, gh + 6), (gw + 6, gh + 6)]):
            img.paste(_fit_focus(imgs[i], (W - gw - 6 if x else gw, ph - gh - 6 if y0 else gh), foci[i]), (x, y0))
    d = ImageDraw.Draw(img)
    y = ph + 70
    nf = F("sans", "black", p.get("name_size", 66))
    d.text((M, y), p["name"], font=nf, fill=INK); y += int(nf.size * 1.6)
    for line in p.get("lines", []):
        y = para(d, (M, y), line, F("sans", "regular", 36), INK, W - 2 * M, 1.6) + 14
    return img


def list_clean(p, ctx):
    """极简文字页：标题，下面每家店一行店名一行介绍。"""
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    y = 110
    d.text((M, y), p.get("headline", "还有这几家"), font=F("sans", "black", 64), fill=INK); y += 150
    for e in p.get("entries", []):
        d.text((M, y), e["name"], font=F("sans", "bold", 40), fill=INK); y += 62
        y = para(d, (M, y), e["text"], F("sans", "regular", 34), INK, W - 2 * M, 1.5) + 54
    return img


def spot_list(p, ctx):
    """没有照片的几家店合在一页，纯文字。"""
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    y = 80
    if p.get("headline"):
        d.text((M, y), p["headline"], font=F("sans", "black", 64), fill=INK); y += 110
    for i, e in enumerate(p.get("entries", [])):
        if i:
            d.line([(M, y), (W - M, y)], fill=(220, 210, 196), width=2); y += 30
        c = (214, 69, 65) if e.get("cat", "r") == "r" else (0, 128, 128)
        d.ellipse([M, y + 16, M + 18, y + 34], fill=c)
        d.text((M + 32, y), e["name"], font=F("sans", "black", 42), fill=INK); y += 60
        d.text((M + 32, y), e["addr"], font=F("sans", "medium", 27), fill=GREY); y += 44
        y = para(d, (M + 32, y), e["text"], F("sans", "regular", 31), INK, 828, 1.45) + 20
    return img


def cover_split(p, ctx):
    """上下两张照片，中间一条标题带。"""
    img = Image.new("RGB", (W, H), CREAM)
    a, b = p["images"][:2]
    img.paste(_img(a, (W, 480)), (0, 0))
    img.paste(_img(b, (W, 480)), (0, 853))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 480, W, 853], fill=p.get("band", CREAM))
    ink = INK if not p.get("band") else CREAM
    if p.get("label"):
        d.text((M, 508), p["label"], font=F("sans", "bold", 26), fill=CORAL)
    y = 560
    for line in p.get("headline", []):
        f = fit("sans", "black", line, 860, 92, 52)
        d.text((M, y), line, font=f, fill=ink)
        y += int(f.size * 1.18)
    if p.get("sub"):
        para(d, (M, y + 6), p["sub"], F("sans", "medium", 30), ink, 860, 1.4, max_lines=1)
    tags = p.get("tags", [])
    if tags:
        f = F("sans", "bold", 26)
        for (x, yy), t in zip([(M, 420), (M, 1270)], tags):
            rrect(d, [x - 14, yy - 6, x + tw(f, t) + 14, yy + 42], 22, fill=(20, 20, 20))
            d.text((x, yy), t, font=f, fill=CREAM)
    return img


def photo_grid(p, ctx):
    """标题加四宫格照片，每张配一行说明。"""
    img = paper(p.get("bg", CREAM)); d = ImageDraw.Draw(img)
    if p.get("label"):
        d.text((M, 70), p["label"], font=F("sans", "bold", 26), fill=CORAL)
    y = headline_y = 112
    for line in p.get("headline", []):
        f = fit("serif", "black", line, 860, 68, 44)
        d.text((M, y), line, font=f, fill=INK); y += int(f.size * 1.25)
    y += 20
    cells = list(zip(p["images"], p.get("captions", [""] * len(p["images"]))))[:4]
    cw, ch, gap = 420, 450, 20
    for i, (im, cap) in enumerate(cells):
        x = M + (i % 2) * (cw + gap)
        yy = y + (i // 2) * (ch + 80)
        img.paste(_img(im, (cw, ch)), (x, yy))
        para(d, (x, yy + ch + 12), cap, F("sans", "medium", 26), INK, cw, 1.35, max_lines=2)
    return img


def _compare_body(d, p, y):
    cols = p["cols"]
    first_w = 210
    cw = (860 - first_w) / len(cols)
    bf, lf = F("sans", "regular", BODY + 6), F("sans", "bold", BODY + 6)
    for j, c in enumerate(cols):
        d.text((M + first_w + j * cw, y), c, font=fit("sans", "black", c, cw - 20, 40, 26), fill=INK)
    y += 80
    d.line([(M, y - 18), (W - M, y - 18)], fill=INK, width=3)
    for row in p["rows"]:
        h = max([para_height(str(v), bf, cw - 24, 1.45) for v in row[1:]] + [56])
        d.text((M, y), row[0], font=lf, fill=CORAL)
        for j, v in enumerate(row[1:]):
            para(d, (M + first_w + j * cw, y), str(v), bf, INK, cw - 24, 1.45)
        y += h + 34
        d.line([(M, y - 18), (W - M, y - 18)], fill=(214, 206, 192), width=1)
    if p.get("note"):
        y = para(d, (M, y + 24), p["note"], F("serif", "regular", BODY + 4), (70, 66, 60), 860, 1.6)
    return y


def compare(p, ctx):
    """对比表：几家店并排比较。内容不多时整体往页面中间放。"""
    img = paper((246, 241, 231)); d = ImageDraw.Draw(img)
    if p.get("label"):
        d.text((M, 80), p["label"], font=F("sans", "bold", 26), fill=CORAL)
    y = 130
    for line in p.get("headline", []):
        f = fit("serif", "black", line, 860, 84, 52)
        d.text((M, y), line, font=f, fill=INK); y += int(f.size * 1.25)
    scratch = ImageDraw.Draw(Image.new("RGB", (W, H * 2)))
    h = _compare_body(scratch, p, 0)
    _compare_body(d, p, y + max(40, int((H - 120 - y - h) * 0.4)))
    layouts.brand(d, GREY, y=1420)
    return img


def story(p, ctx):
    """长文页：一张横幅照片加几段正文，适合讲人物故事。"""
    img = paper((246, 241, 231)); d = ImageDraw.Draw(img)
    img.paste(_img(p["image"], (W, 480)), (0, 0))
    d = ImageDraw.Draw(img)
    y = 525
    if p.get("label"):
        d.text((M, y), p["label"], font=F("sans", "bold", 26), fill=CORAL); y += 50
    for line in p.get("headline", []):
        f = fit("serif", "black", line, 860, 60, 40)
        d.text((M, y), line, font=f, fill=INK); y += int(f.size * 1.3)
    y += 16
    for para_text in p.get("paragraphs", []):
        y = para(d, (M, y), para_text, F("serif", "regular", BODY + 6), (50, 48, 45), 860, 1.7) + 26
    if p.get("quote") and y < H - 200:
        d.line([(M, y + 20), (M, y + 150)], fill=CORAL, width=6)
        para(d, (M + 34, y + 24), p["quote"], F("serif", "bold", 44), INK, 820, 1.4, max_lines=2)
    layouts.brand(d, GREY, y=1420)
    return img


def closing(p, ctx):
    """结尾页：一句话总结加互动问题。"""
    img = paper(p.get("bg", NAVY), grain=8); d = ImageDraw.Draw(img)
    ink = CREAM if p.get("bg", NAVY) in (NAVY, TEAL, INK) else INK
    y = 230
    for line in p.get("headline", []):
        f = fit("serif", "black", line, 860, 80, 48)
        d.text((M, y), line, font=f, fill=ink); y += int(f.size * 1.3)
    y += 30
    for item in p.get("lines", []):
        y = para(d, (M, y), item, F("sans", "regular", BODY + 2), ink, 860, 1.6) + 14
    q = p.get("question", "")
    if q:
        top = H - 333
        rrect(d, [M, top, W - M, top + 190], 20, outline=CORAL, width=3)
        para(d, (M + 34, top + 38), q, F("sans", "bold", 40), ink, 790, 1.35, max_lines=2)
    layouts.brand(d, ink, y=1420)
    return img


def venue(p, ctx):
    """店铺页：沿用周报的照片海报版式。"""
    item = dict(p)
    item["image"] = {"path": p["image"]}
    item.setdefault("kind", "venue")
    item.setdefault("num", 0)
    return layouts.photo_poster(item, ctx)


def number(p, ctx):
    item = dict(p); item.setdefault("kind", "venue"); item.setdefault("num", 0)
    return layouts.number_poster(item, ctx)


def _caption_band(img, d, y0, caption, sub=None):
    _shade(img, (0, y0, W, H), 175)
    d = ImageDraw.Draw(img)
    y = y0 + 34
    if caption:
        f = fit("sans", "black", caption, 860, 52, 34)
        d.text((M, y), caption, font=f, fill=CREAM); y += int(f.size * 1.35)
    if sub:
        para(d, (M, y), sub, F("sans", "regular", BODY), SAND, 860, 1.45, max_lines=2)
    return d


def _fit_focus(path, size, focus=None):
    if not focus:
        return _img(path, size)
    return ImageOps.fit(Image.open(path).convert("RGB"), size, method=Image.LANCZOS, centering=tuple(focus))


def _tag(d, text, y):
    """照片上的小标签：一行短字，深色圆角底。"""
    f = F("sans", "bold", 30)
    rrect(d, [M - 18, y - 10, M + tw(f, text) + 18, y + 48], 26, fill=(20, 20, 20))
    d.text((M, y - 2), text, font=f, fill=CREAM)


def photo_full(p, ctx):
    """整版照片，底部一条说明；只写 tag 时是一个小标签；都不写就是纯照片。"""
    img = _fit_focus(p["image"], (W, H), p.get("focus"))
    d = ImageDraw.Draw(img)
    if p.get("tag"):
        _tag(d, p["tag"], H - 90)
    if p.get("label"):
        f = F("sans", "bold", 26)
        rrect(d, [M - 16, 64, M + tw(f, p["label"]) + 16, 112], 24, fill=(20, 20, 20))
        d.text((M, 70), p["label"], font=f, fill=CREAM)
    if p.get("caption") or p.get("sub"):
        _caption_band(img, d, H - 240 if p.get("sub") else H - 180, p.get("caption"), p.get("sub"))
    return img


def cover_quad(p, ctx):
    """封面：四张图拼成2×2，标题放在四张图的交汇处。"""
    gap = p.get("gap", 8)
    img = Image.new("RGB", (W, H), CREAM)
    imgs = p["images"][:4]
    foci = p.get("focus") or [None] * 4
    hw, hh = (W - gap) // 2, (H - gap) // 2
    boxes = [(0, 0), (hw + gap, 0), (0, hh + gap), (hw + gap, hh + gap)]
    for (x, y), path, fc in zip(boxes, imgs, foci):
        img.paste(_fit_focus(path, (W - hw - gap if x else hw, H - hh - gap if y else hh), fc), (x, y))
    d = ImageDraw.Draw(img)
    lines = p.get("headline", [])
    size = min(fit("sans", "black", line, 640, 84, 48).size for line in lines)
    f = F("sans", "black", size)
    step = int(size * 1.28)
    bw = max(tw(f, line) for line in lines) + 2 * 56
    bh = step * len(lines) + 2 * 44 - (step - size)
    bx, by = (W - bw) // 2, (H - bh) // 2
    d.rectangle([bx, by, bx + bw, by + bh], fill=CREAM)
    y = by + 40
    for line in lines:
        d.text(((W - tw(f, line)) // 2, y), line, font=f, fill=INK)
        y += step
    return img


def cover_five(p, ctx):
    """封面：上方标题，下方一张大图加一排四张小方图，留白干净。"""
    m, g = 44, 12
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    lines = p.get("headline", [])
    f = F("sans", "black", min(fit("sans", "black", l, W - 2 * m, 74, 50).size for l in lines))
    y = m + 6
    for line in lines:
        d.text((m, y), line, font=f, fill=INK); y += int(f.size * 1.26)
    top = y + 22
    imgs = p["images"][:5]; foci = p.get("focus") or [None] * 5
    sw = (W - 2 * m - 3 * g) // 4
    bh = H - m - sw - g - top
    img.paste(_fit_focus(imgs[0], (W - 2 * m, bh), foci[0]), (m, top))
    x = m
    for i in range(4):
        w = sw if i < 3 else W - m - x
        img.paste(_fit_focus(imgs[i + 1], (w, sw), foci[i + 1]), (x, top + bh + g)); x += sw + g
    return img


def photo_duo(p, ctx):
    """上下两张照片，各配一行说明。"""
    img = Image.new("RGB", (W, H), INK)
    a, b = p["images"][:2]
    caps = p.get("captions", ["", ""])
    fa, fb = (p.get("focus") or [None, None])[:2]
    img.paste(_fit_focus(a, (W, 656), fa), (0, 0))
    img.paste(_fit_focus(b, (W, 657), fb), (0, 676))
    d = ImageDraw.Draw(img)
    f = F("sans", "bold", 30)
    for (y, cap) in [(576, caps[0]), (H - 80, caps[1])]:
        if cap:
            rrect(d, [M - 18, y - 10, M + tw(f, cap) + 18, y + 48], 26, fill=(20, 20, 20))
            d.text((M, y - 2), cap, font=f, fill=CREAM)
    return img


def closing_photo(p, ctx):
    """结尾页：上半张照片，下半部分是互动问题。"""
    img = paper(p.get("bg", NAVY), grain=8)
    img.paste(_img(p["image"], (W, 690)), (0, 0))
    d = ImageDraw.Draw(img)
    ink = CREAM
    y = 740
    for line in p.get("headline", []):
        f = fit("serif", "black", line, 860, 64, 40)
        d.text((M, y), line, font=f, fill=ink); y += int(f.size * 1.3)
    for item in p.get("lines", []):
        y = para(d, (M, y + 6), item, F("sans", "regular", BODY), SAND, 860, 1.5) + 6
    q = p.get("question", "")
    if q:
        top = max(y + 30, H - 293)
        rrect(d, [M, top, W - M, top + 170], 20, outline=CORAL, width=3)
        para(d, (M + 34, top + 34), q, F("sans", "bold", 38), ink, 790, 1.35, max_lines=2)
    layouts.brand(d, ink, y=1420)
    return img



def spot_rich(p, ctx):
    """详细单店卡：上面4到6张照片拼图，下面店名、奖项、地点和一整段介绍，字号自动缩放放得下。"""
    img = Image.new("RGB", (W, H), CREAM)
    imgs = p.get("images", [])[:6]
    foci = p.get("focus") or [None] * len(imgs)
    G = 5
    ph = p.get("photo_h", 600)
    n = len(imgs)
    if n == 4:
        cells = [(0, 0, 2, 1), (2, 0, 2, 1), (0, 1, 2, 1), (2, 1, 2, 1)]; cols = 4
    elif n == 5:
        cells = [(0, 0, 3, 1), (3, 0, 3, 1), (0, 1, 2, 1), (2, 1, 2, 1), (4, 1, 2, 1)]; cols = 6
    else:
        cells = [(0, 0, 2, 1), (2, 0, 2, 1), (4, 0, 2, 1), (0, 1, 2, 1), (2, 1, 2, 1), (4, 1, 2, 1)]; cols = 6
    cw = (W - G * (cols - 1)) / cols; rh = (ph - G) / 2
    for i, (cx, cy, sw, sh) in enumerate(cells[:n]):
        x0 = round(cx * (cw + G)); y0 = round(cy * (rh + G))
        x1 = round((cx + sw) * (cw + G) - G) if cx + sw < cols else W
        y1 = round((cy + sh) * (rh + G) - G) if cy + sh < 2 else ph
        img.paste(_fit_focus(imgs[i], (x1 - x0, y1 - y0), foci[i] if i < len(foci) else None), (x0, y0))
    d = ImageDraw.Draw(img)
    y = ph + 46
    if p.get("award"):
        af = F("sans", "bold", 30)
        aw = tw(af, p["award"])
        rrect(d, [M, y, M + aw + 36, y + 50], 25, fill=ACCENT if "ACCENT" in globals() else (214, 98, 40))
        d.text((M + 18, y + 6), p["award"], font=af, fill=(255, 255, 255))
        y += 72
    nf = fit("sans", "black", p["name"], W - 2 * M, 60, 40)
    d.text((M, y), p["name"], font=nf, fill=INK); y += int(nf.size * 1.35)
    if p.get("where"):
        d.text((M, y), p["where"], font=F("sans", "medium", 28), fill=(120, 110, 100)); y += 50
    if p.get("price"):
        d.text((M, y), p["price"], font=F("sans", "bold", 30), fill=(196, 84, 30)); y += 54
    y += 6
    text = p.get("text", "")
    room = H - 50 - y
    for size in range(32, 21, -1):
        f = F("sans", "regular", size)
        if para_height(text, f, W - 2 * M, 1.55) <= room: break
    para(d, (M, y), text, f, INK, W - 2 * M, 1.55)
    return img


def cover_hero3(p, ctx):
    """封面：上面一张大图铺满，底部渐暗压大标题；下面一排三张小图，白缝。"""
    img = Image.new("RGB", (W, H), (255, 255, 255))
    imgs = p["images"]; foci = p.get("focus") or [None] * 4
    G = 6; bh = p.get("hero_h", 1000)
    hero = _fit_focus(imgs[0], (W, bh), foci[0]).convert("RGB")
    grad = Image.new("L", (1, bh), 0)
    for yy in range(bh):
        grad.putpixel((0, yy), int(235 * max(0, (yy - bh * 0.45) / (bh * 0.55)) ** 1.4))
    hero = Image.composite(Image.new("RGB", (W, bh), (8, 6, 6)), hero, grad.resize((W, bh)))
    img.paste(hero, (0, 0))
    sw = (W - 2 * G) // 3
    for i in range(3):
        x = i * (sw + G)
        img.paste(_fit_focus(imgs[i + 1], (W - 2 * (sw + G) if i == 2 else sw, H - bh - G), foci[i + 1]), (x, bh + G))
    d = ImageDraw.Draw(img)
    lines = p.get("headline", [])
    y = bh - 60 - sum(int(fit("sans", "black", l, W - 2 * M, 120, 70).size * 1.18) for l in lines)
    for k, l in enumerate(lines):
        f = fit("sans", "black", l, W - 2 * M, 120, 70)
        col = tuple(p.get("accent", (255, 196, 60))) if k == len(lines) - 1 else (255, 255, 255)
        d.text((M + 4, y + 4), l, font=f, fill=(0, 0, 0))
        d.text((M, y), l, font=f, fill=col)
        y += int(f.size * 1.18)
    return img

REGISTRY = {"cover_hero3": cover_hero3, "spot_rich": spot_rich, "photo_full": photo_full, "photo_duo": photo_duo, "closing_photo": closing_photo, "cover_photo": cover_photo, "cover_full": cover_full, "cover_quad": cover_quad, "cover_five": cover_five, "cover_film": cover_film, "cover_hero": cover_hero, "cover_sleeve": cover_sleeve, "cover_bignum": cover_bignum, "cover_mosaic": cover_mosaic, "spot": spot, "spot_list": spot_list, "spot_clean": spot_clean, "list_clean": list_clean, "cover_split": cover_split, "photo_grid": photo_grid, "compare": compare,
            "story": story, "closing": closing, "venue": venue, "number": number}


from .night_layouts import REGISTRY as _NIGHT
REGISTRY.update(_NIGHT)
