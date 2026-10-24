"""网页抓取与正文解析。"""
import json, re, time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from . import config

_last = [0.0]


def get(url: str, binary: bool = False):
    s = config.settings()["http"]
    wait = s["polite_delay_seconds"] - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    r = requests.get(url, headers={"User-Agent": s["user_agent"]}, timeout=s["timeout_seconds"])
    _last[0] = time.time()
    r.raise_for_status()
    return r.content if binary else r.text


def listing_links(html: str, base: str, pattern: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for a in soup.find_all("a", href=True):
        href = urljoin(base, a["href"].split("#")[0].split("?")[0])
        if re.search(pattern, href) and href.rstrip("/") != base.rstrip("/") and href not in out:
            out.append(href)
    return out


def _meta(soup, *names):
    for n in names:
        tag = soup.find("meta", attrs={"property": n}) or soup.find("meta", attrs={"name": n})
        if tag and tag.get("content"):
            return tag["content"].strip()
    return None


def _jsonld_date(soup):
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(s.string or "")
        except Exception:
            continue
        for d in data if isinstance(data, list) else [data]:
            if isinstance(d, dict) and d.get("datePublished"):
                return d["datePublished"]
    return None


def parse_article(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    published = (_meta(soup, "article:published_time", "datePublished") or _jsonld_date(soup)
                 or (soup.find("time").get("datetime") if soup.find("time") and soup.find("time").get("datetime") else None))
    for bad in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        bad.decompose()
    body = soup.find("article") or soup.find("main") or soup.body or soup
    paras = [p.get_text(" ", strip=True) for p in body.find_all(["p", "h2", "h3", "li"])]
    text = "\n".join(p for p in paras if len(p) > 25)
    captions = [c.get_text(" ", strip=True) for c in soup.find_all(["figcaption"])]
    credit_lines = [t for t in captions + paras if re.match(r"^(Photo|Image|Images|Credit)s?\b", t, re.I)]
    return {
        "url": url,
        "title": _meta(soup, "og:title") or (soup.title.get_text(strip=True) if soup.title else ""),
        "published": (published or "")[:10] or None,
        "image_url": _meta(soup, "og:image", "twitter:image"),
        "image_credit": credit_lines[0] if credit_lines else None,
        "text": text[:20000],
    }


def og_image(url: str):
    try:
        return parse_article(get(url), url)["image_url"]
    except Exception:
        return None
