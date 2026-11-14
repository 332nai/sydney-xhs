"""悉尼最适合华人的鸡尾酒：每家酒吧一张卡，上面4到6张环境和酒的照片，下面是介绍和代表鸡尾酒。
酒单都核对过2026年9月到11月的菜单。照片来自各酒吧官网和媒体报道。
用法：python3 tools/cocktail_cards.py 图片目录 输出目录"""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
W, H = 1080, 1440
SRC, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
BG = (22, 16, 16); IVORY = (242, 234, 220); GOLD = (214, 176, 112); MUTED = (170, 158, 146)
def zh(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def serif(s, w="Bold"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSerifCJK-{w}.ttc", s, index=2)

def crop(spec, w, h):
    spec = list(spec) if isinstance(spec, tuple) else [spec]
    name, fx, fy = spec + [.5, .5][len(spec) - 1:]
    im = ImageOps.exif_transpose(Image.open(f"{SRC}/{name}")).convert("RGB")
    s = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * s)), max(h, round(im.height * s))), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    return ImageEnhance.Color(im.crop((round(x), round(y), round(x) + w, round(y) + h)).filter(ImageFilter.UnsharpMask(1.2, 25, 2))).enhance(1.05)

def wrap(text, font, width):
    toks = re.findall(r"[A-Za-z0-9&'.$,:@]+|.", text); lines, cur = [], ""
    for t in toks:
        if font.getlength(cur + t) > width and cur and t not in "，。、！？）：；": lines.append(cur); cur = t.lstrip()
        else: cur += t
    if cur: lines.append(cur)
    return lines

G = 6
LABEL = {"Spice Temple": "草莓柚子", "Saké": "绿茶梅子", "Teahouse": "茉莉抹茶", "Bennelong": "茉莉荔枝",
         "Maybe Sammy": "迷你荔枝", "Bar Bridge": "柚子柑橘", "Grain": "黄油米香", "Eau de Vie": "柚子姜汁"}
def label(img, text, box):
    x0, y0, x1, y1 = box; d = ImageDraw.Draw(img); f = zh(84, "Black")
    while f.getlength(text) > (x1 - x0) - 40: f = zh(f.size - 4, "Black")
    d.text((x0 + ((x1 - x0) - f.getlength(text)) / 2, y1 - f.size - 44), text, font=f, fill=(255, 244, 222), stroke_width=8, stroke_fill=(24, 14, 10))
def mosaic(img, photos, top, hp):
    """4到6张拼图：左上一张大图，其余排在右边和下面"""
    n = len(photos); bigw = int(W * .62); r1 = int(hp * .62)
    if n == 4:
        boxes = [(0, top, bigw, top + r1), (bigw + G, top, W, top + r1)]
        bw = (W - G) // 2; boxes += [(0, top + r1 + G, bw, top + hp), (bw + G, top + r1 + G, W, top + hp)]
    else:
        half = (r1 - G) // 2
        boxes = [(0, top, bigw, top + r1), (bigw + G, top, W, top + half), (bigw + G, top + half + G, W, top + r1)]
        k = n - 3; bw = (W - G * (k - 1)) // k
        boxes += [(i * (bw + G), top + r1 + G, i * (bw + G) + bw, top + hp) for i in range(k)]
    for p, (x0, y0, x1, y1) in zip(photos, boxes): img.paste(crop(p, x1 - x0, y1 - y0), (x0, y0))
    return boxes[0]

def card(fn, name, where, intro, drinks, photos):
    fn_ = zh(32, "Bold"); fd = zh(28); fi = zh(30)
    th = 84 + 52 + len(wrap(intro, fi, 960)) * 44 + 16
    for dn, price, desc in drinks: th += 46 + len(wrap(desc, fd, 950)) * 40 + 12
    hp = min(860, H - th - 60)
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    b0 = mosaic(img, photos, 0, hp)
    if name in LABEL: label(img, LABEL[name], b0)
    y = hp + 30
    d.text((60, y), name, font=serif(58), fill=IVORY); y += 84
    d.text((62, y), where, font=zh(28), fill=GOLD); y += 52
    for ln in wrap(intro, fi, 960): d.text((62, y), ln, font=fi, fill=MUTED); y += 44
    y += 16
    for dn, price, desc in drinks:
        t = dn + ("　" + price if price else "")
        d.text((62, y), t, font=fn_, fill=IVORY); y += 46
        for ln in wrap(desc, fd, 950): d.text((62, y), ln, font=fd, fill=MUTED); y += 40
        y += 12
    assert y < H - 10 and hp > 600, (name, y, hp)
    img.save(f"{OUT}/{fn}", quality=93)

