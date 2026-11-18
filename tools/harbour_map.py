"""卡通悉尼海港地图：用OpenStreetMap瓦片取出水面形状，重新画成卡通风格（米色陆地、蓝色水面、深色描边），
再加海港大桥和歌剧院小图标。harbour(w, h, bounds, tiles_dir) 返回 (图, xy函数)"""
import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageChops
Z = 14
SEA = (150, 206, 230); LAND = (246, 234, 202); EDGE = (40, 60, 80)
BRIDGE = ((-33.8555, 151.2093), (-33.8480, 151.2112)); OPERA = (-33.8568, 151.2153)

def _txy(lat, lon):
    n = 2 ** Z; return (lon + 180) / 360 * n * 256, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n * 256

def water_mask(bounds, tiles_dir):
    la0, la1, lo0, lo1 = bounds
    X0, Y0 = _txy(la0, lo0); X1, Y1 = _txy(la1, lo1)
    tx0, ty0, tx1, ty1 = int(X0 // 256), int(Y0 // 256), int(X1 // 256), int(Y1 // 256)
    mos = Image.new("RGB", ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256), (255, 255, 255))
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            f = os.path.join(tiles_dir, f"{Z}_{tx}_{ty}.png")
            if os.path.exists(f): mos.paste(Image.open(f).convert("RGB"), ((tx - tx0) * 256, (ty - ty0) * 256))
    crop = mos.crop((int(X0 - tx0 * 256), int(Y0 - ty0 * 256), int(X1 - tx0 * 256), int(Y1 - ty0 * 256)))
    px = crop.load(); m = Image.new("L", crop.size, 0); mp = m.load()
    for y in range(crop.size[1]):
        for x in range(crop.size[0]):
            r, g, b = px[x, y]
            if abs(r - 170) < 14 and abs(g - 211) < 14 and abs(b - 223) < 14: mp[x, y] = 255
    # 去掉水上的文字和小噪点
    m = m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    return m

def harbour(w, h, bounds, tiles_dir, S=2):
    la0, la1, lo0, lo1 = bounds
    m = water_mask(bounds, tiles_dir).resize((w * S, h * S), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3 * S))
    m = m.point(lambda v: 255 if v > 128 else 0)
    edge = ImageChops.subtract(m.filter(ImageFilter.MaxFilter(2 * S * 2 + 1)), m)
    im = Image.new("RGB", (w * S, h * S), LAND); im.paste(SEA, (0, 0), m); im.paste(EDGE, (0, 0), edge)
    X0, Y0 = _txy(la0, lo0); X1, Y1 = _txy(la1, lo1)
    def xy(la, lo, s=S):
        X, Y = _txy(la, lo); return ((X - X0) / (X1 - X0) * w * s, (Y - Y0) / (Y1 - Y0) * h * s)
    d = ImageDraw.Draw(im)
    (a, b) = BRIDGE; x1, y1 = xy(*a); x2, y2 = xy(*b)
    d.line((x1, y1, x2, y2), fill=(60, 60, 70), width=4 * S)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2; L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** .5
    d.arc((mx - L / 2 - 4 * S, my - L / 2 + 6 * S, mx + L / 2 + 4 * S, my + L / 2 + 6 * S), 195, 345, fill=(60, 60, 70), width=4 * S)
    cx, cy = xy(*OPERA)
    for i, r in enumerate((15, 11, 8)):
        ox = cx - 9 * S + i * 9 * S; r *= S
        d.pieslice((ox - r, cy - r, ox + r, cy + r), 180, 270, fill=(255, 255, 255), outline=EDGE, width=2 * S)
    return im.resize((w, h), Image.LANCZOS), (lambda la, lo: xy(la, lo, 1))
