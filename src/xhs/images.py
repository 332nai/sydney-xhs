"""配图：为每条稿件找一张照片，下载到本期目录。找不到就用不需要照片的版式。"""
import io

from PIL import Image

from . import config, fetch, store


def _credit_ok(credit: str) -> int:
    """返回优先级：2 = 店方提供，1 = 普通，0 = 不想用。"""
    s = config.settings()["images"]
    c = credit or ""
    if any(w in c for w in s["avoid_credit_words"]):
        return 0
    if any(w in c for w in s["preferred_credit_words"]):
        return 2
    return 1


def candidates(lead: dict) -> list:
    out = []
    rank = _credit_ok(lead.get("image_credit"))
    if lead.get("image_url") and rank == 2:
        out.append(lead["image_url"])
    if lead.get("kind") == "venue" and lead.get("venue_website"):
        img = fetch.og_image(lead["venue_website"])
        if img:
            out.append(img)
    if lead.get("image_url") and rank == 1:
        out.append(lead["image_url"])
    return out


def download(url: str, dest) -> bool:
    try:
        im = Image.open(io.BytesIO(fetch.get(url, binary=True))).convert("RGB")
    except Exception:
        return False
    if im.width < config.settings()["images"]["min_width"]:
        return False
    im.save(dest, quality=92)
    return True


def attach(issue: dict, log=print) -> dict:
    db = store.connect()
    folder = config.issue_dir(issue["issue_no"]) / "img"
    folder.mkdir(exist_ok=True)
    for it in issue["items"]:
        if it.get("image", {}).get("path"):
            continue  # 主编手动换过的图不覆盖
        lead = store.get(db, it.get("lead_id", "")) if it.get("lead_id") else None
        if not lead:
            continue
        for url in candidates(lead):
            dest = folder / f"{it['num']:02d}.jpg"
            if download(url, dest):
                it["image"] = {"path": str(dest), "url": url}
                log(f"  图片 {it['num']:02d}：{url}")
                break
        else:
            log(f"  图片 {it['num']:02d}：没有合适的照片，使用设计版式")
    return issue
