"""悉尼牛排馆人均从低到高：12宫格首页、排行、结论、6张两店一页的介绍。
用法：python3 tools/omakase_cards.py 图片目录 老杨图标目录 输出目录"""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
Image.MAX_IMAGE_PIXELS = None
W, H = 1080, 1440
SRC, ICONS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
CREAM = (248, 244, 236); INK = (26, 28, 36); GREY = (70, 66, 60); LINE = (214, 206, 192)
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

def icon(img, pose, x, y, h):
    ic = Image.open(f"{ICONS}/{pose}.png").convert("RGBA"); ic = ic.resize((round(ic.width * h / ic.height), h), Image.LANCZOS)
    img = img.convert("RGBA"); sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 255), (x + 4, y + 6), ic.split()[3].point(lambda v: int(v * .3)))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8))); img.alpha_composite(ic, (x, y)); return img.convert("RGB")

def wrap(text, font, width):
    toks = re.findall(r"[A-Za-z0-9&'.$,:]+|.", text); lines, cur = [], ""
    for t in toks:
        if font.getlength(cur + t) > width and cur and t not in "，。、！？）：；": lines.append(cur); cur = t.lstrip()
        else: cur += t
    if cur: lines.append(cur)
    return lines


RED = (150, 30, 24)
def half(img, y0, hh, photo, name, price, verdict, intro, order):
    ph = 280; img.paste(crop(photo, W, ph), (0, y0)); d = ImageDraw.Draw(img)
    fn_ = serif(54); fp = zh(46, "Black"); fv = zh(36, "Bold"); fi = zh(32); lh = 46
    y = y0 + ph + 22
    d.text((60, y), name, font=fn_, fill=INK); t = "人均" + price
    d.text((W - 60 - fp.getlength(t), y + 4), t, font=fp, fill=INK)
    y += 76
    for ln in wrap(verdict, fv, 960): d.text((62, y), ln, font=fv, fill=RED); y += 52
    y += 4
    for ln in wrap(intro, fi, 960): d.text((62, y), ln, font=fi, fill=GREY); y += lh
    y += 6
    for ln in wrap(order, fi, 960): d.text((62, y), ln, font=fi, fill=INK); y += lh
    assert y < y0 + hh - 6, (name, y - y0)
def page(fn, a, b):
    img = Image.new("RGB", (W, H), CREAM)
    half(img, 0, 720, *a); half(img, 720, 720, *b)
    ImageDraw.Draw(img).rectangle((0, 716, W, 724), fill=CREAM)
    img.save(f"{OUT}/{fn}", quality=93)

