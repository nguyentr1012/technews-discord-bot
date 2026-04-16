import httpx
from selectolax.parser import HTMLParser
from loguru import logger


def scrape_github_trending(limit:int=3) -> list[dict]:
    try:
        resp = httpx.get("https://github.com/trending",
        params ={"since": "daily", "spoken_language_code": "en"},
        headers={"User-Agent": "TechDigestBot/1.0"}, timeout=10)

        tree = HTMLParser(resp.text)
        repos =[]
        for article in tree.css("article.Box-row")[:limit]:
            name_el = article.css_first("h2 a")
            description_el = article.css_first("p")
            language_el = article.css_first("[itemprop='programmingLanguage']")
            today_el = article.css_first("span.d-inline-block.float-sm-right")
            if not name_el:
                continue
            href = name_el.attributes.get("href","")
            repos.append({
                "name": href.strip("/").replace(" ", ""),
                "url": f"https://github.com{href}",
                "description": description_el.text() if description_el else "",
                "language": language_el.text() if language_el else "",
                "today": today_el.text() if today_el else "",
            })
        logger.info(f"Found {len(repos)} repositories from GitHub trending")
        return repos
    except Exception as e:
        logger.error(f"Error scraping GitHub trending: {e}")
        return []
