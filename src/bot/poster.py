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
        url=article.get("source_url", ""),
        description=summary.get("summary_vi", ""),
        color=CATEGORY_COLORS.get(summary.get("category", "other"), 0x5865F2),
    )
    embed.add_field(name="Nguồn", value=article.get("source_name", ""), inline=True)
    tags = " ".join(summary.get("tags", []))
    if tags:
        embed.add_field(name="Tags", value=tags, inline=True)
    embed.set_footer(text="TechDigest • Gemini 2.5 Flash")
    return embed


async def post_digest(
    channel,
    crawl_data: dict,
    article_summaries: list,
    release_summaries: list,
    github_repos: list,
    github_summaries: list,
):
    from datetime import datetime

    today = datetime.now().strftime("%A, %d/%m/%Y")
    await channel.send(f"```\n📅 TECH DIGEST — {today}\n```")

    # 📰 Tin nổi bật
    await channel.send("**📰 TIN NỔI BẬT**")
    articles = crawl_data["articles"]
    for i, s in enumerate(article_summaries[:4]):
        if i < len(articles):
            await channel.send(embed=build_embed(articles[i], s))
            await asyncio.sleep(0.5)

    # 🤖 AI Releases — chỉ khi có
    releases = crawl_data.get("ai_releases", [])
    if release_summaries and releases:
        await channel.send("**🤖 AI/MODEL RELEASES**")
        for i, s in enumerate(release_summaries[:3]):
            if i < len(releases):
                await channel.send(embed=build_embed(releases[i], s))
                await asyncio.sleep(0.5)

    # 🔥 GitHub Trending
    if github_summaries and github_repos:
        lines = []
        for i, s in enumerate(github_summaries):
            if i < len(github_repos):
                r = github_repos[i]
                lines.append(
                    f"• **{r['name']}** — {s.get('summary_vi', '')} ★ {r['stars_today']} [↗](<{r['url']}>)"
                )
        if lines:
            await channel.send("**🔥 GITHUB TRENDING**\n" + "\n".join(lines))

    logger.info("Digest posted ✓")
