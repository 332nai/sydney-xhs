"""发布包：把卡片图和可直接复制的文字放进一个文件夹，主编在手机上照着发。"""
import shutil

from . import config, store


def pack(issue: dict, title_index: int = 0) -> str:
    folder = config.issue_dir(issue["issue_no"])
    out = folder / "publish"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    for i, png in enumerate(sorted((folder / "cards").glob("*.png")), 1):
        shutil.copy(png, out / f"{i:02d}.png")
    post = issue["post"]
    (out / "post.txt").write_text(f"{post['titles'][title_index]}\n\n{post['body']}\n\n{' '.join(post['tags'])}\n", encoding="utf-8")
    db = store.connect()
    store.mark_used(db, [it["lead_id"] for it in issue["items"] if it.get("lead_id")], issue["issue_no"])
    return str(out)
