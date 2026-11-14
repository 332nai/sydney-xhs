"""悉尼海景餐厅人均从低到高：首页多选项、排行、结论、两店一页的介绍。
人均 = 一个前菜加一个主菜（取菜单中位价），不算饮料；只有套餐的按最便宜的晚餐套餐。
用法：python3 tools/view_cards.py 图片目录 输出目录"""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
Image.MAX_IMAGE_PIXELS = None
W, H = 1080, 1440
SRC, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
CREAM = (246, 244, 238); INK = (18, 32, 46); GREY = (70, 76, 82); LINE = (204, 210, 212); SEA = (22, 92, 120)
CRM = (255, 244, 214); BRN = (20, 34, 44); GOLD = (255, 200, 70)
def zh(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def serif(s): return ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", s, index=2)

def crop(spec, w, h):
    spec = list(spec) if isinstance(spec, tuple) else [spec]
    name, fx, fy, z = spec + [.5, .5, 1.0][len(spec) - 1:]
    im = ImageOps.exif_transpose(Image.open(f"{SRC}/{name}")).convert("RGB")
    s = max(w / im.width, h / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    return ImageEnhance.Color(im.crop((round(x), round(y), round(x) + w, round(y) + h)).filter(ImageFilter.UnsharpMask(1.5, 30, 2))).enhance(1.05)

def wrap(text, font, width):
    toks = re.findall(r"[A-Za-z0-9&'.$,:]+|.", text); lines, cur = [], ""
    for t in toks:
        if font.getlength(cur + t) > width and cur and t not in "，。、！？）：；": lines.append(cur); cur = t.lstrip()
        else: cur += t
    if cur: lines.append(cur)
    return lines

def outlined(d, xy, text, f, sw, fill=CRM):
    d.text(xy, text, font=f, fill=fill, stroke_width=sw, stroke_fill=BRN)

def blur_name(t, text, f, cx, y, r=6.5):
    """店名写上再糊掉：看得出是店名，认不出是哪家"""
    lay = Image.new("RGBA", t.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    w = f.getlength(text); x = cx - w / 2
    d.text((x, y), text, font=f, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 200))
    box = (int(x - 24), int(y - 14), int(x + w + 24), int(y + f.size + 24))
    reg = lay.crop(box).filter(ImageFilter.GaussianBlur(r)); lay.paste(reg, box)
    base = t.convert("RGBA"); base.alpha_composite(lay); return base.convert("RGB")

# (店名, 人均, 景, 结论, 介绍, 怎么点, 照片[菜, 景])
V = [
 ("Opera Bar", "$68", "看大桥", "全悉尼最便宜的明信片海景，坐下就是海港大桥。",
  "歌剧院脚下的露天大排档，不用订位，天天有现场音乐。景和隔壁几百块的餐厅一模一样，吃的是简单的海鲜和汉堡。",
  "怎么点：椒盐鱿鱼$26，加一份炸鱼薯条，傍晚去占位。",
  [("operabar/s_9.jpg", .5, .5), ("operabar/s_11.jpg", .5, .5)]),
 ("Bergs", "$68", "看邦迪", "邦迪最好的位置，楼上一半的价钱。",
  "Bondi Icebergs Club二楼的小餐厅，窗外就是那个上了无数明信片的海边泳池。和楼上的Icebergs Dining Room看的是同一片海。",
  "怎么点：一个前菜一个意面，中午去光线最好。",
  [("bergs/s_11.webp", .5, .5), ("bergs/s_7.png", .5, .5)]),
 ("Café Sydney", "$79", "看夜景", "看大桥夜景最稳的一家，请客户不会出错。",
  "环形码头Customs House的顶楼，大露台正对海港大桥。菜是澳式海鲜，生蚝和海鲜拼盘是招牌，晚上灯亮起来最好看。",
  "怎么点：一打生蚝两个人分，再各点一个主菜。",
  [("cafesyd/to_106137645.jpg", .5, .5), ("cafesyd/to_106011696.jpg", .5, .5)]),
 ("Nobu", "$84", "看日落", "外地朋友想吃熟悉的味道，带来这里。",
  "Crown Sydney里的Nobu，窗外是巴兰加鲁的海港，傍晚太阳正好落在对面。全球连锁的招牌一样不少，周六加收10%，周日15%。",
  "怎么点：鲣鱼辣椒刺身$37，味噌银鳕鱼$68。",
  [("nobu/c_7.jpg", .5, .5), ("nobu/c_9.jpg", .5, .5)]),
 ("Doyles", "$92", "带爸妈", "带爸妈最合适，坐渡轮过去就是一天。",
  "Watsons Bay海滩上的老牌海鲜馆，一家人做了五代。从环形码头坐渡轮过去，吃完沿着海边走到悬崖看海，长辈都喜欢。",
  "怎么点：炸鱼薯条或者海鲜拼盘，一定要坐户外。",
  [("dy2/DoylesontheBeach_0083-1-scaled.jpg", .5, .6), ("dy2/DoylesontheBeach_0057-1-scaled.jpg", .5, .5)]),
 ("a'Mare", "$95", "看海港", "意大利菜里最有仪式感，意面在桌边现做。",
  "Crown Sydney一楼，Alessandro Pavoni的意大利餐厅，落地窗外是巴兰加鲁的海港。青酱意面在你面前拌，海鲜都是澳洲本地的。",
  "怎么点：生鲷鱼$36，桌边青酱意面$42。",
  [("amare/c_4.jpg", .5, .5), ("amare/c_5.jpg", .5, .5)]),
 ("Bathers' Pavilion", "$105", "海滩边", "离城最远，也最安静，适合慢慢吃一顿。",
  "北岸Balmoral海滩上一栋白色的老建筑，前面是海湾，后面是棕榈树。周末白天去，吃完可以在沙滩上走一圈。",
  "怎么点：两道菜$105，前菜加主菜。",
  [("bathers/to_106395839.jpg", .5, .5), ("bathers/to_105972952.jpg", .5, .5)]),
 ("Catalina", "$130", "约会", "约会首选，整面落地窗，看水上飞机在面前起降。",
  "Rose Bay的海湾上，餐厅一半伸到水面。白桌布、帆船、对面就是城市的天际线，开了三十多年，是悉尼人庆祝纪念日的老地方。",
  "怎么点：周一到周四两道菜$130，海鲜是强项。",
  [("catalina/to_106214786.jpg", .5, .5), ("catalina/to_106214785.jpg", .5, .5)]),
 ("Icebergs", "$135", "最不值", "景和楼下Bergs一样，多出来的$67是菜和服务。",
  "邦迪泳池正上方，悉尼最有名的海景餐厅之一，意大利菜，蓝色的装修很上镜。菜不差，但只想看邦迪，楼下就够了。",
  "怎么点：两道菜$135，金枪鱼塔塔加大虾意面。",
  [("icebergs/to_106175726.jpg", .5, .5), ("icebergs/to_106115580.jpg", .5, .5)]),
 ("Aria", "$225", "看歌剧院", "求婚首选，窗外正对歌剧院。",
  "Matt Moran的餐厅，在环形码头东侧，一边是歌剧院，一边是海港大桥。晚餐只有四道菜，坐窗边要提早订。",
  "怎么点：四道菜$225，订位时说想要窗边。",
  [("aria/to_105913825.jpg", .5, .5), ("aria/to_105913818.jpg", .5, .5)]),
 ("Bennelong", "$240", "一生一次", "这11家里最贵，因为你坐在歌剧院里面。",
  "歌剧院最小的那个帆顶下面，抬头是贝壳一样的混凝土拱顶，窗外是海港。晚餐三道菜，主菜有Blackmore和牛牛胸和Murray鳕鱼。来悉尼一次，值得进去吃一顿。",
  "怎么点：三道菜$240，进门前在帆顶下拍照。",
  [("bn2/3.png", .5, .5), ("bn2/4.png", .5, .5)]),
]
NAMES = [v[0] for v in V]; PR = {v[0]: v[1] for v in V}; TAG = {v[0]: v[2] for v in V}

def half(img, y0, hh, v, ph=300):
    name, price, tag, verdict, intro, order, pics = v
    pw = W // 2
    img.paste(crop(pics[0], pw - 2, ph), (0, y0)); img.paste(crop(pics[1], pw - 2, ph), (pw + 2, y0))
    d = ImageDraw.Draw(img); fn_ = serif(54); fp = zh(46, "Black"); fv = zh(36, "Bold"); fi = zh(32); lh = 46
    y = y0 + ph + 22
    d.text((60, y), name, font=fn_, fill=INK); t = "人均" + price
    d.text((W - 60 - fp.getlength(t), y + 4), t, font=fp, fill=INK)
    y += 78
    for ln in wrap(verdict, fv, 960): d.text((62, y), ln, font=fv, fill=SEA); y += 52
    y += 4
    for ln in wrap(intro, fi, 960): d.text((62, y), ln, font=fi, fill=GREY); y += lh
    y += 6
    for ln in wrap(order, fi, 960): d.text((62, y), ln, font=fi, fill=INK); y += lh
    assert y < y0 + hh - 6, (name, y - y0)

def page(fn, a, b=None):
    img = Image.new("RGB", (W, H), CREAM)
    if b: half(img, 0, 720, a, 280); half(img, 720, 720, b, 280); ImageDraw.Draw(img).rectangle((0, 716, W, 724), fill=CREAM)
    else: half(img, 0, H, a, 1060)
    img.save(f"{OUT}/{fn}", quality=93)

for k, i in enumerate(range(0, 10, 2)): page(f"{k + 3:02d}.jpg", V[i], V[i + 1])
page("08.jpg", V[10])

# 01 排行
img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
d.text((60, 64), "悉尼海景餐厅人均", font=serif(84), fill=INK)
d.text((62, 182), "一个前菜加一个主菜，不算饮料，只有套餐的按套餐算", font=zh(34), fill=GREY)
fn_ = zh(44, "Medium"); fp = zh(44, "Bold"); ft = zh(32, "Bold"); y = 280; lh = (H - 320) // 11
for i, n in enumerate(NAMES):
    d.text((60, y), f"{i + 1:>2}", font=fp, fill=GREY); d.text((130, y), n, font=fn_, fill=INK)
    tx = 130 + fn_.getlength(n) + 22; d.text((tx, y + 8), TAG[n], font=ft, fill=SEA)
    pw = fp.getlength(PR[n]); x0 = tx + ft.getlength(TAG[n]) + 20; x1 = W - 60 - pw - 20
    for xx in range(int(x0), int(x1), 14): d.ellipse((xx, y + 32, xx + 4, y + 36), fill=LINE)
    d.text((W - 60 - pw, y), PR[n], font=fp, fill=INK); y += lh
img.save(f"{OUT}/01.jpg", quality=93)

# 02 老杨的结论
img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
d.text((60, 64), "老杨的结论", font=serif(84), fill=INK)
C = [("最划算", "Opera Bar", "人均$68，看的是和几百块餐厅一样的海港大桥。"),
     ("同一片海", "Bergs 对比 Icebergs", "邦迪泳池那个景，楼下$68，楼上$135，只为看海选楼下。"),
     ("带爸妈", "Doyles", "坐渡轮去Watsons Bay，炸鱼薯条，长辈最开心。"),
     ("约会", "Catalina", "整面落地窗，水上飞机在面前起降。"),
     ("求婚", "Aria", "窗外正对歌剧院，晚上亮灯那一刻最好。"),
     ("一生一次", "Bennelong", "坐在歌剧院帆顶下面吃饭，全世界只有这一家。")]
y = 210; f1 = zh(36, "Bold")
for tag, n, s_ in C:
    d.text((60, y + 10), tag, font=f1, fill=SEA)
    d.text((60 + f1.getlength(tag) + 28, y), n, font=serif(52), fill=INK); y += 82
    for ln in wrap(s_, zh(34), 960): d.text((62, y), ln, font=zh(34), fill=GREY); y += 50
    y += 32
assert y < H, y
img.save(f"{OUT}/02.jpg", quality=93)

# ===== 首页 =====
CT = {"Opera Bar": "最划算", "Bergs": "看邦迪", "Café Sydney": "看夜景", "Catalina": "约会", "Aria": "看歌剧院", "Bennelong": "一生一次",
      "Icebergs": "看邦迪", "Doyles": "带爸妈", "Nobu": "看日落"}
CP = {"Opera Bar": ("operabar/s_11.jpg", .5, .55), "Bergs": ("bergs/s_7.png", .5, .45), "Café Sydney": ("cafesyd/to_106011696.jpg", .45, .5),
      "Catalina": ("catalina/to_106214785.jpg", .5, .5), "Aria": ("aria/to_105913818.jpg", .3, .5), "Bennelong": ("bn2/3.png", .5, .5),
      "Icebergs": ("icebergs/to_106115580.jpg", .5, .5), "Doyles": ("dy2/DoylesontheBeach_0057-1-scaled.jpg", .5, .5),
      "Nobu": ("nobu/c_9.jpg", .5, .5)}

def title(d, top, y=40):
    f1 = zh(108, "Black"); f2 = zh(64, "Black"); f3 = zh(88, "Black")
    d.text((60, y), top, font=f1, fill=CRM)
    yy = y + 135; d.text((60, yy + 15), "人均", font=f2, fill=CRM); x = 60 + f2.getlength("人均") + 16
    d.text((x, yy), "$68", font=f3, fill=GOLD); x += f3.getlength("$68") + 16
    d.text((x, yy + 15), "到", font=f2, fill=CRM); x += f2.getlength("到") + 16
    d.text((x, yy), "$240", font=f3, fill=GOLD)

def tile(n, w, h, ftag, fp, fname, tagy=18):
    t = crop(CP[n], w, h); d = ImageDraw.Draw(t)
    outlined(d, ((w - ftag.getlength(CT[n])) / 2, tagy), CT[n], ftag, max(5, ftag.size // 12))
    outlined(d, ((w - fp.getlength(PR[n])) / 2, h / 2 - fp.size / 2), PR[n], fp, 8)
    return blur_name(t, n, fname, w / 2, h - fname.size - 34)

def cov_hero(fn, pick, top="悉尼海景餐厅"):
    img = Image.new("RGB", (W, H), (14, 26, 36)); d = ImageDraw.Draw(img); title(d, top)
    cw, ch = (W - 6) // 2, (H - 300 - 6) // 3
    for i, n in enumerate(pick):
        t = tile(n, cw - 6, ch - 6, zh(64, "Black"), zh(96, "Black"), zh(46, "Black"))
        img.paste(t, (3 + (i % 2) * cw + 3, 300 + (i // 2) * ch + 3))
    img.save(f"{OUT}/{fn}", quality=93)

def cov_four(fn, pick):
    img = Image.new("RGB", (W, H), (14, 26, 36)); cw, ch = W // 2, H // 2
    for i, n in enumerate(pick):
        t = tile(n, cw - 4, ch - 4, zh(84, "Black"), zh(132, "Black"), zh(50, "Black"), tagy=30)
        img.paste(t, ((i % 2) * cw + 2, (i // 2) * ch + 2))
    img.save(f"{OUT}/{fn}", quality=93)

def cov_versus(fn):
    img = Image.new("RGB", (W, H), (14, 26, 36)); d = ImageDraw.Draw(img); hh = (H - 260) // 2
    f1 = zh(84, "Black"); d.text((60, 50), "同一片邦迪海", font=f1, fill=CRM); d.text((60, 150), "楼下楼上差一倍", font=f1, fill=GOLD)
    for k, (n, spec) in enumerate([("Bergs", ("bergs/s_7.png", .5, .5)), ("Icebergs", ("icebergs/to_106115580.jpg", .5, .5))]):
        t = crop(spec, W, hh - 6); dd = ImageDraw.Draw(t); fb = zh(150, "Black")
        outlined(dd, (60, 30), "楼下" if k == 0 else "楼上", zh(84, "Black"), 7)
        outlined(dd, (W - 60 - fb.getlength("人均" + PR[n]), hh - 230), "人均" + PR[n], fb, 10)
        t = blur_name(t, n, zh(50, "Black"), 200, hh - 90)
        img.paste(t, (0, 260 + k * hh + 3))
    img.save(f"{OUT}/{fn}", quality=93)

cov_hero("cover_A.jpg", ["Opera Bar", "Bergs", "Café Sydney", "Catalina", "Aria", "Bennelong"])
cov_hero("cover_B.jpg", ["Opera Bar", "Bergs", "Doyles", "Catalina", "Aria", "Bennelong"], top="来悉尼吃海景")
cov_four("cover_C.jpg", ["Opera Bar", "Catalina", "Aria", "Bennelong"])
cov_versus("cover_D.jpg")
print("ok")
