"""悉尼水果日历帖：澳洲东部卡通地图，标出主要水果产地。
用法：python3 tools/fruit_map.py 照片目录 老杨图标目录 输出目录
地图数据：data/geo/au_states.geojson"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

W, H = 1080, 1440
SRC, ICONS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
GEO = os.path.join(os.path.dirname(__file__), "..", "data", "geo", "au_states.geojson")
INK = (34, 32, 30)
def zh(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def P(lon, lat): return (40 + (lon - 124) * 29.5, 250 + (-9.5 - lat) * 33.1)

def photo(spec, r):
    spec = list(spec) if isinstance(spec, tuple) else [spec]
    name, fx, fy, z = spec + [.5, .5, 1.0][len(spec) - 1:]
    im = ImageOps.exif_transpose(Image.open(f"{SRC}/{name}")).convert("RGB")
    s = max(2 * r / im.width, 2 * r / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - r, 0), im.width - 2 * r); y = min(max(fy * im.height - r, 0), im.height - 2 * r)
    im = im.crop((round(x), round(y), round(x) + 2 * r, round(y) + 2 * r))
    return ImageEnhance.Color(im).enhance(1.12)

def icon(img, pose, x, y, h):
    ic = Image.open(f"{ICONS}/{pose}.png").convert("RGBA")
    ic = ic.resize((round(ic.width * h / ic.height), h), Image.LANCZOS)
    img = img.convert("RGBA"); sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 255), (x + 4, y + 6), ic.split()[3].point(lambda v: int(v * .3)))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8))); img.alpha_composite(ic, (x, y))
    return img.convert("RGB")

STATES = json.load(open(GEO))["features"]
LABELS = {"Queensland": ("昆士兰", 141.6, -19.2), "New South Wales": ("新州", 145.0, -31.2), "Victoria": ("维州", 143.5, -37),
          "Tasmania": ("塔州", 143.2, -42.3), "South Australia": ("南澳", 134.5, -29.5), "Northern Territory": ("北领地", 133.8, -22.5)}

# 水果：照片, 名字, 产地说明, 气泡位置, 产地点
FRUITS = [
    (("mango2/07.jpg", .22, .62, 1.7), "芒果", "北领地为主，昆士兰北部也有", (250, 520), [(130.84, -12.46), (132.26, -14.47)], (240, 160, 20)),
    ("mangosteen/02.jpg", "山竹 红毛丹", "Cairns到Townsville之间", (930, 330), [(145.92, -17.93)], (110, 50, 100)),
    ("lychee/02.jpg", "荔枝", "约99%产自昆士兰", (975, 600), [(150.6, -23.2)], (226, 86, 100)),
    ("mandarin/02.jpg", "柑橘", "Gayndah最早上市", (520, 760), [(151.61, -25.63)], (240, 140, 30)),
    ("blueberry/03.jpg", "蓝莓", "Coffs Harbour一带", (975, 870), [(153.11, -30.30)], (70, 90, 160)),
    ("cherry/03.jpg", "樱桃", "Young、维州、塔州", (480, 1170), [(148.30, -34.31), (147.0, -42.0)], (176, 30, 50)),
    ("strawberry/02.jpg", "草莓", "冬天昆士兰，夏天塔州", (960, 1230), [(147.55, -42.75)], (226, 50, 70)),
]

def render(fn, bg, sea, land, border, state_cols, chip_bg, chip_txt, title_col, sub_col, pose):
    img = Image.new("RGB", (W, H), bg)
    mp = Image.new("RGB", (W, H), sea); md = ImageDraw.Draw(mp)
    mask = Image.new("L", (W, H), 0); mk = ImageDraw.Draw(mask)
    for f in STATES:
        g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        col = state_cols.get(f["properties"]["STATE_NAME"], land) if state_cols else land
        for poly in polys:
            pts = [P(*c) for c in poly[0]]
            if len(pts) < 20: continue
            md.polygon(pts, fill=col); mk.polygon(pts, fill=255)
    for f in STATES:
        g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            pts = [P(*c) for c in poly[0]]
            if len(pts) < 20: continue
            md.line(pts + [pts[0]], fill=border, width=3, joint="curve")
    clip = Image.new("L", (W, H), 0); ImageDraw.Draw(clip).rounded_rectangle((30, 240, W - 30, H - 30), 40, fill=255)
    img.paste(mp, (0, 0), clip)
    d = ImageDraw.Draw(img)
    for k, (t, lon, lat) in LABELS.items():
        x, y = P(lon, lat); f = zh(34, "Bold"); d.text((x - f.getlength(t) / 2, y), t, font=f, fill=(*border,))
    d.text((60, 50), "悉尼吃的水果", font=zh(64), fill=title_col)
    d.text((60, 128), "从哪里来", font=zh(96), fill=title_col)
    # 连线和产地点
    for spec, name, note, (bx, by), pts, col in FRUITS:
        for lon, lat in pts:
            x, y = P(lon, lat)
            d.line((bx, by, x, y), fill=col, width=4)
    for spec, name, note, (bx, by), pts, col in FRUITS:
        r = 64
        ph = photo(spec, r); m = Image.new("L", (2 * r, 2 * r), 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
        sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).ellipse((bx - r + 3, by - r + 8, bx + r + 3, by + r + 8), fill=120)
        img.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(7))); d = ImageDraw.Draw(img)
        d.ellipse((bx - r - 7, by - r - 7, bx + r + 7, by + r + 7), fill="white")
        img.paste(ph, (bx - r, by - r), m); d = ImageDraw.Draw(img)
        f1, f2 = zh(34, "Black"), zh(24, "Bold")
        tw = max(f1.getlength(name), f2.getlength(note)) + 32
        x0 = min(max(bx - tw / 2, 40), W - 40 - tw); y0 = by + r + 6
        if name in ("蓝莓", "荔枝"): x0, y0 = bx - r - 14 - tw, by - 42
        d.rounded_rectangle((x0, y0, x0 + tw, y0 + 84), 18, fill=chip_bg)
        d.text((x0 + 16, y0 + 4), name, font=f1, fill=col)
        d.text((x0 + 16, y0 + 48), note, font=f2, fill=chip_txt)
    d = ImageDraw.Draw(img)
    for spec, name, note, (bx, by), pts, col in FRUITS:
        for lon, lat in pts:
            x, y = P(lon, lat)
            d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=col, outline="white", width=4)
    # 悉尼
    sx, sy = P(151.21, -33.87)
    d.ellipse((sx - 16, sy - 16, sx + 16, sy + 16), fill=INK, outline="white", width=5)
    f = zh(38, "Black"); d.text((sx - 104, sy - 26), "悉尼", font=f, fill=INK, stroke_width=5, stroke_fill="white")
    img = icon(img, pose, W - 250, 30, 190)
    img.save(f"{OUT}/{fn}", quality=93)

render("map_A.jpg", (248, 243, 234), (176, 214, 226), (240, 226, 196), (170, 150, 120), None, "white", (90, 84, 76), INK, None, "13_探店")
pastel = {"Queensland": (250, 214, 150), "New South Wales": (196, 224, 170), "Victoria": (170, 206, 226), "Tasmania": (240, 190, 190),
          "South Australia": (238, 200, 160), "Northern Territory": (232, 176, 140), "Western Australia": (226, 210, 170),
          "Australian Capital Territory": (196, 224, 170)}
render("map_B.jpg", (255, 244, 220), (120, 190, 214), None, (255, 255, 255), pastel, "white", (90, 84, 76), INK, None, "15_美食推荐")
print("ok")
