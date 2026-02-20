# Knowledgebase RAG – Design (2026-02-20)

## Goal
Build a personal knowledge base with RAG. Ingest URLs via a Telegram bot, store everything as Markdown in an Obsidian vault, embed into a QMD collection, and answer natural language queries with time‑aware + source‑weighted ranking. Summaries are saved daily to Obsidian (no Telegraph).

## Architecture (Split Services)
**Bot → Queue → Worker → API**
- **Telegram bot**: Receives messages, enqueues ingestion jobs, accepts queries.
- **Queue**: File‑based markdown tasks (`task-YYYYMMDD.md`).
- **Worker**: Reads tasks, ingests content with OpenClaw skills, writes Markdown, embeds to QMD.
- **API/Query engine**: Semantic search + ranking; returns short answers + citations.

## Storage
- **Obsidian vault**: `workspace/knowledgebase/<source_type>/YYYYMMDD-title.md`
- **Tasks**: `workspace/knowledgebase/tasks/task-YYYYMMDD.md`
- **QMD collection**: `knowledgebase`

## Queue Format
One file per day:
```
- [ ] 2026-02-20 https://example.com
- [X] 2026-02-20 https://example.com
- [F] 2026-02-20 https://example.com
- [2] 2026-02-20 https://example.com
```
Statuses:
- `[ ]` pending
- `[X]` completed
- `[F]` failed
- `[<number>]` retry count

Worker scans **last 3 days** of task files.

## Ingestion Pipelines
**Articles**
- Primary: `web_fetch`
- Paywalled: `debug-browser` headless session

**YouTube**
- Tier 1: transcript skill (CC)
- Tier 2: Whisper transcription
  - `yt-dlp` audio
  - `ffmpeg` mono + compressed
  - Whisper (local or API)

**X/Twitter**
- Use `bird` skill
- Fetch full threads
- If tweet links to article: ingest tweet thread + linked article

**PDF**
- Use `pypdf/marker` to extract text

**Entity Extraction**
- Local NER model
- Store entities in YAML front‑matter

## Markdown Output Template
```
---
source_url: ...
source_type: article|youtube|twitter|pdf|paywalled
created_at: ISO8601
entities:
  people: [...]
  companies: [...]
  concepts: [...]
---

# Title

Content...
```

## Query + Ranking
- Semantic search in QMD `knowledgebase`
- Recency boost (30‑day half‑life): `exp(-age_days/30)`
- Source weights (Option A):
  - Paywalled/browser: **1.5**
  - PDF: **1.3**
  - YouTube: **1.2**
  - Article: **1.0**
  - Twitter/X: **0.8**

**Response format (Telegram):**
- Short answer
- Bullet citations with titles + links

## Scheduling
- Overnight ingestion (cron, evenly spread)
- Daily summary at **07:00 Europe/London**
- Summary saved into Obsidian vault as Markdown

## Notes / Constraints
- Minimal custom code; leverage OpenClaw skills where possible
- Separate bot using provided token
- Debug‑browser for paywalled extraction (headless)
- No Telegraph posting