V = [
 ("york.jpg", "24 York", "$55", "下班一个人吃牛排，最不用动脑的一家。",
  "Rockpool同一个集团开的巴黎风牛排薯条馆，整个菜单只有一种牛排，你只需要选酱汁。上菜快，下午4点到6点马天尼和Negroni只要$12。",
  "两个人：两份牛排薯条，加一份沙拉。"),
 (("alfies.jpg", .5, .5), "Alfie's", "$60", "$39的干式熟成西冷，全悉尼最划算的一块好牛排。",
  "Bistecca和The Gidley同一个团队，220克Riverine西冷在店里自己干式熟成，15分钟上桌，配大蒜芥末辣根做的绿酱。马天尼从保温壶里倒，是悉尼最冰的之一。",
  "两个人：两块西冷，一个前菜，两个配菜。"),
 (("porteno.jpg", .62, .5), "Porteño", "$130", "朋友聚会最热闹，吃的是阿根廷炭火，不只是牛排。",
  "带动悉尼拉美餐厅风潮的阿根廷烤肉馆。招牌是北昆士兰草饲和牛裙肉，切片铺在烤红椒上，淋很多橄榄油。炭烤鱿鱼和焦糖布丁也别错过。",
  "两个人：一块两人份牛排，一个前菜，两个配菜。"),
 ("bistecca.jpg", "Bistecca", "$130", "高端牛排馆里性价比第一，只做一种牛排，而且做到极致。",
  "地下室里只卖佛罗伦萨T骨，$21一百克，你说要多重，切好先端来给你看。只用橄榄木和铁皮木的烟熏一下，西冷和菲力两边都吃得到。进门手机要收起来。",
  "两个人：一公斤T骨，一个前菜，两个配菜。"),
 ("chophouse.jpg", "Chophouse", "$140", "请客户吃午饭最稳的一家，菜单一页纸，不会出错。",
  "Matt Moran的CBD牛排馆，墙上嵌着干式熟成柜。想吃他家Oberon农场的牛，要点带骨那一栏，按一百克算钱，有最低重量。配菜里的花椰菜芝士焗很受欢迎。",
  "两个人：一公斤带骨牛排，一个前菜，两个配菜。"),
 (("margaret.jpg", .5, .5), "Margaret", "$140", "带爸妈来最合适，套餐省心，而且是澳洲排名第一的牛排餐厅。",
  "Neil Perry在双湾的旗舰店，用他妈妈的名字命名。今年世界最佳牛排餐厅榜单上是澳洲第一。$140的分享套餐有前菜、CopperTree农场牛菲力、配菜和甜品，不用纠结怎么点。",
  "两个人：$140一位的分享套餐。"),
 (("gidley.jpg", .5, .5), "The Gidley", "$145", "约会首选，天鹅绒包厢，手机进门就收走。",
  "CBD地下室，进门服务员帮你挂外套，把手机装进皮袋，带你进有帘子的天鹅绒卡座。这里rib eye是主角，可以点带骨的，也可以点很少见的spinalis，就是肋眼外圈最嫩的那一圈。它家汉堡也是悉尼最好吃的之一。",
  "两个人：一公斤带骨肋眼，一个前菜，两个配菜。"),
 (("woodcut.jpg", .5, .5), "Woodcut", "$180", "贵在场面，适合带外地朋友来见世面。",
  "Crown Sydney一楼，四个开放厨房分别管火、烟、冰、蒸，厨师之间戴耳机沟通，能坐300人。最好吃的还是木柴烤的牛排，平日酒吧有$15鸡尾酒的欢乐时光。",
  "两个人：一公斤Black Onyx T骨，一个前菜，两个配菜。"),
 ("intl.jpg", "The Grill", "$195", "CBD新开的高级牛排馆，团队来自Shell House。",
  "Martin Place的The International里的高级餐厅，厨师团队待过Sepia、Aria、Oncore、Icebergs。木柴烤的大块牛排装在银盘里上桌，已经进了世界最佳牛排餐厅榜。吃完可以上楼去天台酒吧。",
  "两个人：一块木柴烤大份牛排，一个前菜，两个配菜。"),
 ("rockpool.jpg", "Rockpool", "$205", "贵，但开了十几年从没失过手，悉尼牛排馆的标杆。",
  "Hunter Street的老牌牛排馆，肉全部在店里干式熟成，用木柴烤。牛来自澳洲最好的几家牧场，有David Blackmore全血和牛、Cape Grim草饲牛。配菜很多，mac and cheese一定要点。",
  "两个人：一公斤Rockpool Reserve T骨，一个前菜，两个配菜。"),
 (("sixhead.jpg", .5, .5), "6Head", "$220", "一半的钱花在海港景色上，带人来拍照很值。",
  "环形码头西岸的老仓库Campbell's Stores里，坐在户外就能看歌剧院和海港大桥。招牌战斧$375一公斤，还有自家的和牛肋眼。酱汁和配菜很出色，黄油土豆泥一定要点。",
  "两个人：一公斤招牌战斧，一个前菜，两个配菜。"),
 (("firedoor.jpg", .5, .5), "Firedoor", "$240", "这辈子至少去一次，这12家里最贵，但别处吃不到。",
  "Surry Hills，厨房不用电也不用煤气，只烧木柴。主厨Lennox Hastie做了一块150天干式熟成的带骨牛肋，几乎拿遍了所有奖。坐吧台可以看他烤肉。周五周六中午有单点。",
  "两个人：晚餐只有六道菜套餐，$240一位。"),
]
for i in range(0, 12, 2): page(f"{i // 2 + 3:02d}.jpg", V[i], V[i + 1])

# 01 排行
TAG = ["一个人吃", "最划算", "朋友聚会", "最值", "请客户", "带爸妈", "约会", "见世面", "最新", "标杆", "看风景", "一生一次"]
img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
d.text((60, 64), "悉尼牛排馆人均", font=serif(84), fill=INK)
d.text((62, 182), "两个人分一块招牌牛排，加一个前菜两个配菜，不算酒", font=zh(34), fill=GREY)
fn_ = zh(44, "Medium"); fp = zh(44, "Bold"); ft = zh(28, "Bold"); y = 270; lh = (H - 300) // 12
for i, (_, n, p, *_r) in enumerate(V):
    d.text((60, y), f"{i + 1:>2}", font=fp, fill=GREY); d.text((130, y), n, font=fn_, fill=INK)
    tx = 130 + fn_.getlength(n) + 20; tw = ft.getlength(TAG[i]) + 24
    d.rounded_rectangle((tx, y + 8, tx + tw, y + 52), radius=8, fill=RED); d.text((tx + 12, y + 11), TAG[i], font=ft, fill="white")
    pw = fp.getlength(p); x0 = tx + tw + 20; x1 = W - 60 - pw - 20
    for xx in range(int(x0), int(x1), 14): d.ellipse((xx, y + 32, xx + 4, y + 36), fill=LINE)
    d.text((W - 60 - pw, y), p, font=fp, fill=INK); y += lh
