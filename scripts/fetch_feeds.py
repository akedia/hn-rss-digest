#!/usr/bin/env python3
"""Fetch RSS/Atom feeds and return recent articles as JSON."""

import argparse
import json
import os
import re
import sys
import socket
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta

try:
    import feedparser
except ImportError:
    os.system(f"{sys.executable} -m pip install feedparser -q")
    import feedparser

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEEDS_PATH = os.path.join(SKILL_DIR, "references", "feeds.json")


def parse_date(entry):
    """Extract published date from a feed entry as a UTC datetime."""
    for key in ("published_parsed", "updated_parsed"):
        tp = entry.get(key)
        if tp:
            try:
                return datetime(*tp[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    for key in ("published", "updated"):
        ds = entry.get(key)
        if ds:
            try:
                from email.utils import parsedate_to_datetime
                return parsedate_to_datetime(ds).astimezone(timezone.utc)
            except Exception:
                pass
    return None


def clean_summary(entry):
    """Get a plain-text summary, max 200 chars."""
    raw = entry.get("summary", "") or entry.get("description", "") or ""
    text = re.sub(r"<[^>]+>", "", raw)
    text = text.replace("\n", " ").strip()
    if len(text) > 200:
        text = text[:197] + "..."
    return text


def fetch_one(feed_info, cutoff):
    """Fetch a single feed and return recent articles."""
    name = feed_info["name"]
    url = feed_info["xmlUrl"]
    articles = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "HN-RSS-Digest/1.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        raw = resp.read(1024 * 512)  # Max 512KB per feed
        d = feedparser.parse(raw)
        if d.bozo and not d.entries:
            return articles
        for entry in d.entries:
            pub = parse_date(entry)
            if pub is None or pub < cutoff:
                continue
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            if not title or not link:
                continue
            articles.append({
                "title": title,
                "link": link,
                "published": pub.isoformat() if pub else None,
                "feed": name,
                "summary": clean_summary(entry),
            })
    except Exception as e:
        print(f"[WARN] Failed to fetch {name}: {e}", file=sys.stderr)
    return articles


def main():
    parser = argparse.ArgumentParser(description="Fetch recent articles from HN popular blogs")
    parser.add_argument("--hours", type=int, default=24, help="Look back N hours (default 24)")
    parser.add_argument("--limit", type=int, default=50, help="Max articles to output (default 50)")
    parser.add_argument("--workers", type=int, default=10, help="Concurrent workers (default 10)")
    parser.add_argument("--feeds", type=str, default=FEEDS_PATH, help="Path to feeds.json")
    parser.add_argument("--timeout", type=int, default=60, help="Overall timeout in seconds (default 60)")
    args = parser.parse_args()

    with open(args.feeds, "r") as f:
        feeds = json.load(f)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=args.hours)
    all_articles = []

    socket.setdefaulttimeout(10)

    pool = ThreadPoolExecutor(max_workers=args.workers)
    futures = {pool.submit(fetch_one, feed, cutoff): feed["name"] for feed in feeds}

    try:
        for future in as_completed(futures, timeout=args.timeout):
            name = futures[future]
            try:
                result = future.result(timeout=1)
                all_articles.extend(result)
            except Exception as e:
                print(f"[WARN] {name}: {e}", file=sys.stderr)
    except TimeoutError:
        print(f"[WARN] Overall timeout reached, proceeding with collected articles", file=sys.stderr)

    # Don't wait for remaining threads
    pool.shutdown(wait=False, cancel_futures=True)

    # Sort by published date, newest first
    all_articles.sort(key=lambda a: a["published"] or "", reverse=True)

    if args.limit and len(all_articles) > args.limit:
        all_articles = all_articles[:args.limit]

    json.dump(all_articles, sys.stdout, ensure_ascii=False, indent=2)
    print(file=sys.stdout)


if __name__ == "__main__":
    main()
