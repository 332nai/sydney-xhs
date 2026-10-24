"""单篇模式的版式。每一页用哪个版式，直接写在帖子数据文件的 pages 里。"""
from PIL import Image, ImageDraw

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
    """整版照片，底部深色区放大标题。"""
    img = Image.new("RGB", (W, H), INK)
    img.paste(_img(p["image"], (W, 1060)), (0, 0))
    d = ImageDraw.Draw(img)
    if p.get("label"):
        f = F("sans", "bold", 26)
        rrect(d, [M - 16, 64, M + tw(f, p["label"]) + 16, 112], 24, fill=(20, 20, 20))
        d.text((M, 70), p["label"], font=f, fill=CREAM)
    y = 1100
    acc = p.get("accent")
    for i, line in enumerate(p.get("headline", [])):
        f = fit("sans", "black", line, 860, 96, 56)
        d.text((M, y), line, font=f, fill=CORAL if acc and acc in line and i == 0 else CREAM)
        y += int(f.size * 1.2)
    if p.get("sub"):
        para(d, (M, y + 10), p["sub"], F("sans", "medium", 32), SAND, 860, 1.4, max_lines=2)
    return img


def cover_split(p, ctx):
    """上下两张照片，中间一条标题带。"""
    img = Image.new("RGB", (W, H), CREAM)
    a, b = p["images"][:2]
    img.paste(_img(a, (W, 560)), (0, 0))
    img.paste(_img(b, (W, 560)), (0, 940))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 560, W, 940], fill=p.get("band", CREAM))
    ink = INK if not p.get("band") else CREAM
    if p.get("label"):
        d.text((M, 588), p["label"], font=F("sans", "bold", 26), fill=CORAL)
    y = 640
    for line in p.get("headline", []):
        f = fit("sans", "black", line, 860, 92, 52)
        d.text((M, y), line, font=f, fill=ink)
        y += int(f.size * 1.18)
    if p.get("sub"):
        para(d, (M, y + 6), p["sub"], F("sans", "medium", 30), ink, 860, 1.4, max_lines=1)
    tags = p.get("tags", [])
    if tags:
        f = F("sans", "bold", 26)
        for (x, yy), t in zip([(M, 500), (M, 1380)], tags):
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
    cw, ch, gap = 420, 520, 20
    for i, (im, cap) in enumerate(cells):
        x = M + (i % 2) * (cw + gap)
        yy = y + (i // 2) * (ch + 90)
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
    _compare_body(d, p, y + max(40, int((1380 - y - h) * 0.4)))
    layouts.brand(d, GREY, y=1420)
    return img


def story(p, ctx):
    """长文页：一张横幅照片加几段正文，适合讲人物故事。"""
    img = paper((246, 241, 231)); d = ImageDraw.Draw(img)
    img.paste(_img(p["image"], (W, 560)), (0, 0))
    d = ImageDraw.Draw(img)
    y = 610
    if p.get("label"):
        d.text((M, y), p["label"], font=F("sans", "bold", 26), fill=CORAL); y += 50
    for line in p.get("headline", []):
        f = fit("serif", "black", line, 860, 60, 40)
        d.text((M, y), line, font=f, fill=INK); y += int(f.size * 1.3)
    y += 16
    for para_text in p.get("paragraphs", []):
        y = para(d, (M, y), para_text, F("serif", "regular", BODY + 6), (50, 48, 45), 860, 1.7) + 26
    if p.get("quote") and y < 1200:
        d.line([(M, y + 20), (M, y + 150)], fill=CORAL, width=6)
        para(d, (M + 34, y + 24), p["quote"], F("serif", "bold", 44), INK, 820, 1.4, max_lines=2)
    layouts.brand(d, GREY, y=1420)
    return img


def closing(p, ctx):
    """结尾页：一句话总结加互动问题。"""
    img = paper(p.get("bg", NAVY), grain=8); d = ImageDraw.Draw(img)
    ink = CREAM if p.get("bg", NAVY) in (NAVY, TEAL, INK) else INK
    y = 260
    for line in p.get("headline", []):
        f = fit("serif", "black", line, 860, 80, 48)
        d.text((M, y), line, font=f, fill=ink); y += int(f.size * 1.3)
    y += 30
    for item in p.get("lines", []):
        y = para(d, (M, y), item, F("sans", "regular", BODY + 2), ink, 860, 1.6) + 14
    q = p.get("question", "")
    if q:
        top = 1120
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


REGISTRY = {"cover_photo": cover_photo, "cover_split": cover_split, "photo_grid": photo_grid, "compare": compare,
            "story": story, "closing": closing, "venue": venue, "number": number}
