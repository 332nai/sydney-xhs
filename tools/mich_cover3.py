"""米其林厨师在悉尼的店：用户提供的米其林牌匾照片做封面（去掉牌匾上的年份），下方白字标题。
用法：python3 mich_cover3.py out.jpg"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W, H = 1080, 1440
NOTO = "/usr/share/fonts/opentype/noto/"
def S(w, s): return ImageFont.truetype(NOTO + f"NotoSerifCJK-{w}.ttc", s, index=2)
im = Image.open("data/post_img/mi_plaque.jpg").convert("RGB")
import numpy as np, cv2
a = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
mask = np.zeros(a.shape[:2], np.uint8); mask[600:720, 1660:1950] = 255   # 牌匾上的年份
a = cv2.inpaint(a, mask, 9, cv2.INPAINT_TELEA)
im = Image.fromarray(cv2.cvtColor(a, cv2.COLOR_BGR2RGB))
s = H / im.height; im = im.resize((round(im.width * s), H), Image.LANCZOS)
x0 = round(1807 * s - W / 2)
img = im.crop((x0, 0, x0 + W, H)).filter(ImageFilter.UnsharpMask(2, 60, 2))
img = ImageEnhance.Contrast(img).enhance(1.05)
ov = Image.new("L", (1, H))
for yy in range(H):
    t = (yy - H * .52) / (H * .48)
    ov.putpixel((0, yy), int(max(0, min(1, t)) ** 1.1 * 215))
img = Image.composite(Image.new("RGB", (W, H), (12, 10, 8)), img, ov.resize((W, H)))
d = ImageDraw.Draw(img)
K = ImageFont.truetype(NOTO + "NotoSansCJK-Medium.ttc", 92, index=2)
d.text((W / 2 + 4, 600), "2027", font=K, fill=(250, 246, 244), anchor="mm")   # 牌匾上的年份
d.text((80, H - 430), "米其林厨师", font=S("Black", 140), fill="white")
d.text((80, H - 250), "在悉尼开的店", font=S("Black", 140), fill="white")
img.save(sys.argv[1], quality=93)
