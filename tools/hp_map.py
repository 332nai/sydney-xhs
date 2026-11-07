"""悉尼房价帖：卡通地图，三种风格。数据：Cotality HVI 2026年11月报告，悉尼年跌幅最小的10个SA3（住宅，过去12个月）。
其余所有SA3跌幅都超过5.1%。用法：python3 tools/hp_map.py 老杨图标目录 输出目录"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1080, 1440
ICONS, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
CREAM = (244, 239, 230); INK = (28, 33, 45); RED = (201, 90, 74); TEAL = (40, 128, 128)
def zh(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)

X0, Y0 = 40, 330
def P(lon, lat): return (X0 + (lon - 150.25) / 1.35 * 1000, Y0 + (-33.22 - lat) / 1.2 * 1000)

COAST = [(151.62, -33.15), (151.55, -33.30), (151.47, -33.42), (151.40, -33.52), (151.33, -33.57), (151.34, -33.62),
         (151.30, -33.72), (151.29, -33.80), (151.285, -33.85), (151.28, -33.90), (151.26, -33.96), (151.23, -33.99),
         (151.20, -34.03), (151.17, -34.07), (151.13, -34.13), (151.06, -34.25), (150.97, -34.38), (150.90, -34.50)]
SLOW = [(150.0, -34.6), (150.0, -33.0), (151.7, -33.0)]
HARBOUR = [(151.27, -33.84), (151.22, -33.85), (151.17, -33.84), (151.10, -33.83), (151.03, -33.82)]
HAWK = [(151.31, -33.58), (151.24, -33.55), (151.15, -33.53), (151.05, -33.50), (150.95, -33.47)]
BOTANY = (151.19, -34.00)

# 跌幅最少的10个区：名字, 经纬度, 年跌幅, 标签左上角
TEN = [("Wollondilly", 150.58, -34.18, 1.4, (330, 1180)), ("Camden", 150.69, -34.04, 1.6, (110, 975)),
       ("Wyong", 151.42, -33.28, 1.8, (640, 345)), ("Blue Mountains", 150.42, -33.68, 3.0, (60, 585)),
       ("Richmond-Windsor", 150.78, -33.58, 3.0, (300, 500)), ("Auburn", 151.03, -33.855, 3.7, (560, 720)),
       ("Campbelltown", 150.83, -34.07, 3.8, (510, 1070)), ("Gosford", 151.32, -33.43, 4.7, (620, 470)),
       ("Fairfield", 150.93, -33.87, 4.9, (390, 905)), ("Penrith", 150.69, -33.76, 5.1, (90, 790))]
INNER = [("CBD", 151.21, -33.87), ("Inner West", 151.14, -33.89), ("东区", 151.25, -33.90), ("下北岸", 151.20, -33.82),
         ("Parramatta", 151.00, -33.81), ("北海滩", 151.28, -33.70)]

def land_mask():
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    d.polygon([P(*p) for p in SLOW[:2]] + [P(*p) for p in [SLOW[2]] + COAST], fill=255)
    for line, w in [(HARBOUR, 22)]:
        d.line([P(*p) for p in line], fill=0, width=w, joint="curve")
    bx, by = P(*BOTANY); d.ellipse((bx - 34, by - 22, bx + 34, by + 22), fill=0)
    m = m.filter(ImageFilter.GaussianBlur(9)).point(lambda v: 255 if v > 128 else 0)
    return m

def render(bg, sea, land, patch, outline, title_col, sub_col, chip_bg, chip_txt, pct_col, inner_col, style):
    img = Image.new("RGB", (W, H), bg)
    m = land_mask()
    mp = Image.new("RGB", (W, H), sea)
    mp.paste(land, (0, 0), m)
    pm = Image.new("L", (W, H), 0); pd = ImageDraw.Draw(pm)
    for _, lon, lat, _, _ in TEN:
        x, y = P(lon, lat); r = 58 if lat > -33.5 else 78
        pd.ellipse((x - r, y - r, x + r, y + r), fill=255)
    pm = ImageChops.multiply(pm.filter(ImageFilter.GaussianBlur(18)), m)
    mp.paste(patch, (0, 0), pm)
    edge = ImageChops.subtract(m.filter(ImageFilter.MaxFilter(9)), m)
    mp.paste(outline, (0, 0), edge)
    clip = Image.new("L", (W, H), 0); ImageDraw.Draw(clip).rounded_rectangle((40, Y0 - 10, W - 40, 1340), 40, fill=255)
    img.paste(mp, (0, 0), clip)
    d = ImageDraw.Draw(img)
    # 海浪小装饰
    for wx, wy in [(900, 640), (930, 800), (880, 1200), (960, 1260)]:
        for k in range(3):
            d.arc((wx + k * 26, wy, wx + k * 26 + 26, wy + 20), 200, 340, fill=(255, 255, 255), width=4)
    # 标题
    d.text((70, 50), "悉尼过去一年", font=zh(64), fill=title_col)
    d.text((70, 130), "没有一个区在涨", font=zh(96), fill=title_col)
    for name, lon, lat, v, (bx, by) in TEN:
        x, y = P(lon, lat)
        f1, f2 = zh(26, "Bold"), zh(40)
        t2 = f"-{v}%"; wbox = max(f1.getlength(name), f2.getlength(t2)) + 32
        cx = min(max(x, bx), bx + wbox); cy = min(max(y, by), by + 88)
        d.line((x, y, cx, cy), fill=chip_txt, width=3)
        d.rounded_rectangle((bx, by, bx + wbox, by + 88), 18, fill=chip_bg, outline=chip_txt if style == "tag" else None, width=3)
        d.text((bx + 16, by + 6), name, font=f1, fill=chip_txt)
        d.text((bx + 16, by + 34), t2, font=f2, fill=pct_col)
        d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=pct_col, outline="white", width=4)
    # CBD和内城提示
    x, y = P(151.21, -33.87)
    d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=inner_col, outline="white", width=4)
    d.line((x + 10, y + 8, 850, 990), fill=inner_col, width=3)
    d.rounded_rectangle((830, 980, 1030, 1110), 22, fill=inner_col)
    for i, ln in enumerate(["内西、东区", "北岸、CBD"]):
        d.text((850, 994 + i * 52), ln, font=zh(34, "Bold"), fill="white")
    # 底部说明
    d.rounded_rectangle((40, 1360, W - 40, 1420), 30, fill=inner_col)
    t = "红色区域：跌幅都超过5.1%　悉尼整体跌9.4%"; f = zh(32, "Bold")
    d.text(((W - f.getlength(t)) / 2, 1370), t, font=f, fill=bg if style != "dark" else INK)
    d.text((72, 258), "跌得最少的10个区都在外圈", font=zh(34, "Medium"), fill=sub_col)
    return img

render(CREAM, (168, 205, 214), (222, 128, 110), (246, 214, 190), (120, 60, 50), INK, (110, 104, 96), "white", INK, TEAL, RED, "chip").save(f"{OUT}/map_A.jpg", quality=93)
render(INK, (40, 56, 80), (160, 66, 58), (215, 160, 130), (230, 120, 100), CREAM, (180, 176, 168), (244, 239, 230), INK, TEAL, (240, 150, 130), "dark").save(f"{OUT}/map_B.jpg", quality=93)
render((250, 236, 214), (120, 190, 205), (232, 120, 96), (252, 222, 170), INK, INK, (110, 90, 70), (255, 214, 102), INK, INK, RED, "tag").save(f"{OUT}/map_C.jpg", quality=93)
print("ok")
