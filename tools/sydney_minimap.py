"""卡通悉尼小地图：海岸线、海港、Botany Bay、CBD歌剧院小图标，红色图钉标出位置。
用法：from sydney_minimap import minimap; img = minimap(lat, lon, label, font)"""
from PIL import Image, ImageDraw, ImageFilter

# 大致范围：北到Palm Beach，南到Cronulla
LAT0, LAT1, LON0, LON1 = -33.50, -34.11, 151.02, 151.40
COAST = [(-33.55, 151.335), (-33.578, 151.326), (-33.600, 151.333), (-33.635, 151.333), (-33.655, 151.322),
         (-33.680, 151.312), (-33.710, 151.305), (-33.750, 151.300), (-33.772, 151.296), (-33.790, 151.292),
         (-33.805, 151.300), (-33.822, 151.303), (-33.832, 151.290), (-33.842, 151.286), (-33.862, 151.287),
         (-33.890, 151.281), (-33.905, 151.272), (-33.915, 151.267), (-33.925, 151.262), (-33.950, 151.261),
         (-33.975, 151.256), (-33.998, 151.250), (-34.005, 151.232), (-34.010, 151.215), (-34.030, 151.190),
         (-34.050, 151.160), (-34.070, 151.152), (-34.090, 151.150), (-34.11, 151.150)]
HARBOUR = [(-33.832, 151.292), (-33.840, 151.275), (-33.848, 151.255), (-33.855, 151.230), (-33.856, 151.212),
           (-33.850, 151.195), (-33.840, 151.170), (-33.835, 151.140), (-33.828, 151.100), (-33.818, 151.040)]
MIDDLE = [(-33.832, 151.270), (-33.815, 151.258), (-33.800, 151.250), (-33.790, 151.235)]
PITTWATER = [(-33.578, 151.318), (-33.600, 151.305), (-33.630, 151.300), (-33.655, 151.300)]
BOTANY = [(-33.995, 151.245), (-33.975, 151.215), (-33.960, 151.180), (-33.975, 151.140), (-34.000, 151.120),
          (-34.020, 151.150), (-34.012, 151.200), (-34.008, 151.232)]
CBD = (-33.858, 151.214)

def minimap(lat, lon, label, font, w=250, h=330, bounds=None):
    global LAT0, LAT1, LON0, LON1
    if bounds: LAT0, LAT1, LON0, LON1 = bounds
    S = 3; W, H = w * S, h * S; pad = 14 * S; mh = H - 70 * S
    def xy(la, lo):
        return (pad + (lo - LON0) / (LON1 - LON0) * (W - 2 * pad), pad + (la - LAT0) / (LAT1 - LAT0) * (mh - 2 * pad))
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, W - 1, H - 1), radius=26 * S, fill=(255, 252, 244, 255), outline=(30, 52, 70, 255), width=4 * S)
    # 海
    sea = (158, 212, 232, 255); land = (246, 232, 196, 255); edge = (30, 52, 70, 255)
    m = Image.new("RGBA", (W, H), (0, 0, 0, 0)); md = ImageDraw.Draw(m)
    md.rounded_rectangle((pad, pad, W - pad, mh), radius=18 * S, fill=sea)
    poly = [xy(la, lo) for la, lo in COAST]
    landpoly = [(pad, pad)] + [(min(x, W - pad), y) for x, y in poly] + [(pad, mh)]
    md.polygon(landpoly, fill=land)
    for line, wd in ((HARBOUR, 9), (MIDDLE, 6), (PITTWATER, 7)):
        md.line([xy(*p) for p in line], fill=sea, width=wd * S, joint="curve")
        for p in (line[0], line[-1]):
            x, y = xy(*p); r = wd * S / 2; md.ellipse((x - r, y - r, x + r, y + r), fill=sea)
    md.polygon([xy(*p) for p in BOTANY], fill=sea)
    md.line(poly, fill=edge, width=3 * S, joint="curve")
    # 小浪花
    for (la, lo) in ((LAT0 + (LAT1 - LAT0) * .22, LON1 - (LON1 - LON0) * .12), (LAT0 + (LAT1 - LAT0) * .55, LON1 - (LON1 - LON0) * .08), (LAT0 + (LAT1 - LAT0) * .85, LON1 - (LON1 - LON0) * .14)):
        x, y = xy(la, lo)
        for k in range(2):
            md.arc((x - 14 * S + k * 14 * S, y - 6 * S, x + k * 14 * S, y + 6 * S), 200, 340, fill=(255, 255, 255, 255), width=3 * S)
    # 只保留圆角框内
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).rounded_rectangle((pad, pad, W - pad, mh), radius=18 * S, fill=255)
    card.paste(m, (0, 0), mask)
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((pad, pad, W - pad, mh), radius=18 * S, outline=edge, width=3 * S)
    # CBD 歌剧院小图标
    cx, cy = xy(*CBD)
    for i, s_ in enumerate((14, 10, 7)):
        ox = cx - 12 * S + i * 9 * S; s_ *= S
        d.pieslice((ox - s_, cy - s_, ox + s_, cy + s_), 180, 270, fill=(255, 255, 255, 255), outline=edge, width=2 * S)
    # 图钉
    px, py = xy(lat, lon); r = 15 * S
    d.ellipse((px - r, py - 2.6 * r, px + r, py - 0.6 * r), fill=(226, 64, 52, 255), outline=(255, 255, 255, 255), width=3 * S)
    d.polygon([(px - 0.75 * r, py - 1.25 * r), (px + 0.75 * r, py - 1.25 * r), (px, py)], fill=(226, 64, 52, 255))
    d.ellipse((px - 0.38 * r, py - 1.98 * r, px + 0.38 * r, py - 1.22 * r), fill=(255, 255, 255, 255))
    card = card.resize((w, h), Image.LANCZOS)
    dd = ImageDraw.Draw(card)
    tw = font.getlength(label)
    dd.text(((w - tw) / 2, h - 62 + (54 - font.size) / 2 - 4), label, font=font, fill=(30, 52, 70))
    return card

def paste_map(img, card, x, y):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 90), (x + 6, y + 8), card.split()[3])
    base = Image.alpha_composite(img.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(8)))
    base.alpha_composite(card, (x, y)); return base.convert("RGB")
