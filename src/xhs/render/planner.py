"""给每条稿件分配版式。规则：
1. 稿件里手动写了 "layout" 就用它（主编在审核时可以指定）
2. 否则按素材决定候选版式，依次尝试
3. 同一版式每期最多出现 max_same_family_per_week 次，相邻两张不能同版式
4. 没有照片也没有数字的新店，三家一组放进拍立得拼贴
"""
from .. import config

FAMILIES = ["clipping", "before_after", "number_poster", "qa_cards", "photo_poster", "band_poster", "polaroids"]


def candidates(it: dict) -> list:
    has_img = bool(it.get("image", {}).get("path"))
    c = []
    if it.get("kind") == "venue":
        if has_img:
            c.append("photo_poster")
        if it.get("big_number"):
            c.append("number_poster")
        if it.get("explainer"):
            c.append("band_poster")  # 有背景故事的店值得单独一张
        c.append("polaroids")
    else:
        if it.get("before_after"):
            c.append("before_after")
        if it.get("qa"):
            c.append("qa_cards")
        if it.get("big_number"):
            c.append("number_poster")
        if it.get("date_badge"):
            c.append("clipping")
        if has_img:
            c.append("photo_poster")
        c.append("clipping")
    return c


def plan(issue: dict) -> list:
    """返回页面列表：[("cover", None), ("map", None), (版式, [条目]), …, ("editor", None)]"""
    cap = config.settings()["render"]["max_same_family_per_week"]
    used, pages, last, pol = {}, [], None, []
    for it in issue["items"]:
        fam = it.get("layout")
        if not fam:
            for c in candidates(it):
                if c == "polaroids" or (used.get(c, 0) < cap and c != last):
                    fam = c
                    break
            fam = fam or candidates(it)[-1]
        if fam == "polaroids":
            pol.append(it)
            if len(pol) == 3:
                pages.append(("polaroids", pol)); pol = []
            last = "polaroids"
            continue
        used[fam] = used.get(fam, 0) + 1
        pages.append((fam, [it]))
        last = fam
    if pol:
        pages.append(("polaroids", pol))
    return [("cover", None), ("map", None)] + pages + [("editor", None)]
