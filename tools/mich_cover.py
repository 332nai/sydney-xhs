"""米其林厨师在悉尼的店：编辑风封面（上图下字，宋体标题）。用法：python3 mich_cover.py out.png"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def S(w, s): return ImageFont.truetype(NOTO + f"NotoSerifCJK-{w}.ttc", s, index=2)
def K(w, s): return ImageFont.truetype(NOTO + f"NotoSansCJK-{w}.ttc", s, index=2)
PAPER, INK, GREY, ACC = (250, 248, 244), (22, 22, 22), (120, 116, 110), (150, 40, 30)
M, PH = 80, 880
img = Image.new("RGB", (W, H), PAPER)
im = Image.open("data/post_img/mi_fire_10.jpg").convert("RGB")
s = max(W / im.width, PH / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
x = (im.width - W) // 2; y = (im.height - PH) // 2
img.paste(ImageEnhance.Color(im.crop((x, y, x + W, y + PH))).enhance(1.05), (0, 0))
d = ImageDraw.Draw(img)
d.text((M, PH + 52), "悉尼", font=K("Medium", 32), fill=ACC)
d.text((M, PH + 96), "米其林厨师", font=S("Black", 132), fill=INK)
d.text((M, PH + 276), "在悉尼开的店", font=S("SemiBold", 72), fill=INK)
d.text((M, PH + 392), "5家已经开业，3家2027年开", font=K("Regular", 34), fill=GREY)
img.save(sys.argv[1])
