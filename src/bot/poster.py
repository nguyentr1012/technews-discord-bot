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
    if not isinstance(summary, dict):
        summary = {}
    
    title = article.get("title") or "Tin tức công nghệ"
    embed = discord.Embed(
        title=title[:256],
        url=article.get("source_url", ""),
        description=summary.get("summary_vi", "Không có tóm tắt."),
        color=CATEGORY_COLORS.get(summary.get("category", "other"), 0x5865F2),
    )
    embed.add_field(
        name="Nguồn",
        value=article.get("source_name", "Nguồn tin"),
        inline=True,
    )
    
    tags_list = summary.get("tags", [])
    if isinstance(tags_list, list):
        tags = " ".join(tags_list)
    else:
        tags = str(tags_list) if tags_list else ""

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
    articles = crawl_data.get("articles", [])
    if not articles:
        await channel.send("⚠️ *Không lấy được tin tức nào từ các nguồn RSS (Có thể IP của server hosting đã bị các trang tin chặn).*")
    elif not article_summaries:
        await channel.send("⚠️ *Lỗi tóm tắt tin tức (Có thể do chưa cấu hình hoặc sai API Key Gemini trên Hosting).*")
    else:
        for i, s in enumerate(article_summaries[:4]):
            if i < len(articles):
                await channel.send(embed=build_embed(articles[i], s))
                await asyncio.sleep(0.5)

    # 🤖 AI Releases — chỉ khi có
    releases = crawl_data.get("ai_releases", [])
    if releases:
        await channel.send("**🤖 AI/MODEL RELEASES**")
        if not release_summaries:
            await channel.send("⚠️ *Lỗi tóm tắt các bản phát hành AI từ Gemini.*")
        else:
            for i, s in enumerate(release_summaries[:3]):
                if i < len(releases):
                    await channel.send(embed=build_embed(releases[i], s))
                    await asyncio.sleep(0.5)

    # 🔥 GitHub Trending
    github_repos = github_repos or []
    if github_repos:
        if not github_summaries:
            await channel.send("**🔥 GITHUB TRENDING**\n⚠️ *Lỗi tóm tắt GitHub Trending từ Gemini.*")
        else:
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
