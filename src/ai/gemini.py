import json
from google import genai
from google.genai import types
from loguru import logger
from src.config import GEMINI_API_KEY

_client = genai.Client(api_key=GEMINI_API_KEY)
_MODEL = "gemini-2.5-flash"


def _clean_json(text: str) -> str:
    """Strip markdown code fences nếu Gemini bọc backtick."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
    return text.strip()


def summarize_articles(articles: list[dict]) -> list[dict]:
    """Gộp tất cả bài → 1 Gemini call → JSON array."""
    if not articles:
        return []

    block = ""
    for i, a in enumerate(articles):
        content = (a.get("content_raw") or "")[:600]
        block += f"\n---ARTICLE_{i}---\nTitle: {a['title']}\nSource: {a['source_name']}\nContent: {content}\n"

    prompt = f"""Bạn là trợ lý tổng hợp tin tức công nghệ. Tóm tắt TỪNG bài sau thành tiếng Việt.
Giữ nguyên thuật ngữ kỹ thuật tiếng Anh. Mỗi summary 3-4 câu ngắn gọn.

{block}

Trả về JSON array thuần túy (không markdown, không backtick):
[{{"id":0,"summary_vi":"...","tags":["#AI"],"category":"AI|startup|security|hardware|opensource|release|other"}}]"""

    try:
        response = _client.models.generate_content(
            model=_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=2048,
            ),
        )
        return json.loads(_clean_json(response.text))
    except Exception as ex:
        logger.error(f"[Gemini] summarize_articles lỗi: {ex}")
        return []


def summarize_github_repos(repos: list[dict]) -> list[dict]:
    """Tóm tắt GitHub repos → 1 call."""
    if not repos:
        return []

    block = "\n".join(
        f"REPO_{i}: {r['name']} | {r.get('description', '')} | {r.get('language', '')}"
        for i, r in enumerate(repos)
    )
    prompt = f"""Mô tả TỪNG repo sau thành 1 câu tiếng Việt tối đa 15 từ.

{block}

Trả về JSON array thuần túy (không markdown, không backtick):
[{{"id":0,"summary_vi":"..."}}]"""

    try:
        response = _client.models.generate_content(
            model=_MODEL,
            contents=prompt,
        )
        return json.loads(_clean_json(response.text))
    except Exception as ex:
        logger.error(f"[Gemini] summarize_github lỗi: {ex}")
        return []