BARS = [
 ("Spice Temple", "CBD，Bligh Street的地下室",
  "Neil Perry创办的川湘云菜馆，特调单按十二生肖设计，每个属相一杯，找自己属相那杯点。",
  [("兔 Rabbit", "$29", "茉莉和接骨木花，花香清新。"),
   ("猪 Pig", "$44", "玫瑰、荔枝加气泡，一壶可以几个人分。"),
   ("羊 Sheep", "$29", "草莓加柚子，酸甜顺口。")],
  ["st_07.jpg", "st_13.jpg", "st_14.jpg", "st_09.jpg", "st_04.jpg"]),
 ("Saké", "The Rocks",
  "日料餐厅，特调大量用梅子、绿茶、玄米茶和柚子，很对中国人的口味。",
  [("Hummingbird 蜂鸟", "$30", "青柠叶加绿茶梅子和百香果。"),
   ("Miss Wednesday", "$28", "荔枝、玫瑰和香草，再加一点青柠。"),
   ("Kogane Sour", "$29", "玄米茶香，加烤西柚和柚子。"),
   ("Sesame Fuma Fashioned", "$32", "芝麻香很浓，适合喜欢浓郁口味的人。")],
  ["sk_01c.jpg", "sk_10.jpg", "sk_11.jpg", "sk_00.jpg", "sk_07.jpg"]),
 ("Teahouse", "Barangaroo，Crown Sydney三楼",
  "丝绒沙发、金色装饰、鸟笼卡座，户外露台看得到海港。特调大多用中国茶，还能配点心。",
  [("Jade Sour 翡翠", "$26", "茉莉花茶加杏仁，绵密的泡沫上撒抹茶粉。"),
   ("荔枝玫瑰", "$26", "荔枝加玫瑰茶，花香果香都有。"),
   ("Blossom Breeze 桂花", "$26", "桂花茶的香气，加西柚和一点盐，咸香清爽。")],
  ["th_05.jpg", "th_01.jpg", "th_02.jpg", "th_04.jpg", "th_06.jpg"]),
 ("Bennelong", "悉尼歌剧院里",
  "坐在歌剧院的帆顶下面，窗外是海港和CBD夜景。现在的特调单叫Sip the Canvas，每一杯都以一幅名画命名。",
  [("戴珍珠耳环的少女", "$34", "茉莉、柚子和荔枝苏打，花香果香都很淡雅。"),
   ("神奈川冲浪里", "$30", "日本卡波斯柑和海盐风味，偏咸鲜。")],
  ["ben_02.jpg", "ben_04.jpg", "ben_03.jpg", "ben_07.jpg", "ben_08.jpg"]),
 ("Maybe Sammy", "The Rocks",
  "多次入选世界50佳，主题是60年代的拉斯维加斯，店员穿粉色西装。现在的特调单叫Showtime，每一杯对应一部电影或剧。",
  [("迷你荔枝", "$15", "小杯装，下午时段只要$8。"),
   ("Peaky Blinders", "$27", "茉莉、苹果和绿茶苏打，茶香明显。"),
   ("Mad Men", "$30", "乌龙茶加谷物香，偏浓郁。")],
  [("ms_06.jpg", .6, .5), "ms_14.jpg", "ms_15.jpg", "ms_09.jpg", "ms_04.jpg"]),
 ("Bar Bridge", "CBD，Bridge Street地下，离环形码头几分钟",
  "2026年4月新开，Bar Planet同一个团队。红色丝绒卡座和台灯，很有复古电影感。下午4点到6点有优惠。",
  [("Citron", "", "柚子加柑橘，清爽带果香。"),
   ("Highlight", "", "哈密瓜加玄米茶苏打，很清爽。")],
  [("bb_00.png", .45, .5), "bb_01.png", "bb_03.png", "bb_02.png", "bb_05.jpg"]),
 ("Grain", "环形码头旁，Four Seasons一楼",
  "Four Seasons一楼的lounge，安静，适合聊天。每杯招牌特调都配一口小吃。",
  [("Golden Grain", "$34", "用黄油米调出一股米香。"),
   ("Woman in the City", "$28", "芝麻香加气泡葡萄，很特别。"),
   ("Wings to a Poem", "$30", "上面一层班兰香气。")],
  ["gr_00.jpg", "gr_07.jpg", "gr_03.png", "gr_04.jpg", "gr_05.jpg"]),
 ("Eau de Vie", "CBD，Wynyard火车站旁边的小巷里",
  "悉尼最早的一批隐藏式小店，曾经排进世界50佳第13名。灯光很暗，店员爱用火、烟和干冰做表演。",
  [("Yuzu Mule", "$26起", "柚子酱、蜂蜜、青柠加姜汁汽水，先有姜的微辣，最后是柚子香。"),
   ("Smokey Rob Roy", "$36.5", "店主的招牌，罩在木烟里端上桌，打开时满桌烟雾。")],
  ["edv5.jpg", "edv3.jpg", ("edv1.webp", .45, .5), "edv4.jpg", "edv2.jpg", "edv6.jpg"]),
]
for i, (n, w, intro, dr, ph) in enumerate(BARS):
    card(f"{i + 1:02d}.jpg", n, w, intro, dr, ph)

