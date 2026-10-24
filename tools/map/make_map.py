import sys, json
sys.path.insert(0, '.')
import tiles
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"b": "NotoSansCJK-Bold.ttc", "k": "NotoSansCJK-Black.ttc", "m": "NotoSansCJK-Medium.ttc"}[w], s, index=2)
INTER = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf", 26)
RED, TEAL, INK = (214, 69, 65), (0, 128, 128), (25, 28, 30)
vs = json.load(open("final.json"))
col = lambda v: RED if v["cat"] == "r" else TEAL

def soften(img):
    img = ImageEnhance.Color(img).enhance(0.45)
    return Image.blend(img, Image.new("RGB", img.size, (250, 248, 244)), 0.28)

def pin(d, x, y, n, c, r=21):
    d.ellipse([x - r - 3, y - r - 3, x + r + 3, y + r + 3], fill="white")
    d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    t = str(n); f = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf", 24 if n < 10 else 21)
    d.text((x - f.getlength(t) / 2, y - 15), t, font=f, fill="white")

def label(d, x, y, text, side="r", f=None):
    f = f or F("b", 26)
    tw = f.getlength(text); pad = 10
    if side == "r": bx = x + 30
    elif side == "l": bx = x - 30 - tw - 2 * pad
    by = y - 22
    d.rounded_rectangle([bx, by, bx + tw + 2 * pad, by + 44], 10, fill="white", outline=(210, 205, 198), width=2)
    d.text((bx + pad, by + 5), text, font=f, fill=INK)

# ---------- 主图 ----------
MAP_H = 1010
lats = [v["lat"] for v in vs]; lons = [v["lon"] for v in vs]
clat = (min(lats) + max(lats)) / 2 + 0.0002; clon = (min(lons) + max(lons)) / 2 + 0.0003
main, px = tiles.render(clat, clon, 16, W, MAP_H, scale=0.74)
main = soften(main)
canvas = Image.new("RGB", (W, H), (250, 248, 244))
canvas.paste(main, (0, 0))
d = ImageDraw.Draw(canvas)
groups = {"bhq": [v for v in vs if v.get("grp") == "bhq"], "mbr": [v for v in vs if v.get("grp") == "mbr"]}
side = {1: "r", 10: "l", 11: "r", 12: "r", 13: "r"}
for v in vs:
    if v.get("grp"): continue
    x, y = px(v["lat"], v["lon"])
    pin(d, x, y, v["n"], col(v)); label(d, x, y, v["name"], side[v["n"]])
gpos = {}
for g, members in groups.items():
    gx = sum(px(m["lat"], m["lon"])[0] for m in members) / len(members)
    gy = sum(px(m["lat"], m["lon"])[1] for m in members) / len(members)
    gpos[g] = (gx, gy)
    d.ellipse([gx - 34, gy - 34, gx + 34, gy + 34], fill=(255, 255, 255), outline=INK, width=4)
    t = "A" if g == "bhq" else "B"
    f = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", 36)
    d.text((gx - f.getlength(t) / 2, gy - 23), t, font=f, fill=INK)
    label(d, gx, gy + 2, "Bakehouse Quarter｜4家" if g == "bhq" else "Majors Bay Road｜4家", "r" if g == "bhq" else "l")
# 标题
tf = F("k", 46)
TY = 215
d.rounded_rectangle([M0 := 372, TY, M0 + 560, TY + 150], 18, fill=(255, 255, 255), outline=(210, 205, 198), width=2)
d.text((M0 + 26, TY + 14), "Concord一带吃什么", font=tf, fill=INK)
lf = F("m", 24)
lx, ly = M0 + 28, TY + 92
for c, t in [(RED, "餐厅"), (TEAL, "咖啡店")]:
    d.ellipse([lx, ly + 6, lx + 22, ly + 28], fill=c); d.text((lx + 30, ly), t, font=lf, fill=INK); lx += 150
d.text((W - 190, MAP_H - 30), "© OpenStreetMap", font=F("m", 18), fill=(110, 105, 98))
d.line([(0, MAP_H), (W, MAP_H)], fill=(220, 214, 206), width=3)

# ---------- 两张放大图 ----------
def inset(members, z, scale, box, title, letter, offsets):
    x0, y0, w, h = box
    clat = (max(m["lat"] for m in members) + min(m["lat"] for m in members)) / 2
    clon = (max(m["lon"] for m in members) + min(m["lon"] for m in members)) / 2
    im, ipx = tiles.render(clat + offsets.get("dlat", 0), clon + offsets.get("dlon", 0), z, w, h, scale=scale)
    im = soften(im)
    canvas.paste(im, (x0, y0))
    dd = ImageDraw.Draw(canvas)
    dd.rectangle([x0, y0, x0 + w - 1, y0 + h - 1], outline=(200, 194, 186), width=3)
    f = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", 30)
    dd.ellipse([x0 + 16, y0 + 14, x0 + 62, y0 + 60], fill="white", outline=INK, width=3)
    dd.text((x0 + 39 - f.getlength(letter) / 2, y0 + 17), letter, font=f, fill=INK)
    tf = F("b", 25); tw = tf.getlength(title)
    dd.rounded_rectangle([x0 + 70, y0 + 16, x0 + 70 + tw + 20, y0 + 58], 10, fill="white")
    dd.text((x0 + 80, y0 + 20), title, font=tf, fill=INK)
    for m in members:
        mx, my = ipx(m["lat"], m["lon"]); mx += x0; my += y0
        pin(dd, mx, my, m["n"], col(m), r=19)
        lab = offsets["labels"][m["n"]]
        f2 = F("b", 22); t = m["name"]; tw2 = f2.getlength(t)
        if lab == "r": bx, by = mx + 26, my - 19
        elif lab == "l": bx, by = mx - 26 - tw2 - 16, my - 19
        elif lab == "u": bx, by = mx - (tw2 + 16) / 2, my - 66
        else: bx, by = mx - (tw2 + 16) / 2, my + 26
        dd.rounded_rectangle([bx, by, bx + tw2 + 16, by + 38], 8, fill="white", outline=(210, 205, 198), width=2)
        dd.text((bx + 8, by + 4), t, font=f2, fill=INK)
    return im

GAP = 14
iw = (W - 3 * GAP) // 2; ih = H - MAP_H - 2 * GAP
inset(groups["bhq"], 18, 1.35, (GAP, MAP_H + GAP, iw, ih), "Bakehouse Quarter", "A",
      {"labels": {2: "d", 3: "u", 4: "u", 5: "d"}, "dlat": 0.00003})
inset(groups["mbr"], 19, 1.0, (2 * GAP + iw, MAP_H + GAP, iw, ih), "Majors Bay Road", "B",
      {"labels": {6: "l", 7: "r", 8: "l", 9: "r"}, "dlat": 0.0, "dlon": 0.00005})
canvas.save("concord_map.png")
print("ok", gpos)
