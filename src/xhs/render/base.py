"""排版共用工具：字体、换行、纸张质感、照片裁切。"""
import math, random

from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1000, 1333  # 3:4 设计画布，保存时放大到 config 里的 output_size
M = 70  # 左右页边距

from .. import config as _config

_fonts = _config.settings()["render"].get("fonts", {})
NOTO = _fonts.get("noto_dir", "/usr/share/fonts/opentype/noto/")
INTER = _fonts.get("inter_dir", "/usr/share/fonts/opentype/inter/")
LORA = _fonts.get("lora_file", "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf")
SANS = {"light": "NotoSansCJK-Light.ttc", "regular": "NotoSansCJK-Regular.ttc", "medium": "NotoSansCJK-Medium.ttc",
        "bold": "NotoSansCJK-Bold.ttc", "black": "NotoSansCJK-Black.ttc"}
SERIF = {"light": "NotoSerifCJK-Light.ttc", "regular": "NotoSerifCJK-Regular.ttc", "medium": "NotoSerifCJK-Medium.ttc",
         "semibold": "NotoSerifCJK-SemiBold.ttc", "bold": "NotoSerifCJK-Bold.ttc", "black": "NotoSerifCJK-Black.ttc"}
_cache = {}


def F(kind, weight, size):
    key = (kind, weight, int(size))
    if key not in _cache:
        size = int(size)
        if kind == "sans":
            _cache[key] = ImageFont.truetype(NOTO + SANS[weight], size, index=2)
        elif kind == "serif":
            _cache[key] = ImageFont.truetype(NOTO + SERIF[weight], size, index=2)
        elif kind == "inter":
            _cache[key] = ImageFont.truetype(INTER + f"InterDisplay-{weight}.otf", size)
        elif kind == "lora":
            f = ImageFont.truetype(LORA, size)
            try:
                f.set_variation_by_name(weight)
            except Exception:
                pass
            _cache[key] = f
    return _cache[key]


# 颜色
CREAM = (244, 239, 230)
INK = (24, 24, 26)
CORAL = (226, 85, 63)
NAVY = (27, 42, 65)
MUSTARD = (217, 164, 65)
TEAL = (15, 59, 58)
SAND = (231, 215, 193)
NEWS = (237, 232, 221)
NEWSRED = (196, 30, 46)
GREY = (110, 106, 100)
WHITE = (255, 255, 255)

NO_START = set("，。、：；！？）」』”’》%")


def tokens(text):
    out, buf = [], ""
    for ch in text:
        if ch.isascii() and (ch.isalnum() or ch in "$.%'&+/:#"):
            buf += ch
        else:
            if buf:
                out.append(buf); buf = ""
            out.append(ch)
    if buf:
        out.append(buf)
    return out


def wrap(text, font, maxw):
    lines = []
    for para in str(text).split("\n"):
        line = ""
        for t in tokens(para):
            trial = line + t
            if font.getlength(trial) <= maxw or not line.strip() or t in NO_START:
                line = trial
            else:
                lines.append(line.rstrip())
                line = "" if t == " " else t
        lines.append(line.rstrip())
    return lines


def para(d, xy, text, font, fill, maxw, lh=1.55, max_lines=None):
    x, y = xy
    step = int(font.size * lh)
    lines = wrap(text, font, maxw)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:-1] + "…"
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += step
    return y


def para_height(text, font, maxw, lh=1.55):
    return len(wrap(text, font, maxw)) * int(font.size * lh)


def tw(font, s):
    return font.getlength(s)


def fit(kind, weight, text, maxw, start, minimum):
    """从 start 字号往下缩，直到一行放得下。"""
    size = start
    while size > minimum and F(kind, weight, size).getlength(text) > maxw:
        size -= 4
    return F(kind, weight, size)


def paper(bg, grain=10):
    img = Image.new("RGB", (W, H), bg)
    noise = Image.effect_noise((W, H), grain).convert("L")
    return Image.blend(img, Image.merge("RGB", [noise] * 3), 0.045)


def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


def cover_crop(path, size):
    im = Image.open(path).convert("RGB")
    return ImageOps.fit(im, size, method=Image.LANCZOS, centering=(0.5, 0.45))


def jitter_line(d, pts, fill, width, amp=2.0, seg=18, seed=3):
    rnd = random.Random(seed)
    out = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        n = max(2, int(math.hypot(x2 - x1, y2 - y1) / seg))
        for i in range(n):
            t = i / n
            out.append((x1 + (x2 - x1) * t + rnd.uniform(-amp, amp), y1 + (y2 - y1) * t + rnd.uniform(-amp, amp)))
    out.append(pts[-1])
    d.line(out, fill=fill, width=width, joint="curve")


def kicker_text(item):
    if item.get("label"):
        return item["label"]  # 单篇模式里直接写好的标签
    kind = "新店" if item.get("kind") == "venue" else ("活动" if item.get("kind") == "event" else "社区动态")
    tag = item.get("kicker") or item.get("suburb") or ""
    if item.get("kind") == "venue":
        tag = item.get("suburb") or tag
    return f"{kind} {item['num']:02d}｜{tag}"


def draw_mixed(d, xy, text, size, fill, latin=("inter", "Black"), cjk=("sans", "black")):
    """大数字里混有中文或符号（如 ㎡、元）时，非 ASCII 字符改用中文字体。返回总宽度。"""
    x, y = xy
    runs, cur, cur_ascii = [], "", None
    for ch in text:
        a = ch.isascii()
        if cur and a != cur_ascii:
            runs.append((cur, cur_ascii)); cur = ""
        cur += ch; cur_ascii = a
    if cur:
        runs.append((cur, cur_ascii))
    for run, a in runs:
        f = F(*latin, size) if a else F(*cjk, int(size * 0.55))
        dy = 0 if a else int(size * 0.38)
        d.text((x, y + dy), run, font=f, fill=fill)
        x += f.getlength(run)
    return x - xy[0]


def mixed_width(text, size, latin=("inter", "Black"), cjk=("sans", "black")):
    w = 0
    for ch in text:
        w += F(*latin, size).getlength(ch) if ch.isascii() else F(*cjk, int(size * 0.55)).getlength(ch)
    return w
