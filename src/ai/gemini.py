import json
import google.generativeai as genai
from loguru import logger
from src.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
_model = genai.GenerativeModel("gemini-2.5-flash")

def _clean_json(text:str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
    return text

def summarize_article(articles:list[dict]) -> list[dict]:
    if not articles:
        return []
    block = ""
    for i, a in enumerate(articles):
        block += f"\n---ARTICLE_{i}---\nTitle: {a['title']}\nSource: {a['source_name']}\nContent: {(a.get('content_raw') or '')[:600]}\n"

    prompt = f"""Bạn là trợ lý tổng hợp tin tức công nghệ. Tóm tắt TỪNG bài sau thành tiếng Việt.
Giữ nguyên thuật ngữ kỹ thuật tiếng Anh. Mỗi summary 3-4 câu ngắn gọn.

{block}

Trả về JSON array thuần túy (không markdown, không backtick):
[{{"id":0,"summary_vi":"...","tags":["#AI"],"category":"AI|startup|security|hardware|opensource|release|other"}}]"""

    try:
        response = _model.generate_content(prompt)
        result = json.loads(_clean_json(response.text))
        return result
    except Exception as e:
        logger.error(f"Error summarizing articles: {e}")
        return []

def summarize_github_repos(repos: list[dict]) -> list[dict]:
    if not repos:
        return []
    block = "\n".join(
        f"REPO_{i}: {r['name']} | {r.get('description','')} | {r.get('language','')}"
        for i, r in enumerate(repos)
    )
    prompt = f"""Mô tả TỪNG repo sau thành 1 câu tiếng Việt tối đa 15 từ.

{block}

Trả về JSON array thuần túy:
[{{"id":0,"summary_vi":"..."}}]"""

    try:
        resp = _model.generate_content(prompt)
        return json.loads(_clean_json(resp.text))
    except Exception as ex:
        logger.error(f"[Gemini] summarize_github lỗi: {ex}")
        return []