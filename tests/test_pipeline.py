"""离线测试：用假的网页和假的模型回复，把整条流水线跑一遍。运行：python -m pytest tests"""
import json, shutil, sys
from datetime import date, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from xhs import collect, config, fetch, llm, publish, regions, review, revise, select, store, verify, write  # noqa: E402
from xhs.render import render_issue  # noqa: E402

TODAY = date(2026, 10, 24)


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "data_dir", lambda: tmp_path)
    prompts = tmp_path / "prompts"
    shutil.copytree(config.PROMPTS, prompts)
    real_prompt = config.prompt
    monkeypatch.setattr(config, "PROMPTS", prompts)
    monkeypatch.setattr(config, "prompt", lambda n: (prompts / f"{n}.md").read_text(encoding="utf-8"))
    return tmp_path


# ------------------------------------------------------------------ 片区与时效
def test_regions():
    assert regions.classify([], "A new cafe opened in North Sydney near Sydney Harbour")[1] == "lower_north"
    assert regions.classify(["Surry Hills"])[1] == "east"
    assert regions.classify(["Rhodes"])[1] == "inner_west"
    assert regions.classify(["Parramatta"], "Parramatta Road in Parramatta") == (None, None)
    assert regions.classify([], "Lunch in Darlo this week")[0] == "Darlinghurst"


def test_windows():
    v = lambda days: {"kind": "venue", "opened_date": (TODAY - timedelta(days=days)).isoformat()}
    c = lambda days: {"kind": "community", "published": (TODAY - timedelta(days=days)).isoformat()}
    assert select.eligible(v(50), TODAY) and not select.eligible(v(70), TODAY)
    assert select.eligible(c(10), TODAY) and not select.eligible(c(20), TODAY)


def test_rule_checks_catch_problems(sandbox):
    issue = json.loads((config.ROOT / "data/fixtures/issue_001.json").read_text(encoding="utf-8"))
    issue["cover"]["headline_lines"] = ["内城这一周", "变了9件事"]
    issue["items"][0]["lede"] = "姐妹们，Metro 要通车了"
    issue["items"][1]["points"][0] = "T8 — 不停了"
    probs = [p["problem"] for p in verify.rule_checks(issue, TODAY)]
    assert any("内城" in p for p in probs)
    assert any("姐妹们" in p for p in probs)
    assert any("破折号" in p for p in probs)


# ------------------------------------------------------------------ 整条流水线
ARTICLES = {
    "https://x.test/metro": ("community", "Sydenham", "2026-10-22", None),
    "https://x.test/enmore": ("community", "Enmore", "2026-10-21", None),
    "https://x.test/ame": ("venue", "Darlinghurst", "2026-10-20", "2026-10-22"),
    "https://x.test/kiddo": ("venue", "Surry Hills", "2026-09-10", "2026-09-10"),
    "https://x.test/old": ("venue", "Newtown", "2026-06-01", "2026-06-01"),
    "https://x.test/parra": ("venue", "Parramatta", "2026-10-20", "2026-10-20"),
}


def fake_html(url):
    kind, suburb, pub, opened = ARTICLES[url]
    body = " ".join([f"This is a story about {suburb}, Sydney."] * 30)
    return (f"<html><head><meta property='og:title' content='{url}'><meta property='article:published_time' content='{pub}T08:00:00'>"
            f"</head><body><article><p>{body}</p><p>Photo: Courtesy of the venue</p></article></body></html>")


def fake_llm(prompt, model_key="write_model"):
    if "提取一条结构化线索" in prompt:
        url = prompt.split("文章链接：")[1].split("\n")[0].strip()
        kind, suburb, pub, opened = ARTICLES[url]
        return {"kind": kind, "is_roundup": False, "name": url.rsplit("/", 1)[1].title(), "suburbs": [suburb],
                "address": "1 Test Street", "opened_date": opened, "event_dates": [], "hours": None, "price": "$20",
                "team": None, "venue_website": None, "image_credit": "Photo: Courtesy of the venue",
                "summary_zh": "测试概要。", "key_facts": ["事实一", "事实二"]}
    if "每周新鲜事周报" in prompt:
        ids = [l.split("=")[1].split("]")[0] for l in prompt.split("[lead_id")[1:]]
        items = []
        for lid in ids:
            items.append({"lead_id": lid, "kind": "community" if "社区" in prompt else "venue", "toc": "测试目录",
                          "kicker": "测试", "headline": ["测试标题"], "lede": "测试导语。", "points": ["要点一", "要点二"],
                          "facts": {"name": "测试店", "address": "1 Test Street"}})
        return {"cover": {"headline_lines": ["这周悉尼", f"变了{len(items)}件事"], "highlight": str(len(items)), "sticker": []},
                "items": items, "editor_note": {"headline": "编辑判断", "paragraphs": ["第一段。"], "question": "你怎么看？"},
                "post": {"titles": ["标题一", "标题二", "标题三"], "body": "正文。", "tags": ["#悉尼生活"]}}
    if "事实核查编辑" in prompt:
        return {"ok": True, "issues": []}
    if "主编对本期稿件提了批注" in prompt:
        issue = json.loads(prompt.split("原稿：\n")[1].split("\n\n主编批注")[0])
        issue["items"][0]["headline"] = ["改过的标题"]
        return {"issue": issue, "new_rules": ["标题不要用问句"]}
    raise AssertionError("未知提示词")


def test_full_pipeline(sandbox, monkeypatch):
    monkeypatch.setattr(collect, "_links", lambda src: list(ARTICLES) if src["id"] == "cityhub" else [])
    monkeypatch.setattr(fetch, "get", lambda url, binary=False: fake_html(url))
    monkeypatch.setattr(llm, "ask_json", fake_llm)

    stats = collect.run(TODAY, log=lambda *a: None)
    assert stats["new"] == 4 and stats["out_of_area"] == 1  # Parramatta 在范围外，6月那篇太旧

    db = store.connect()
    chosen = select.choose(store.candidates(db), TODAY)
    assert {l["suburb"] for l in chosen} == {"Sydenham", "Enmore", "Darlinghurst", "Surry Hills"}
    assert [l["kind"] for l in chosen][:2] == ["community", "community"]  # 社区动态排在前面

    issue = write.write_issue(chosen, 1, TODAY)
    assert issue["publish_date"] == "2026-10-29"  # 下一个周四
    write.save(issue)
    report = verify.run(issue, TODAY)
    assert verify.blocking(report) == []

    files = render_issue(issue)
    assert len(files) >= 6
    r = review.build_local(issue)
    assert Path(r["html"]).exists() and Path(r["comments"]).exists()

    comments = review.read_local_comments(1)
    comments[1]["批注"] = "标题改一下"
    res = revise.run(issue, comments)
    assert res["issue"]["items"][0]["headline"] == ["改过的标题"]
    assert "标题不要用问句" in (config.PROMPTS / "editor_rules.md").read_text(encoding="utf-8")
    assert (config.issue_dir(1) / "issue.v1.json").exists()  # 旧版本保留

    out = publish.pack(res["issue"])
    assert (Path(out) / "post.txt").read_text(encoding="utf-8").startswith("标题一")
    assert store.candidates(db) == []  # 用过的线索不会再入选
