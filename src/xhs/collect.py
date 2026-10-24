"""采集：按 config/sources.yaml 抓文章，用模型抽成结构化线索，存进线索库。"""
from datetime import date, timedelta

import feedparser

from . import config, fetch, llm, regions, store


def _links(src: dict) -> list:
    if src["type"] == "rss":
        feed = feedparser.parse(fetch.get(src["url"]))
        return [e.link for e in feed.entries]
    if src["type"] == "listing":
        return fetch.listing_links(fetch.get(src["url"]), src["url"], src["link_pattern"])
    raise ValueError(f"未知来源类型：{src['type']}")


def _too_old(published: str, today: date) -> bool:
    if not published:
        return False
    w = config.settings()["windows"]
    oldest = today - timedelta(days=max(w["venue_days"], w["community_days"]) + 7)
    try:
        return date.fromisoformat(published[:10]) < oldest
    except ValueError:
        return False


def extract(article: dict) -> dict:
    p = config.prompt("extract").format(published=article["published"] or "未知", url=article["url"], text=article["text"])
    return llm.ask_json(p, model_key="extract_model")


def run(today: date = None, only: list = None, log=print) -> dict:
    today = today or date.today()
    db = store.connect()
    cap = config.settings()["http"]["max_articles_per_source"]
    stats = {"new": 0, "skipped": 0, "out_of_area": 0, "errors": 0}
    for src in config.load("sources")["sources"]:
        if not src.get("enabled") or (only and src["id"] not in only):
            continue
        try:
            links = _links(src)[:cap]
        except Exception as e:
            log(f"[{src['id']}] 列表读取失败：{e}"); stats["errors"] += 1
            continue
        log(f"[{src['id']}] 找到 {len(links)} 篇")
        for url in links:
            if store.seen(db, url):
                stats["skipped"] += 1; continue
            try:
                art = fetch.parse_article(fetch.get(url), url)
                if _too_old(art["published"], today) or len(art["text"]) < 300:
                    store.save(db, {"url": url, "source_id": src["id"], "published": art["published"], "status": "rejected"})
                    stats["skipped"] += 1; continue
                facts = extract(art)
                suburb, region = regions.classify(facts.get("suburbs"), art["text"][:3000])
                status = "new" if region and facts.get("kind") in ("venue", "community", "event") else "out_of_area"
                store.save(db, {
                    "url": url, "source_id": src["id"], "published": art["published"], "kind": facts.get("kind"),
                    "is_roundup": int(bool(facts.get("is_roundup"))), "name": facts.get("name") or facts.get("title_en"),
                    "suburb": suburb, "region": region, "opened_date": facts.get("opened_date"),
                    "event_dates": facts.get("event_dates") or [], "image_url": art["image_url"],
                    "image_credit": facts.get("image_credit") or art["image_credit"], "venue_website": facts.get("venue_website"),
                    "data": facts, "article_text": art["text"], "status": status,
                })
                stats["new" if status == "new" else "out_of_area"] += 1
                log(f"  + {status:11s} {facts.get('kind')}: {facts.get('name') or art['title']} ({suburb})")
            except Exception as e:
                log(f"  ! {url}：{e}"); stats["errors"] += 1
    return stats
