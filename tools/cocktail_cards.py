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

def card(fn, name, where, intro, drinks, photos):
    fn_ = zh(32, "Bold"); fd = zh(28); fi = zh(30)
    th = 84 + 52 + len(wrap(intro, fi, 960)) * 44 + 16
    for dn, price, desc in drinks: th += 46 + len(wrap(desc, fd, 950)) * 40 + 12
    hp = min(860, H - th - 60)
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    mosaic(img, photos, 0, hp)
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
 ("Bar See See", "CBD，Porter House酒店顶楼，楼下是中餐厅Lee Ho Fook",
  "2025年10月开的白酒酒吧，酒单以茅台为主角，装修用了茅台飞天的图案，下酒菜是Lee Ho Fook做的椒盐莲藕片和生蚝。",
  [("High Low Martini", "$29", "店里的招牌马天尼。"),
   ("Strawberry & Yuzu Spritz", "$23", "草莓加柚子的气泡酒，酒感轻。")],
  ["ss_01.jpg", "ss_00.jpg", "ss_04.jpg", "ss_03.jpg", "ss_05.jpg", "ss_02.jpg"]),
 ("Teahouse", "Barangaroo，Crown Sydney三楼",
  "丝绒沙发、金色装饰、鸟笼卡座，户外露台看得到海港。鸡尾酒大多用中国茶入酒，还能配点心。",
  [("Jade Sour", "$26", "金酒加茉莉花茶和杏仁，蛋白打出绵密泡沫，上面撒抹茶粉。"),
   ("Lychee and Rose Martini", "$26", "伏特加加荔枝和玫瑰茶，蛋白打出泡沫。"),
   ("Blossom Breeze", "$26", "桂花茶泡过的龙舌兰，加西柚和一点盐，咸香清爽。"),
   ("Sichuan Boulevardier", "$26", "花椒泡过的威士忌，加Aperol和甜味美思。")],
  ["th_05.jpg", "th_01.jpg", "th_02.jpg", "th_04.jpg", "th_06.jpg"]),
 ("Eau de Vie", "CBD，Wynyard火车站旁边的小巷里",
  "澳洲最早的一批隐藏式鸡尾酒吧，曾经排进世界50佳酒吧第13名。灯光很暗，调酒师爱用火、烟和干冰做表演。",
  [("Smokey Rob Roy", "$36.5", "老板的招牌，几款威士忌加朗姆和自制甜味美思，罩在木烟里端上桌。"),
   ("Yuzu Mule", "$26起", "柚子酱、蜂蜜、青柠加姜汁啤酒，先有姜的微辣，最后是柚子香。"),
   ("Kitty @ The Cocobongo", "$31.5", "伏特加加百香果、接骨木花和香草，蛋白泡沫很绵密。")],
  [("edv1.webp", .45, .5), "edv3.jpg", "edv2.jpg", "edv4.jpg", "edv5.jpg", "edv6.jpg"]),
 ("Bennelong Bar", "悉尼歌剧院里",
  "坐在歌剧院的帆顶下面喝酒，窗外是海港和CBD夜景。现在的酒单叫Sip the Canvas，每一杯都以一幅名画命名。",
  [("Girl with a Pearl Earring", "$34", "茉莉花金酒加Lillet、柚子酒和荔枝苏打，花香果香都很淡雅。"),
   ("The Great Wave off Kanagawa", "$30", "日本Roku金酒加日本味美思和卡波斯柑，偏咸鲜。"),
   ("Clouds of Passion", "$36", "草莓椰子伏特加加百香果和香草，上面盖一朵香气云，是十多年的招牌。")],
  ["ben_04.jpg", "ben_02.jpg", "ben_03.jpg", "ben_07.jpg", "ben_08.jpg"]),
 ("Bar Bridge", "CBD，Bridge Street地下，离环形码头几分钟",
  "2026年4月开的马天尼酒吧，Bar Planet同一个团队。红色丝绒卡座和台灯，下午4点到6点马天尼$13。",
  [("Citron Martini", "", "柚子金酒加柑橘伏特加，清爽带果香。"),
   ("Highlight", "", "哈密瓜加玄米茶苏打，很清爽。"),
   ("Kimchi Martini", "", "牡蛎壳金酒加泡菜调味和海带伏特加，咸鲜重口。")],
  ["bb_01.png", "bb_00.png", "bb_03.png", "bb_02.png", "bb_05.jpg"]),
 ("Maybe Sammy", "The Rocks",
  "多次入选世界50佳酒吧，主题是60年代的拉斯维加斯，调酒师穿粉色西装。现在的酒单叫Showtime，每一杯对应一部电影或剧。",
  [("Peaky Blinders", "$27", "Benriach威士忌加雪莉酒、茉莉、苹果蜂蜜酒和绿茶苏打，茶香明显。"),
   ("迷你荔枝马天尼", "$15", "小杯装，下午欢乐时光$8。"),
   ("迷你茉莉花Negroni", "$15", "经典Negroni加茉莉花茶。")],
  [("ms_14.jpg", .5, .5), "ms_15.jpg", "ms_06.jpg", "ms_09.jpg", "ms_04.jpg"]),
 ("Grain", "环形码头旁，四季酒店一楼",
  "酒店里的酒吧，安静，适合小酌聊天。每杯招牌鸡尾酒都配一口小吃。",
  [("Golden Grain", "$34", "波本加黑麦威士忌和黄油米，有一股米香。"),
   ("Woman in the City", "$28", "黑麦威士忌加芝麻酊和气泡葡萄，芝麻香很特别。"),
   ("Wings to a Poem", "$30", "波本加奶酪Campari，上面一层班兰香气。")],
  ["gr_00.jpg", "gr_07.jpg", "gr_03.png", "gr_04.jpg", "gr_05.jpg"]),
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
cover("cover_A.jpg", ["th_05.jpg", ("edv1.webp", .45, .5), "ss_04.jpg", "bb_01.png", "ben_02.jpg", "gr_00.jpg"], "悉尼最适合华人的", "鸡尾酒")
cover("cover_B.jpg", ["ss_01.jpg", "th_05.jpg", "gr_03.png", "ss_03.jpg", ("edv1.webp", .45, .5), "bb_00.png"], "茉莉、桂花、荔枝", "悉尼的东方鸡尾酒")
print("ok")
