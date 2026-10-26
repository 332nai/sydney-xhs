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
    # 帽子图例
    lf = F("b", 34); items = [("三帽 2家", 3), ("两帽 44家", 2), ("一帽 117家", 1)]
    tw_ = sum(lf.getlength(s) + 70 for s, _ in items); x = (W - tw_) / 2; y = cy + 290
    for s, h in items:
        d.rounded_rectangle([x, y, x + lf.getlength(s) + 44, y + 54], 27, fill=HAT[h])
        d.text((x + 22, y + 5), s, font=lf, fill="white"); x += lf.getlength(s) + 70
    img.save(out)


def hats_icon(d, x, y, n):
    for i in range(n):
        cx = x + i * 26
        d.polygon([(cx, y + 18), (cx + 20, y + 18), (cx + 16, y + 4), (cx + 4, y + 4)], fill=HAT[n])
        d.rectangle([cx - 3, y + 18, cx + 23, y + 22], fill=HAT[n])
    return x + n * 26 + 6


def page(entries, title, idx, total, out):
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
    d.text((56, 44), title, font=F("k", 44), fill=INK)
    pf = F("m", 24); s = f"{idx}/{total}"; d.text((W - 56 - pf.getlength(s), 58), s, font=pf, fill=(140, 130, 120))
    y = 122; n = len(entries); rowh = (H - y - 40) / n
    nf, mf, df = F("b", 30), F("m", 22), F("r", 23)
    for i, e in enumerate(entries):
        yy = y + i * rowh
        if i: d.line([(56, yy - 6), (W - 56, yy - 6)], fill=(222, 214, 200), width=1)
        x = hats_icon(d, 56, yy + 8, e["hats"])
        d.text((x + 6, yy), e["name"], font=nf, fill=INK)
        meta = f"{e['loc']}  ·  {e['price']}"
        while mf.getlength(meta) > W - 112 and len(meta) > 10: meta = meta[:-2]
        d.text((56, yy + 42), meta, font=mf, fill=HAT[e["hats"]])
        desc = e["desc"]
        while df.getlength(desc) > W - 112: desc = desc[:-2] + "…" if not desc.endswith("…") else desc[:-3] + "…"
        d.text((56, yy + 72), desc, font=df, fill=(70, 66, 62))
    img.save(out)


if __name__ == "__main__":
    data = json.load(open(sys.argv[1])); od = sys.argv[2]; os.makedirs(od, exist_ok=True)
    cover(f"{od}/01.png")
    groups = [("三帽 · 两帽 悉尼", [e for e in data if e["hats"] >= 2 and e["region"] == "悉尼"]),
              ("两帽 · NSW及ACT", [e for e in data if e["hats"] == 2 and e["region"] != "悉尼"]),
              ("一帽 · 悉尼", [e for e in data if e["hats"] == 1 and e["region"] == "悉尼"]),
              ("一帽 · NSW及ACT", [e for e in data if e["hats"] == 1 and e["region"] != "悉尼"])]
    chunks = []
    for t, es in groups:
        k = -(-len(es) // 13); per = -(-len(es) // k)
        for j in range(k): chunks.append((t, es[j * per:(j + 1) * per]))
    for i, (t, es) in enumerate(chunks, 1):
        page(es, t, i, len(chunks), f"{od}/{i + 1:02d}.png")
    print(len(chunks), [len(c[1]) for c in chunks])
