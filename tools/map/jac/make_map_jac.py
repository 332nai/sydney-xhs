"""悉尼精品咖啡地图 v2：一张连续全图 + 每个区一张图。
用法：python3 make_maps2.py outdir
标签自动避让；手动微调写在 place2.json：{"图名": {"店key": [dx, dy]}}，dx/dy是标签中心相对店的位置。"""
import sys, json, os, math
sys.path.insert(0, '..')
import tiles
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"b": "NotoSansCJK-Bold.ttc", "k": "NotoSansCJK-Black.ttc", "m": "NotoSansCJK-Medium.ttc"}[w], s, index=2)
OLD, NEW, INK, BG, DARK = (118, 72, 190), (118, 72, 190), (25, 28, 30), (250, 248, 244), (44, 30, 72)
COL = {"o": OLD, "n": NEW}
ALL = []
PLACE = {}
BAND = 250
MAP_H = H - BAND


def ov(a, b):
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))


def seg_hits(p, q, r):
    """线段p→q是否穿过矩形r（采样）"""
    for i in range(1, 10):
        t = i / 10; x = p[0] + (q[0] - p[0]) * t; y = p[1] + (q[1] - p[1]) * t
        if r[0] < x < r[2] and r[1] < y < r[3]: return True
    return False


def draw_map(name, vs, bounds, line2, fs, chips, out, pad=(70, 60)):
    (la0, la1), (lo0, lo1) = bounds
    clat, clon = (la0 + la1) / 2, (lo0 + lo1) / 2
    for Z in (17, 16, 15, 14):
        x0, y0 = tiles.merc(la1, lo0, Z); x1, y1 = tiles.merc(la0, lo1, Z)
        s = min((W - 2 * pad[0]) / (x1 - x0), (MAP_H - 2 * pad[1]) / (y1 - y0))
        if s >= 0.62: break
    m, mpx = tiles.render(clat, clon, Z, W, MAP_H, scale=s)
    m = Image.blend(ImageEnhance.Color(m).enhance(0.4), Image.new("RGB", m.size, BG), 0.32)
    img = Image.new("RGB", (W, H), BG); img.paste(m, (0, 0)); d = ImageDraw.Draw(img)
    f = F("b", fs); bh = int(fs * 1.55); pr = max(6, fs // 2.4)
    for ch in chips:
        cw = f.getlength(ch["text"]) + fs * 0.8; cx, cy = ch["xy"]
        if cx < 0: cx = W - cw + cx
        ch["_r"] = (cx - 6, cy - 6, cx + cw + 6, cy + bh + 6)
    # 图例：地图左下角，小而淡
    fl = F("m", 17); LX, LY = 18, MAP_H - 44
    lw = 2 * (18 + 8 + fl.getlength("老牌")) + 22 + 20
    
    pts = {v["key"]: mpx(v["lat"], v["lon"]) for v in vs}
    pins = {k: (x - pr - 2, y - pr - 2, x + pr + 2, y + pr + 2) for k, (x, y) in pts.items()}
    # 先放周围最挤的店
    def crowd(v):
        x, y = pts[v["key"]]; return -sum(1 for q in pts.values() if abs(q[0] - x) < 160 and abs(q[1] - y) < 80)
    placed = {}; lines = []
    man = PLACE.get(name, {})
    for v in sorted(vs, key=crowd):
        k = v["key"]; x, y = pts[k]; bw = f.getlength(v["name"]) + fs * 0.8
        cands = []
        if k in man:
            dx, dy = man[k]; cands = [(x + dx - bw / 2, y + dy - bh / 2, 0)]
        else:
            g = pr + 6
            for rr in (0, 1, 2, 3, 4):
                for (ax, ay) in ((1, 0), (-1, 0), (1, -1), (-1, -1), (1, 1), (-1, 1), (0, -1), (0, 1)):
                    ex = g + rr * fs * 1.6; ey = rr * bh * 0.95 + (bh * 0.7 if ay else 0)
                    if ax == 1: bx = x + ex
                    elif ax == -1: bx = x - ex - bw
                    else: bx = x - bw / 2
                    if ay == 0: by = y - bh / 2
                    elif ay == -1: by = y - ey - bh / 2 - (g if ax == 0 else 0)
                    else: by = y + ey - bh / 2 + (g if ax == 0 else 0)
                    cands.append((bx, by, rr * 40 + (0 if ay == 0 else 8)))
        best = None
        for bx, by, pen in cands:
            bx = min(max(bx, 8), W - bw - 8); by = min(max(by, 8), MAP_H - bh - 8)
            r = (bx, by, bx + bw, by + bh)
            anchor = (r[0] if r[0] >= x else r[2] if r[2] <= x else x, (r[1] + r[3]) / 2)
            c = pen + sum(ov(r, b) for b in placed.values()) * 20 + sum(ov(r, p) for kk, p in pins.items() if kk != k) * 12
            c += ov(r, pins[k]) * 30
            c += sum(400 for b in placed.values() if seg_hits((x, y), anchor, b))
            c += sum(250 for (p, q) in lines if seg_hits(p, q, r))
            for chip in chips:
                c += ov(r, chip.get("_r", (0, 0, 0, 0))) * 20
            if best is None or c < best[0]: best = (c, r, anchor)
        placed[k] = best[1]; lines.append(((x, y), best[2]))
    for v in vs:
        k = v["key"]; x, y = pts[k]; r = placed[k]
        ax, ay = (r[0] if r[0] >= x else r[2] if r[2] <= x else x), ((r[1] + r[3]) / 2 if (r[0] >= x or r[2] <= x) else (r[3] if r[3] <= y else r[1]))
        if math.hypot(ax - x, ay - y) > pr + 4:
            d.line([(x, y), (ax, ay)], fill=COL[v["cat"]], width=2)
    for v in vs:
        r = placed[v["key"]]
        d.rounded_rectangle(r, max(5, fs // 3), fill="white", outline=COL[v["cat"]], width=2)
        d.text((r[0] + fs * 0.4, r[1] + (bh - fs) / 2 - fs * 0.18), v["name"], font=f, fill=INK)
    for v in vs:
        x, y = pts[v["key"]]
        d.ellipse([x - pr - 2, y - pr - 2, x + pr + 2, y + pr + 2], fill="white")
        d.ellipse([x - pr + 1, y - pr + 1, x + pr - 1, y + pr - 1], fill=COL[v["cat"]])
    # 图外的店：边缘提示
    for ch in chips:
        if ch.get("legend"): continue
        t = ch["text"]; bw = f.getlength(t) + fs * 0.8; bx, by = ch["xy"]
        if bx < 0: bx = W - bw + bx
        d.rounded_rectangle([bx, by, bx + bw, by + bh], max(5, fs // 3), fill="white", outline=COL[ch["cat"]], width=2)
        d.text((bx + fs * 0.4, by + (bh - fs) / 2 - fs * 0.18), t, font=f, fill=INK)
    d.text((W - 150, MAP_H - 24), "© OpenStreetMap", font=F("m", 14), fill=(115, 110, 104))
    d.rectangle([0, MAP_H, W, H], fill=DARK)
    f1 = F("k", 84)
    if line2:
        d.text((70, MAP_H + 32), "悉尼蓝花楹打卡地图", font=f1, fill="white")
        d.text((72, MAP_H + 148), line2, font=F("k", 54), fill=(200, 170, 255))
    else:
        d.text((70, MAP_H + (BAND - 84) / 2 - 18), "悉尼蓝花楹打卡地图", font=f1, fill="white")
    img.save(out)
    return {k: tuple(round(c) for c in p) for k, p in pts.items()}



if __name__ == "__main__":
    vs = [
        {"key": "k", "name": "Kirribilli · McDougall St", "lat": -33.8442, "lon": 151.2138, "cat": "o"},
        {"key": "l", "name": "Lavender Bay · 秘密花园", "lat": -33.8448, "lon": 151.2068, "cat": "o"},
        {"key": "b", "name": "皇家植物园", "lat": -33.8628, "lon": 151.2157, "cat": "o"},
        {"key": "r", "name": "First Fleet Park", "lat": -33.8608, "lon": 151.2091, "cat": "o"},
        {"key": "u", "name": "悉尼大学主楼", "lat": -33.8858, "lon": 151.1890, "cat": "o"},
        {"key": "p", "name": "Paddington · Five Ways", "lat": -33.8823, "lon": 151.2283, "cat": "o"},
        {"key": "h", "name": "Hunters Hill", "lat": -33.8348, "lon": 151.1541, "cat": "o"},
        {"key": "w", "name": "Woolloomooloo · Cathedral St", "lat": -33.8723, "lon": 151.2159, "cat": "o"},
        {"key": "g", "name": "Greenwich", "lat": -33.8385, "lon": 151.1816, "cat": "o"},
    ]
    print(draw_map("jac", vs, ((-33.8900, -33.8320), (151.1500, 151.2320)), "9个地方，花期到11月底", 20, [], sys.argv[1], (80, 70)))
