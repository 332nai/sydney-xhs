"""写稿：把入选线索交给模型，生成一期周报的稿件 JSON。"""
import json
from datetime import date, timedelta

from . import config, llm, regions

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def next_publish_date(today: date) -> date:
    target = WEEKDAYS.index(config.settings()["weekly_issue"]["publish_weekday"])
    return today + timedelta(days=(target - today.weekday()) % 7 or 7)


def lead_brief(l: dict) -> str:
    d = l.get("data") or {}
    lines = [f"[lead_id={l['id']}] 类型：{l['kind']}；街区：{l['suburb']}（{regions.region_name(l['region'])}）"]
    for label, key in [("名称", "name"), ("地址", "address"), ("开业日期", "opened_date"), ("营业时间", "hours"),
                       ("价格", "price"), ("团队", "team")]:
        if d.get(key):
            lines.append(f"{label}：{d[key]}")
    lines.append(f"文章发布：{l.get('published')}")
    lines.append(f"概要：{d.get('summary_zh', '')}")
    for f in d.get("key_facts") or []:
        lines.append(f"・{f}")
    return "\n".join(lines)


def write_issue(leads: list, issue_no: int, today: date = None) -> dict:
    today = today or date.today()
    s = config.settings()
    p = config.prompt("write_weekly").format(
        account_name=s["account_name"], style_guide=config.prompt("style_guide"),
        editor_rules=config.prompt("editor_rules"), leads="\n\n".join(lead_brief(l) for l in leads))
    draft = llm.ask_json(p)
    return assemble(draft, leads, issue_no, next_publish_date(today))


def assemble(draft: dict, leads: list, issue_no: int, publish: date) -> dict:
    by_id = {l["id"]: l for l in leads}
    items = []
    for i, it in enumerate(draft["items"], 1):
        lead = by_id.get(it.get("lead_id"))
        it["num"] = i
        if lead:
            it.setdefault("suburb", lead["suburb"])
            it["region"] = lead["region"]
            it["sources"] = [lead["url"]]
        items.append(it)
    return {"issue_no": issue_no, "publish_date": publish.isoformat(), "cover": draft["cover"], "items": items,
            "editor_note": draft["editor_note"], "post": draft["post"]}


def save(issue: dict) -> str:
    path = config.issue_dir(issue["issue_no"]) / "issue.json"
    path.write_text(json.dumps(issue, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def load(issue_no: int) -> dict:
    return json.loads((config.issue_dir(issue_no) / "issue.json").read_text(encoding="utf-8"))
