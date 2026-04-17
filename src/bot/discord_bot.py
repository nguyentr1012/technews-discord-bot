import discord
from discord.ext import commands, tasks
from datetime import time
from loguru import logger

from src.config import DISCORD_TOKEN, DISCORD_CHANNEL_ID, DIGEST_HOUR, DIGEST_MINUTE
from src.crawler.rss import crawl_all
from src.crawler.github_trending import scrape_github_trending
from src.ai.gemini import summarize_article, summarize_github_repos
from src.bot.poster import post_digest

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


async def run_pipeline(channel):
    """Chạy toàn bộ pipeline: crawl → summarize → post."""
    logger.info("Bắt đầu chạy pipeline...")

    crawl_data = crawl_all()
    github_repos = scrape_github_trending(limit=5)

    article_summaries = summarize_article(crawl_data["articles"][:8])
    release_summaries = summarize_article(crawl_data.get("ai_releases", []))
    github_summaries = summarize_github_repos(github_repos)

    await post_digest(
        channel,
        crawl_data,
        article_summaries,
        release_summaries,
        github_repos,
        github_summaries,
    )


@bot.event
async def on_ready():
    logger.info(f"Bot đã online: {bot.user}")
    await bot.tree.sync()
    if not daily_digest.is_running():
        daily_digest.start()


@tasks.loop(time=time(hour=DIGEST_HOUR, minute=DIGEST_MINUTE))
async def daily_digest():
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        await run_pipeline(channel)
    else:
        logger.error(f"Không tìm thấy channel {DISCORD_CHANNEL_ID}")


@bot.tree.command(name="digest", description="Chạy digest thủ công ngay bây giờ")
async def cmd_digest(interaction: discord.Interaction):
    await interaction.response.send_message("⏳ Đang xử lý...", ephemeral=True)
    await run_pipeline(interaction.channel)


@bot.tree.command(name="ping", description="Kiểm tra bot còn sống không")
async def cmd_ping(interaction: discord.Interaction):
    await interaction.response.send_message("🟢 Bot đang hoạt động!", ephemeral=True)


def start():
    bot.run(DISCORD_TOKEN)
