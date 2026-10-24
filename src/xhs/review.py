"""审核台。两种方式，二选一：
1. 本地：生成 review.html（看图和核实结果）+ comments.yaml（写批注）
2. Notion：把每条稿件推到 Notion 数据库，在 Notion 里改状态和写批注，再拉回来
"""
import html, json, os
from pathlib import Path

import yaml

from . import config, verify

STATUSES = ["待审", "通过", "需修改", "撤下"]


# ------------------------------------------------------------------ 本地审核
def build_local(issue: dict) -> dict:
    folder = config.issue_dir(issue["issue_no"])
    report_path = folder / "verify.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {"rules": [], "facts": []}
    problems = verify.blocking(report)
    cards = sorted((folder / "cards").glob("*.png"))
    parts = [f"<h1>第{issue['issue_no']:02d}期 审核</h1><p>计划发布：{issue['publish_date']}</p>"]
    if problems:
        parts.append("<h2>需要处理的问题</h2><ul>" + "".join(f"<li>{html.escape(p)}</li>" for p in problems) + "</ul>")
    else:
        parts.append("<p>规则检查和事实核查都通过了。</p>")
    parts.append("<h2>卡片</h2><div class='grid'>" + "".join(f"<figure><img src='cards/{c.name}'><figcaption>{c.name}</figcaption></figure>" for c in cards) + "</div>")
    post = issue["post"]
    parts.append("<h2>标题备选</h2><ol>" + "".join(f"<li>{html.escape(t)}</li>" for t in post["titles"]) + "</ol>")
    parts.append(f"<h2>正文</h2><pre>{html.escape(post['body'])}</pre><p>{html.escape(' '.join(post['tags']))}</p>")
    css = ("body{font-family:-apple-system,'PingFang SC',sans-serif;max-width:1100px;margin:24px auto;padding:0 16px;color:#222}"
           ".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px}img{width:100%;border-radius:6px}"
           "pre{white-space:pre-wrap;background:#f5f2ec;padding:16px;border-radius:8px}li{margin:6px 0}")
    (folder / "review.html").write_text(f"<!doctype html><meta charset='utf-8'><title>第{issue['issue_no']}期审核</title><style>{css}</style>{''.join(parts)}", encoding="utf-8")

    cpath = folder / "comments.yaml"
    if not cpath.exists():
        tmpl = {"说明": "每条写状态（通过/需修改/撤下）和批注。批注写清楚要怎么改。封面和正文的意见写在 0 号。",
                "条目": {0: {"名称": "封面、标题与正文", "状态": "待审", "批注": ""}}}
        for it in issue["items"]:
            tmpl["条目"][it["num"]] = {"名称": it.get("toc", ""), "状态": "待审", "批注": ""}
        cpath.write_text(yaml.safe_dump(tmpl, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return {"html": str(folder / "review.html"), "comments": str(cpath), "problems": problems}


def read_local_comments(issue_no: int) -> dict:
    data = yaml.safe_load((config.issue_dir(issue_no) / "comments.yaml").read_text(encoding="utf-8"))
    return {int(k): v for k, v in (data.get("条目") or {}).items()}


# ------------------------------------------------------------------ Notion 审核
def _notion():
    token, db = os.environ.get("NOTION_TOKEN"), os.environ.get("NOTION_REVIEW_DB")
    if not token or not db:
        raise RuntimeError("需要设置 NOTION_TOKEN 和 NOTION_REVIEW_DB（审核数据库的 ID）。")
    from notion_client import Client
    return Client(auth=token), db


def _rt(text):
    text = str(text or "")
    return {"rich_text": [{"text": {"content": text[i:i + 1900]}} for i in range(0, min(len(text), 9500), 1900)]}


def push_notion(issue: dict, report: dict) -> int:
    """数据库需要这些属性：名称(标题)、期数(数字)、编号(数字)、状态(单选)、批注(文本)、卡片文字(文本)、核实问题(文本)。"""
    client, db = _notion()
    problems = verify.blocking(report)
    rows = [(0, "封面、标题与正文", "\n".join(issue["post"]["titles"]) + "\n\n" + issue["post"]["body"])]
    rows += [(it["num"], it.get("toc", ""), verify.card_text(it)) for it in issue["items"]]
    for num, name, text in rows:
        mine = [p for p in problems if p.startswith(f"第{num:02d}条")] if num else [p for p in problems if p.startswith(("封面", "正文"))]
        client.pages.create(parent={"database_id": db}, properties={
            "名称": {"title": [{"text": {"content": f"{issue['issue_no']:02d}期｜{num:02d}｜{name}"}}]},
            "期数": {"number": issue["issue_no"]}, "编号": {"number": num},
            "状态": {"select": {"name": "需修改" if mine else "待审"}},
            "卡片文字": _rt(text), "核实问题": _rt("\n".join(mine)), "批注": _rt(""),
        })
    return len(rows)


def pull_notion(issue_no: int) -> dict:
    client, db = _notion()
    res = client.databases.query(database_id=db, filter={"property": "期数", "number": {"equals": issue_no}})
    out = {}
    for page in res["results"]:
        p = page["properties"]
        num = int(p["编号"]["number"])
        out[num] = {"状态": (p["状态"]["select"] or {}).get("name", "待审"),
                    "批注": "".join(t["plain_text"] for t in p["批注"]["rich_text"])}
    return out
