import httpx
import feedparser
from loguru import logger
from src.config import RSS_SOURCES, AI_RELEASE_SOURCES, AI_RELEASE_KEYWORDS, PRIORITY_KEYWORDS


def fetch_rss(url:str, name:str) -> list[dict]:
    """
    lấy rss feed từ url và trả về danh sách các bài viết
    """

    try:
        resp = httpx.get(url, timeout=15, headers ={"User-Agent": "TechDigestBot/1.0"}, follow_redirects=True)
        feed = feedparser.parse(resp.text)
        articles =[]
        for entry in feed.entries[:15]:
            articles.append({
                "source_name": name,
                "source_type": 'article',
                "source_url": entry.get('link', ''),
                "title": entry.get('title', ''),
                "content_raw": entry.get('summary', '')[:2000],
            })
        logger.info(f"Found {len(articles)} articles from {name}")
        return articles
    except Exception as ex:
        logger.error(f"Error fetching RSS feed from {name}: {ex}")
        return []


def fetch_hackernews() -> list[dict]:
    """
    lấy bài viết từ hackernews
    """
    try:
        resp = httpx.get("https://hn.algolia.com/api/v1/search",
                         params={"tags": "front_page", "hitsPerPage": 15}, timeout=10)
        articles =[]
        for h in resp.json().get('hits', []):
            articles.append({
                "source_name": "hackernews",
                "source_type": 'article',
                "source_url": h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
                "title": h.get('title', ''),
                "content_raw": h.get('story_text', '') or "",
                "hn_points": h.get('points', 0),
            })
        logger.info(f"Found {len(articles)} articles from hackernews")
        return articles
    except Exception as e:
        logger.error(f"Error fetching HackerNews: {e}")
        return []

def is_ai_release(title: str, content: str = "") -> bool:
    text = (title + " " + content[:300]).lower()
    return any(keyword.lower() in text for keyword in AI_RELEASE_KEYWORDS)

def score_article(a: dict) -> float:
    score = {"techcrunch": 1.2, "arstechnica": 1.3, "hackernews": 1.5}.get(a.get("source_name", ""), 1.0)
    score += min(a.get("hn_points", 0) / 100, 2.0)
    tl = a.get("title", "").lower()
    score += sum(0.3 for kw in PRIORITY_KEYWORDS if kw.lower() in tl)
    return score


def crawl_all() -> dict:
    articles = []
    for s in RSS_SOURCES:
        articles += fetch_hackernews() if s["is_api"] else fetch_rss(s["url"], s["name"])

    releases = []
    for s in AI_RELEASE_SOURCES:
        for item in fetch_rss(s["url"], s["name"]):
            if is_ai_release(item["title"], item.get("content_raw", "")):
                item["source_type"] = "ai_release"
                releases.append(item)

    for a in articles:
        a["score"] = score_article(a)
    articles.sort(key=lambda x: x["score"], reverse=True)

    return {"articles": articles[:20], "ai_releases": releases[:5]}