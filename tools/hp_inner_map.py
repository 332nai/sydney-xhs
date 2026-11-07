"""悉尼房价帖：主城区卡通地图，三种风格。
数据：Domain House Price Report 2026年6月季度（4到6月），各SA3独立屋中位价三个月的变化；Bondi一带用公寓数据。
用法：python3 tools/hp_inner_map.py 输出目录"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1080, 1440
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
CREAM = (244, 239, 230); INK = (28, 33, 45); RED = (201, 90, 74)
def zh(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def P(lon, lat): return (40 + (lon - 151.0) * 3125, 330 + (-33.70 - lat) * 3765)

COAST = [(151.33, -33.66), (151.305, -33.72), (151.30, -33.76), (151.29, -33.795), (151.305, -33.815), (151.30, -33.83),
         (151.285, -33.84), (151.285, -33.87), (151.275, -33.89), (151.26, -33.92), (151.26, -33.95), (151.245, -33.97),
         (151.25, -34.05)]
HARBOUR = [((151.285, -33.835), 70), ((151.26, -33.845), 60), ((151.235, -33.855), 46), ((151.21, -33.853), 34),
           ((151.185, -33.848), 30), ((151.16, -33.842), 26), ((151.13, -33.836), 22), ((151.10, -33.832), 18),
           ((151.075, -33.83), 14), ((151.04, -33.822), 10), ((151.00, -33.815), 8)]
MIDDLE = [((151.27, -33.832), 24), ((151.258, -33.812), 18), ((151.245, -33.80), 16), ((151.232, -33.795), 13), ((151.218, -33.785), 10), ((151.205, -33.77), 7)]
LANECOVE = [((151.165, -33.843), 13), ((151.156, -33.83), 11), ((151.148, -33.815), 9), ((151.136, -33.80), 7), ((151.13, -33.785), 5)]
COOKS = [((151.175, -33.945), 16), ((151.15, -33.925), 10), ((151.12, -33.915), 8), ((151.09, -33.92), 6)]
BOTANY = [(151.12, -34.10), (151.12, -33.975), (151.16, -33.965), (151.195, -33.965), (151.225, -33.975), (151.245, -33.99), (151.25, -34.10)]

# 名字, 经纬度, 三个月少了多少, 名字放在哪
AREAS = [("Chatswood、Lane Cove", 151.168, -33.788, 187500, "above"),
         ("North Sydney、Mosman", 151.235, -33.835, 162500, "below"),
         ("Strathfield、Burwood、Ashfield", 151.10, -33.877, 140000, "above"),
         ("Ryde、Hunters Hill", 151.098, -33.80, 120000, "below"),
         ("Marrickville、Petersham", 151.15, -33.912, 115000, "below"),
         ("Dee Why一带", 151.275, -33.745, 110500, "below"),
         ("Bondi一带（公寓）", 151.258, -33.893, 100000, "below")]

def river(d, pts, col):
    for (a, wa), (b, wb) in zip(pts, pts[1:]):
        (x0, y0), (x1, y1) = P(*a), P(*b)
        n = 12
        for i in range(n + 1):
            t = i / n; x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t; r = (wa + (wb - wa) * t) / 2
            d.ellipse((x - r, y - r, x + r, y + r), fill=col)

def land_mask():
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    d.polygon([(0, 0)] + [P(*p) for p in COAST] + [(0, H)], fill=255)
    for line in (HARBOUR, MIDDLE, LANECOVE): river(d, line, 0)
    d.polygon([P(*p) for p in BOTANY], fill=0)
    return m.filter(ImageFilter.GaussianBlur(5)).point(lambda v: 255 if v > 128 else 0)

def halo_text(img, x, y, t, f, fill, halo):
    sh = Image.new("L", img.size, 0); ImageDraw.Draw(sh).text((x, y), t, font=f, fill=255, stroke_width=6, stroke_fill=255)
    img.paste(halo, (0, 0), sh.filter(ImageFilter.GaussianBlur(1)))
    ImageDraw.Draw(img).text((x, y), t, font=f, fill=fill)

def render(bg, sea, land, outline, title_col, sub_col, bub, bub_txt, name_col, halo, style):
    img = Image.new("RGB", (W, H), bg)
    m = land_mask(); mp = Image.new("RGB", (W, H), sea); mp.paste(land, (0, 0), m)
    edge = ImageChops.subtract(m.filter(ImageFilter.MaxFilter(7)), m); mp.paste(outline, (0, 0), edge)
    clip = Image.new("L", (W, H), 0); ImageDraw.Draw(clip).rounded_rectangle((40, 320, W - 40, 1340), 40, fill=255)
    img.paste(mp, (0, 0), clip)
    d = ImageDraw.Draw(img)
    for wx, wy in [(960, 640), (975, 1000), (930, 1230)]:
        for k in range(3): d.arc((wx + k * 22, wy, wx + k * 22 + 22, wy + 18), 200, 340, fill="white", width=4)
    d.text((70, 50), "悉尼主城区", font=zh(64), fill=title_col)
    d.text((70, 130), "3个月少了多少", font=zh(96), fill=title_col)
    d.text((72, 258), "今年4到6月，独立屋中位价的变化", font=zh(34, "Medium"), fill=sub_col)
    # CBD
    x, y = P(151.207, -33.868)
    d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=name_col, outline=halo, width=3)
    halo_text(img, x - 30, y + 16, "CBD", zh(32, "Black"), name_col, halo)
    d = ImageDraw.Draw(img)
    for name, lon, lat, v, pos in AREAS:
        x, y = P(lon, lat); r = 56 + (v - 100000) / 87500 * 36
        if style == "dark":
            d.ellipse((x - r - 8, y - r - 8, x + r + 8, y + r + 8), fill=(*bub, ), outline=None)
        sh = Image.new("L", img.size, 0); ImageDraw.Draw(sh).ellipse((x - r + 4, y - r + 8, x + r + 4, y + r + 8), fill=110)
        img.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(6))); d = ImageDraw.Draw(img)
        d.ellipse((x - r, y - r, x + r, y + r), fill=bub, outline="white" if style != "tag" else INK, width=5 if style != "tag" else 4)
        t = f"{v/10000:.1f}".rstrip("0").rstrip(".") + "万"
        f = zh(int(r * .5)); d.text((x - f.getlength(t) / 2, y - f.size * .68), t, font=f, fill=bub_txt)
        fn = zh(30, "Black"); tw = fn.getlength(name)
        ny = y - r - 48 if pos == "above" else y + r + 8
        nx = min(max(x - tw / 2, 56), W - 56 - tw)
        halo_text(img, nx, ny, name, fn, name_col, halo); d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 1360, W - 40, 1420), 30, fill=bub)
    t = "圆越大，跌得越多（单位：澳币）"; f = zh(32, "Bold")
    d.text(((W - f.getlength(t)) / 2, 1370), t, font=f, fill=bub_txt)
    return img

render(CREAM, (160, 205, 220), (236, 226, 204), (120, 110, 95), INK, (110, 104, 96), RED, "white", INK, (236, 226, 204), "light").save(f"{OUT}/inner_A.jpg", quality=93)
render(INK, (36, 52, 76), (64, 74, 96), (120, 140, 170), CREAM, (180, 176, 168), RED, "white", CREAM, (64, 74, 96), "dark").save(f"{OUT}/inner_B.jpg", quality=93)
render((250, 236, 214), (120, 190, 205), (200, 226, 170), INK, INK, (110, 90, 70), (255, 206, 84), INK, INK, (200, 226, 170), "tag").save(f"{OUT}/inner_C.jpg", quality=93)
print("ok")
