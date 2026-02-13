---
name: hn-rss-digest
description: RSS daily digest of the most popular Hacker News blogs in 2025. Aggregates tech news from 90+ top HN blogs into a concise daily summary.
---

# HN RSS Daily Digest

Generate a daily digest of new articles from the most popular blogs on Hacker News (2025 edition). Covers 90+ tech blogs including simonwillison.net, krebsonsecurity.com, daringfireball.net, paulgraham.com, and more.

## Usage

### Quick one-liner

```bash
cd /home/clawd/clawd/skills/hn-rss-digest
python3 scripts/fetch_feeds.py | python3 scripts/generate_digest.py
```

### Step by step

1. **Fetch recent articles** (last 24 hours by default):
```bash
python3 scripts/fetch_feeds.py --hours 24 --limit 50
```

2. **Generate the digest** (pipe from step 1):
```bash
python3 scripts/fetch_feeds.py | python3 scripts/generate_digest.py --format markdown --lang en
```

### Options

**fetch_feeds.py**:
- `--hours N` — Look back N hours (default: 24)
- `--limit N` — Max articles (default: 50)
- `--workers N` — Concurrent fetchers (default: 10)
- `--feeds PATH` — Custom feeds.json path

**generate_digest.py**:
- `--input FILE` — Read JSON from file instead of stdin
- `--format markdown|dingtalk` — Output format (default: markdown)
- `--lang en|cn` — Output language (default: en)

### DingTalk daily report

```bash
python3 scripts/fetch_feeds.py --hours 24 | python3 scripts/generate_digest.py --format dingtalk --lang cn
```

### Save to file

```bash
python3 scripts/fetch_feeds.py > /tmp/articles.json
python3 scripts/generate_digest.py --input /tmp/articles.json > /tmp/digest.md
```

## Feed Sources

All feeds are stored in `references/feeds.json`. They come from the OPML export of [The Most Popular Blogs of Hacker News in 2025](https://refactoringenglish.com/tools/hn-popularity/).

## Dependencies

- Python 3
- `feedparser` (`pip install feedparser`)
