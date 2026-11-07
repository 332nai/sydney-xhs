"""悉尼一年水果季节：日历卡。数据来自Sydney Markets四季应季指南（每月应季水果清单）。
用法：python3 tools/fruit_calendar.py 输出目录（输出calendar.jpg，作为第01张）"""
import sys, os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1440
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
CREAM = (248, 243, 234); INK = (34, 32, 30); GREY = (130, 124, 116); LINE = (226, 218, 204)
def zh(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)

MONTHS = [11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
def span(a, b): return list(range(a, b + 1)) if a <= b else list(range(a, 13)) + list(range(1, b + 1))
FRUITS = [("枇杷", [11], (236, 168, 60)), ("樱桃", span(11, 1), (176, 30, 50)), ("荔枝", span(12, 2), (226, 86, 100)),
          ("桃子", span(12, 2), (246, 150, 110)), ("葡萄", span(12, 5), (120, 70, 140)), ("李子", span(1, 3), (140, 50, 90)),
          ("红毛丹", span(1, 2), (210, 50, 60)), ("山竹", span(2, 3), (100, 40, 90)), ("无花果", span(2, 3), (150, 90, 110)),
          ("石榴", span(3, 5), (196, 40, 50)), ("苹果", span(3, 9), (214, 60, 50)), ("亚洲梨", span(3, 7), (200, 180, 90)),
          ("猕猴桃", span(3, 8), (120, 150, 60)), ("柿子", span(4, 5), (232, 120, 40)), ("释迦", span(4, 7), (130, 170, 110)),
          ("柑橘", span(4, 9), (240, 140, 30)), ("脐橙", span(5, 8), (244, 156, 40)), ("柚子", span(6, 10), (196, 200, 90)),
          ("草莓", span(7, 10) + span(12, 2), (226, 50, 70)), ("血橙", span(8, 9), (200, 60, 40)),
          ("芒果", span(9, 2), (250, 170, 30)), ("菠萝", span(9, 2), (232, 190, 40)), ("西瓜蜜瓜", span(10, 2), (90, 160, 90)),
          ("蓝莓", span(10, 2), (70, 90, 160))]

def _key(f):
    idx = sorted(MONTHS.index(m) for m in f[1])
    end = idx[0]
    while end + 1 in idx: end += 1
    return (idx[0], -end)
FRUITS.sort(key=_key)
img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
d.text((70, 60), "悉尼水果日历", font=zh(96, "Black"), fill=INK)
d.text((74, 190), "每种水果在悉尼的应季月份，从现在的11月排起", font=zh(34), fill=GREY)
x0, x1, ytop = 220, 1030, 290
cw = (x1 - x0) / 12
for i, m in enumerate(MONTHS):
    cx = x0 + cw * (i + .5)
    if m in (12, 1, 2): bg = (252, 232, 214)
    elif m in (3, 4, 5): bg = (246, 236, 214)
    elif m in (6, 7, 8): bg = (226, 234, 240)
    else: bg = (230, 240, 222)
    d.rectangle((x0 + cw * i, ytop, x0 + cw * (i + 1), 1380), fill=bg)
    t = f"{m}"; f = zh(30, "Black"); d.text((cx - f.getlength(t) / 2, ytop + 8), t, font=f, fill=INK)
    f2 = zh(20); d.text((cx - f2.getlength("月") / 2, ytop + 44), "月", font=f2, fill=GREY)
for name, a_, b_, col in [("夏天", 1, 3, (214, 120, 70)), ("秋天", 4, 6, (170, 130, 60)), ("冬天", 7, 9, (80, 110, 140)), ("春天", 10, 11, (90, 140, 80))]:
    f = zh(26, "Bold"); cx = x0 + cw * (a_ + b_ + 1) / 2
    d.text((cx - f.getlength(name) / 2, 1388), name, font=f, fill=col)
# 现在
d.rounded_rectangle((x0 + 4, ytop - 40, x0 + cw - 4, ytop - 6), 14, fill=INK)
f = zh(22, "Bold"); d.text((x0 + cw / 2 - f.getlength("现在") / 2, ytop - 38), "现在", font=f, fill="white")
rh = (1380 - ytop - 84) / len(FRUITS); y = ytop + 84
for name, months, col in FRUITS:
    d.line((70, y + rh, x1, y + rh), fill=LINE, width=1)
    f = zh(30, "Bold"); d.text((74, y + rh / 2 - 22), name, font=f, fill=INK)
    idx = [i for i, m in enumerate(MONTHS) if m in months]
    runs = []
    for i in idx:
        if runs and runs[-1][1] == i - 1: runs[-1][1] = i
        else: runs.append([i, i])
    for a_, b_ in runs:
        d.rounded_rectangle((x0 + cw * a_ + 5, y + 9, x0 + cw * (b_ + 1) - 5, y + rh - 9), int((rh - 18) / 2), fill=col)
    y += rh
img.save(f"{OUT}/calendar.jpg", quality=93)
print("ok")
