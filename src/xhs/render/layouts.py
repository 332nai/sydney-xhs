"""十种版式。每个函数接收稿件数据，返回一张 1000x1500 的图。
新增版式：写一个函数，再在 planner.py 的 FAMILIES 里登记。"""
import math
from datetime import date

from PIL import Image, ImageDraw, ImageFilter

from .. import config
from .base import *  # noqa: F401,F403

BODY = config.settings()["render"]["body_size"]
FACT_LABELS = [("address", "地址"), ("hours", "营业"), ("price", "价格"), ("team", "团队"), ("opened", "开业")]


def brand(d, color, y=1420, align="left"):
    if not config.settings().get("show_brand", True):
        return
    y = min(y, H - 43)
    f = F("sans", "medium", 22)
    t = config.settings()["account_name"]
    x = M if align == "left" else W - M - tw(f, t)
    d.text((x, y), t, font=f, fill=color)


def headline_block(d, lines, x, y, maxw, kind, weight, start, minimum, fill, gap=1.12):
    for ln in lines:
        f = fit(kind, weight, ln, maxw, start, minimum)
        d.text((x, y), ln, font=f, fill=fill)
        y += int(f.size * gap)
    return y


def bullets(d, items, x, y, maxw, fill, dot, font=None, gap=10):
    font = font or F("sans", "regular", BODY)
    for it in items:
        d.ellipse([x + 4, y + 16, x + 16, y + 28], fill=dot)
        y = para(d, (x + 36, y), it, font, fill, maxw - 36, 1.45) + gap
    return y


def fact_rows(d, facts, x, y, label_col, text_col, maxw=860):
    f_l, f_v = F("sans", "bold", BODY), F("sans", "regular", BODY)
    for key, label in FACT_LABELS:
        v = (facts or {}).get(key)
        if not v:
            continue
        d.text((x, y), label, font=f_l, fill=label_col)
        y = para(d, (x + 110, y), str(v), f_v, text_col, maxw - 110, 1.45) + 14
    return y


