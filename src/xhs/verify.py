"""核实：先做规则检查（时效、禁用词、字数），再让模型逐条对照原文。"""
import json, re
from datetime import date

from . import config, llm, select, store

BANNED = ["姐妹们", "宝子", "家人们", "绝绝子", "yyds", "冲鸭", "以店方为准", "来源：", "照片位"]
DASHES = ["—", "–", "──"]


def card_text(it: dict) -> str:
    parts = [" ".join(it.get("headline", [])), it.get("lede", "")] + it.get("points", [])
    for k in ("explainer", "impact"):
        if it.get(k):
            parts.append(it[k])
    for k in ("date_badge", "big_number"):
        if it.get(k):
            parts.append(f"{it[k]['value']} {it[k]['label']}")
    for qa in it.get("qa", []):
        parts += [qa["q"], qa["a"]]
    for ba in it.get("before_after", []):
        parts.append(" ".join(str(v) for v in ba.values() if v))
    parts += [f"{k}：{v}" for k, v in (it.get("facts") or {}).items() if v]
    return "\n".join(p for p in parts if p)


def rule_checks(issue: dict, today: date) -> list:
    problems = []
    big = issue["cover"]["headline_lines"]
    for line in big:
        if "内城" in line:
            problems.append({"where": "封面", "problem": "封面大字出现“内城”"})
    db = store.connect()
    for it in issue["items"]:
        where = f"第{it['num']:02d}条"
        text = card_text(it)
        for w in BANNED:
            if w in text:
                problems.append({"where": where, "problem": f"出现禁用词“{w}”"})
        for d in DASHES:
            if d in text:
                problems.append({"where": where, "problem": "出现破折号或连接号"})
        if any("内城" in h for h in it.get("headline", [])):
            problems.append({"where": where, "problem": "大标题出现“内城”"})
        for h in it.get("headline", []):
            if len(h) > 12:
                problems.append({"where": where, "problem": f"标题“{h}”太长，卡片上会挤"})
        lead = store.get(db, it.get("lead_id", "")) if it.get("lead_id") else None
        if lead and not select.eligible(lead, today):
            problems.append({"where": where, "problem": "已超出时效窗口"})
    body = issue["post"]["body"]
    if len(body) > 1000:
        problems.append({"where": "正文", "problem": f"正文 {len(body)} 字，超过小红书上限"})
    for w in BANNED + DASHES:
        if w in body:
            problems.append({"where": "正文", "problem": f"正文出现“{w}”"})
    return problems


def fact_checks(issue: dict, today: date, log=print) -> list:
    db = store.connect()
    out = []
    for it in issue["items"]:
        lead = store.get(db, it.get("lead_id", "")) if it.get("lead_id") else None
        if not lead or not lead.get("article_text"):
            out.append({"num": it["num"], "ok": False, "issues": [{"claim": "全部", "verdict": "unsupported", "why": "找不到原文，无法核实", "fix": ""}]})
            continue
        p = config.prompt("verify").format(today=today.isoformat(), card=card_text(it), sources=lead["article_text"][:12000])
        res = llm.ask_json(p)
        res["num"] = it["num"]
        out.append(res)
        log(f"  核实 {it['num']:02d}：{'通过' if res.get('ok') and not res.get('issues') else '有问题'}")
    return out


def run(issue: dict, today: date = None, use_llm: bool = True, log=print) -> dict:
    today = today or date.today()
    report = {"rules": rule_checks(issue, today), "facts": fact_checks(issue, today, log) if use_llm else []}
    path = config.issue_dir(issue["issue_no"]) / "verify.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def blocking(report: dict) -> list:
    """返回会阻止“通过”的问题：规则问题全部算，核实里 overstated/unsupported/outdated 算。"""
    out = [f"{p['where']}：{p['problem']}" for p in report["rules"]]
    for f in report["facts"]:
        for i in f.get("issues", []):
            out.append(f"第{f['num']:02d}条：{i['verdict']}，{i['claim']}（{i['why']}）")
    return out
