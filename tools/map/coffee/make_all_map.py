"""悉尼精品咖啡地图：一张图放全部店。上半部分CBD和Surry Hills，下半部分Inner West，两种颜色区分老牌和新秀。"""
import sys, json, os
sys.path.insert(0, '..')
import tiles
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"b": "NotoSansCJK-Bold.ttc", "k": "NotoSansCJK-Black.ttc", "m": "NotoSansCJK-Medium.ttc"}[w], s, index=2)
OLD, NEW, INK, BG = (140, 82, 44), (232, 106, 34), (25, 28, 30), (250, 248, 244)
COL = {"o": OLD, "n": NEW}
vs = json.load(open("all.json"))
place = json.load(open("all_place.json")) if os.path.exists("all_place.json") else {}
FS, BH, OFF = 17, 27, 11
f = F("b", FS)

BAND = 270
# 面板：名称, 纬度范围, 经度范围, y起点, 高度
A = dict(lat=(-33.8885, -33.8605), lon=(151.1925, 151.2300), y=0, h=700)
B = dict(lat=(-33.9150, -33.8890), lon=(151.1340, 151.2020), y=706, h=1440 - BAND - 706)

def inpanel(v, p):
    return p["lat"][0] <= v["lat"] <= p["lat"][1] and p["lon"][0] <= v["lon"] <= p["lon"][1]

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

def overlap(a, b):
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))

for p in (A, B):
    lats, lons = p["lat"], p["lon"]
    clat, clon = sum(lats) / 2, sum(lons) / 2
    best = None
    for Z in (17, 16, 15, 14):
        x0, y0 = tiles.merc(lats[1], lons[0], Z); x1, y1 = tiles.merc(lats[0], lons[1], Z)
        s = min(W / (x1 - x0), p["h"] / (y1 - y0))
        if s >= 0.7: best = (Z, s); break
    Z, s = best
    m, mpx = tiles.render(clat, clon, Z, W, p["h"], scale=s)
    m = Image.blend(ImageEnhance.Color(m).enhance(0.45), Image.new("RGB", m.size, BG), 0.30)
    img.paste(m, (0, p["y"]))
    pv = [v for v in vs if not v.get("offmap") and inpanel(v, p)]
    pts = {v["key"]: (mpx(v["lat"], v["lon"])[0], mpx(v["lat"], v["lon"])[1] + p["y"]) for v in pv}
    boxes = []
    pins = [(x - 8, y - 8, x + 8, y + 8) for x, y in pts.values()]
    order = sorted(pv, key=lambda v: pts[v["key"]][0])
    for v in order:
        x, y = pts[v["key"]]; t = v["name"]; bw = f.getlength(t) + 14
        if v["key"] in place:
            side, dy = place[v["key"]]; cands = [(side, dy)]
        else:
            cands = [(sd, dy) for dy in (0, -16, 16, -30, 30, -46, 46) for sd in ("r", "l")]
        scored = []
        for i, (sd, dy) in enumerate(cands):
            bx = x + OFF if sd == "r" else x - OFF - bw
            bx = min(max(bx, 8), W - bw - 8)
            by = min(max(y + dy - BH / 2, p["y"] + 8), p["y"] + p["h"] - BH - 8)
            r = (bx, by, bx + bw, by + BH)
            cost = sum(overlap(r, b) for b in boxes) * 3 + sum(overlap(r, q) for q in pins) * 2 + i * 6
            scored.append((cost, r))
        r = min(scored)[1]; boxes.append(r)
        # 引线
        cx = r[0] if r[0] > x else r[2]
        d.line([(x, y), (cx, (r[1] + r[3]) / 2)], fill=COL[v["cat"]], width=2)
        v["_box"] = r
    for v in pv:
        r = v["_box"]
        d.rounded_rectangle(r, 7, fill="white", outline=COL[v["cat"]], width=2)
        d.text((r[0] + 7, r[1] + 1), v["name"], font=f, fill=INK)
    for v in pv:
        x, y = pts[v["key"]]
        d.ellipse([x - 8, y - 8, x + 8, y + 8], fill="white"); d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=COL[v["cat"]])
    print({v["key"]: tuple(round(c) for c in pts[v["key"]]) for v in pv})
    missing = [v["key"] for v in vs if not v.get("offmap") and not inpanel(v, A) and not inpanel(v, B)]
    if p is B and missing: print("NOT PLACED", missing)

# 两个面板之间的分隔
d.rectangle([0, 700, W, 706], fill="white")

# 北岸的Ratio：上方边缘箭头提示
for v in vs:
    if v.get("offmap"):
        t = "↑ " + v["name"] + " · Crows Nest"; bw = f.getlength(t) + 14
        bx, by = 640, 14
        d.rounded_rectangle([bx, by, bx + bw, by + BH], 7, fill="white", outline=COL[v["cat"]], width=2)
        d.text((bx + 7, by + 1), t, font=f, fill=INK)

DARK = (24, 24, 26)
d.rectangle([0, H - BAND, W, H], fill=DARK)
f1 = F("k", 92)
d.text((70, H - BAND + 34), "悉尼精品咖啡地图", font=f1, fill=(255, 255, 255))
fl = F("b", 40)
y = H - BAND + 160
x = 74
for lab, c in (("老牌", OLD), ("新秀", NEW)):
    d.ellipse([x, y + 12, x + 30, y + 42], fill="white"); d.ellipse([x + 7, y + 19, x + 23, y + 35], fill=c)
    d.text((x + 44, y), lab, font=fl, fill=(255, 255, 255)); x += 44 + fl.getlength(lab) + 56
d.text((W - 170, H - BAND - 26), "© OpenStreetMap", font=F("m", 15), fill=(110, 105, 98))
img.save(sys.argv[1] if len(sys.argv) > 1 else "coffee_map_all.png")
