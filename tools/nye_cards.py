"""悉尼跨年烟花免费和低价看点：地图、几点满、分区介绍、要票的、注意事项。
数据来自悉尼跨年官网各看点页面（容量、开门时间、通常几点满）。
用法：python3 tools/nye_cards.py 瓦片目录 输出目录"""
import sys, os, re, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harbour_map import harbour, SEA, LAND, EDGE
TILES, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1440
NAVY = (16, 24, 44); CREAM = (250, 246, 238); INK = (28, 32, 48); GREY = (96, 100, 112); RED = (214, 64, 52); GOLD = (255, 196, 70)
def zh(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def serif(s): return ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", s, index=2)
def wrap(text, font, width):
    toks = re.findall(r"[A-Za-z0-9&'.$,:%]+|.", text); lines, cur = [], ""
    for t in toks:
        if font.getlength(cur + t) > width and cur and t not in "，。、！？）：；": lines.append(cur); cur = t.lstrip()
        else: cur += t
    if cur: lines.append(cur)
    return lines

# 区, 编号, 名字, 坐标, 开门, 几点满, 容量, 看到什么
S = [
 ("歌剧院和植物园", 1, "Bennelong Lawn", (-33.8586, 151.2148), "9am", "10:30am", "1,000", "歌剧院正上方，大桥、歌剧院和城市夜景全都有。"),
 ("歌剧院和植物园", 2, "Tarpeian Lawn", (-33.8590, 151.2142), "9:30am", "12:30pm", "3,500", "离烟花最近的地方之一。"),
 ("歌剧院和植物园", 3, "Fleet Steps", (-33.8612, 151.2212), "10am", "11:30am", "3,000", "歌剧院和大桥同框的经典角度。"),
 ("歌剧院和植物园", 4, "Mrs Macquaries Point", (-33.8597, 151.2225), "10am", "11:30am", "10,000", "明信片角度，场地大，可以买吃的。"),
 ("环形码头", 5, "Hickson Road Reserve", (-33.8554, 151.2103), "9am", "1:30pm", "2,800", "大桥脚下，对面就是歌剧院。"),
 ("环形码头", 6, "Campbells Cove", (-33.8574, 151.2099), "9am", "3pm", "9,200", "大桥和歌剧院都看得到。"),
 ("The Rocks和Barangaroo", 7, "Dawes Point", (-33.8548, 151.2086), "10am", "7:30pm", "32,000", "就在大桥下面，全场最大，满得最晚。"),
 ("环形码头", 8, "East Circular Quay", (-33.8599, 151.2129), "9am", "3pm", "10,000", "正对大桥，看不到歌剧院。"),
 ("环形码头", 9, "West Circular Quay", (-33.8610, 151.2093), "9am", "4pm", "16,000", "人最多的码头，视野有限。"),
 ("The Rocks和Barangaroo", 10, "Observatory Hill", (-33.8588, 151.2051), "2pm", "6pm", "4,500", "坐在草坡上看大桥西面，有大树会挡。"),
 ("The Rocks和Barangaroo", 11, "Barangaroo Reserve", (-33.8574, 151.2017), "11am", "2:30pm", "8,500", "看大桥西面，有表演和现场音乐。"),
 ("北岸", 12, "Mary Booth Reserve", (-33.8502, 151.2158), "9am", "2pm", "2,500", "大桥和歌剧院都看得到，坐火车很近。"),
 ("北岸", 13, "Upper Bradfield Park", (-33.8478, 151.2122), "9am", "3pm", "6,400", "大桥旁边的大草地，歌剧院也在视线里。"),
 ("北岸", 14, "Lavender Bay", (-33.8438, 151.2069), "9am", "3pm", "3,000", "看大桥西面，还能看到月神公园。"),
 ("北岸", 15, "Cremorne Point", (-33.8461, 151.2290), "1pm", "", "", "看大桥东面，人比南岸少。"),
 ("Darling Harbour和Pyrmont", 16, "Darling Harbour", (-33.8711, 151.2008), "10am", "", "28,000", "有自己的烟花，9点和12点各一场，开到凌晨4点，带小孩最方便。"),
 ("Darling Harbour和Pyrmont", 17, "Pirrama Park", (-33.8632, 151.1933), "10am", "", "8,000", "看大桥西面，平地好走，适合推婴儿车。"),
 ("Darling Harbour和Pyrmont", 18, "Giba Park", (-33.8640, 151.1926), "4pm", "8pm", "2,200", "看大桥西面和Balmain的海湾。"),
 ("Balmain", 19, "Illoura Reserve", (-33.8587, 151.1964), "8am", "", "2,850", "Balmain东头，看大桥西面。"),
 ("Balmain", 20, "Thornton Park", (-33.8569, 151.1956), "3:30pm", "", "1,000", "视野很好，但很快就挤满。"),
 ("Balmain", 21, "Mort Bay Park", (-33.8541, 151.1851), "8am", "", "3,000", "正对大桥西面，家庭最多。"),
 ("Balmain", 22, "Birchgrove Park", (-33.8497, 151.1816), "8am", "", "5,000", "看大桥西面，场地大。"),
 ("东区", 23, "Embarkation Park", (-33.8677, 151.2236), "4pm", "8:30pm", "1,200", "树多，视野比较窄。"),
 ("东区", 24, "McKell Park", (-33.8668, 151.2394), "12pm", "", "1,000", "看城市天际线和大桥。"),
 ("东区", 25, "Yarranabbe Park", (-33.8721, 151.2355), "3pm", "", "10,000", "场地大，看大桥的视野有限。"),
 ("东区", 26, "Rose Bay Foreshore", (-33.8698, 151.2686), "3pm", "", "1,500", "离得远，人也少。"),
]
AREAS = ["歌剧院和植物园", "环形码头", "The Rocks和Barangaroo", "北岸", "Darling Harbour和Pyrmont", "Balmain", "东区"]
ACOL = dict(zip(AREAS, [(214, 64, 52), (230, 140, 30), (196, 150, 40), (60, 140, 90), (40, 150, 170), (60, 110, 190), (140, 80, 170)]))
S.sort(key=lambda s: AREAS.index(s[0]))
S = [(s[0], i + 1) + s[2:] for i, s in enumerate(S)]
BND = (-33.836, -33.876, 151.176, 151.276)

def place_labels(pts, r, xmax, ymax):
    """简单排斥：编号圆圈互相推开，再用细线连回原点"""
    lab = [[x, y] for x, y in pts]
    for _ in range(300):
        moved = False
        for i in range(len(lab)):
            for j in range(i + 1, len(lab)):
                dx = lab[j][0] - lab[i][0]; dy = lab[j][1] - lab[i][1]; dd = math.hypot(dx, dy) or .01
                if dd < 2 * r + 4:
                    push = (2 * r + 4 - dd) / 2; ux, uy = dx / dd, dy / dd
                    lab[i][0] -= ux * push; lab[i][1] -= uy * push; lab[j][0] += ux * push; lab[j][1] += uy * push; moved = True
        for i, (x, y) in enumerate(pts):  # 轻轻拉回
            lab[i][0] += (x - lab[i][0]) * .02; lab[i][1] += (y - lab[i][1]) * .02
            lab[i][0] = min(max(lab[i][0], r + 4), xmax - r - 4); lab[i][1] = min(max(lab[i][1], r + 4), ymax - r - 4)
        if not moved: break
    return lab

def pins(img, xy, items, r=19, font=None, night=False):
    d = ImageDraw.Draw(img); font = font or zh(22, "Black")
    pts = [xy(*s[3]) for s in items]; lab = place_labels(pts, r, img.width, img.height)
    for (px, py), (lx, ly) in zip(pts, lab):
        d.line((px, py, lx, ly), fill=(255, 255, 255) if night else EDGE, width=2)
        d.ellipse((px - 4, py - 4, px + 4, py + 4), fill=(255, 255, 255) if night else EDGE)
    for s, (lx, ly) in zip(items, lab):
        c = ACOL[s[0]]
        d.ellipse((lx - r, ly - r, lx + r, ly + r), fill=c, outline="white", width=3)
        t = str(s[1]); d.text((lx - font.getlength(t) / 2, ly - font.size / 2 - 3), t, font=font, fill="white")

# 01 全图
def page_map(fn):
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
    d.text((50, 40), "悉尼跨年免费看点地图", font=serif(72), fill=INK)
    d.text((52, 140), "26个不用票的看点，按颜色分7个区", font=zh(34), fill=GREY)
    mp, xy = harbour(W - 60, 760, BND, TILES)
    pins(mp, xy, S)
    m = Image.new("L", mp.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *mp.size), radius=26, fill=255)
    img.paste(mp, (30, 210), m); d = ImageDraw.Draw(img)
    d.rounded_rectangle((30, 210, W - 30, 970), radius=26, outline=EDGE, width=3)
    y = 1000
    for a in AREAS:
        nums = [x for x in S if x[0] == a]
        d.ellipse((60, y + 10, 92, y + 42), fill=ACOL[a])
        d.text((110, y), f"{nums[0][1]}到{nums[-1][1]}  {a}", font=zh(38, "Black"), fill=INK)
        y += 60
    img.save(f"{OUT}/{fn}", quality=93)

