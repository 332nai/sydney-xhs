"""悉尼163家帽子餐厅：封面 + 每页13家的列表页。用法：python3 hats163.py all.json outdir"""
import sys, json, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"b": "NotoSansCJK-Bold.ttc", "k": "NotoSansCJK-Black.ttc", "m": "NotoSansCJK-Medium.ttc", "r": "NotoSansCJK-Regular.ttc"}[w], s, index=2)
P = os.path.join(os.path.dirname(__file__), "..", "data", "post_img") + "/"
INK, CREAM, DARK = (24, 24, 26), (246, 241, 232), (20, 18, 18)
HAT = {3: (196, 30, 58), 2: (226, 120, 20), 1: (40, 110, 160)}
GOLD = (240, 190, 70)


def fill(src, w, h, fx=.5, fy=.5):
    im = Image.open(src).convert("RGB")
    s = max(w / im.width, h / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    return im.crop((round(x), round(y), round(x) + w, round(y) + h))


def cover(out):
    tiles = ["gfg_sp_09.jpg", "gfg_sx_11.jpg", "gfg_se_16.jpg", "gfg_bd_41.jpg", "gfg_mu_18.jpg", "gfg_ol_02.jpg",
             "mkf_om_08.jpg", "mkf_c20_04.jpg", "af_po_pasta.jpg", "gfg_sp_03.jpg", "mkf_bb_05.jpg", "gfg_se_19.jpg"]
    img = Image.new("RGB", (W, H), DARK)
    cols, rows, g = 3, 4, 4
    cw = (W - g * (cols - 1)) // cols; ch = (H - g * (rows - 1)) // rows
    for i, t in enumerate(tiles):
        x = (i % cols) * (cw + g); y = (i // cols) * (ch + g)
        im = ImageEnhance.Color(fill(P + t, cw, ch)).enhance(1.15)
        img.paste(im, (x, y))
    # 中间压暗带
    ov = Image.new("L", (1, H))
    for yy in range(H):
        c = abs(yy - H * 0.52) / (H * 0.30)
        ov.putpixel((0, yy), int(max(0, 1 - c) ** 0.8 * 225))
    img = Image.composite(Image.new("RGB", (W, H), (10, 8, 8)), img, ov.resize((W, H)))
    d = ImageDraw.Draw(img)
    cy = int(H * 0.52)
    t1 = "悉尼今年获奖"
    f1 = F("k", 76); d.text(((W - f1.getlength(t1)) / 2, cy - 300), t1, font=f1, fill="white")
    big = "163"; fb = F("k", 330)
    bw = fb.getlength(big); unit = "家"; fu = F("k", 120)
    tx = (W - bw - fu.getlength(unit) - 10) / 2
    d.text((tx + 6, cy - 230 + 6), big, font=fb, fill=(0, 0, 0))
    d.text((tx, cy - 230), big, font=fb, fill=GOLD)
    d.text((tx + bw + 10, cy - 10), unit, font=fu, fill=GOLD)
    t2 = "帽子餐厅全在这里！"
    f2 = F("k", 92); d.text(((W - f2.getlength(t2)) / 2, cy + 150), t2, font=f2, fill="white")
    img.save(out)


def hats_icon(d, x, y, n):
    for i in range(n):
        cx = x + i * 26
        d.polygon([(cx, y + 18), (cx + 20, y + 18), (cx + 16, y + 4), (cx + 4, y + 4)], fill=HAT[n])
        d.rectangle([cx - 3, y + 18, cx + 23, y + 22], fill=HAT[n])
    return x + n * 26 + 6


AREAS = [
    ("CBD · 环形码头 · Barangaroo", ["CBD", "Circular Quay", "Barangaroo", "Circular Quay／The Rocks", "Haymarket", "Pyrmont"]),
    ("Surry Hills · Redfern · Chippendale", ["Surry Hills", "Redfern", "Chippendale", "Darlington", "Zetland"]),
    ("Darlinghurst · Potts Point · Paddington", ["Darlinghurst", "Potts Point", "Woolloomooloo", "Rushcutters Bay", "Paddington"]),
    ("Inner West · Newtown · Marrickville", ["Newtown", "Enmore", "Erskineville", "Stanmore", "Marrickville", "Summer Hill", "Balmain", "Glebe／新鱼市场"]),
    ("东区 · Double Bay · Bondi", ["Double Bay", "Rose Bay", "Bondi", "Randwick"]),
    ("北岸 · Manly · Mosman", ["Milsons Point", "North Sydney", "Mosman", "Balmoral Beach", "Manly", "Freshwater", "North Willoughby"]),
    ("大悉尼其他区域", ["Penrith", "Windsor", "Berowra Waters", "Hurstville", "Eastwood", "Wolli Creek", "North Strathfield"]),
    ("猎人谷 · 纽卡斯尔 · 中央海岸", ["Pokolbin", "Mount View", "Newcastle", "Newcastle／Wickham", "Terrigal"]),
    ("南高地 · 南海岸 · 卧龙岗", ["Burradoo", "Mittagong", "Berry", "Shoalhaven Heads", "Wollongong"]),
    ("蓝山 · Orange · Mudgee", ["Blackheath", "Megalong Valley", "Orange", "Mudgee"]),
    ("北河区 · Byron Bay", ["Byron Bay", "Byron hinterland／Nashua", "Bangalow", "Murwillumbah", "Pottsville", "Cabarita Beach", "Bellingen", "Tenterfield"]),
    ("堪培拉 · Albury", ["Canberra", "Canberra／Acton", "Canberra／Campbell", "Canberra／Kingston", "Canberra／Red Hill", "Ainslie", "Pialligo", "Albury"]),
]
ROWH, HEADH, TOP, BOT = 92, 66, 56, 30


def paginate(data):
    pages, cur, h = [], [], TOP
    for title, locs in AREAS:
        es = sorted([e for e in data if e["loc"] in locs], key=lambda e: (-e["hats"], e["name"].lower()))
        first = True
        for e in es:
            need = ROWH + (HEADH if first else 0)
            if h + need > H - BOT:
                pages.append(cur); cur, h = [], TOP; first = True; need = ROWH + HEADH
            if first:
                cur.append(("head", title + ("" if not any(x[0] == "head" and x[1].startswith(title) for p in pages for x in p) else "（续）"))); h += HEADH; first = False
            cur.append(("e", e)); h += ROWH
    pages.append(cur)
    return pages


def page(items, idx, total, out):
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
    pf = F("m", 22); s = f"{idx}/{total}"; d.text((W - 50 - pf.getlength(s), 20), s, font=pf, fill=(150, 140, 130))
    y = TOP
    nf, mf, df, hf = F("b", 32), F("m", 25), F("r", 25), F("k", 36)
    prev_e = False
    for kind, e in items:
        if kind == "head":
            d.rounded_rectangle([44, y + 6, W - 44, y + 58], 12, fill=INK)
            d.text((66, y + 9), e, font=hf, fill="white")
            y += HEADH; prev_e = False; continue
        if prev_e: d.line([(56, y - 4), (W - 56, y - 4)], fill=(222, 214, 200), width=1)
        x = hats_icon(d, 56, y + 10, e["hats"])
        d.text((x + 8, y), e["name"], font=nf, fill=INK)
        meta = f"{e['loc'].split('／')[0]}  ·  {e['price']}"
        nx = x + 8 + nf.getlength(e["name"]) + 20
        if nx + mf.getlength(meta) < W - 56:
            d.text((nx, y + 7), meta, font=mf, fill=HAT[e["hats"]]); dy = 46
        else:
            d.text((56, y + 44), meta, font=mf, fill=HAT[e["hats"]]); dy = 78
        desc = e["desc"]
        lim = W - 112
        if dy == 46:
            # 介绍最多两行
            lines, cur = [], ""
            for ch in desc:
                if df.getlength(cur + ch) > lim: lines.append(cur); cur = ch
                else: cur += ch
            lines.append(cur); lines = lines[:1]
            if len(lines[0]) < len(desc): lines[0] = lines[0][:-1] + "…"
            if len(lines) == 2 and df.getlength(lines[1]) > lim - 30: lines[1] = lines[1][:-2] + "…"
            for k, l in enumerate(lines): d.text((56, y + 46 + k * 32), l, font=df, fill=(70, 66, 62))
        else:
            while df.getlength(desc) > lim: desc = desc[:-2] + "…" if not desc.endswith("…") else desc[:-3] + "…"
            d.text((56, y + dy), desc, font=df, fill=(70, 66, 62))
        y += ROWH; prev_e = True
    img.save(out)


if __name__ == "__main__":
    data = json.load(open(sys.argv[1])); od = sys.argv[2]; os.makedirs(od, exist_ok=True)
    cover(f"{od}/01.png")
    pages = paginate(data)
    assert sum(1 for p in pages for k, _ in p if k == "e") == len(data), "missing entries"
    for i, items in enumerate(pages, 1):
        page(items, i, len(pages), f"{od}/{i + 1:02d}.png")
    chunks = pages
    print(len(chunks), [sum(1 for k,_ in c if k=='e') for c in chunks])
