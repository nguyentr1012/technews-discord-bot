import asyncio
import discord
from loguru import logger

CATEGORY_COLORS = {
    "AI": 0x7B2FBE,
    "startup": 0x00A878,
    "security": 0xE63946,
    "hardware": 0xF4A261,
    "opensource": 0x0099FF,
    "release": 0xFF6B35,
    "other": 0x5865F2,
}


def build_embed(article: dict, summary: dict) -> discord.Embed:
    embed = discord.Embed(
        title=article["title"][:256],
        url=article.get("source url", ""),
        description=summary.get("summary_vi", ""),
        color=CATEGORY_COLORS.get(article.get("category", "other"), 0x5865F2),
    )
    embed.add_field(name="Nguồn", value=article.get("source_name", ""), inline=True)
    tags = " ".join(summary.get("tags", []))
    if tags:
        embed.add_field(name="Tags", value=tags, inline=True)
    embed
