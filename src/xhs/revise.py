"""按主编批注改稿，并把通用的意见沉淀为编辑规则（先放进“待确认”）。"""
import json
import shutil

from . import config, llm, write


def comments_text(comments: dict) -> str:
    lines = []
    for num, c in sorted(comments.items()):
        if c.get("状态") == "撤下":
            lines.append(f"[{num:02d}] 撤下这一条，并重新编号，封面目录同步删除")
        elif c.get("批注"):
            lines.append(f"[{num:02d}] {c['批注']}")
    return "\n".join(lines)


def run(issue: dict, comments: dict) -> dict:
    text = comments_text(comments)
    if not text:
        return {"issue": issue, "new_rules": [], "changed": False}
    folder = config.issue_dir(issue["issue_no"])
    n = len(list(folder.glob("issue.v*.json"))) + 1
    shutil.copy(folder / "issue.json", folder / f"issue.v{n}.json")  # 保留旧版本，随时可以回退
    p = config.prompt("revise").format(style_guide=config.prompt("style_guide"), editor_rules=config.prompt("editor_rules"),
                                       issue=json.dumps(issue, ensure_ascii=False, indent=1), comments=text)
    res = llm.ask_json(p)
    new_issue = res["issue"]
    for i, it in enumerate(new_issue["items"], 1):
        it["num"] = i
    write.save(new_issue)
    add_pending_rules(res.get("new_rules") or [])
    return {"issue": new_issue, "new_rules": res.get("new_rules") or [], "changed": True}


def add_pending_rules(rules: list):
    if not rules:
        return
    path = config.PROMPTS / "editor_rules.md"
    text = path.read_text(encoding="utf-8").rstrip() + "\n"
    existing = set(l.strip("- ").strip() for l in text.splitlines())
    for r in rules:
        if r.strip() not in existing:
            text += f"- {r.strip()}\n"
    path.write_text(text, encoding="utf-8")
