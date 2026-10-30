"""悉尼Happy Hour：一周生蚝日历页和优惠清单页。用法：python3 hh_pages.py 输出目录"""
import sys
from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def F(w, s): return ImageFont.truetype(NOTO + {"k": "NotoSansCJK-Black.ttc", "b": "NotoSansCJK-Bold.ttc", "m": "NotoSansCJK-Medium.ttc", "r": "NotoSansCJK-Regular.ttc"}[w], s, index=2)
CREAM, INK, CORAL, TEAL, GREY, LINE = (247, 242, 233), (28, 26, 24), (226, 92, 60), (0, 128, 128), (120, 112, 104), (226, 216, 202)
od = sys.argv[1]

import re
def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for ch in re.findall(r"[A-Za-z&'$.0-9]+(?: [A-Za-z&'][A-Za-z&'.]*)*|.", text):
        if font.getlength(cur + ch) > maxw: lines.append(cur); cur = ch
        else: cur += ch
    return lines + [cur] if cur else lines

# 一周生蚝日历
CAL = [("周一", "Pier Bar、The Rover、The Roosevelt、Jane、The Winery、The Charles"),
       ("周二", "Pier Bar、The Rover、The Roosevelt、Jane、The Winery、The Charles"),
       ("周三", "以上全部，加上The Morrison和Corner House"),
       ("周四", "周一那几家，加上Harbour View（$1.5）和Corner House"),
       ("周五", "周一那几家，加上Corner House、Rose of Australia全天、The London"),
       ("周六", "Bat & Ball（$1，卖完即止）、The Rover、The Roosevelt、Jane、The Charles、Corner House、The Erko"),
       ("周日", "The Roosevelt、Jane、The Charles、Corner House、The Erko")]
img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
d.text((70, 80), "一周生蚝日历", font=F("k", 78), fill=INK)
d.text((72, 190), "每天都有地方吃便宜生蚝", font=F("m", 34), fill=GREY)
y = 290; fd, ft = F("k", 46), F("r", 36)
for day, txt in CAL:
    d.rounded_rectangle([70, y, 190, y + 64], 18, fill=CORAL)
    d.text((86, y + 4), day, font=fd, fill="white")
    ls = wrap(d, txt, ft, W - 230 - 70)
    for i, l in enumerate(ls): d.text((230, y + 8 + i * 52), l.strip("、"), font=ft, fill=INK)
    y += max(64, 10 + len(ls) * 52) + 44
    d.line([(70, y - 18), (W - 70, y - 18)], fill=LINE, width=2)
img.save(f"{od}/hh_cal.png")

# 优惠清单
OY = [("$1", "Bat & Ball Hotel", "Redfern", "周六，卖完即止", "悉尼最便宜的生蚝，去晚了就没了"),
      ("$1.5", "Harbour View Hotel", "The Rocks", "周四晚上6点到7点", "海港大桥脚下的老酒吧"),
      ("$2", "Pier Bar", "Walsh Bay", "周一到周五下午5点到6点", "海边码头位置，鸡尾酒$12"),
      ("$2", "The Rover", "Surry Hills", "周一到周六下午4点到6点", "啤酒$6，金汤力$8，葡萄酒$10"),
      ("$2", "The Charles", "CBD", "每天晚上9点以后", "迷你鸡尾酒$13，汉堡$18"),
      ("$2", "The Morrison", "CBD", "周三晚上6点到7点", "George Street上的老牌生蚝吧"),
      ("$2", "The Roosevelt", "Potts Point", "工作日5点到6点半，周末2点到6点半", "马天尼$13，可乐饼$3")]
OY2 = [("$2", "The Corner House", "Bondi", "周三到周日下午5点到6点", "楼上酒吧，Aperol Spritz $12"),
       ("$2", "The Erko", "Erskineville", "周六周日", "Tommy's玛格丽特$14"),
       ("$2.5", "Rose of Australia", "Erskineville", "周五全天", "公众假期除外"),
       ("$3", "Jane", "Surry Hills", "周一到周四5点到6点，周五到周日4点到6点", "葡萄酒$10，金汤力$10"),
       ("$4", "The Winery", "Surry Hills", "周一到周五下午4点到6点", "葡萄酒和瓶装啤酒$11"),
       ("$4", "The London Hotel", "Balmain", "周五", "Spritz $14")]
DR = [("$5", "MoshPit", "Erskineville", "周二到周五下午5点到7点", "扎啤和葡萄酒$5"),
      ("$5", "The Chatswood", "Chatswood", "周一到周五下午4点到6点", "啤酒和葡萄酒$5"),
      ("$6", "Frisco Hotel", "Woolloomooloo", "每天下午4点到6点", "精选啤酒和葡萄酒"),
      ("$6", "Four in Hand", "Paddington", "周一到周五下午4点到6点", "葡萄酒和扎啤"),
      ("$6", "Coopers Hotel", "Newtown", "周一到周五下午5点到7点", "啤酒、葡萄酒和烈酒")]
def listpage(title, sub, rows, col, out, rowh=150):
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
    d.text((70, 80), title, font=F("k", 72), fill=INK)
    d.text((72, 180), sub, font=F("m", 32), fill=GREY)
    y = 270
    for price, name, area, when, extra in rows:
        fp = F("k", 64 if len(price) <= 2 else 52)
        d.text((70, y + 8), price, font=fp, fill=col)
        x = 250
        d.text((x, y), name, font=F("b", 46), fill=INK)
        d.text((x + F("b", 46).getlength(name) + 18, y + 14), area, font=F("m", 30), fill=GREY)
        d.text((x, y + 66), when, font=F("m", 33), fill=col)
        d.text((x, y + 114), extra, font=F("r", 32), fill=(70, 66, 62))
        y += rowh
        d.line([(70, y - 8), (W - 70, y - 8)], fill=LINE, width=2)
    img.save(out)
listpage("生蚝Happy Hour", "价格是一只生蚝的价格", OY, CORAL, f"{od}/hh_oy1.png", 166)
listpage("生蚝Happy Hour（续）", "价格是一只生蚝的价格", OY2, CORAL, f"{od}/hh_oy2.png", 190)
listpage("5到6刀喝一杯", "价格是一杯啤酒或葡萄酒", DR, TEAL, f"{od}/hh_dr.png", 210)
