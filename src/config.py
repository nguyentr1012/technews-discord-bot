import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DIGEST_HOUR = os.getenv("DIGEST_HOUR")
DIGEST_MINUTE = os.getenv("DIGEST_MINUTE")

RSS_SOURCES = [
    {"name": "techcrunch",  "url": "https://techcrunch.com/feed/",                         "is_api": False},
    {"name": "arstechnica", "url": "https://feeds.arstechnica.com/arstechnica/index",       "is_api": False},
    {"name": "hackernews",  "url": "https://hn.algolia.com/api/v1/search?tags=front_page", "is_api": True},
    {"name": "reddit_tech", "url": "https://www.reddit.com/r/technology/.rss",             "is_api": False},
    {"name": "reddit_ml",   "url": "https://www.reddit.com/r/MachineLearning/.rss",        "is_api": False},
]

AI_RELEASE_SOURCES = [
    {"name": "openai",     "url": "https://openai.com/news/rss.xml"},
    {"name": "anthropic",  "url": "https://www.anthropic.com/rss.xml"},
    {"name": "huggingface","url": "https://huggingface.co/blog/feed.xml"},
    {"name": "meta_ai",    "url": "https://ai.meta.com/blog/rss/"},
]

AI_RELEASE_KEYWORDS = [
    "release", "launch", "announce", "introduce", "unveil",
    "GPT-", "Claude ", "Gemini ", "Llama ", "Mistral ",
    "open-weight", "weights released", "now available", "open source model",
]

PRIORITY_KEYWORDS = [
    "LLM", "AI agent", "RAG", "fine-tuning", "multimodal",
    "funding", "acquisition", "open source", "benchmark", "SOTA",
]