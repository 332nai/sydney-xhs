"""悉尼房价跌回五年前：数据卡片（封面加7张，按读者身份分开讲），全部用PIL直接画图表。
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
for i, ln in enumerate(["比2月高点低10.1%", "比2021年10月还低1.5%", "买房、还贷、投资、租房", "各看一张就够"]):
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

# ---------- 02 加息五次 ----------
img, d, y0 = page(2, "为什么跌", "今年加息5次\n利率回到18年最高", "澳储行现金利率")
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
img.save(f"{OUT}/02.jpg", quality=93)

# ---------- 03 有房贷的人 ----------
img, d, y0 = page(3, "如果你有房贷", "每100万贷款\n每月多还约$806", "平均浮动利率从约5.45%升到约6.7%，30年本息还款计算")
rows = [("50万贷款", 403), ("80万贷款", 645), ("100万贷款", 806), ("150万贷款", 1209)]
y = y0 + 60
for lab, v in rows:
    d.text((80, y + 14), lab, font=zh(40, "Bold"), fill=INK)
    bl = v / 1300 * 400
    d.rectangle((360, y, 360 + bl, y + 76), fill=RED if lab.startswith("100") else NAVY)
    d.text((360 + bl + 18, y + 8), f"+${v:,}/月", font=num(46), fill=RED if lab.startswith("100") else NAVY)
    y += 120
y += 40
d.rounded_rectangle((80, y, 1000, y + 300), 24, fill="white")
yy = y + 34
for ln, f, col in [("可以做的事", zh(38, "Black"), INK), ("老客户的利率常常比新客户高。", zh(34), (70, 66, 60)),
                   ("拿着别家给新客户的报价去问自己的银行，", zh(34), (70, 66, 60)), ("谈不下来就考虑转贷。", zh(34), (70, 66, 60))]:
    d.text((116, yy), ln, font=f, fill=col); yy += 60
img.save(f"{OUT}/03.jpg", quality=93)

# ---------- 04 想买房的人 ----------
img, d, y0 = page(4, "如果你想买房", "买家能谈价了\n但能借的也少了", "现在是买方市场的几个信号")
cards = [("39天", "平均挂牌时间", "2020年8月以来最长"), ("4.7%", "平均砍价幅度", "2019年5月以来最大"),
         ("-30%", "悉尼成交量", "比去年同期少三成"), ("-11.5%", "借款额度", "同样收入能借的钱")]
gx, gy = 80, y0 + 40; cw, chh = 450, 330
for i, (big, lab, note) in enumerate(cards):
    x = gx + (i % 2) * (cw + 20); y = gy + (i // 2) * (chh + 20)
    d.rounded_rectangle((x, y, x + cw, y + chh), 24, fill="white")
    d.text((x + 36, y + 30), big, font=num(80 if len(big) < 5 else 68), fill=RED)
    d.text((x + 36, y + 170), lab, font=zh(38, "Black"), fill=INK)
    d.text((x + 36, y + 232), note, font=zh(30), fill=GREY)
y = gy + 2 * (chh + 20) + 30
for ln in ["年初拿到的贷款预批额度要重新算。", "房子挂得越久越好谈，可以多看几套再出价。", "悉尼独立屋一年跌了10.8%，公寓跌了5.6%。"]:
    d.text((80, y), ln, font=zh(36), fill=(70, 66, 60)); y += 58
img.save(f"{OUT}/04.jpg", quality=93)

# ---------- 05 投资者 ----------
img, d, y0 = page(5, "如果你是投资者", "负扣税和资本利得税\n2027年7月1日起改", "5月联邦预算宣布，现在已经立法")
y = y0 + 60; lx = 140
d.line((lx, y, lx, y + 620), fill=INK, width=6)
events = [("2026年5月12日晚7:30", "这个时间点之前已经持有的投资房，\n不受负扣税新规影响。", NAVY),
          ("2027年7月1日起：负扣税", "5月12日之后买的二手投资房，出租亏损\n不能再抵工资收入的税。新建房不受影响。", RED),
          ("2027年7月1日起：资本利得税", "50%折扣取消，改成按通胀调整成本，\n另设30%的最低税率。只算这天之后的增值。", RED)]
for t, desc, col in events:
    d.ellipse((lx - 22, y - 4, lx + 22, y + 40), fill=col)
    d.text((lx + 50, y - 6), t, font=zh(40, "Black"), fill=col)
    yy = y + 56
    for ln in desc.split("\n"):
        d.text((lx + 50, yy), ln, font=zh(32), fill=(70, 66, 60)); yy += 48
    y += 230
y += 20
for ln in ["悉尼租金回报率3.5%，投资贷款利率接近7%，", "大多数投资房每月都在倒贴。算账时，", "倒贴的部分以后能不能抵税，结果差很多。"]:
    d.text((80, y), ln, font=zh(34), fill=INK); y += 54
img.save(f"{OUT}/05.jpg", quality=93)

# ---------- 06 租房的人 ----------
img, d, y0 = page(6, "如果你在租房", "房租还在涨\n但涨得慢了", "悉尼过去12个月房租变化")
y = y0 + 70
for lab, v in [("独立屋", 4.6), ("公寓", 3.0)]:
    d.text((80, y + 12), lab, font=zh(40, "Bold"), fill=INK)
    bl = v / 6 * 600
    d.rectangle((300, y, 300 + bl, y + 80), fill=TEAL)
    d.text((300 + bl + 18, y + 6), f"+{v}%", font=num(54), fill=TEAL)
    y += 130
y += 40
for big, txt in [("2.3%", "全国空置率，2022年1月以来最高"), ("0.9%", "全国近三个月房租涨幅，2025年1月以来最低")]:
    d.text((80, y), big, font=num(90), fill=RED)
    d.text((80 + num(90).getlength(big) + 30, y + 40), txt, font=zh(34), fill=INK)
    y += 150
y += 20
d.rounded_rectangle((80, y, 1000, y + 190), 24, fill="white")
d.text((116, y + 32), "续租时可以试着谈", font=zh(38, "Black"), fill=INK)
d.text((116, y + 96), "空房多了，房东找新租客要花时间。", font=zh(34), fill=(70, 66, 60))
img.save(f"{OUT}/06.jpg", quality=93)

# ---------- 07 饭桌上的三个数 ----------
img, d, y0 = page(7, "饭桌上说得出来的", "三个数\n记住就够了")
items = [("40年", "最快的一次下跌", "首府城市7个月跌了8.1%，比2022年那轮还快"),
         ("0个", "悉尼没有一个区在涨", "过去12个月涨幅最高的Wollondilly也跌了1.4%"),
         ("4.85%", "18年来最高的利率", "11月3日加息后，是2008年以来最高")]
y = y0 + 40
for big, lab, note in items:
    d.text((80, y), big, font=num(120), fill=RED)
    d.text((80, y + 160), lab, font=zh(44, "Black"), fill=INK)
    d.text((80, y + 222), note, font=zh(30), fill=GREY)
    y += 320
img.save(f"{OUT}/07.jpg", quality=93)
print("ok")