# 02 几点就满
def page_full(fn):
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
    d.text((50, 40), "这些看点通常几点满", font=serif(76), fill=INK)
    d.text((52, 150), "按官网写的通常满场时间排，满了就不让进", font=zh(34), fill=GREY)
    def tkey(t):
        h, m = (t[:-2].split(":") + ["0"])[:2]; h = int(h) % 12 + (12 if t.endswith("pm") else 0); return h * 60 + int(m)
    L = sorted([s for s in S if s[5]], key=lambda s: tkey(s[5]))
    y = 230; ft = zh(42, "Black"); fn_ = zh(38, "Bold")
    for s in L:
        t = s[5].replace("am", "").replace("pm", ""); ap = "上午" if s[5].endswith("am") else ("中午" if s[5].startswith("12") else ("下午" if tkey(s[5]) < 18 * 60 else "晚上"))
        d.text((60, y), ap + t, font=ft, fill=RED)
        d.ellipse((340, y + 14, 366, y + 40), fill=ACOL[s[0]])
        d.text((382, y + 4), s[2], font=fn_, fill=INK)
        y += 72
    assert y < H - 40, y
    img.save(f"{OUT}/{fn}", quality=93)

# 03到07 分区
def page_area(fn, area):
    items = [s for s in S if s[0] == area]
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 16), fill=ACOL[area])
    d.text((50, 44), area, font=serif(68), fill=INK)
    # 小地图，只标本区
    la = [s[3][0] for s in items]; lo = [s[3][1] for s in items]
    pad = .006; b = (max(la) + pad, min(la) - pad, min(lo) - pad * 1.6, max(lo) + pad * 1.6)
    # 保持比例
    cla = (b[0] + b[1]) / 2; clo = (b[2] + b[3]) / 2; span_lo = max(b[3] - b[2], (b[0] - b[1]) * 1.2 * 2.55)
    span_la = span_lo / 2.55 / 1.2
    b = (cla + span_la / 2, cla - span_la / 2, clo - span_lo / 2, clo + span_lo / 2)
    mp, xy = harbour(W - 100, 360, b, TILES); pins(mp, xy, items, r=22, font=zh(26, "Black"))
    m = Image.new("L", mp.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *mp.size), radius=22, fill=255)
    img.paste(mp, (50, 140), m); d = ImageDraw.Draw(img); d.rounded_rectangle((50, 140, W - 50, 500), radius=22, outline=EDGE, width=3)
    y = 530; rowh = (H - 560) // max(len(items), 4)
    big = len(items) <= 4
    fname = zh(40 if big else 34, "Black"); fs = zh(30 if big else 27, "Bold"); fd = zh(30 if big else 26)
    for s in items:
        d.ellipse((50, y + 4, 92, y + 46), fill=ACOL[area]); t = str(s[1]); f = zh(24, "Black")
        d.text((71 - f.getlength(t) / 2, y + 9), t, font=f, fill="white")
        d.text((110, y), s[2], font=fname, fill=INK)
        info = [f"{s[4]}开门"] + ([f"通常{s[5]}满"] if s[5] else []) + ([f"容纳{s[6]}人"] if s[6] else [])
        x = 110; yy = y + fname.size + 14
        for k, it in enumerate(info):
            col = RED if it.endswith("满") else GREY; d.text((x, yy), it, font=fs, fill=col); x += fs.getlength(it) + 28
        yy += fs.size + 12
        for ln in wrap(s[7], fd, W - 170): d.text((110, yy), ln, font=fd, fill=INK); yy += fd.size + 12
        y = max(y + rowh, yy + 10) if big else yy + 22
    assert y < H, (area, y)
    img.save(f"{OUT}/{fn}", quality=93)

