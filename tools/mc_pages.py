"""墨尔本杯科普：编辑风（照片在上，宋体标题，正文黑体，一种深绿点缀）。用法：python3 mc_pages.py 输出目录"""
import sys, re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def S(w, s): return ImageFont.truetype(NOTO + f"NotoSerifCJK-{w}.ttc", s, index=2)
def K(w, s): return ImageFont.truetype(NOTO + f"NotoSansCJK-{w}.ttc", s, index=2)
PAPER, INK, GREY, ACC = (250, 248, 244), (22, 22, 22), (120, 116, 110), (24, 82, 58)
M = 80
P = "data/post_img/mc25_"
od = sys.argv[1]

def photo(path, w, h, fy=.5, fx=.5):
    im = Image.open(path).convert("RGB")
    s = max(w / im.width, h / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    return ImageEnhance.Color(im.crop((round(x), round(y), round(x) + w, round(y) + h))).enhance(1.05)

def wrap(text, font, maxw):
    out = []
    for para in text.split("\n"):
        cur = ""
        for tok in re.findall(r"[A-Za-z0-9$.,'%]+(?: [A-Za-z][A-Za-z.']*)*|.", para):
            if font.getlength(cur + tok) > maxw and cur and tok not in "，。；：、）”」": out.append(cur); cur = tok
            else: cur += tok
        out.append(cur); out.append("")
    return out[:-1]

def page(n, img_path, kicker, title, body, out, ph=640, fy=.5, fx=.5):
    img = Image.new("RGB", (W, H), PAPER)
    img.paste(photo(img_path, W, ph, fy, fx), (0, 0))
    d = ImageDraw.Draw(img)
    y = ph + 50
    d.text((M, y), f"{n:02d}  {kicker}", font=K("Medium", 30), fill=ACC)
    y += 54
    tf = S("Bold", 72)
    while tf.getlength(title) > W - 2 * M: tf = S("Bold", tf.size - 4)
    d.text((M, y), title, font=tf, fill=INK); y += tf.size + 48
    bf = K("Regular", 38)
    for line in wrap(body, bf, W - 2 * M):
        if line == "": y += 24; continue
        d.text((M, y), line, font=bf, fill=INK); y += 62
    img.save(out)

# 封面
img = Image.new("RGB", (W, H), PAPER)
img.paste(photo(P + "cover.jpg", W, 900, .5, .55), (0, 0))
d = ImageDraw.Draw(img)
d.text((M, 960), "11月3日 星期二", font=K("Medium", 30), fill=ACC)
d.text((M, 1010), "墨尔本杯", font=S("Black", 150), fill=INK)
d.text((M, 1210), "你需要知道的一切", font=S("SemiBold", 68), fill=INK)
img.save(f"{od}/mc_01.png")

PAGES = [
 ("p01.jpg", "时间和地点", "悉尼人照常上班", "比赛在墨尔本的Flemington赛马场，11月3日星期二下午3点左右开跑。悉尼和墨尔本同一个时区，所以悉尼时间也是3点。\n全程3200米，跑完只要三分多钟。\n墨尔本当天是公众假期，悉尼不放假，想看直播得在上班时间抽空。", .45),
 ("p02.jpg", "外号", "“让一个国家停下来的比赛”", "这是墨尔本杯在澳洲最常见的外号。第一届是1861年，今年是第166届。\n每年开跑那几分钟，不少办公室、学校和酒吧都会把电视打开，大家一起看完再回去干活。", .55),
 ("p03.jpg", "奖金", "总奖金超过1000万澳元", "去年的冠军拿走450万澳元，外加一座价值几十万的金杯。\n奖杯用18K金手工打造，每年做一个新的，直接归冠军马的马主所有。\n从2025年开始，参赛的24匹马不管跑第几，每匹至少能分到10万澳元。", .45),
 ("p04.jpg", "规则", "越强的马，背得越重", "墨尔本杯是让磅赛：赛前官方会给每匹马定一个负重，实力越强，要背的铅块越重。最轻是50公斤，最重的那匹至少57公斤。\n目的是把实力拉平，所以冷门马经常赢。2015年夺冠的马，赔率是100赔1。", .5),
 ("p05.jpg", "出赛名单", "300多匹报名，只有24匹能上场", "每年有三四百匹马报名，经过几轮筛选，最后最多只能有24匹出赛。\n比赛前的星期六会抽闸位，也就是每匹马的起跑位置。号码越小越靠内道，跑的距离更短，一般被认为更有利。", .4),
 ("p06.jpg", "赔率", "$8是什么意思", "新闻里常看到某匹马“$8”。意思是押1块钱，如果它赢了，连本带利拿回8块。\n数字越小，代表越被看好。热门马常常只有$5左右，冷门马可以到$100以上。\n看懂这个数字，就能大概知道比赛前谁是热门。", .5),
 ("p07.jpg", "Sweep", "朋友之间最常见的玩法", "Sweep是一种小额抽签：每人交几块钱，随机抽到一匹马，按名次分奖池，有的还会给最后一名一份安慰奖。\n在维州，Sweep的奖池不能超过5000澳元，组织的人也不能从中抽成。", .5),
 ("p08.jpg", "穿搭", "帽子是重点", "赛马日有专门的时装比赛Fashions on the Field，现场会评出男女最佳着装。\n女士一般戴礼帽或头饰（fascinator），男士穿西装。很多人即使不去现场，也会在当天的聚会上这样打扮。", .35),
 ("p09.jpg", "传奇", "这些名字值得记住", "Makybe Diva是唯一一匹三连冠的马，从2003年赢到2005年。\n2015年，Michelle Payne成为第一位赢得墨尔本杯的女骑师。\n去年，Jamie Melham骑着Half Yours夺冠，又一位女骑师站上了领奖台。", .5),
 ("p10.jpg", "争议", "掌声之外", "墨尔本杯也一直有争议。2013年以来，至少有6匹马在杯赛日死亡，动物保护团体每年都会呼吁改革赛马制度。\n2014年，当年的热门马Admire Rakti赛后心脏衰竭死亡；2018年，The Cliffs of Moher在比赛中受伤后被安乐死。", .5),
]
for i, (im, k, t, b, fy) in enumerate(PAGES, 2):
    page(i - 1, P + im, k, t, b, f"{od}/mc_{i:02d}.png", 600, fy)
