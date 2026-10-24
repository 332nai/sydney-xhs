"""选题：从线索库里挑出本期周报的条目。规则参数在 config/settings.yaml。"""
from datetime import date, timedelta

from . import config


def _d(s):
    try:
        return date.fromisoformat(str(s)[:10])
    except (TypeError, ValueError):
        return None


def eligible(lead: dict, today: date) -> bool:
    w = config.settings()["windows"]
    if lead["kind"] == "venue":
        ref = _d(lead.get("opened_date")) or _d(lead.get("published"))
        return bool(ref) and today - timedelta(days=w["venue_days"]) <= ref <= today
    if lead["kind"] == "community":
        ref = _d(lead.get("published"))
        return bool(ref) and today - timedelta(days=w["community_days"]) <= ref <= today
    return False  # 活动类留给“本周值得去”栏目


def score(lead: dict, today: date) -> float:
    ref = _d(lead.get("opened_date")) or _d(lead.get("published")) or today
    s = 1.0 - min((today - ref).days, 60) / 60
    if lead.get("is_roundup"):
        s -= 0.4
    if lead.get("image_url"):
        s += 0.15
    facts = (lead.get("data") or {}).get("key_facts") or []
    s += min(len(facts), 6) * 0.03
    return s


def _dedupe(leads):
    seen, out = set(), []
    for l in leads:
        key = (l.get("name") or l["url"]).strip().lower()
        if key not in seen:
            seen.add(key); out.append(l)
    return out


def _pick(pool, n, today, region_counts):
    chosen = []
    pool = sorted(pool, key=lambda l: score(l, today), reverse=True)
    while pool and len(chosen) < n:
        # 同一片区重复出现会被降权，保证每期覆盖面
        best = max(pool, key=lambda l: score(l, today) - 0.25 * region_counts.get(l["region"], 0))
        pool.remove(best); chosen.append(best)
        region_counts[best["region"]] = region_counts.get(best["region"], 0) + 1
    return chosen


def choose(leads: list, today: date = None) -> list:
    today = today or date.today()
    cfg = config.settings()["weekly_issue"]
    ok = _dedupe([l for l in leads if eligible(l, today)])
    comm = [l for l in ok if l["kind"] == "community"]
    venue = [l for l in ok if l["kind"] == "venue"]
    counts = {}
    n_comm = min(len(comm), max(cfg["min_community"], cfg["max_items"] // 2 - 1))
    picked_c = _pick(comm, n_comm, today, counts)
    n_venue = min(len(venue), cfg["max_items"] - len(picked_c))
    picked_v = _pick(venue, n_venue, today, counts)
    return picked_c + picked_v


def report(leads: list, today: date = None) -> dict:
    today = today or date.today()
    cfg = config.settings()["weekly_issue"]
    chosen = choose(leads, today)
    n_c = sum(1 for l in chosen if l["kind"] == "community")
    n_v = len(chosen) - n_c
    warnings = []
    if n_c < cfg["min_community"]:
        warnings.append(f"社区动态只有 {n_c} 条，少于设定的 {cfg['min_community']} 条")
    if n_v < cfg["min_venue"]:
        warnings.append(f"新店只有 {n_v} 家，少于设定的 {cfg['min_venue']} 家")
    if len(chosen) < cfg["min_items"]:
        warnings.append(f"本期只有 {len(chosen)} 条，少于最低 {cfg['min_items']} 条")
    return {"chosen": chosen, "warnings": warnings}