# 08 要票的和低价的
def page_tickets(fn):
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
    d.text((50, 44), "要票的和低价的", font=serif(76), fill=INK)
    B = [("免费但要抢票", RED, [
          ("歌剧院前广场", "12月26日上午10点放票，免费。只能中午12点到下午3点入场，迟到不让进，容纳6,000人。"),
          ("Cahill Expressway", "抽签已经结束，中签的人12月4日前会收到通知。")]),
         ("今年已经没票", GREY, [
          ("Bradleys Head和Strickland Estate", "免费票都发完了。下午5点或6点后如果没满，没票的人也能进。")]),
         ("付费但还有票", (60, 110, 190), [
          ("Dudley Page Reserve", "成人$70，青少年$30，小孩免费，家庭票$180。在Dover Heights，人少，能看到整个海港的烟花，下午5:30开门。"),
          ("Taronga Zoo", "$125起，在动物园里看，有不同套餐。")])]
    y = 170
    for title, col, rows in B:
        d.rounded_rectangle((50, y, 50 + zh(38, "Black").getlength(title) + 40, y + 62), radius=14, fill=col)
        d.text((70, y + 6), title, font=zh(38, "Black"), fill="white"); y += 86
        for n, t in rows:
            d.text((60, y), n, font=zh(40, "Black"), fill=INK); y += 58
            for ln in wrap(t, zh(32), 950): d.text((62, y), ln, font=zh(32), fill=GREY); y += 46
            y += 18
        y += 20
    assert y < H, y
    img.save(f"{OUT}/{fn}", quality=93)