# ------------------------------------------------------------------ 封面：杂志目录
def cover(issue, ctx):
    img = paper(CREAM); d = ImageDraw.Draw(img)
    s = config.settings()
    d.text((M, 70), s["account_name"], font=F("sans", "bold", 28), fill=INK)
    t = f"周报 No.{issue['issue_no']:02d}"
    d.text((W - M - tw(F("sans", "medium", 28), t), 70), t, font=F("sans", "medium", 28), fill=INK)
    d.line([(M, 120), (W - M, 120)], fill=INK, width=3); d.line([(M, 128), (W - M, 128)], fill=INK, width=1)

    l1, l2 = (issue["cover"]["headline_lines"] + ["", ""])[:2]
    hl = issue["cover"].get("highlight", "")
    hf = fit("serif", "black", l1, 860, 150, 90)
    d.text((62, 170), l1, font=hf, fill=INK)
    x, y2 = 62, 170 + int(hf.size * 1.17)
    if hl and hl in l2:
        a, b = l2.split(hl, 1)
        d.text((x, y2), a, font=hf, fill=INK); x += tw(hf, a)
        nf = F("inter", "Black", int(hf.size * 1.4))
        d.text((x + 6, y2 - int(hf.size * 0.18)), hl, font=nf, fill=CORAL); x += tw(nf, hl) + 16
        d.text((x, y2), b, font=hf, fill=INK)
    else:
        d.text((x, y2), l2, font=hf, fill=INK)

    sticker = [s_ for s_ in issue["cover"].get("sticker", []) if s_][:3]
    if sticker:
        r = 92
        st = Image.new("RGBA", (2 * r + 20, 2 * r + 20), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.ellipse([10, 10, 10 + 2 * r, 10 + 2 * r], fill=CORAL)
        sd.ellipse([20, 20, 2 * r, 2 * r], outline=CREAM, width=2)
        for i, line in enumerate(sticker):
            f = fit("sans", "black", line, 150, 40, 24)
            sd.text((10 + r - tw(f, line) / 2, 38 + i * 44), line, font=f, fill=CREAM)
        st = st.rotate(-12, resample=Image.BICUBIC, expand=True)
        img.paste(st, (850 - st.width // 2, 585 - st.height // 2), st)

    d.line([(M, 590), (W - M, 590)], fill=INK, width=1)
    y = 625
    groups = [("社区", [i for i in issue["items"] if i["kind"] != "venue"]), ("新店", [i for i in issue["items"] if i["kind"] == "venue"])]
    n_rows = sum(len(g) for _, g in groups)
    step = 66 if n_rows <= 9 else 56
    for g, items in groups:
        if not items:
            continue
        d.text((M, y), g, font=F("sans", "black", 30), fill=CORAL); y += 56
        for it in items:
            d.text((M, y + 2), f"{it['num']:02d}", font=F("inter", "Bold", 30), fill=CORAL)
            f = fit("sans", "medium", it.get("toc", ""), 760, BODY + 4, 24)
            d.text((140, y), it.get("toc", ""), font=f, fill=INK)
            y += step
        y += 22
    d.line([(M, 1395), (W - M, 1395)], fill=INK, width=1)
    pub = date.fromisoformat(issue["publish_date"])
    d.text((M, 1418), f"{pub.year}年{pub.month}月{pub.day}日  ·  向右滑看地图", font=F("sans", "regular", 24), fill=GREY)
    return img


# ------------------------------------------------------------------ 本期地图
def _project(points, box):
    lats = [p[0] for p in points]; lons = [p[1] for p in points]
    lat0, lat1, lon0, lon1 = min(lats), max(lats), min(lons), max(lons)
    pad_lat = max((lat1 - lat0) * 0.12, 0.006); pad_lon = max((lon1 - lon0) * 0.12, 0.006)
    lat0, lat1, lon0, lon1 = lat0 - pad_lat, lat1 + pad_lat, lon0 - pad_lon, lon1 + pad_lon
    x0, y0, x1, y1 = box
    kx = math.cos(math.radians(-33.87))
    sx = (x1 - x0) / ((lon1 - lon0) * kx); sy = (y1 - y0) / (lat1 - lat0)
    s = min(sx, sy)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    mlat, mlon = (lat0 + lat1) / 2, (lon0 + lon1) / 2
    proj = lambda lat, lon: (cx + (lon - mlon) * kx * s, cy - (lat - mlat) * s)
    proj.px_per_km = s / 111.0
    return proj


def map_card(issue, ctx):
    coords = config.load("suburb_coords")
    img = paper((234, 240, 233)); d = ImageDraw.Draw(img)
    n = len(issue["items"])
    d.text((M, 80), f"本期{n}件事", font=F("serif", "black", 76), fill=INK)
    d.text((M, 182), "都发生在这张图上", font=F("serif", "bold", 46), fill=INK)
    subs = []
    for it in issue["items"]:
        s = it.get("suburb")
        if s in coords and s not in subs:
            subs.append(s)
    pts = [coords["CBD"]] + [coords[s] for s in subs]
    proj = _project(pts, (130, 330, 870, 1240))
    occupied = []

    labels = []

    def free(box):
        return all(box[2] < o[0] or box[0] > o[2] or box[3] < o[1] or box[1] > o[3] for o in occupied)

    def line_clear(x1, y1, x2, y2):
        for t in (0.35, 0.5, 0.65, 0.8):
            px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
            if any(b[0] < px < b[2] and b[1] < py < b[3] for b in labels):
                return False
        return True

    cx, cy = proj(*coords["CBD"])
    # 以 CBD 为圆心的距离圈，帮助读者判断远近
    ring_col, rf = (200, 210, 200), F("inter", "Medium", 22)
    for km in (2, 5, 10, 15):
        r = km * proj.px_per_km
        if r < 60 or r > 1200:
            continue
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ring_col, width=2)
        lx, ly = cx + r * 0.7071 + 6, cy + r * 0.7071 - 4
        if 40 < lx < W - 80 and 280 < ly < 1280:
            d.text((lx, ly), f"{km} km", font=rf, fill=(150, 160, 150))
    d.regular_polygon((cx, cy, 16), 4, rotation=45, fill=INK)
    d.text((cx + 22, cy - 16), "CBD", font=F("inter", "Bold", 28), fill=INK)
    occupied.append((cx - 20, cy - 20, cx + 90, cy + 20))
    lf = F("inter", "SemiBold", 26)
    pos = {}
    for s in subs:
        x, y = proj(*coords[s])
        pos[s] = (x, y)
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=INK)
        wlab = tw(lf, s)
        lx = x + 18 if x + 18 + wlab < W - 40 else x - 18 - wlab
        d.text((lx, y - 16), s, font=lf, fill=INK)
        occupied.append((lx - 4, y - 18, lx + wlab + 4, y + 18))
        labels.append((lx - 4, y - 18, lx + wlab + 4, y + 18))
        occupied.append((x - 10, y - 10, x + 10, y + 10))
    pf = F("inter", "Bold", 24)
    dirs = [(0, -72), (60, -60), (72, 0), (60, 60), (0, 72), (-60, 60), (-72, 0), (-60, -60), (0, -110), (110, 0), (0, 110), (-110, 0)]
    for it in issue["items"]:
        s = it.get("suburb")
        if s not in pos:
            continue
        x, y = pos[s]
        col = NAVY if it["kind"] == "venue" else CORAL
        for dx, dy in dirs:
            px, py = x + dx, y + dy
            box = (px - 26, py - 26, px + 26, py + 26)
            if free(box) and line_clear(x, y, px, py) and 40 < px < W - 40 and 280 < py < 1280:
                break
        occupied.append(box)
        d.line([(x, y), (px, py)], fill=col, width=2)
        d.ellipse([px - 24, py - 24, px + 24, py + 24], fill=col)
        num = f"{it['num']:02d}"
        d.text((px - tw(pf, num) / 2, py - 15), num, font=pf, fill=CREAM)
    y = 1330
    d.ellipse([M, y, M + 30, y + 30], fill=CORAL); d.text((M + 44, y - 2), "社区动态", font=F("sans", "medium", 26), fill=INK)
    d.ellipse([380, y, 410, y + 30], fill=NAVY); d.text((424, y - 2), "新店", font=F("sans", "medium", 26), fill=INK)
    brand(d, GREY, y=1400, align="right")
    return img


# ------------------------------------------------------------------ 报纸剪报
def clipping(it, ctx):
    img = paper(NEWS, grain=18); d = ImageDraw.Draw(img)
    d.text((M, 70), "本周快报", font=F("serif", "black", 40), fill=INK)
    k = kicker_text(it)
    d.text((W - M - tw(F("sans", "bold", 24), k), 84), k, font=F("sans", "bold", 24), fill=NEWSRED)
    d.line([(M, 135), (W - M, 135)], fill=INK, width=4); d.line([(M, 143), (W - M, 143)], fill=INK, width=1)
    y = headline_block(d, it.get("headline", []), M, 180, 860, "serif", "black", 84, 56, INK, 1.3)
    y = para(d, (M, y + 10), it.get("lede", ""), F("serif", "medium", 34), INK, 860, 1.5) + 30
    body = F("serif", "regular", BODY)
    if it.get("date_badge"):
        by = y
        d.rectangle([M, by, M + 330, by + 300], outline=INK, width=3)
        vf = fit("inter", "Black", it["date_badge"]["value"], 280, 110, 60)
        d.text((M + 26, by + 22), it["date_badge"]["value"], font=vf, fill=NEWSRED)
        lab = it["date_badge"]["label"].split(" ", 1)
        d.text((M + 30, by + 160), lab[0], font=fit("sans", "black", lab[0], 270, 54, 30), fill=INK)
        if len(lab) > 1:
            d.text((M + 30, by + 232), lab[1], font=fit("sans", "medium", lab[1], 270, 34, 22), fill=INK)
        cx = 440
        yy = by
        for p in it.get("points", []):
            yy = para(d, (cx, yy), p, body, INK, 490) + 14
        d.line([(cx - 20, by), (cx - 20, max(yy, by + 300))], fill=INK, width=1)
        y = max(yy, by + 320) + 30
    else:
        for p in it.get("points", []):
            y = para(d, (M, y), "■ " + p, body, INK, 860) + 12
        y += 18
    if it.get("impact"):
        d.line([(M, y), (W - M, y)], fill=INK, width=2)
        d.text((M, y + 24), "对周边居民的影响", font=F("serif", "bold", 38), fill=INK)
        para(d, (M, y + 90), it["impact"], body, INK, 860)
    brand(d, GREY, y=1410, align="right")
    return img


# ------------------------------------------------------------------ 前后对比
T4 = (0, 90, 163)


def _chip(d, x, y, text, col, f, pad=18, h=54):
    w = tw(f, text) + pad * 2
    rrect(d, [x, y, x + w, y + h], h // 2, fill=col)
    d.text((x + pad, y + (h - f.size) / 2 - 6), text, font=f, fill=WHITE)
    return x + w


def before_after(it, ctx):
    img = paper(NAVY, grain=8); d = ImageDraw.Draw(img)
    d.text((M, 80), kicker_text(it), font=F("sans", "bold", 26), fill=CORAL)
    hl = it.get("headline", [])
    if hl:
        d.text((M, 130), hl[0], font=fit("sans", "black", hl[0], 860, 110, 60), fill=CORAL)
    if len(hl) > 1:
        d.text((M, 270), hl[1], font=fit("sans", "bold", hl[1], 860, 62, 40), fill=CREAM)
    rows = it.get("before_after", [])[:5]
    y = 400
    rh = 132 if len(rows) <= 4 else 112
    cf = F("sans", "bold", 28)
    for r in rows:
        rrect(d, [M, y, W - M, y + rh], 20, fill=(36, 54, 82))
        d.text((100, y + 14), r["name"], font=F("inter", "Bold", 42), fill=CREAM)
        cy = y + rh - 64
        x = _chip(d, 100, cy, r.get("before", ""), (150, 60, 55), cf)
        if r.get("after"):
            d.text((x + 16, cy + 2), "→", font=F("inter", "Bold", 36), fill=CREAM)
            _chip(d, x + 64, cy, r["after"], T4, cf)
        elif r.get("note"):
            d.text((x + 22, cy + 8), r["note"], font=F("sans", "regular", 28), fill=SAND)
        y += rh + 16
    if it.get("points"):
        y += 10
        d.text((M, y), "其他变化", font=F("sans", "bold", 34), fill=CORAL); y += 58
        y = bullets(d, it["points"], M, y, 860, CREAM, CORAL)
    if it.get("impact"):
        h = para_height(it["impact"], F("sans", "medium", BODY), 800) + 50
        top = max(y + 20, 1385 - h)
        rrect(d, [M, top, W - M, top + h], 16, outline=SAND, width=2)
        para(d, (100, top + 22), it["impact"], F("sans", "medium", BODY), SAND, 800, 1.45)
    return img


# ------------------------------------------------------------------ 数据海报
NUMBER_PALETTES = [
    {"bg": MUSTARD, "ink": INK, "num": CREAM, "num2": INK, "accent": INK},
    {"bg": TEAL, "ink": WHITE, "num": SAND, "num2": SAND, "accent": SAND},
    {"bg": (233, 226, 244), "ink": INK, "num": (92, 63, 160), "num2": INK, "accent": (92, 63, 160)},
]


def _number_body(d, it, pal, y):
    bn = it["big_number"]
    size = 220
    while size > 120 and mixed_width(bn["value"], size) > 860:
        size -= 8
    draw_mixed(d, (60, y), bn["value"], size, pal["num"])
    y += int(size * 1.12)
    y = para(d, (76, y), bn["label"], F("sans", "medium", BODY), pal["ink"], 840) + 30
    d.line([(M, y), (W - M, y)], fill=pal["accent"], width=2); y += 30
    if it.get("kind") == "venue" and it.get("facts"):
        y = fact_rows(d, it["facts"], M, y, pal["accent"], pal["ink"]) + 10
    else:
        y = bullets(d, it.get("points", []), M, y, 860, pal["ink"], pal["accent"])
    if it.get("explainer") or it.get("impact"):
        y = para(d, (M, y + 10), it.get("explainer") or it.get("impact"), F("sans", "regular", BODY), pal["ink"], 860)
    return y


def number_poster(it, ctx):
    pal = NUMBER_PALETTES[ctx["variant"] % len(NUMBER_PALETTES)]
    img = paper(pal["bg"], grain=10); d = ImageDraw.Draw(img)
    d.text((M, 80), kicker_text(it), font=F("sans", "bold", 26), fill=pal["ink"])
    y = headline_block(d, it.get("headline", []), M, 128, 860, "sans", "black", 76, 48, pal["ink"], 1.3)
    y = para(d, (M, y + 10), it.get("lede", ""), F("sans", "regular", BODY), pal["ink"], 860) + 30
    scratch = ImageDraw.Draw(Image.new("RGB", (W, H * 2)))
    h = _number_body(scratch, it, pal, 0)
    free_space = H - 120 - y - h
    _number_body(d, it, pal, y + max(0, int(free_space * 0.45)))
    brand(d, pal["ink"], y=1420)
    return img


# ------------------------------------------------------------------ 问答卡
def qa_cards(it, ctx):
    img = paper((247, 243, 236)); d = ImageDraw.Draw(img)
    d.text((M, 80), kicker_text(it), font=F("sans", "bold", 26), fill=CORAL)
    hl = it.get("headline", [])
    y = 128
    if len(hl) > 1:
        d.text((M, y), hl[0], font=fit("serif", "bold", hl[0], 640, 54, 36), fill=INK); y += 82
        d.text((M, y), hl[1], font=fit("serif", "black", hl[1], 660, 92, 56), fill=INK); y += 140
    elif hl:
        d.text((M, y), hl[0], font=fit("serif", "black", hl[0], 660, 92, 56), fill=INK); y += 140
    if it.get("date_badge"):
        st = Image.new("RGBA", (260, 260), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.ellipse([10, 10, 250, 250], outline=NEWSRED, width=6); sd.ellipse([26, 26, 234, 234], outline=NEWSRED, width=2)
        v = it["date_badge"]["value"]; lab = it["date_badge"]["label"][:5]
        vf = fit("inter", "Black", v, 190, 64, 36); lf = fit("sans", "black", lab, 190, 36, 22)
        sd.text((130 - tw(vf, v) / 2, 66), v, font=vf, fill=NEWSRED)
        sd.text((130 - tw(lf, lab) / 2, 150), lab, font=lf, fill=NEWSRED)
        st = st.rotate(14, resample=Image.BICUBIC, expand=True)
        img.paste(st, (745, 30), st)
    y = max(y, 360)
    cols = [WHITE, (234, 240, 233), WHITE]
    body = F("sans", "regular", BODY)
    for i, qa in enumerate(it.get("qa", [])[:3]):
        h = 90 + para_height(qa["a"], body, 720) + 30
        rrect(d, [M, y, W - M, y + h], 22, fill=cols[i % 3], outline=(220, 214, 204), width=2)
        d.text((100, y + 22), "Q", font=F("lora", "Bold", 64), fill=CORAL)
        d.text((170, y + 34), qa["q"], font=F("sans", "bold", 36), fill=INK)
        para(d, (170, y + 96), qa["a"], body, (60, 58, 55), 720)
        y += h + 26
    brand(d, GREY, y=1420)
    return img


# ------------------------------------------------------------------ 照片海报
def photo_poster(it, ctx):
    img = Image.new("RGB", (W, H), CREAM)
    ph = 740
    img.paste(cover_crop(it["image"]["path"], (W, ph)), (0, 0))
    d = ImageDraw.Draw(img)
    k = kicker_text(it)
    kf = F("sans", "bold", 26)
    rrect(d, [M - 16, 64, M + tw(kf, k) + 16, 112], 24, fill=(20, 20, 20))
    d.text((M, 70), k, font=kf, fill=CREAM)
    img = Image.blend(img, img, 0)  # 保持照片原样，不加滤镜
    d = ImageDraw.Draw(img)
    y = ph + 40
    title = " ".join(it.get("headline", []))
    tf = fit("sans", "black", title, 860, 64, 40)
    d.text((M, y), title, font=tf, fill=INK); y += int(tf.size * 1.6)
    y = para(d, (M, y), it.get("lede", ""), F("sans", "regular", BODY), (60, 58, 55), 860, 1.5, max_lines=2) + 20
    if it.get("kind") == "venue":
        y = fact_rows(d, it.get("facts"), M, y, CORAL, INK)
    else:
        y = bullets(d, it.get("points", [])[:3], M, y, 860, INK, CORAL)
    if it.get("explainer") and y < H - 130:
        para(d, (M, y + 6), it["explainer"], F("sans", "regular", BODY), (90, 84, 76), 860, 1.45, max_lines=2)
    return img


# ------------------------------------------------------------------ 色带海报（没有照片的新店）
BAND_SETS = [
    [(196, 48, 43), (226, 120, 58), (222, 170, 64), (60, 92, 160), (226, 120, 58), (196, 48, 43)],
    [(42, 74, 62), (118, 140, 96), (214, 196, 150), (180, 92, 60), (118, 140, 96), (42, 74, 62)],
    [(30, 40, 70), (70, 96, 150), (200, 180, 220), (230, 140, 120), (70, 96, 150), (30, 40, 70)],
]


def band_poster(it, ctx):
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
    bands = BAND_SETS[ctx["variant"] % len(BAND_SETS)]
    bw = W / len(bands)
    for i, c in enumerate(bands):
        d.rectangle([i * bw, 0, (i + 1) * bw, 860], fill=c)
    ov = Image.new("RGBA", (W, 860), (20, 12, 10, 80)); img.paste(ov, (0, 0), ov); d = ImageDraw.Draw(img)
    d.text((M, 80), kicker_text(it), font=F("sans", "bold", 28), fill=CREAM)
    name = (it.get("facts") or {}).get("name") or (it.get("headline") or [""])[0]
    nf = fit("lora", "Bold", name, 880, 300, 110)
    d.text((54, 480 - nf.size), name, font=nf, fill=CREAM)
    hl = " ".join(h for h in it.get("headline", []) if h != name)
    if hl:
        d.text((M, 620), hl, font=fit("sans", "black", hl, 860, 56, 36), fill=CREAM)
    para(d, (M, 708), it.get("lede", ""), F("sans", "medium", 34), CREAM, 860, 1.4, max_lines=2)
    y = fact_rows(d, it.get("facts"), M, 920, CORAL, INK)
    if it.get("explainer"):
        d.line([(M, y + 10), (W - M, y + 10)], fill=(210, 200, 185), width=2)
        para(d, (M, y + 36), it["explainer"], F("sans", "regular", BODY), (70, 66, 60), 860)
    return img


# ------------------------------------------------------------------ 拍立得拼贴（几家新店合在一张）
STAMP_COLS = [(196, 120, 40), (150, 40, 40), (40, 70, 60)]


def _polaroid(it, col, rot):
    pw, ph = 430, 560
    p = Image.new("RGBA", (pw, ph), (252, 250, 245, 255)); pd = ImageDraw.Draw(p)
    if it.get("image", {}).get("path"):
        p.paste(cover_crop(it["image"]["path"], (pw - 44, 308)), (22, 22))
    else:
        pd.rectangle([22, 22, pw - 22, 330], fill=col)
        stamp = it.get("kicker") or it.get("suburb", "")
        sf = fit("sans", "black", stamp, pw - 80, 76, 40)
        pd.text((pw / 2 - tw(sf, stamp) / 2, 140), stamp, font=sf, fill=CREAM)
    name = (it.get("facts") or {}).get("name") or " ".join(it.get("headline", []))
    pd.text((28, 346), name, font=fit("inter", "Bold", name, pw - 56, 34, 22), fill=INK)
    addr = (it.get("facts") or {}).get("address", "")
    cap = f"{it.get('suburb', '')}｜{it.get('lede', '')}" + (f" {addr}" if addr else "")
    para(pd, (28, 398), cap, F("serif", "regular", 24), (60, 58, 55), pw - 56, 1.5, max_lines=4)
    sh = Image.new("RGBA", (pw + 40, ph + 40), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([20, 26, pw + 20, ph + 26], fill=(0, 0, 0, 60))
    sh = sh.filter(ImageFilter.GaussianBlur(10)); sh.paste(p, (20, 20), p)
    return sh.rotate(rot, resample=Image.BICUBIC, expand=True)


def polaroids(items, ctx):
    img = paper((205, 184, 154), grain=24); d = ImageDraw.Draw(img)
    nums = [i["num"] for i in items]
    head = f"新店 {nums[0]:02d}" + (f" 至 {nums[-1]:02d}" if len(nums) > 1 else "")
    d.text((M, 70), head, font=F("sans", "bold", 28), fill=INK)
    cn = {1: "一", 2: "两", 3: "三"}[len(items)]
    d.text((M, 115), f"{cn}家值得顺路去的", font=F("serif", "black", 68), fill=INK)
    spots = [(34, 220, -5), (488, 250, 4), (270, 830, -2)] if len(items) == 3 else [(34, 300, -4), (488, 700, 3)][:len(items)]
    for it, (x, y, r), col in zip(items, spots, STAMP_COLS):
        pol = _polaroid(it, col, r)
        img.paste(pol, (x, y), pol)
        t = Image.new("RGBA", (140, 40), (245, 238, 210, 170)).rotate(r * 1.5, expand=True)
        img.paste(t, (x + 170, y + 6), t)
    return img


# ------------------------------------------------------------------ 编辑判断
def editor(issue, ctx):
    img = paper((246, 241, 231)); d = ImageDraw.Draw(img)
    note = issue["editor_note"]
    d.rectangle([0, 0, W, 18], fill=CORAL)
    d.text((M, 90), note.get("headline", "编辑判断"), font=F("serif", "black", 80), fill=INK)
    d.line([(M, 210), (190, 210)], fill=CORAL, width=6)
    y = 250
    for i, p in enumerate(note.get("paragraphs", [])):
        f = F("serif", "bold", 40) if i == 0 else F("serif", "regular", BODY + 2)
        y = para(d, (M, y), p, f, INK if i == 0 else (50, 48, 45), 860, 1.5 if i == 0 else 1.65) + 20
    y = max(y + 20, 1100)
    rrect(d, [M, y, W - M, y + 200], 18, fill=(236, 228, 214))
    q = note.get("question", "")
    para(d, (100, y + 40), q, F("serif", "bold", 40), INK, 800, 1.4, max_lines=2)
    d.text((100, y + 140), "评论区告诉我们，下期可能就写它。", font=F("serif", "regular", BODY), fill=(70, 66, 60))
    brand(d, GREY, y=1410)
    return img
