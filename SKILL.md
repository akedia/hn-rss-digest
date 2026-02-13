---
name: hn-rss-digest
description: >-
  RSS daily digest of the most popular Hacker News blogs in 2025.
  Aggregates tech news from 92 top HN blogs into a concise daily summary with Chinese summaries.
  Use when: generating tech blog daily reports, checking what's new in the tech blogosphere,
  HN popular blogs digest, RSS aggregation, tech news summary.
  Triggers: HN日报, RSS日报, 技术博客, Hacker News, tech blogs digest, RSS digest.
---

# HN RSS Daily Digest

从 HN 2025 最受欢迎的 92 个技术博客中聚合最新文章，生成每日摘要。

## 日报生成流程

### 第一步：抓取文章

```bash
cd <SKILL_DIR>
python3 scripts/fetch_feeds.py --hours 24 --limit 20 > /tmp/hn_articles.json
```

### 第二步：生成日报并发送

日报需要 **中文摘要**，脚本只输出英文原文摘要。生成后必须由 Agent 将标题和摘要翻译为中文再发送。

格式要求（和 X/Twitter 日报保持一致）：

```markdown
# 🗞️ HN 热门博客日报 YYYY-MM-DD
> 来自 HN 2025 最受欢迎的 92 个技术博客，本期精选 N 篇新文章。

---

## 1. [中文标题]
> from [博客名] YYYY-MM-DD

**📝 摘要**：[中文摘要，2-3 句话概括核心内容]

**🔗 原文**：[查看原文](URL)

---

## 2. ...
```

### 格式规范

- 标题和摘要必须是 **中文**
- 摘要 2-3 句话，抓核心信息，不要直译
- 前 10 篇详细写（编号 + 摘要），剩余用列表简写
- 通过 DingTalk markdown message 发送（`message action=send`）
- 文末注明数据来源

### 参数说明

**fetch_feeds.py**:
- `--hours N` — 回溯小时数（默认 24）
- `--limit N` — 最大文章数（默认 50，日报建议 20）
- `--workers N` — 并发数（默认 10）
- `--timeout N` — 总超时秒数（默认 60）

**generate_digest.py**:
- `--input FILE` — 从文件读取（默认 stdin）
- `--format markdown|dingtalk` — 输出格式
- `--lang cn|en` — 输出语言（默认 cn）

## Feed 来源

`references/feeds.json` 包含 92 个 RSS 源，来自 [HN 2025 Popularity Contest](https://refactoringenglish.com/tools/hn-popularity/)。

主要博客：simonwillison.net, paulgraham.com, krebsonsecurity.com, daringfireball.net, geohot, gwern, pluralistic.net 等。

## 注意事项

- 部分 RSS（如 paulgraham.com）没有时间戳，脚本会自动跳过无日期的文章
- 抓取 92 个源需要约 30-45 秒
- 少数源可能因反爬/超时失败，脚本会跳过并继续
