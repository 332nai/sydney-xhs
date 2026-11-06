"""悉尼房价跌回五年前：数据卡片（封面加8张），全部用PIL直接画图表。
数据来源：Cotality HVI 2026年11月报告（截至10月31日）、RBA 2026年11月3日决议、ATO税改页面。
用法：python3 tools/hp_cards.py 老杨图标目录 输出目录"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1440
ICONS, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

CREAM = (244, 239, 230); INK = (28, 33, 45); GREY = (120, 116, 108); LINE = (214, 206, 192)
RED = (201, 90, 74); NAVY = (46, 79, 110); TEAL = (40, 128, 128); PALE_RED = (233, 190, 180)

def zh(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def num(s): return ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc", s, index=2)

def page(no, kicker, title, sub=None, bg=CREAM):
    img = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(img)
    d.text((80, 80), f"{no:02d}", font=zh(30, "Bold"), fill=RED)
    d.text((140, 80), kicker, font=zh(30, "Medium"), fill=GREY)
    y = 140
    for ln in title.split("\n"):
        d.text((76, y), ln, font=zh(76, "Black"), fill=INK); y += 100
    if sub:
        y += 6
        for ln in sub.split("\n"):
            d.text((80, y), ln, font=zh(36), fill=(80, 76, 70)); y += 54
    return img, d, y + 30

def ctext(d, x, y, t, f, fill):
    d.text((x - f.getlength(t) / 2, y), t, font=f, fill=fill)

def icon(img, pose, x, y, h):
    ic = Image.open(f"{ICONS}/{pose}.png").convert("RGBA")
    ic = ic.resize((round(ic.width * h / ic.height), h), Image.LANCZOS)
    img = img.convert("RGBA")
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 255), (x + 4, y + 6), ic.split()[3].point(lambda v: int(v * .3)))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8)))
    img.alpha_composite(ic, (x, y))
    return img.convert("RGB")

# ---------- 00 封面 ----------
c = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(c)
# 背景里的下行折线
pts = [(0, 520), (160, 470), (300, 430), (430, 380), (560, 330), (640, 300), (720, 360), (820, 450), (930, 560), (1080, 700)]
for i in range(len(pts) - 1):
    d.line((pts[i], pts[i + 1]), fill=(60, 70, 88), width=10)
d.line((pts[5], pts[6], pts[7], pts[8], pts[9]), fill=RED, width=12, joint="curve")
d.ellipse((640 - 16, 300 - 16, 640 + 16, 300 + 16), fill=CREAM)
d.text((600, 240), "2月高点", font=zh(32, "Bold"), fill=CREAM)
d.text((80, 760), "悉尼房价", font=zh(84, "Black"), fill=CREAM)
d.text((80, 870), "跌回五年前", font=zh(150, "Black"), fill=CREAM)
for i, ln in enumerate(["比2月高点低10.1%", "比2021年10月还低1.5%", "利率、借款能力、税改、房租", "8张图讲清楚"]):
    d.text((84, 1070 + i * 58), ln, font=zh(40), fill=(200, 196, 188))
c = icon(c, "01_看菜单", W - 330, H - 300, 250)
c.save(f"{OUT}/00.jpg", quality=93)

# ---------- 01 跌了多少：关键时点的中位价 ----------
img, d, y0 = page(1, "跌了多少", "高点到现在\n少了13万", "悉尼住宅中位价（独立屋和公寓合计）")
bars = [("2016年10月", 876549, NAVY), ("2021年10月", 1196913, NAVY), ("2025年10月", 1301279, NAVY),
        ("2026年2月\n高点", 1311412, NAVY), ("2026年10月\n现在", 1178959, RED)]
top, base = y0 + 120, 1250; maxv = 1400000
bw, gap = 150, 42; x = 80
for lab, v, col in bars:
    h = (v / maxv) * (base - top)
    d.rectangle((x, base - h, x + bw, base), fill=col)
    ctext(d, x + bw / 2, base - h - 54, f"${v/1e6:.2f}m", zh(38, "Bold"), col)
    for j, ln in enumerate(lab.split("\n")):
        ctext(d, x + bw / 2, base + 18 + j * 40, ln, zh(30), INK if col == RED else GREY)
    x += bw + gap
d.text((80, base + 110), "现在的$1.18m，比2021年10月的$1.20m还低1.5%。", font=zh(32, "Bold"), fill=RED)
img.save(f"{OUT}/01.jpg", quality=93)

# ---------- 02 40年来最快 ----------
img, d, y0 = page(2, "跌得多快", "40年来\n最快的一次下跌", "各次下跌开始后的头7个月，首府城市房价合计跌幅")
rows = [("2017到2019年那轮", 1.2, NAVY, "当时是有记录以来最深的一次"), ("2022到2023年那轮", 7.0, NAVY, "加息最猛的那一年"),
        ("2026年这一轮", 8.1, RED, "从3月高点算起")]
y = y0 + 110; maxp = 9.0
for lab, p, col, note in rows:
    d.text((80, y), lab, font=zh(40, "Bold"), fill=INK)
    d.text((80, y + 56), note, font=zh(28), fill=GREY)
    bl = (p / maxp) * 820
    d.rectangle((80, y + 110, 80 + bl, y + 180), fill=col)
    d.text((80 + bl + 20, y + 112), f"-{p}%", font=num(56), fill=col)
    y += 300
img.save(f"{OUT}/02.jpg", quality=93)

# ---------- 03 加息五次 ----------
img, d, y0 = page(3, "为什么跌", "今年加息5次\n利率回到18年最高", "澳储行现金利率")
pts = [("25年2月", 4.10), ("25年5月", 3.85), ("25年8月", 3.60), ("26年2月", 3.85), ("26年3月", 4.10), ("26年5月", 4.35), ("26年9月", 4.60), ("26年11月", 4.85)]
lo, hi = 3.4, 5.0; top, base = y0 + 90, 1200; left, right = 110, 1000
def py(v): return base - (v - lo) / (hi - lo) * (base - top)
for g in (3.5, 4.0, 4.5, 5.0):
    d.line((left, py(g), right, py(g)), fill=LINE, width=2)
    d.text((40, py(g) - 18), f"{g:.1f}", font=zh(26), fill=GREY)
step = (right - left) / (len(pts) - 1)
prev = None
for i, (lab, v) in enumerate(pts):
    x = left + i * step; y = py(v)
    col = RED if i >= 3 else NAVY
    if prev:
        d.line((prev[0], prev[1], x, prev[1]), fill=col if i >= 3 else NAVY, width=8)
        d.line((x, prev[1], x, y), fill=col if i >= 3 else NAVY, width=8)
    d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=col)
    ctext(d, x, y - 56, f"{v:.2f}%", zh(28, "Bold"), col)
    ctext(d, x, base + 20, lab, zh(24), GREY)
    prev = (x, y)
d.text((left, base + 80), "去年降息3次，今年2月起转为加息，11月3日这次是今年第5次。", font=zh(30), fill=INK)
img.save(f"{OUT}/03.jpg", quality=93)

# ---------- 04 借款能力 ----------
img, d, y0 = page(4, "加息意味着什么", "同样的收入\n能借的钱少了10万以上", "一个中位收入家庭的借款能力变化")
y = y0 + 80
d.rectangle((80, y, 1000, y + 120), fill=NAVY)
d.text((110, y + 30), "加息前能借到的额度", font=zh(40, "Bold"), fill="white")
d.text((820, y + 24), "100%", font=num(52), fill="white")
y += 170
d.rectangle((80, y, 80 + 920 * 0.885, y + 120), fill=RED)
d.rectangle((80 + 920 * 0.885, y, 1000, y + 120), outline=RED, width=4)
d.text((110, y + 30), "现在", font=zh(40, "Bold"), fill="white")
d.text((80 + 920 * 0.885 - 190, y + 24), "88.5%", font=num(52), fill="white")
y += 200
d.text((80, y), "-11.5%", font=num(150), fill=RED)
d.text((80, y + 200), "约等于少借10.5万澳币以上", font=zh(48, "Bold"), fill=INK)
y += 300
for ln in ["银行批贷款看的是你每月还不还得起。利率每升一次，", "同一份收入能撑起的贷款就小一截。这比全国房价从", "3月高点跌掉的约6.3万澳币还要多。"]:
    d.text((80, y), ln, font=zh(34), fill=(70, 66, 60)); y += 54
img.save(f"{OUT}/04.jpg", quality=93)

# ---------- 05 独立屋vs公寓 ----------
img, d, y0 = page(5, "谁跌得多", "独立屋\n比公寓跌得多", "悉尼过去12个月价格变化和现在的中位价")
cols = [("独立屋", -10.8, 1438090, RED), ("公寓", -5.6, 857872, NAVY)]
base = y0 + 140; x = 140
for lab, p, mv, col in cols:
    h = abs(p) / 12 * 640
    d.rectangle((x, base, x + 300, base + h), fill=col)
    ctext(d, x + 150, base + h + 20, f"{p}%", num(70), col)
    ctext(d, x + 150, base - 70, lab, zh(44, "Black"), INK)
    ctext(d, x + 150, base + h + 120, f"中位价 ${mv/1e6:.2f}m", zh(34), GREY)
    x += 480
d.line((100, base, 980, base), fill=INK, width=3)
img.save(f"{OUT}/05.jpg", quality=93)

# ---------- 06 房租还在涨 ----------
img, d, y0 = page(6, "房租呢", "房价在跌\n房租还在涨", "悉尼过去12个月的变化")
y = y0 + 90
rows = [("独立屋", -10.8, 4.6), ("公寓", -5.6, 3.0)]
mid = 540
d.line((mid, y - 20, mid, y + 520), fill=INK, width=3)
d.text((mid - 260, y - 70), "房价", font=zh(34, "Bold"), fill=RED)
d.text((mid + 160, y - 70), "房租", font=zh(34, "Bold"), fill=TEAL)
for lab, pv, rv in rows:
    d.text((80, y + 40), lab, font=zh(38, "Black"), fill=INK)
    bl = abs(pv) / 12 * 360
    d.rectangle((mid - bl, y + 120, mid, y + 190), fill=RED)
    d.text((mid - bl - 4 - num(40).getlength(f"{pv}%"), y + 125), f"{pv}%", font=num(40), fill=RED) if mid - bl > 260 else d.text((mid - bl + 10, y + 125), f"{pv}%", font=num(40), fill="white")
    rl = rv / 12 * 360
    d.rectangle((mid, y + 120, mid + rl, y + 190), fill=TEAL)
    d.text((mid + rl + 16, y + 125), f"+{rv}%", font=num(40), fill=TEAL)
    y += 260
y += 60
for ln in ["一涨一跌，悉尼的租金回报率到了3.5%。", "首府城市平均3.77%，是2015年5月以来最高。", "但投资贷款利率已经接近7%，", "大多数投资房仍然是每月倒贴。"]:
    d.text((80, y), ln, font=zh(36), fill=(70, 66, 60)); y += 58
img.save(f"{OUT}/06.jpg", quality=93)

# ---------- 07 税改时间线 ----------
img, d, y0 = page(7, "另一个原因", "负扣税和资本利得税\n2027年7月1日起改", "5月联邦预算宣布，现在已经立法")
y = y0 + 80; lx = 140
d.line((lx, y, lx, y + 760), fill=INK, width=6)
events = [("2026年5月12日晚7:30", "预算公布。这个时间点之前已经持有的\n投资房，不受负扣税新规影响。", NAVY),
          ("2027年7月1日起：负扣税", "5月12日之后买的二手投资房，出租亏损\n不能再抵工资收入的税。新建房不受影响。", RED),
          ("2027年7月1日起：资本利得税", "50%折扣取消，改成按通胀调整成本，\n另设30%的最低税率。只算这天之后的增值。", RED)]
for t, desc, col in events:
    d.ellipse((lx - 22, y - 4, lx + 22, y + 40), fill=col)
    d.text((lx + 50, y - 6), t, font=zh(40, "Black"), fill=col)
    yy = y + 56
    for ln in desc.split("\n"):
        d.text((lx + 50, yy), ln, font=zh(32), fill=(70, 66, 60)); yy += 48
    y += 270
d.text((80, y + 10), "6月季度新增投资贷款跌了8.6%，是2022年9月以来最大的季度跌幅。", font=zh(30), fill=INK)
img.save(f"{OUT}/07.jpg", quality=93)

# ---------- 08 接下来看什么 ----------
img, d, y0 = page(8, "接下来看什么", "四个信号\n决定会不会继续跌")
cards = [("-30%", "悉尼成交量", "比去年同期少三成，\n买家明显变少"),
         ("39天", "平均挂牌时间", "2020年8月以来最长"),
         ("4.7%", "平均砍价幅度", "2019年5月以来最大"),
         ("12月8日", "下次议息", "有经济学家预计\n明年2月还会再加")]
gx, gy = 80, y0 + 60; cw, chh = 450, 420
for i, (big, lab, note) in enumerate(cards):
    x = gx + (i % 2) * (cw + 20); y = gy + (i // 2) * (chh + 20)
    d.rounded_rectangle((x, y, x + cw, y + chh), 24, fill="white")
    d.text((x + 36, y + 40), big, font=num(84 if len(big) < 5 else 66), fill=RED)
    d.text((x + 36, y + 180), lab, font=zh(38, "Black"), fill=INK)
    yy = y + 246
    for ln in note.split("\n"):
        d.text((x + 36, yy), ln, font=zh(30), fill=GREY); yy += 44
img.save(f"{OUT}/08.jpg", quality=93)
print("ok")
