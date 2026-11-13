"""悉尼唐人街搬家史：档案风今昔对比。首页、路线图、四张今昔卡。
用法：python3 tools/chinatown_cards.py 图片目录 老杨图标目录 输出目录"""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
Image.MAX_IMAGE_PIXELS = None
W, H = 1080, 1440
SRC, ICONS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
PAPER = (236, 229, 214); INK = (32, 28, 24); SEP = (120, 92, 60); RED = (150, 36, 30)
def serif(s): return ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", s, index=2)
def serifr(s): return ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc", s, index=2)

def crop(spec, w, h, old=False):
    spec = list(spec) if isinstance(spec, tuple) else [spec]
    name, fx, fy, z = spec + [.5, .5, 1.0][len(spec) - 1:]
    im = ImageOps.exif_transpose(Image.open(f"{SRC}/{name}")).convert("RGB")
    s = max(w / im.width, h / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    im = im.crop((round(x), round(y), round(x) + w, round(y) + h))
    return im.filter(ImageFilter.UnsharpMask(1.2, 40, 2)) if old else ImageEnhance.Color(im.filter(ImageFilter.UnsharpMask(1.5, 30, 2))).enhance(1.05)

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

def stamp(d, x, y, text, size=56):
    f = serif(size); w = f.getlength(text)
    d.rectangle((x, y, x + w + 36, y + size + 26), fill=PAPER); d.text((x + 18, y + 6), text, font=f, fill=INK)


def framed(img, photo, box, label, old, size=48):
    x0, y0, x1, y1 = box; pad = 12
    ImageDraw.Draw(img).rectangle(box, fill="white")
    im = crop(photo, x1 - x0 - 2 * pad, y1 - y0 - 2 * pad, old); img.paste(im, (x0 + pad, y0 + pad))
    stamp(ImageDraw.Draw(img), x0 + pad, y1 - pad - size - 34, label, size)

def locator(img, stop):
    """右上角小地图：竖线是George St，上面是第一站，下面东边第二站、西边第三站"""
    d = ImageDraw.Draw(img); x0, y0, x1, y1 = 850, 20, 1040, 200
    d.rectangle((x0, y0, x1, y1), fill=(226, 216, 196), outline=SEP, width=2)
    cx = (x0 + x1) // 2; d.line((cx, y0 + 18, cx, y1 - 14), fill=INK, width=5)
    pts = {1: (cx, y0 + 46), 2: (cx + 46, y1 - 46), 3: (cx - 46, y1 - 46)}
    d.line((cx - 46, y1 - 46, cx + 46, y1 - 46), fill=SEP, width=3)
    f = serif(26)
    for k, (px, py) in pts.items():
        on = k == stop; r = 22 if on else 16
        d.ellipse((px - r, py - r, px + r, py + r), fill=RED if on else (170, 158, 138), outline=INK, width=2)
        t = "一二三"[k - 1]; d.text((px - f.getlength(t) / 2, py - 17), t, font=f, fill="white")

def card(fn, head, sub, photos, text, stop=None):
    """一页一到两张大图，下面一大段文字。photos里每项是(图, 标签, 是否老照片)"""
    img = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(img)
    if stop: locator(img, stop)
    d.text((60, 46), head, font=serif(70), fill=INK); d.text((62, 140), sub, font=serifr(38), fill=SEP)
    d.line((60, 205, 850 if stop else W - 60, 205), fill=INK, width=3)
    f = serifr(34); lines = wrap(text, f, 960); th = len(lines) * 52 + 30
    avail = H - 228 - th - 40; n = len(photos); gh = (avail - 12 * (n - 1)) // n
    y = 228
    for ph, lab, old in photos:
        framed(img, ph, (60, y, W - 60, y + gh), lab, old, 44); y += gh + 12
    y += 22
    for ln in lines: d.text((60, y), ln, font=f, fill=INK); y += 52
    assert y < H - 8 and gh > 300, (fn, y, gh)
    img.save(f"{OUT}/{fn}", quality=93)

def gallery(fn, head, sub, photos, text):
    img = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(img)
    d.text((60, 46), head, font=serif(70), fill=INK); d.text((62, 140), sub, font=serifr(38), fill=SEP)
    d.line((60, 205, W - 60, 205), fill=INK, width=3)
    top = 228; gh = 470; xs = [(60, 535), (545, W - 60)]
    for i, (ph, lab) in enumerate(photos):
        r, c = divmod(i, 2); x0, x1 = xs[c]; y0 = top + r * (gh + 10)
        framed(img, ph, (x0, y0, x1, y0 + gh), lab, True, 38)
    f = serifr(34); y = top + 2 * (gh + 10) + 20
    for ln in wrap(text, f, 960): d.text((60, y), ln, font=f, fill=INK); y += 52
    assert y < H - 8, (fn, y)
    img.save(f"{OUT}/{fn}", quality=93)

P = [
 ("02.jpg", "起点：第一批华人", "1818年到1850年代", [("old_352.jpg", "当年的悉尼港码头", True)],
  "有记录的第一位华人移民叫麦世英，广东人，1818年来到悉尼，住在Parramatta，后来还开了一家旅馆。1848年，一艘帆船从华南运来121个签了合约的劳工，一半留在悉尼。1851年新州发现金矿，消息传回广东，大批华人坐船过来淘金，到1861年新州已经有13,000个华人。", None),
 ("03.jpg", "第一站 The Rocks", "1850年代到1900年前后",
  [("old_116.jpg", "The Rocks的华人家具厂", True), (("old_137.jpg", .5, .5), "1900年 George St上的华人宿舍", True)],
  "金矿挖完之后，很多华人回到悉尼城里，先住在离码头最近的The Rocks，也就是今天海港大桥脚下的老城区。他们沿着George St开杂货店、饭馆、给同乡住的宿舍，还有好几家家具作坊。19世纪末，悉尼最有钱的华商也住在这里。", 1),
 ("04.jpg", "人越来越多", "1861年到1900年",
  [(("old_176.jpg", .5, .45), "1908年 George St上的华人商号", True), (("now_231george.jpg", .5, .55), "今天的George St，The Rocks", False)],
  "1861年悉尼城里只登记了189个华人，1871年336人，1881年已经有1,321人。人多了，限制也来了：1881年和1888年两次立法，华人入境要交人头税。到了1900年，城里大部分华人已经往南搬，搬到中央车站北边的Haymarket。", 1),
 ("05.jpg", "第二站 Campbell St", "城南Haymarket，George St东边",
  [(("c_wexford.jpg", .5, .55), "1900年 Wexford St", True), (("c_campbell1900.jpg", .5, .55), "1900年 Campbell St", True)],
  "那时候城南有一个大菜市场，叫Belmore Markets，就在Campbell St上。这栋楼今天还在，改成了演音乐剧的Capitol Theatre剧院。华人菜农每天把菜拉到这里卖，晚上就近住下，于是周围几条街开起了宿舍、杂货铺和小饭馆，一直延伸到东边的Wexford St。这一片就是第二个唐人街。", 2),
 ("06.jpg", "一条街被整个拆掉", "1900年到1906年",
  [(("c_wexford_bedroom.jpg", .5, .55), "1900年 Wexford St上华人住的后院", True), (("old_131.jpg", .5, .5), "1906年拆之前的Wexford St", True)],
  "1900年悉尼闹鼠疫，政府派人清理贫民区，顺手拍下了这些照片。华人住的地方经常被市政府上门检查。1906年，市政府以清理贫民窟为由，把整条Wexford St拆掉，724人被赶走。", 2),
 ("07.jpg", "原址变成了大马路", "1906年以后",
  [(("now_wentworth.jpg", .5, .55), "原来的Wexford St，今天的Wentworth Ave", False)],
  "Wexford St拆掉后，原地修了一条通往中央车站的大路，就是今天的Wentworth Ave。被赶走的华人只能另找地方住，刚好George St西边正在盖一个新的大菜市场，第三个唐人街就这样开始了。", 2),
 ("08.jpg", "第三站 Dixon St", "城南Haymarket，George St西边",
  [(("old_315.jpg", .5, .5), "1933年 新菜市场旁的华人水果车", True), (("old_223.png", .5, .4), "1950年 Dixon St", True)],
  "1909到1915年，George St西边盖起了新的大菜市场，就是今天Market City楼下的Paddy's Markets。旧的Belmore Markets在1912年关掉，华人也跟着过了George St往西搬，其实只挪了几百米。到1930年代，Dixon St已经是大家公认的唐人街。", 3),
 ("09.jpg", "战后的唐人街", "1940年代到1960年代",
  [(("old_015.jpg", .45, .45, 1.08), "1954年 Dixon St的店铺", True), (("old_222.jpg", .5, .5), "1949年 新中国酒家", True)],
  "1901年澳洲开始实行白澳政策，限制非白人移民，加上更早的入境限制，全澳华人从1880年的3万7千多人，降到1911年大约2万3千人。二战后政策慢慢松动，1947年起华商的太太和孩子可以留下来。1950年代又有一批东南亚华人学生来澳洲读书，很多人常来这条街。", 3),
 ("10.jpg", "要不要把它变成唐人街", "1961年到1979年",
  [(("old_089.jpg", .5, .5), "1970年代 还能通车的Dixon St", True), (("old_093.jpg", .5, .45), "1979年 Dixon St", True)],
  "1961年市政府就讨论过，要不要把Dixon St做成正式的唐人街。1960年代末，大菜市场的批发生意搬到了西边的Flemington，这一片空出来可以重新规划。1970年代初白澳政策彻底取消，市政府成立了专门的华人委员会，开始改造Dixon St。", 3),
 ("11.jpg", "牌楼立起来了", "1979年到1980年",
  [(("old_097.jpg", .5, .5), "1980年 开街当天", True), (("old_080.jpg", .5, .5), "1984年 Dixon St", True)],
  "1979年中秋节开始，Dixon St不再让车走，改成步行街。委员会花了3万澳元修牌楼，请华裔建筑师Henry Tsang设计。1980年悉尼市长来剪彩，街两头的牌楼就是那时候立起来的。柱子上刻的英文意思是：古老的中国举世闻名；守住自由与信任，就守住了过去的美德。", 3),
 ("12.jpg", "今天的唐人街", "1970年代到2026年",
  [(("now_dixon1.jpg", .5, .45), "2026年的牌楼", False), (("now_dixon2.jpg", .5, .6), "2026年的Dixon St", False)],
  "1970年代以后，新移民从中国大陆、台湾、香港、新加坡、马来西亚过来，很多是受过教育的专业人士。从海港边的The Rocks，到老菜市场旁的Campbell St，再到新菜市场旁的Dixon St，唐人街一直跟着菜市场和生计在走。", 3),
]
for p_ in P: card(*p_)
gallery("13.jpg", "老照片里的华人生活", "1900年代到1970年代",
  [(("old_108.jpg", .5, .5), "1900年代 菜贩"), (("old_227.jpg", .5, .5), "1979 Tai Yuen餐馆"), (("old_128.jpg", .5, .5), "Surry Hills的孩子"), (("old_226.jpg", .5, .5), "1979 Tai Yuen酒楼")],
  "早期华人在悉尼多是菜农、小贩、家具工人和店主。菜农天不亮就把菜运进城，挑着担子走街串巷，市场旁边就是他们的寄宿屋、饭馆和杂货铺。孩子们在小巷里跟邻居家的孩子一起玩。到了1970年代，Dixon St一带已经是一家接一家的酒楼。")

# 01 路线图：George St从北到南，第二、三站隔着George St一东一西
img = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(img)
d.text((60, 46), "唐人街搬家路线", font=serif(70), fill=INK); d.text((62, 140), "沿着George St，从北搬到南", font=serifr(38), fill=SEP)
d.line((60, 205, W - 60, 205), fill=INK, width=3)
x = W // 2; y0, y1 = 290, 1170
d.line((x, y0, x, y1), fill=INK, width=10)
fG = serif(40); d.text((x + 20, 560), "George St", font=fG, fill=SEP)
fs, fb, fn = serifr(32), serif(46), serif(40)
def dot(xx, yy): d.ellipse((xx - 22, yy - 22, xx + 22, yy + 22), fill=RED, outline=INK, width=4)
d.text((x - 300, y0 - 64), "北：Circular Quay码头", font=fs, fill=SEP)
dot(x, 360); d.text((x + 48, 318), "1850s 第一站", font=fn, fill=RED); d.text((x + 48, 372), "The Rocks", font=fb, fill=INK)
d.text((x + 48, 436), "海港大桥脚下", font=fs, fill=SEP)
# Haymarket 区块
d.rectangle((70, 760, W - 70, 1110), outline=SEP, width=3)
d.text((90, 772), "Haymarket", font=serif(44), fill=SEP)
d.line((x - 200, 950, x, 950), fill=RED, width=6); d.line((x, 950, x + 200, 950), fill=RED, width=6)
dot(x + 210, 950); dot(x - 210, 950)
d.text((x + 70, 840), "1890s 第二站", font=fn, fill=RED); d.text((x + 70, 986), "Campbell St", font=fb, fill=INK)
d.text((x + 70, 1046), "老菜市场旁", font=fs, fill=SEP)
d.text((90, 840), "1910s 第三站", font=fn, fill=RED); d.text((90, 986), "Dixon St", font=fb, fill=INK)
d.text((90, 1046), "新菜市场旁", font=fs, fill=SEP)
d.text((x - 170, 880), "往西", font=serif(36), fill=RED)
d.text((x - 120, y1 + 20), "南：Central车站", font=fs, fill=SEP)
f = serifr(34); yy = 1240
for ln in wrap("第二站和第三站都在Haymarket，只隔一条George St。老菜市场Belmore Markets今天是Capitol Theatre剧院，新菜市场就是今天的Paddy's Markets。", f, 960): d.text((60, yy), ln, font=f, fill=INK); yy += 50
img.save(f"{OUT}/01.jpg", quality=93)

# 首页：上旧下新，中间档案纸条写标题
def cover(fn, old, new, oy, ny):
    c = Image.new("RGB", (W, H), PAPER)
    c.paste(crop(old, W, 640, True), (0, 0)); c.paste(crop(new, W, 640), (0, 800))
    d = ImageDraw.Draw(c); f = serif(92)
    d.text((60, 652), "悉尼唐人街搬过三次家", font=f, fill=INK)
    stamp(d, 30, 540, oy, 56); stamp(d, 30, 1330, ny, 56)
    icon(c, "06_拍照打卡", W - 230, 30, 190).save(f"{OUT}/{fn}", quality=93)
cover("cover_A.jpg", ("old_093.jpg", .5, .45), ("now_dixon1.jpg", .5, .45), "1979", "2026")
cover("cover_B.jpg", ("old_015.jpg", .45, .45, 1.08), ("now_dixon2.jpg", .5, .55), "1954", "2026")
print("ok")