img.save(f"{OUT}/01.jpg", quality=93)

# 02 老杨结论
img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
d.text((60, 64), "老杨的结论", font=serif(84), fill=INK)
C = [("最值", "Bistecca", "人均$130，吃到的是全悉尼数一数二的T骨。比它贵的，大多贵在装修和地段。"),
     ("一个人", "Alfie's", "$39一块干式熟成西冷，比很多酒吧牛排还便宜，品质高一个档次。"),
     ("约会", "The Gidley", "包厢、灯光、收手机，气氛做到了，牛排也撑得住。"),
     ("带爸妈", "Margaret", "套餐不用研究菜单，口味稳，环境安静，长辈最舒服。"),
     ("最不值", "6Head", "牛排不差，但同样的钱在Bistecca能吃得更好，你付的是海景。"),
     ("一生一次", "Firedoor", "最贵，但只烧木柴的厨房全世界都少见，值得专门去一次。")]
y = 210
for tag, n, s_ in C:
    f1 = zh(34, "Bold"); tw = f1.getlength(tag) + 32
    d.rounded_rectangle((60, y + 6, 60 + tw, y + 60), radius=10, fill=RED); d.text((76, y + 10), tag, font=f1, fill="white")
    d.text((60 + tw + 24, y), n, font=serif(54), fill=INK); y += 82
    for ln in wrap(s_, zh(34), 960): d.text((62, y), ln, font=zh(34), fill=GREY); y += 50
    y += 30
assert y < H, y
img.save(f"{OUT}/02.jpg", quality=93)

# 首页12宫格
G = [(v[0], v[1], v[2]) for v in V]
G = [(p, {"The Grill": "The Grill", "The Gidley": "Gidley"}.get(n, n), pr) for p, n, pr in G]
CRM = (255, 244, 214); BRN = (38, 26, 16)
def outlined(d, xy, text, f, sw):
    d.text(xy, text, font=f, fill=CRM, stroke_width=sw, stroke_fill=BRN)
def wrap_words(text, f, maxw):
    lines, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if f.getlength(t) > maxw and cur: lines.append(cur); cur = w
        else: cur = t
    return lines + [cur]
