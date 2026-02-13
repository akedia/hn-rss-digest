#!/usr/bin/env python3
"""Generate a formatted daily digest from fetched RSS articles."""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone


def format_time(iso_str):
    """Format ISO time string to a readable format."""
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%H:%M")
    except Exception:
        return ""


def generate_markdown(articles, lang="en"):
    """Generate markdown digest."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Group by feed
    by_feed = defaultdict(list)
    for a in articles:
        by_feed[a["feed"]].append(a)

    lines = []
    if lang == "cn":
        lines.append(f"# 📰 HN 热门博客日报 — {today}")
        lines.append("")
        lines.append(f"共 **{len(articles)}** 篇新文章，来自 **{len(by_feed)}** 个博客。")
    else:
        lines.append(f"# 📰 HN Popular Blogs Daily Digest — {today}")
        lines.append("")
        lines.append(f"**{len(articles)}** new articles from **{len(by_feed)}** blogs.")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Sort feeds by number of articles (descending)
    for feed_name, feed_articles in sorted(by_feed.items(), key=lambda x: -len(x[1])):
        lines.append(f"## {feed_name}")
        lines.append("")
        for a in feed_articles:
            t = format_time(a.get("published"))
            time_str = f" `{t}`" if t else ""
            lines.append(f"- [{a['title']}]({a['link']}){time_str}")
            if a.get("summary"):
                lines.append(f"  > {a['summary']}")
            lines.append("")
        lines.append("")

    if lang == "cn":
        lines.append("---")
        lines.append("*数据来源：HN 2025 最受欢迎博客 RSS 聚合*")
    else:
        lines.append("---")
        lines.append("*Source: The Most Popular Blogs of Hacker News 2025*")

    return "\n".join(lines)


def generate_dingtalk(articles, lang="en"):
    """Generate simplified format for DingTalk messages."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    by_feed = defaultdict(list)
    for a in articles:
        by_feed[a["feed"]].append(a)

    lines = []
    if lang == "cn":
        lines.append(f"📰 HN热门博客日报 {today}")
        lines.append(f"共{len(articles)}篇新文章")
        lines.append("")
    else:
        lines.append(f"📰 HN Blogs Digest {today}")
        lines.append(f"{len(articles)} new articles")
        lines.append("")

    for feed_name, feed_articles in sorted(by_feed.items(), key=lambda x: -len(x[1])):
        lines.append(f"**{feed_name}**")
        for a in feed_articles:
            lines.append(f"- [{a['title']}]({a['link']})")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate daily digest from fetched articles")
    parser.add_argument("--input", "-i", type=str, default=None, help="Input JSON file (default: stdin)")
    parser.add_argument("--format", "-f", type=str, default="markdown", choices=["markdown", "dingtalk"],
                        help="Output format (default: markdown)")
    parser.add_argument("--lang", "-l", type=str, default="en", choices=["en", "cn"],
                        help="Output language (default: en)")
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
