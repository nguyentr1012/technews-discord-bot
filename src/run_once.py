"""
run_once.py — dùng cho GitHub Actions
Crawl + AI + post Discord rồi thoát, không loop.
"""

import asyncio
import sys
from loguru import logger

logger.remove()
logger.add(
    sys.stdout,
    colorize=False,
    level="INFO",
    format="{time:HH:mm:ss} | {level: <8} | {message}",
)

import discord
from src.config import DISCORD_TOKEN, DISCORD_CHANNEL_ID
from src.crawler.rss import crawl_all
from src.crawler.github_trending import scrape_github_trending
from src.ai.gemini import summarize_articles, summarize_github_repos
from src.bot.poster import post_digest

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    logger.info(f"Connected as {client.user}")
    channel = client.get_channel(DISCORD_CHANNEL_ID)

    if not channel:
        logger.error(f"Không tìm thấy channel ID {DISCORD_CHANNEL_ID}")
        await client.close()
        return

    try:
        crawl_data = crawl_all()
        github_repos = scrape_github_trending(3)
        article_summaries = summarize_articles(crawl_data["articles"])
        release_summaries = (
            summarize_articles(crawl_data["ai_releases"])
            if crawl_data["ai_releases"]
            else []
        )
        github_summaries = summarize_github_repos(github_repos)

        await post_digest(
            channel,
            crawl_data,
            article_summaries,
            release_summaries,
            github_repos,
            github_summaries,
        )
        logger.info("✅ Digest hoàn tất")
    except Exception as e:
        logger.error(f"Pipeline lỗi: {e}")
        raise
    finally:
        await client.close()


client.run(DISCORD_TOKEN)
