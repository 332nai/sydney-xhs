"""没有照片时用的夜色版式：万圣节等活动合集。全部用代码画，不用任何现成图片。"""
import math, random

from PIL import Image, ImageDraw, ImageFilter

from .base import W, H, M, F, CREAM, GREY, fit, para, para_height, rrect, tw, draw_mixed

NIGHT = (17, 14, 22)
ORANGE = (240, 128, 40)
DIM = (170, 160, 150)
LINE = (60, 52, 66)


def _bg(seed=1):
    img = Image.new("RGB", (W, H), NIGHT)
    noise = Image.effect_noise((W, H), 30).convert("L")
    return Image.blend(img, Image.merge("RGB", [noise] * 3), 0.05)


def _label(d, text, y=64):
    if text:
        f = F("sans", "bold", 26)
        rrect(d, [M - 16, y, M + tw(f, text) + 16, y + 48], 24, fill=(40, 34, 46))
        d.text((M, y + 6), text, font=f, fill=CREAM)


def _bat(d, cx, cy, s, fill):
    pts = [(-1, 0), (-0.75, -0.35), (-0.55, -0.1), (-0.35, -0.3), (-0.15, -0.05), (0, -0.2),
           (0.15, -0.05), (0.35, -0.3), (0.55, -0.1), (0.75, -0.35), (1, 0), (0.6, 0.05),
           (0.4, 0.25), (0.2, 0.08), (0, 0.22), (-0.2, 0.08), (-0.4, 0.25), (-0.6, 0.05)]
    d.polygon([(cx + x * s, cy + y * s) for x, y in pts], fill=fill)


def _web(d, ox, oy, r, color):
    angles = [math.radians(a) for a in range(0, 91, 15)]
    for a in angles:
        d.line([(ox, oy), (ox + r * math.cos(a), oy + r * math.sin(a))], fill=color, width=2)
    for k in range(1, 7):
        rr = r * k / 6.5
        pts = []
        for i, a in enumerate(angles):
            sag = 0.92 if i % 2 else 1.0
            pts.append((ox + rr * sag * math.cos(a), oy + rr * sag * math.sin(a)))
        d.line(pts, fill=color, width=2)


def cover_halloween(p, ctx):
    img = _bg()
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    mx, my, mr = W - 260, 330, 190
    gd.ellipse([mx - mr - 90, my - mr - 90, mx + mr + 90, my + mr + 90], fill=(120, 60, 20))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    img = Image.composite(glow, img, glow.convert("L").point(lambda v: min(255, v * 2)))
    d = ImageDraw.Draw(img)
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=ORANGE)
    for cx, cy, cr in [(mx - 60, my - 50, 34), (mx + 70, my + 40, 22), (mx - 10, my + 90, 16)]:
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(226, 112, 32))
    _web(d, -10, -10, 430, (90, 82, 96))
    sx = 300
    d.line([(sx, 0), (sx, 470)], fill=(120, 110, 125), width=2)
    d.ellipse([sx - 16, 466, sx + 16, 500], fill=(10, 8, 12))
    d.ellipse([sx - 11, 452, sx + 11, 474], fill=(10, 8, 12))
    for side in (-1, 1):
        for k, dy in enumerate([470, 480, 490, 500]):
            d.line([(sx, dy), (sx + side * 34, dy - 16 + k * 10), (sx + side * 44, dy + 10 + k * 6)], fill=(10, 8, 12), width=3)
    for cx, cy, s in [(mx - 300, my + 150, 46), (mx - 170, my - 210, 32), (mx + 150, my + 230, 38)]:
        _bat(d, cx, cy, s, (10, 8, 12) if abs(cx - mx) < mr and abs(cy - my) < mr else (52, 44, 58))
    _label(d, p.get("label"))
    lines = p.get("headline", [])
    y = H - 110 - 150 * len(lines)
    for i, line in enumerate(lines):
        f = fit("sans", "black", line, 860, 150 if i == 0 else 120, 70)
        d.text((M, y), line, font=f, fill=CREAM if i == 0 else ORANGE)
        y += int(f.size * 1.18) + (14 if i == 0 else 0)
    return img


def _head(d, p, y=90):
    if p.get("label"):
        d.text((M, y), p["label"], font=F("sans", "bold", 30), fill=ORANGE)
        y += 60
    for line in p.get("headline", []):
        f = fit("serif", "black", line, 860, 84, 52)
        d.text((M, y), line, font=f, fill=CREAM)
        y += int(f.size * 1.3)
    return y


