#!/usr/bin/env python3
"""Generate a formatted daily digest from fetched RSS articles."""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone


def format_date(iso_str):
    """Format ISO time string."""
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ""


def truncate(text, maxlen=300):
    """Truncate text to maxlen chars."""
    if not text:
        return ""
    text = text.strip()
    if len(text) > maxlen:
        return text[:maxlen-3] + "..."
    return text


def generate_dingtalk(articles, lang="cn"):
    """Generate DingTalk markdown format, matching X daily report style."""
    from datetime import timedelta
    today = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")

    lines = []
    lines.append(f"# 🗞️ HN 热门博客日报 {today}")
    lines.append(f"> 来自 HN 2025 最受欢迎的 92 个技术博客，本期精选 {len(articles)} 篇新文章。")
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, a in enumerate(articles, 1):
        feed = a.get("feed", "")
        title = a.get("title", "")
        link = a.get("link", "")
        summary = truncate(a.get("summary", ""), 300)
        pub = format_date(a.get("published"))

        lines.append(f"## {i}. {title}")
        lines.append(f"> from {feed} {pub}")
        lines.append("")
        if summary:
            lines.append(f"**📝 摘要**：{summary}")
            lines.append("")
        lines.append(f"**🔗 原文**：[查看原文]({link})")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append(f"*数据来源：HN 2025 最受欢迎博客 RSS 聚合 | 共监控 92 个博客*")
    return "\n".join(lines)


def generate_markdown(articles, lang="en"):
    """Generate full markdown digest."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = []
    if lang == "cn":
        lines.append(f"# 🗞️ HN 热门博客日报 {today}")
        lines.append(f"> 来自 HN 2025 最受欢迎的 92 个技术博客，本期精选 {len(articles)} 篇新文章。")
    else:
        lines.append(f"# 🗞️ HN Popular Blogs Daily Digest — {today}")
        lines.append(f"> {len(articles)} new articles from the most popular HN blogs of 2025.")

    lines.append("")
    lines.append("---")
    lines.append("")

    for i, a in enumerate(articles, 1):
        feed = a.get("feed", "")
        title = a.get("title", "")
        link = a.get("link", "")
        summary = truncate(a.get("summary", ""), 300)
        pub = format_date(a.get("published"))

        lines.append(f"## {i}. {title}")
        lines.append(f"> from {feed} {pub}")
        lines.append("")
        if summary:
            if lang == "cn":
                lines.append(f"**📝 摘要**：{summary}")
            else:
                lines.append(f"**📝 Summary**: {summary}")
            lines.append("")
        if lang == "cn":
            lines.append(f"**🔗 原文**：[查看原文]({link})")
        else:
            lines.append(f"**🔗 Link**: [Read more]({link})")
        lines.append("")
        lines.append("---")
        lines.append("")

    if lang == "cn":
        lines.append(f"*数据来源：HN 2025 最受欢迎博客 RSS 聚合 | 共监控 92 个博客*")
    else:
        lines.append(f"*Source: The Most Popular Blogs of Hacker News 2025 | 92 blogs monitored*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate daily digest from fetched articles")
    parser.add_argument("--input", "-i", type=str, default=None, help="Input JSON file (default: stdin)")
    parser.add_argument("--format", "-f", type=str, default="markdown", choices=["markdown", "dingtalk"],
                        help="Output format (default: markdown)")
    parser.add_argument("--lang", "-l", type=str, default="cn", choices=["en", "cn"],
                        help="Output language (default: cn)")
    args = parser.parse_args()

    if args.input:
        with open(args.input, "r") as f:
            articles = json.load(f)
    else:
        articles = json.load(sys.stdin)

    if not articles:
        if args.lang == "cn":
            print("过去24小时没有新文章。")
        else:
            print("No new articles in the past 24 hours.")
        return

    if args.format == "dingtalk":
        print(generate_dingtalk(articles, lang=args.lang))
    else:
        print(generate_markdown(articles, lang=args.lang))


if __name__ == "__main__":
    main()