# 09 注意事项
def page_tips(fn):
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
    d.text((50, 44), "去之前要知道", font=serif(80), fill=INK)
    T = [("两场烟花", "晚上9点有一场家庭烟花，适合带小孩，看完就能走；12点是主场。"),
         ("出去就进不来", "大部分看点出去了不能再进，吃的喝的要一次带够。"),
         ("可以带吃的", "大部分看点能自带野餐，植物园和Barangaroo里也能买吃的。"),
         ("看满场时间出发", "热门的通常上午就满。想晚点去，选Dawes Point、Darling Harbour或者西边Balmain的公园。"),
         ("坐公共交通", "当天大量封路，开车很难停。散场后火车和渡轮会加班，但要排很久。")]
    y = 190
    for h_, t in T:
        d.text((60, y), h_, font=zh(48, "Black"), fill=RED); y += 74
        for ln in wrap(t, zh(38), 950): d.text((62, y), ln, font=zh(38), fill=INK); y += 58
        y += 40
    assert y < H, y
    img.save(f"{OUT}/{fn}", quality=93)

# 首页：夜景地图
def night_map(w, h, b):
    mp, xy = harbour(w, h, b, TILES)
    px = mp.load()
    for yy in range(mp.height):
        for xx in range(mp.width):
            r, g, bb = px[xx, yy]
            if abs(r - SEA[0]) < 30 and abs(g - SEA[1]) < 30 and abs(bb - SEA[2]) < 30: px[xx, yy] = (22, 46, 84)
            elif abs(r - LAND[0]) < 30 and abs(g - LAND[1]) < 30 and abs(bb - LAND[2]) < 30: px[xx, yy] = (14, 20, 36)
            elif r < 90 and g < 100: px[xx, yy] = (70, 110, 160)
    return mp, xy

def burst(d, cx, cy, R, col, n=26):
    for k in range(n):
        a = 2 * math.pi * k / n; r1 = R * .25; r2 = R * (0.85 + random.random() * .15)
        d.line((cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + r2 * math.cos(a), cy + r2 * math.sin(a)), fill=col, width=4)
        d.ellipse((cx + r2 * math.cos(a) - 4, cy + r2 * math.sin(a) - 4, cx + r2 * math.cos(a) + 4, cy + r2 * math.sin(a) + 4), fill=col)