def _centered(p, body):
    """先量一遍标题加正文的高度，再把整块内容在画面里上下居中。"""
    probe = ImageDraw.Draw(Image.new("RGB", (W, H)))
    y0 = _head(probe, p)
    end = body(probe, y0 + 30)
    shift = max(0, (H - 90 - end) // 2)
    img = _bg()
    d = ImageDraw.Draw(img)
    y1 = _head(d, p, 90 + shift)
    body(d, y1 + 30)
    return img


def event_card(p, ctx):
    def body(d, y):
        if p.get("when"):
            f = fit("sans", "black", p["when"], 860, 68, 44)
            d.text((M, y), p["when"], font=f, fill=ORANGE)
            y += int(f.size * 1.6)
        fl, fv = F("sans", "bold", 32), F("sans", "regular", 34)
        for k, v in p.get("facts", []):
            d.text((M, y + 2), k, font=fl, fill=DIM)
            y = para(d, (M + 130, y), v, fv, CREAM, 730, 1.5) + 14
        y += 20
        d.line([(M, y), (W - M, y)], fill=LINE, width=2)
        y += 40
        fb = F("sans", "regular", 35)
        for b in p.get("points", []):
            d.ellipse([M, y + 17, M + 14, y + 31], fill=ORANGE)
            y = para(d, (M + 36, y), b, fb, CREAM, 824, 1.5) + 20
        if p.get("tip"):
            ft = F("sans", "medium", 32)
            h = para_height(p["tip"], ft, 780, 1.5) + 54
            y += 20
            rrect(d, [M, y, W - M, y + h], 18, outline=ORANGE, width=3)
            para(d, (M + 30, y + 26), p["tip"], ft, ORANGE, 780, 1.5)
            y += h
        return y
    return _centered(p, body)


def list_card(p, ctx):
    def body(d, y):
        fn, fm, fx = F("sans", "black", 44), F("sans", "bold", 31), F("sans", "regular", 32)
        for i, e in enumerate(p.get("entries", [])):
            if i:
                d.line([(M, y), (W - M, y)], fill=LINE, width=2)
                y += 30
            d.text((M, y), e["name"], font=fn, fill=CREAM)
            y += 66
            y = para(d, (M, y), e["meta"], fm, ORANGE, 860, 1.45) + 6
            if e.get("note"):
                y = para(d, (M, y), e["note"], fx, DIM, 860, 1.5)
            y += 26
        return y
    return _centered(p, body)


def calendar_card(p, ctx):
    def body(d, y):
        fn, fw, fx = F("inter", "Black", 96), F("sans", "bold", 28), F("sans", "regular", 33)
        days = p.get("days", [])
        for i, row in enumerate(days):
            hot = row.get("hot")
            if hot:
                hgt = 50 + max(124, para_height("\n".join(row["items"]), fx, 620, 1.5))
                rrect(d, [M - 24, y - 18, W - M + 24, y + hgt - 18], 20, fill=(48, 30, 22))
            d.text((M, y - 10), row["day"], font=fn, fill=ORANGE if hot else CREAM)
            d.text((M + 4, y + 100), row["week"], font=fw, fill=ORANGE if hot else DIM)
            yy = y + 8
            for it in row["items"]:
                yy = para(d, (M + 210, yy), it, fx, CREAM, 620, 1.5) + 8
            y = max(yy, y + 146) + 30
            if not hot and i < len(days) - 1 and not days[i + 1].get("hot"):
                d.line([(M + 210, y - 16), (W - M, y - 16)], fill=LINE, width=2)
        return y
    return _centered(p, body)


def event_photo(p, ctx):
    """上面一张活动现场照片，渐变融进夜色，下面是活动信息。"""
    from PIL import ImageOps
    img = _bg()
    ph = p.get("photo_h", 720)
    photo = ImageOps.fit(Image.open(p["image"]).convert("RGB"), (W, ph), method=Image.LANCZOS, centering=tuple(p.get("focus", (0.5, 0.5))))
    img.paste(photo, (0, 0))
    grad = Image.new("L", (1, H), 0)
    for yy in range(ph - 160, ph):
        grad.putpixel((0, yy), int(255 * ((yy - (ph - 160)) / 160) ** 1.4))
    for yy in range(ph, H):
        grad.putpixel((0, yy), 255)
    img = Image.composite(_bg(), img, grad.resize((W, H)))
    d = ImageDraw.Draw(img)
    y = ph - 40
    if p.get("label"):
        d.text((M, y), p["label"], font=F("sans", "bold", 30), fill=ORANGE)
        y += 54
    for line in p.get("headline", []):
        f = fit("serif", "black", line, 860, 76, 48)
        d.text((M, y), line, font=f, fill=CREAM)
        y += int(f.size * 1.3)
    if p.get("when"):
        f = fit("sans", "black", p["when"], 860, 52, 38)
        d.text((M, y + 4), p["when"], font=f, fill=ORANGE)
        y += int(f.size * 1.6)
    fl, fv = F("sans", "bold", 32), F("sans", "regular", 34)
    for k, v in p.get("facts", []):
        d.text((M, y + 2), k, font=fl, fill=DIM)
        y = para(d, (M + 130, y), v, fv, CREAM, 730, 1.45) + 12
    y += 16
    fb = F("sans", "regular", 34)
    for b in p.get("points", []):
        d.ellipse([M, y + 17, M + 13, y + 30], fill=ORANGE)
        y = para(d, (M + 34, y), b, fb, CREAM, 826, 1.45) + 14
    return img


THEMES = {
    "metro": {"NIGHT": (243, 246, 245), "ORANGE": (0, 122, 122), "DIM": (96, 108, 108), "LINE": (208, 220, 218),
              "CREAM": (22, 30, 30)},
    "italia": {"NIGHT": (246, 240, 228), "ORANGE": (196, 38, 46), "DIM": (110, 100, 90), "LINE": (220, 210, 196),
               "CREAM": (28, 26, 24), "ACCENT2": (0, 120, 72)},
}


def _themed(fn):
    """按 p["theme"] 临时换一套配色，画完恢复。"""
    def wrap(p, ctx):
        t = THEMES.get(p.get("theme"))
        if not t:
            return fn(p, ctx)
        g = globals()
        old = {k: g[k] for k in t if k in g}
        g.update(t)
        try:
            return fn(p, ctx)
        finally:
            g.update(old)
    return wrap


REGISTRY = {k: _themed(v) for k, v in {"cover_halloween": cover_halloween, "event_card": event_card, "list_card": list_card, "calendar_card": calendar_card, "event_photo": event_photo}.items()}
