"""悉尼跨年饭价格帖：首页三选一，每家一张卡（上方6张图，下方店名、价格、介绍）。
用法：python3 tools/nye_cards.py 图片目录 老杨图标目录 输出目录"""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
Image.MAX_IMAGE_PIXELS = None
W, H = 1080, 1440
SRC, ICONS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
CREAM = (248, 244, 236); INK = (26, 28, 36); GOLD = (168, 120, 40)
def en(s): return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", s)
def zh(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", s, index=2)
def serif(s): return ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", s, index=2)

def crop(spec, w, h):
    spec = list(spec) if isinstance(spec, tuple) else [spec]
    name, fx, fy, z = spec + [.5, .5, 1.0][len(spec) - 1:]
    im = ImageOps.exif_transpose(Image.open(f"{SRC}/{name}")).convert("RGB")
    s = max(w / im.width, h / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(fx * im.width - w / 2, 0), im.width - w); y = min(max(fy * im.height - h / 2, 0), im.height - h)
    im = im.crop((round(x), round(y), round(x) + w, round(y) + h)).filter(ImageFilter.UnsharpMask(2, 40, 2))
    return ImageEnhance.Color(im).enhance(1.08)

def icon(img, pose, x, y, h):
    ic = Image.open(f"{ICONS}/{pose}.png").convert("RGBA")
    ic = ic.resize((round(ic.width * h / ic.height), h), Image.LANCZOS)
    img = img.convert("RGBA"); sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 255), (x + 4, y + 6), ic.split()[3].point(lambda v: int(v * .3)))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8))); img.alpha_composite(ic, (x, y))
    return img.convert("RGB")

def wrap(text, font, width):
    toks = re.findall(r"[A-Za-z0-9&'.$,ôé]+|.", text)
    lines, cur = [], ""
    for t in toks:
        if font.getlength(cur + t) > width and cur and t not in "，。、！？）：；":
            lines.append(cur); cur = t.lstrip()
        else: cur += t
    if cur: lines.append(cur)
    return lines

def card(fn, name, price, intro, photos):
    img = Image.new("RGB", (W, H), CREAM); cw, ch = W // 3, 470
    for i, p in enumerate(photos): img.paste(crop(p, cw + 1, ch), ((i % 3) * cw, (i // 3) * ch))
    d = ImageDraw.Draw(img)
    fn_ = serif(64) if re.search(r"[一-鿿]", name) else en(64)
    fp = serif(52); fi = zh(38); lines = wrap(intro, fi, 940)
    block = 84 + 78 + len(lines) * 58
    y = 940 + (500 - block) // 2
    d.text((70, y), name, font=fn_, fill=INK)
    d.text((70, y + 84), price, font=fp, fill=GOLD)
    fy = y + 162
    for ln in lines:
        d.text((72, fy), ln, font=fi, fill=(70, 66, 60)); fy += 58
    img.save(f"{OUT}/{fn}", quality=93)

V = [
 ("01.jpg", "BENNELONG", "$2,250到$3,250一位",
  "菜单还没公布。主餐厅是小食加四道菜配酒，楼上Dress Circle是五道菜配更高级的酒，香槟到店和零点各一杯。",
  ["bn_t105455397.jpg", "bn_b13.webp", "bn_t105455388.jpg", "bn_nye.jpg", "bn_t105455402.jpg", "bn_t105455385.jpg"]),
 ("02.jpg", "ALTITUDE", "$1,750到$2,500一位",
  "菜单还没公布。八道菜品鉴套餐，每道配酒，最长可以坐5小时。$2,500保证靠窗座位。",
  [("al_rk1.jpg", .5, .5), "al_wl0.jpg", "al_nye.jpg", ("al_rk2.jpg", .5, .5), "al_wl2.jpg", "al_wl1.jpg"]),
 ("03.jpg", "ARIA", "$1,950一位",
  "芦笋配水牛奶酪和鱼子酱、西澳黑马龙虾、乳鸽配樱桃、M9+和牛配牛尾、芒果香槟、黑松露巧克力，六道菜配六款酒。",
  ["ar_t105913818.jpg", "ar_b6.jpg", "ar_b8.jpg", "ar_b16.jpg", "ar_b1.jpg", "ar_b9.jpg"]),
 ("04.jpg", "WHALEBRIDGE", "$1,200到$1,500一位",
  "鱼子酱挞、生蚝虎虾扇贝拼盘、松露鹅肝肉冻，主菜烤珊瑚鳟和安格斯牛柳，最后是法国奶酪和朗姆酒蛋糕，香槟整晚无限量。",
  ["wb25_mia.jpg", "wb25_v1.jpg", "wb25_menu.jpg", "wb25_v3.jpg", "wb25_bev.jpg", "wb26_s113.jpg"]),
 ("05.jpg", "SAILS", "$1,495一位",
  "蛙蟹挞配鱼子酱、珊瑚鳟刺身、大虾扇贝卷配海胆、干式熟成鸭胸、M9+西冷配羊肚菌、黄桃慕斯，含酒水。",
  ["sa_nye.jpg", "sa_nye3.jpg", "sa_g02.jpg", "sa_to2.jpg", "sa_h.jpg", "sa_nye2.jpg"]),
 ("06.jpg", "几百块的选择", "$295到$395一位",
  "Akti $295：皮塔饼、和牛肉丸、红酒炖牛肉、小羊肩、希腊新年蛋糕。Ripples $335：生蚝、龙虾卷、炸鹌鹑、T骨牛排。Riva $395：蛙蟹配海胆、龙虾意面、罗西尼牛柳。",
  ["ak_to0.jpg", "ak_nye.png", "rc_7.jpg", "rc_3.jpg", "rv_0.jpg", "rv_5.jpg"]),
]
for fn, name, price, intro, ph in V: card(fn, name, price, intro, ph)

# 首页：像真实分享，整张实拍照片，白色普通粗体字，轻阴影，不加色块和拱形
L1, L2 = "悉尼最贵的跨年晚餐", "一位要$3,250"
fc = zh(92, "Bold")
def plain_cover(fn, spec, pose, ty=120, ix=None):
    im = crop(spec, W, H)
    sh = Image.new("L", (W, H), 0); sd = ImageDraw.Draw(sh)
    for i, t in enumerate((L1, L2)): sd.text((72, ty + i * 128), t, font=fc, fill=235, stroke_width=6, stroke_fill=235)
    im.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im)
    for i, t in enumerate((L1, L2)): d.text((72, ty + i * 128), t, font=fc, fill="white")
    icon(im, pose, W - 250, H - 270, 210).save(f"{OUT}/{fn}", quality=93)
plain_cover("cover_A.jpg", ("al_nye.jpg", .5, .55), "01_看菜单")
plain_cover("cover_B.jpg", ("bn_t105455397.jpg", .5, .5), "01_看菜单")
plain_cover("cover_C.jpg", ("ar_t105913818.jpg", .45, .5), "01_看菜单")
print("ok")
