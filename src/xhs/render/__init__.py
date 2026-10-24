"""出图入口：读稿件 JSON，按版式规划生成全部卡片和总览图。"""
import math, os

from PIL import Image

from .. import config
from . import layouts, planner


def render_issue(issue: dict, out_dir=None) -> list:
    out = out_dir or (config.issue_dir(issue["issue_no"]) / "cards")
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith(".png"):
            os.remove(os.path.join(out, f))
    files, variants = [], {}
    for i, (fam, items) in enumerate(planner.plan(issue), 1):
        v = variants.get(fam, 0); variants[fam] = v + 1
        ctx = {"variant": v, "issue": issue}
        if fam == "cover":
            img = layouts.cover(issue, ctx)
        elif fam == "map":
            img = layouts.map_card(issue, ctx)
        elif fam == "editor":
            img = layouts.editor(issue, ctx)
        elif fam == "polaroids":
            img = layouts.polaroids(items, ctx)
        else:
            img = getattr(layouts, fam)(items[0], ctx)
        name = f"{i:02d}_{fam}.png"
        img.save(os.path.join(out, name))
        files.append(os.path.join(out, name))
    overview(files, os.path.join(os.path.dirname(out), "overview.png"))
    return files


def overview(files, dest, cols=5):
    tw_, th, gap = 300, 450, 20
    rows = math.ceil(len(files) / cols)
    sheet = Image.new("RGB", (cols * tw_ + (cols + 1) * gap, rows * th + (rows + 1) * gap), (40, 40, 42))
    for i, f in enumerate(files):
        im = Image.open(f).resize((tw_, th), Image.LANCZOS)
        sheet.paste(im, (gap + (i % cols) * (tw_ + gap), gap + (i // cols) * (th + gap)))
    sheet.save(dest)
