"""判断一条线索属于哪个片区。规则全部来自 config/regions.yaml。"""
import re
from functools import lru_cache

from . import config


@lru_cache(maxsize=1)
def _index():
    cfg = config.load("regions")
    idx = {}
    for key, reg in cfg["regions"].items():
        for s in reg["suburbs"]:
            idx[s.lower()] = (s, key)
        for alias, real in (reg.get("aliases") or {}).items():
            idx[alias.lower()] = (real, key)
    return idx, [p.lower() for p in cfg.get("ignore_phrases", [])], {g.lower() for g in cfg.get("generic", [])}


def region_name(key: str) -> str:
    return config.load("regions")["regions"][key]["name"]


def match_suburbs(text: str, allow_generic: bool = False) -> list:
    """在一段文字里找出覆盖范围内的街区，按出现顺序返回 [(街区, 片区key)]。"""
    idx, ignore, generic = _index()
    low = text.lower()
    for p in ignore:
        low = low.replace(p, " " * len(p))
    found = []
    # 长名字优先，避免 "North Sydney" 被 "Sydney" 抢先
    for name in sorted(idx, key=len, reverse=True):
        if name in generic and not allow_generic:
            continue
        for m in re.finditer(r"(?<![a-z])" + re.escape(name) + r"(?![a-z])", low):
            found.append((m.start(), idx[name]))
            low = low[:m.start()] + " " * len(name) + low[m.end():]
    seen, out = set(), []
    for _, hit in sorted(found):
        if hit[0] not in seen:
            seen.add(hit[0]); out.append(hit)
    return out


def classify(suburbs: list, fallback_text: str = "") -> tuple:
    """优先用抽取出的街区列表；列表里的街区都不在范围内，就判定为范围外。
    只有模型没给出街区时才从正文里找。返回 (街区, 片区key)，范围外返回 (None, None)。"""
    if suburbs:
        for s in suburbs:
            hits = match_suburbs(s, allow_generic=True)
            if hits:
                return hits[0]
        return (None, None)
    hits = match_suburbs(fallback_text)
    return hits[0] if hits else (None, None)