def grid12(fn):
    g = Image.new("RGB", (W, H), (240, 236, 228)); cw, ch = W // 3, H // 4; tw_ = cw - 3; th_ = ch - 3
    fprice = zh(118, "Black"); fname = zh(62, "Black")
    for i, (p, n, pr) in enumerate(G):
        t = crop(p, tw_, th_); d = ImageDraw.Draw(t)
        outlined(d, ((tw_ - fprice.getlength(pr)) / 2, 14), pr, fprice, 9)
        ls = wrap_words(n, fname, tw_ - 30); lh = fname.size + 6; y = th_ - 30 - lh * len(ls)
        for ln in ls: outlined(d, ((tw_ - fname.getlength(ln)) / 2, y), ln, fname, 7); y += lh
        g.paste(t, ((i % 3) * cw + 1, (i // 3) * ch + 1))
    g.save(f"{OUT}/{fn}", quality=93)
grid12("cover.jpg")
print("ok")

# ===== 首页多选项：价格 + 标签 + 模糊店名 =====
TAGS = dict(zip([v[1] for v in V], TAG))
REDB = (200, 30, 24)
def blur_name(t, text, f, cx, y, r=7):
    """把店名写上再糊掉，看得出是店名但认不出是哪家"""
    lay = Image.new("RGBA", t.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    w = f.getlength(text); x = cx - w / 2
    d.rounded_rectangle((x - 16, y - 6, x + w + 16, y + f.size + 14), radius=10, fill=(0, 0, 0, 150))
    d.text((x, y), text, font=f, fill=(255, 255, 255, 255))
    box = (int(x - 20), int(y - 10), int(x + w + 20), int(y + f.size + 18))
    reg = lay.crop(box).filter(ImageFilter.GaussianBlur(r)); lay.paste(reg, box)
    base = t.convert("RGBA"); base.alpha_composite(lay); return base.convert("RGB")
def pill(d, cx, y, text, f, pad=18, fill=REDB):
    outlined(d, (cx - f.getlength(text) / 2, y), text, f, max(5, f.size // 12))
ORDER = [v[1] for v in V]; PIC = {v[1]: v[0] for v in V}; PR = {v[1]: v[2] for v in V}
# 首页上避开盘子上印的店名
PIC["Bistecca"] = ("bistecca.jpg", .55, .62, 1.45); PIC["Alfie's"] = ("alfies.jpg", .28, .62, 1.6)

def cov_grid12(fn, blur=True):
    g = Image.new("RGB", (W, H), (20, 16, 14)); cw, ch = W // 3, H // 4; tw_ = cw - 3; th_ = ch - 3
    fprice = zh(108, "Black"); ftag = zh(54, "Black"); fname = zh(34, "Black")
    for i, n in enumerate(ORDER):
        t = crop(PIC[n], tw_, th_); d = ImageDraw.Draw(t)
        outlined(d, ((tw_ - fprice.getlength(PR[n])) / 2, 10), PR[n], fprice, 9)
        pill(d, tw_ / 2, th_ / 2 - 6, TAGS[n], ftag, pad=16)
        t = blur_name(t, n, fname, tw_ / 2, th_ - 62) if blur else t
        g.paste(t, ((i % 3) * cw + 1, (i // 3) * ch + 1))
    g.save(f"{OUT}/{fn}", quality=93)

def cov_hero(fn):
    """上面大标题，下面6格精选：标签最大，价格其次，店名糊掉"""
    pick = ["Alfie's", "Bistecca", "The Gidley", "Margaret", "6Head", "Firedoor"]
    img = Image.new("RGB", (W, H), (22, 16, 12)); d = ImageDraw.Draw(img)
    f1 = zh(112, "Black"); f2 = zh(64, "Black")
    d.text((60, 40), "悉尼牛排馆", font=f1, fill=CRM)
    d.text((60, 175), "人均", font=f2, fill=CRM); x = 60 + f2.getlength("人均") + 16
    d.text((x, 160), "$55", font=zh(88, "Black"), fill=(255, 196, 64)); x += zh(88, "Black").getlength("$55") + 16
    d.text((x, 175), "到", font=f2, fill=CRM); x += f2.getlength("到") + 16
    d.text((x, 160), "$240", font=zh(88, "Black"), fill=(255, 196, 64))
    cw, ch = (W - 6) // 2, (H - 300 - 6) // 3; ftag = zh(64, "Black"); fp = zh(96, "Black"); fname = zh(36, "Black")
    for i, n in enumerate(pick):
        t = crop(PIC[n], cw - 6, ch - 6); dd = ImageDraw.Draw(t)
        pill(dd, (cw - 6) / 2, 18, TAGS.get(n, ""), ftag, pad=24)
        outlined(dd, (((cw - 6) - fp.getlength(PR[n])) / 2, ch / 2 - 40), PR[n], fp, 8)
        t = blur_name(t, n, fname, (cw - 6) / 2, ch - 70)
        img.paste(t, (3 + (i % 2) * cw + 3, 300 + (i // 2) * ch + 3))
    img.save(f"{OUT}/{fn}", quality=93)

def cov_four(fn):
    """四宫格大图：最值、约会、带爸妈、一生一次"""
    pick = ["Bistecca", "The Gidley", "Margaret", "Firedoor"]
    img = Image.new("RGB", (W, H), (22, 16, 12)); cw, ch = W // 2, H // 2
    ftag = zh(84, "Black"); fp = zh(132, "Black"); fname = zh(40, "Black")
    for i, n in enumerate(pick):
        t = crop(PIC[n], cw - 4, ch - 4); d = ImageDraw.Draw(t)
        pill(d, (cw - 4) / 2, 30, TAGS[n], ftag, pad=28)
        outlined(d, (((cw - 4) - fp.getlength("人均" + PR[n][1:]) * 0 - fp.getlength(PR[n])) / 2, ch / 2 - 40), PR[n], fp, 10)
        t = blur_name(t, n, fname, (cw - 4) / 2, ch - 90, r=8)
        img.paste(t, ((i % 2) * cw + 2, (i // 2) * ch + 2))
    img.save(f"{OUT}/{fn}", quality=93)

def cov_versus(fn):
    """对比：最值 vs 最不值"""
    img = Image.new("RGB", (W, H), (22, 16, 12)); d = ImageDraw.Draw(img); hh = (H - 260) // 2
    f1 = zh(84, "Black"); d.text((60, 50), "同样吃牛排", font=f1, fill=CRM); d.text((60, 150), "差的不只是钱", font=f1, fill=(255, 196, 64))
    for k, n in enumerate(["Bistecca", "6Head"]):
        t = crop(PIC[n], W, hh - 6); dd = ImageDraw.Draw(t)
        pill(dd, 220, 30, TAGS[n] if n != "6Head" else "最不值", zh(80, "Black"), pad=28, fill=REDB if k == 0 else (40, 40, 40))
        outlined(dd, (W - 60 - zh(150, "Black").getlength("人均" + PR[n]), hh - 230), "人均" + PR[n], zh(150, "Black"), 10)
        t = blur_name(t, n, zh(44, "Black"), 200, hh - 90, r=9)
        img.paste(t, (0, 260 + k * hh + 3))
    img.save(f"{OUT}/{fn}", quality=93)

cov_grid12("cover_A.jpg"); cov_hero("cover_B.jpg"); cov_four("cover_C.jpg"); cov_versus("cover_D.jpg")
print("covers ok")
