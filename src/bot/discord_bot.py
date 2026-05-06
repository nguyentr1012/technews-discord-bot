import discord
from discord.ext import commands, tasks
from datetime import time
from loguru import logger

from src.config import DISCORD_TOKEN, DISCORD_CHANNEL_ID, DISCORD_GUILD_ID, DIGEST_HOUR, DIGEST_MINUTE
from src.crawler.rss import crawl_all
from src.crawler.github_trending import scrape_github_trending
from src.ai.gemini import summarize_articles, summarize_github_repos
from src.bot.poster import post_digest

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


async def run_pipeline(channel):
    """Chạy toàn bộ pipeline: crawl → summarize → post."""
    logger.info("Bắt đầu chạy pipeline...")

    crawl_data = crawl_all()
    github_repos = scrape_github_trending(limit=5)

    article_summaries = summarize_articles(crawl_data["articles"][:8])
    release_summaries = summarize_articles(crawl_data.get("ai_releases", []))
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
    
    # Đồng bộ command cho server cụ thể để nhận ngay lập tức (nếu có Guild ID)
    if DISCORD_GUILD_ID:
        try:
            guild = discord.Object(id=int(DISCORD_GUILD_ID))
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
            logger.info(f"Đã đồng bộ slash command cho server (Guild ID): {DISCORD_GUILD_ID}")
        except Exception as e:
            logger.warning(f"Không thể đồng bộ command cho Guild: {e}. Tiến hành đồng bộ toàn cầu...")
            await bot.tree.sync()
    else:
        await bot.tree.sync()
        logger.info("Đã đồng bộ slash command toàn cầu")
        
    if not daily_digest.is_running():
        daily_digest.start()


@tasks.loop(time=time(hour=DIGEST_HOUR, minute=DIGEST_MINUTE))
async def daily_digest():
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        await run_pipeline(channel)
    else:
        logger.error(f"Không tìm thấy channel {DISCORD_CHANNEL_ID}")


# ==========================================
# SLASH COMMANDS (LỆNH /)
# ==========================================
@bot.tree.command(name="digest", description="Chạy digest thủ công ngay bây giờ")
async def cmd_digest(interaction: discord.Interaction):
    await interaction.response.send_message("⏳ Đang xử lý...", ephemeral=True)
    try:
        await run_pipeline(interaction.channel)
    except Exception as e:
        logger.error(f"Lỗi khi chạy slash digest: {e}")


@bot.tree.command(name="ping", description="Kiểm tra bot còn sống không")
async def cmd_ping(interaction: discord.Interaction):
    await interaction.response.send_message("🟢 Bot đang hoạt động!", ephemeral=True)


# ==========================================
# PREFIX COMMANDS (LỆNH !)
# ==========================================
@bot.command(name="digest", help="Cào và gửi tin tức ngay bây giờ")
async def prefix_digest(ctx):
    await ctx.send("⏳ Đang xử lý tin tức... Vui lòng đợi một lát!")
    try:
        await run_pipeline(ctx.channel)
        await ctx.send("✅ Đã hoàn tất gửi Tech Digest!")
    except Exception as e:
        logger.error(f"Lỗi khi chạy prefix digest: {e}")
        await ctx.send(f"❌ Có lỗi xảy ra khi chạy digest: {e}")


@bot.command(name="ping", help="Kiểm tra xem bot còn sống không")
async def prefix_ping(ctx):
    await ctx.send("🟢 Bot đang hoạt động hoàn hảo!")


def start_health_check_server():
    from http.server import BaseHTTPRequestHandler, HTTPServer
    import threading
    import os

    class HealthCheckHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("🟢 Bot is alive and running!".encode("utf-8"))

        def log_message(self, format, *args):
            # Suppress normal ping logs to avoid clogging up console
            pass

    # Render tự động cấp biến PORT, nếu không có mặc định chạy port 8080
    port = int(os.getenv("PORT", "8080"))
    server_address = ("", port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    logger.info(f"Web server Health Check đã khởi động trên port {port}")


def start():
    start_health_check_server()
    bot.run(DISCORD_TOKEN)