def cover_night(fn, title, sub, picks):
    random.seed(3)
    img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
    for c, x, y, R in (((255, 120, 150), 830, 300, 120), ((255, 210, 90), 960, 470, 90), ((140, 220, 255), 700, 470, 80)):
        burst(d, x, y, R, c)
    d.text((50, 50), title[0], font=zh(118, "Black"), fill=(255, 244, 214)); d.text((50, 200), title[1], font=zh(118, "Black"), fill=GOLD)
    d.text((54, 370), sub, font=zh(52, "Black"), fill=(255, 244, 214))
    b = (-33.846, -33.866, 151.192, 151.232)
    mp, xy = night_map(W, 860, b); img.paste(mp, (0, 580)); d = ImageDraw.Draw(img)
    f = zh(40, "Black"); fs = zh(30, "Bold")
    for name, label, dx, dy in picks:
        s = [s for s in S if s[2] == name][0]; px, py = xy(*s[3]); py += 580
        d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=RED, outline="white", width=3)
        lx, ly = px + dx, py + dy; d.line((px, py, lx, ly), fill="white", width=3)
        tw = max(f.getlength(label), fs.getlength(name)) + 32
        bx0 = lx - (tw if dx < 0 else 0); bx0 = min(max(bx0, 12), W - 12 - tw)
        d.rounded_rectangle((bx0, ly - 46, bx0 + tw, ly + 46), radius=14, fill=(255, 244, 214))
        d.text((bx0 + 16, ly - 42), label, font=f, fill=RED); d.text((bx0 + 16, ly + 4), name, font=fs, fill=INK)
    img.save(f"{OUT}/{fn}", quality=93)

def cover_grid(fn):
    img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
    d.text((50, 40), "悉尼跨年烟花", font=zh(116, "Black"), fill=(255, 244, 214))
    d.text((50, 185), "免费看点通常几点满", font=zh(84, "Black"), fill=GOLD)
    P = [("上午10:30", "Bennelong Lawn"), ("上午11:30", "Mrs Macquaries"), ("中午12:30", "Tarpeian Lawn"), ("下午1:30", "Hickson Road"),
         ("下午2:30", "Barangaroo"), ("下午3点", "Campbells Cove"), ("下午6点", "Observatory Hill"), ("晚上7:30", "Dawes Point")]
    cw, ch = (W - 90) // 2, 250
    for i, (t, n) in enumerate(P):
        x = 30 + (i % 2) * (cw + 30); y = 330 + (i // 2) * (ch + 22)
        d.rounded_rectangle((x, y, x + cw, y + ch), radius=26, fill=(30, 44, 76))
        f = zh(84 if len(t) <= 5 else 74, "Black"); d.text((x + 30, y + 30), t, font=f, fill=GOLD)
        d.text((x + 32, y + 30 + f.size + 28), "通常这时满 " + n, font=zh(38, "Bold"), fill=(255, 244, 214))
    img.save(f"{OUT}/{fn}", quality=93)

page_map("01.jpg"); page_full("02.jpg")
for k, a in enumerate(AREAS): page_area(f"{k + 3:02d}.jpg", a)
page_tickets("10.jpg"); page_tips("11.jpg")
def tmin(t):
    h, m = (t[:-2].split(":") + ["0"])[:2]; return (int(h) % 12 + (12 if t.endswith("pm") else 0)) * 60 + int(m)
BANDS = [("通常中午前满", (255, 84, 84), lambda t: t and tmin(t) < 12 * 60 + 1),
         ("通常下午满", (255, 170, 60), lambda t: t and 12 * 60 < tmin(t) <= 17 * 60),
         ("通常傍晚后满", (255, 226, 90), lambda t: t and tmin(t) > 17 * 60),
         ("其他免费看点", (120, 220, 170), lambda t: not t)]

def cover_map(fn):
    img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
    d.text((50, 40), "悉尼跨年烟花", font=zh(120, "Black"), fill=(255, 244, 214))
    d.text((50, 190), "免费看点通常几点满", font=zh(92, "Black"), fill=GOLD)
    top = 340; mh = 760
    mp, xy = night_map(W, mh, BND); img.paste(mp, (0, top)); d = ImageDraw.Draw(img)
    for s_ in S:
        col = [b[1] for b in BANDS if b[2](s_[5])][0]
        x, y = xy(*s_[3]); y += top; r = 15
        d.ellipse((x - r, y - r, x + r, y + r), fill=col, outline=NAVY, width=3)
    y = top + mh + 30; f = zh(52, "Black")
    for k, (lab, col, _) in enumerate(BANDS):
        x = 60 + (k % 2) * 500; yy = y + (k // 2) * 90
        d.ellipse((x, yy + 12, x + 46, yy + 58), fill=col); d.text((x + 66, yy), lab, font=f, fill=(255, 244, 214))
    img.save(f"{OUT}/{fn}", quality=93)

cover_map("cover_A.jpg")
cover_grid("cover_B.jpg")
print("ok")