# 首页
def cover(fn, pics, t1, t2):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    cw = (W - G) // 2; ch = (H - 380 - G * 2) // 3
    for i, p in enumerate(pics): img.paste(crop(p, cw, ch), ((i % 2) * (cw + G), 380 + (i // 2) * (ch + G)))
    d.text((60, 70), t1, font=serif(100), fill=IVORY); d.text((60, 210), t2, font=serif(100), fill=GOLD)
    img.save(f"{OUT}/{fn}", quality=93)
# cover("cover_A.jpg", ["th_05.jpg", ("edv1.webp", .45, .5), "ss_04.jpg", "bb_01.png", "ben_02.jpg", "gr_00.jpg"], "悉尼最适合华人的", "鸡尾酒")
# cover("cover_B.jpg", ["ss_01.jpg", "th_05.jpg", "gr_03.png", "ss_03.jpg", ("edv1.webp", .45, .5), "bb_00.png"], "茉莉、桂花、荔枝", "悉尼的东方鸡尾酒")
print("ok")

# 首页：标题 + 每家一格，写酒吧名和招牌酒中文名
CRM = (255, 244, 222); BRN = (24, 14, 10)
def outlined(d, xy, text, f, sw): d.text(xy, text, font=f, fill=CRM, stroke_width=sw, stroke_fill=BRN)
def fitf(text, maxw, start, w="Black"):
    s = start
    while zh(s, w).getlength(text) > maxw and s > 24: s -= 2
    return zh(s, w)
def cover_full(fn, title):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    ft = fitf(title, W - 100, 120); d.text(((W - ft.getlength(title)) / 2, 50), title, font=ft, fill=IVORY)
    top = 250
    rows = [[("Spice Temple", "草莓柚子", "st_07.jpg"), ("Saké", "绿茶梅子", "sk_01c.jpg"), ("Teahouse", "茉莉抹茶", "th_05.jpg")],
            [("Bennelong", "茉莉荔枝", "ben_02.jpg"), ("Maybe Sammy", "迷你荔枝", ("ms_06.jpg", .6, .5)), ("Grain", "黄油米香", "gr_00.jpg")],
            [("Bar Bridge", "柚子柑橘", ("bb_00.png", .45, .5)), ("Eau de Vie", "柚子姜汁", "edv5.jpg")]]
    rh = (H - top - G * 2) // 3
    for r, row in enumerate(rows):
        k = len(row); tw = (W - G * (k - 1)) // k; y0 = top + r * (rh + G)
        for i, (bar, drink, ph) in enumerate(row):
            t = crop(ph, tw, rh); dd = ImageDraw.Draw(t)
            fd = fitf(drink, tw - 24, 66); fb = fitf(bar, tw - 30, 46, "Black")
            lay = Image.new("RGBA", t.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); bx = (tw - fb.getlength(bar)) / 2
            ld.rounded_rectangle((bx - 14, 18, bx + fb.getlength(bar) + 14, 30 + fb.size + 10), radius=8, fill=(0, 0, 0, 120))
            ld.text((bx, 22), bar, font=fb, fill=(255, 255, 255, 255))
            box = (int(bx - 20), 12, int(bx + fb.getlength(bar) + 20), int(40 + fb.size + 12))
            lay.paste(lay.crop(box).filter(ImageFilter.GaussianBlur(4.2)), box)
            t = t.convert("RGBA"); t.alpha_composite(lay); t = t.convert("RGB"); dd = ImageDraw.Draw(t)
            outlined(dd, ((tw - fd.getlength(drink)) / 2, rh - fd.size - 40), drink, fd, max(6, fd.size // 10))
            img.paste(t, (i * (tw + G), y0))
    img.save(f"{OUT}/{fn}", quality=93)
cover_full("cover_C.jpg", "悉尼最好喝的特调")
print("cover ok")
