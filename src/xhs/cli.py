"""命令行入口。用法见 README.md。"""
import argparse, json, sys
from datetime import date
from pathlib import Path

from . import collect, config, images, publish, review, revise, select, store, verify, write
from .render import render_issue


def _today(a):
    return date.fromisoformat(a.today) if getattr(a, "today", None) else date.today()


def _next_issue_no():
    root = config.data_dir() / "issues"
    nums = [int(p.name) for p in root.glob("[0-9][0-9][0-9]")] if root.exists() else []
    return (max(nums) + 1) if nums else 1


def cmd_collect(a):
    stats = collect.run(_today(a), only=a.only)
    print(f"\n完成：新线索 {stats['new']}，范围外 {stats['out_of_area']}，跳过 {stats['skipped']}，出错 {stats['errors']}")


def cmd_plan(a):
    today = _today(a)
    db = store.connect()
    rep = select.report(store.candidates(db), today)
    for w in rep["warnings"]:
        print("注意：" + w)
    if not rep["chosen"]:
        print("没有可用的线索，先运行 collect。"); return
    for l in rep["chosen"]:
        print(f"  入选 {l['kind']:9s} {l['suburb']:14s} {l.get('name')}")
    if a.dry:
        return
    no = a.issue or _next_issue_no()
    issue = write.write_issue(rep["chosen"], no, today)
    images.attach(issue)
    write.save(issue)
    _finish(issue, today, use_llm=True)


def _finish(issue, today, use_llm):
    report = verify.run(issue, today, use_llm=use_llm)
    render_issue(issue)
    r = review.build_local(issue)
    print(f"\n第{issue['issue_no']:02d}期已生成。")
    print(f"  审核页：{r['html']}")
    print(f"  批注文件：{r['comments']}")
    if r["problems"]:
        print("  需要处理：")
        for p in r["problems"]:
            print("   · " + p)


def cmd_render(a):
    issue = write.load(a.issue)
    images.attach(issue) if a.images else None
    write.save(issue)
    _finish(issue, _today(a), use_llm=a.check)


def cmd_review(a):
    issue = write.load(a.issue)
    if a.notion:
        report = json.loads((config.issue_dir(a.issue) / "verify.json").read_text(encoding="utf-8"))
        print(f"已推送 {review.push_notion(issue, report)} 条到 Notion")
    else:
        print(review.build_local(issue))


def cmd_revise(a):
    issue = write.load(a.issue)
    comments = review.pull_notion(a.issue) if a.notion else review.read_local_comments(a.issue)
    res = revise.run(issue, comments)
    if not res["changed"]:
        print("没有批注，不需要修改。"); return
    if res["new_rules"]:
        print("提炼出的新规则（已放进 prompts/editor_rules.md 的“待确认”，确认后移到“已生效”）：")
        for r in res["new_rules"]:
            print("  · " + r)
    _finish(res["issue"], _today(a), use_llm=True)


def cmd_publish(a):
    issue = write.load(a.issue)
    print("发布包：" + publish.pack(issue, a.title))


def cmd_demo(a):
    """不联网、不调用模型，用第一期样刊数据测试出图。"""
    issue = json.loads((config.ROOT / "data" / "fixtures" / "issue_001.json").read_text(encoding="utf-8"))
    out = config.data_dir() / "demo" / "cards"
    files = render_issue(issue, out_dir=str(out))
    print(f"已生成 {len(files)} 张卡片：{out}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="run.py", description="悉尼资讯小红书自动化")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("collect", help="抓取信息源，更新线索库"); p.add_argument("--only", nargs="*"); p.add_argument("--today"); p.set_defaults(f=cmd_collect)
    p = sub.add_parser("plan", help="选题、写稿、配图、核实、出图"); p.add_argument("--issue", type=int); p.add_argument("--dry", action="store_true", help="只看入选结果"); p.add_argument("--today"); p.set_defaults(f=cmd_plan)
    p = sub.add_parser("render", help="手动改过 issue.json 后重新出图"); p.add_argument("--issue", type=int, required=True); p.add_argument("--images", action="store_true", help="重新找图"); p.add_argument("--check", action="store_true", help="同时跑事实核查"); p.add_argument("--today"); p.set_defaults(f=cmd_render)
    p = sub.add_parser("review", help="生成审核页，或推送到 Notion"); p.add_argument("--issue", type=int, required=True); p.add_argument("--notion", action="store_true"); p.set_defaults(f=cmd_review)
    p = sub.add_parser("revise", help="按批注改稿"); p.add_argument("--issue", type=int, required=True); p.add_argument("--notion", action="store_true"); p.add_argument("--today"); p.set_defaults(f=cmd_revise)
    p = sub.add_parser("publish", help="生成手机发布包，并把用过的线索标记为已用"); p.add_argument("--issue", type=int, required=True); p.add_argument("--title", type=int, default=0, help="用第几个标题，从0开始"); p.set_defaults(f=cmd_publish)
    p = sub.add_parser("demo", help="离线出图测试"); p.set_defaults(f=cmd_demo)
    a = ap.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    main()
