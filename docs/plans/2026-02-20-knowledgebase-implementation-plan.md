# Knowledgebase RAG Implementation Plan

> **For agent:** Use the subagent-driven-development or executing-plans skill to implement this plan task-by-task.

**Goal:** Build a Telegram‑driven personal knowledge base with a file‑based queue, multi‑source ingestion, Obsidian Markdown storage, QMD embeddings, and RAG query with recency + source weighting.
**Architecture:** Split services: Telegram bot → file‑based queue → ingestion worker → query API. Worker uses OpenClaw skills for extraction; minimal custom code.
**Tech Stack:** Python, FastAPI (optional API layer), SQLite‑free file queue, OpenClaw skills (web_fetch, debug‑browser, bird, whisper), QMD.

---

## Task 1: Project scaffold + config

**Files:**
- Create: `pyproject.toml`
- Create: `src/knowledgebase/__init__.py`
- Create: `src/knowledgebase/config.py`
- Create: `.env.example`
- Create: `tests/test_config.py`

**Step 1: Write the failing test**

```python
# tests/test_config.py
from knowledgebase.config import load_config


def test_load_config_reads_required_fields(tmp_path, monkeypatch):
    monkeypatch.setenv("KB_VAULT_PATH", str(tmp_path / "vault"))
    monkeypatch.setenv("KB_TASKS_PATH", str(tmp_path / "tasks"))
    monkeypatch.setenv("KB_QMD_COLLECTION", "knowledgebase")
    monkeypatch.setenv("KB_TELEGRAM_BOT_TOKEN", "x")
    cfg = load_config()
    assert cfg.vault_path.endswith("vault")
    assert cfg.tasks_path.endswith("tasks")
    assert cfg.qmd_collection == "knowledgebase"
    assert cfg.telegram_bot_token == "x"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py::test_load_config_reads_required_fields -v`
Expected: FAIL (module/func not found)

**Step 3: Write minimal implementation**

```python
# src/knowledgebase/config.py
from dataclasses import dataclass
import os


@dataclass
class Config:
    vault_path: str
    tasks_path: str
    qmd_collection: str
    telegram_bot_token: str


def load_config() -> Config:
    return Config(
        vault_path=os.environ["KB_VAULT_PATH"],
        tasks_path=os.environ["KB_TASKS_PATH"],
        qmd_collection=os.environ["KB_QMD_COLLECTION"],
        telegram_bot_token=os.environ["KB_TELEGRAM_BOT_TOKEN"],
    )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py::test_load_config_reads_required_fields -v`
Expected: PASS

**Step 5: Commit**

```bash
git add pyproject.toml src/knowledgebase/__init__.py src/knowledgebase/config.py tests/test_config.py .env.example
git commit -m "feat: add base config"
```

---

## Task 2: File‑based task queue parser

**Files:**
- Create: `src/knowledgebase/queue.py`
- Create: `tests/test_queue.py`

**Step 1: Write the failing test**

```python
# tests/test_queue.py
from knowledgebase.queue import parse_task_line


def test_parse_task_line():
    line = "- [ ] 2026-02-20 https://example.com"
    task = parse_task_line(line)
    assert task["status"] == "pending"
    assert task["date"] == "2026-02-20"
    assert task["url"] == "https://example.com"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_queue.py::test_parse_task_line -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/knowledgebase/queue.py
import re

TASK_RE = re.compile(r"^- \[(?P<status>[^\]]+)\] (?P<date>\d{4}-\d{2}-\d{2}) (?P<url>\S+)")


def parse_task_line(line: str):
    m = TASK_RE.match(line.strip())
    if not m:
        return None
    raw = m.group("status")
    status = "pending" if raw == " " else ("done" if raw == "X" else ("failed" if raw == "F" else "retry"))
    return {"status": status, "date": m.group("date"), "url": m.group("url"), "raw_status": raw}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_queue.py::test_parse_task_line -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/knowledgebase/queue.py tests/test_queue.py
git commit -m "feat: add task queue parser"
```

---

## Task 3: Task file writer (append)

**Files:**
- Modify: `src/knowledgebase/queue.py`
- Create: `tests/test_queue_append.py`

**Step 1: Write the failing test**

```python
# tests/test_queue_append.py
from pathlib import Path
from knowledgebase.queue import append_task


def test_append_task(tmp_path):
    tasks_file = tmp_path / "task-2026-02-20.md"
    append_task(str(tasks_file), "2026-02-20", "https://example.com")
    content = tasks_file.read_text()
    assert "https://example.com" in content
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_queue_append.py::test_append_task -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/knowledgebase/queue.py
from pathlib import Path


def append_task(tasks_file: str, date: str, url: str):
    Path(tasks_file).parent.mkdir(parents=True, exist_ok=True)
    with open(tasks_file, "a", encoding="utf-8") as f:
        f.write(f"- [ ] {date} {url}\n")
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_queue_append.py::test_append_task -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/knowledgebase/queue.py tests/test_queue_append.py
git commit -m "feat: add task file append"
```

---

## Task 4: Task status updater

**Files:**
- Modify: `src/knowledgebase/queue.py`
- Create: `tests/test_queue_update.py`

**Step 1: Write the failing test**

```python
# tests/test_queue_update.py
from knowledgebase.queue import update_task_status


def test_update_task_status(tmp_path):
    f = tmp_path / "task-2026-02-20.md"
    f.write_text("- [ ] 2026-02-20 https://example.com\n")
    update_task_status(str(f), "https://example.com", "X")
    assert "- [X]" in f.read_text()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_queue_update.py::test_update_task_status -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/knowledgebase/queue.py

def update_task_status(tasks_file: str, url: str, new_status: str):
    lines = Path(tasks_file).read_text().splitlines()
    out = []
    for line in lines:
        if url in line:
            out.append(line.replace("- [ ]", f"- [{new_status}]").replace("- [F]", f"- [{new_status}]").replace("- [X]", f"- [{new_status}]") )
        else:
            out.append(line)
    Path(tasks_file).write_text("\n".join(out) + "\n")
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_queue_update.py::test_update_task_status -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/knowledgebase/queue.py tests/test_queue_update.py
git commit -m "feat: add task status update"
```

---

## Task 5: Source type detection

**Files:**
- Create: `src/knowledgebase/detect.py`
- Create: `tests/test_detect.py`

**Step 1: Write the failing test**

```python
# tests/test_detect.py
from knowledgebase.detect import detect_source_type


def test_detect_source_type():
    assert detect_source_type("https://youtu.be/abc") == "youtube"
    assert detect_source_type("https://x.com/user/status/1") == "twitter"
    assert detect_source_type("https://example.com/doc.pdf") == "pdf"
    assert detect_source_type("https://example.com/article") == "article"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_detect.py::test_detect_source_type -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/knowledgebase/detect.py

def detect_source_type(url: str) -> str:
    u = url.lower()
    if "youtu.be" in u or "youtube.com" in u:
        return "youtube"
    if "x.com" in u or "twitter.com" in u:
        return "twitter"
    if u.endswith(".pdf"):
        return "pdf"
    return "article"
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_detect.py::test_detect_source_type -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/knowledgebase/detect.py tests/test_detect.py
git commit -m "feat: add source type detection"
```

---

## Task 6: Obsidian markdown writer

**Files:**
- Create: `src/knowledgebase/obsidian.py`
- Create: `tests/test_obsidian.py`

**Step 1: Write the failing test**

```python
# tests/test_obsidian.py
from knowledgebase.obsidian import write_note


def test_write_note(tmp_path):
    path = write_note(
        vault_path=str(tmp_path),
        source_type="article",
        title="Hello",
        date="2026-02-20",
        content="Body",
        metadata={"source_url": "https://example.com"},
        entities={"people": [], "companies": [], "concepts": []},
    )
    assert path.endswith("article/20260220-hello.md")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_obsidian.py::test_write_note -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/knowledgebase/obsidian.py
from pathlib import Path
import re
import yaml


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "note"


def write_note(vault_path: str, source_type: str, title: str, date: str, content: str, metadata: dict, entities: dict) -> str:
    date_compact = date.replace("-", "")
    fname = f"{date_compact}-{slugify(title)}.md"
    folder = Path(vault_path) / source_type
    folder.mkdir(parents=True, exist_ok=True)
    front = {**metadata, "entities": entities}
    body = f"---\n{yaml.safe_dump(front)}---\n\n# {title}\n\n{content}\n"
    path = folder / fname
    path.write_text(body, encoding="utf-8")
    return str(path)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_obsidian.py::test_write_note -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/knowledgebase/obsidian.py tests/test_obsidian.py
git commit -m "feat: add obsidian markdown writer"
```

---

## Task 7: Entity extraction stub (local model placeholder)

**Files:**
- Create: `src/knowledgebase/entities.py`
- Create: `tests/test_entities.py`

**Step 1: Write the failing test**

```python
# tests/test_entities.py
from knowledgebase.entities import extract_entities


def test_extract_entities():
    text = "Elon Musk founded Tesla"
    entities = extract_entities(text)
    assert "people" in entities
    assert "companies" in entities
    assert "concepts" in entities
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_entities.py::test_extract_entities -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/knowledgebase/entities.py

def extract_entities(text: str) -> dict:
    return {"people": [], "companies": [], "concepts": []}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_entities.py::test_extract_entities -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/knowledgebase/entities.py tests/test_entities.py
git commit -m "feat: add entity extractor stub"
```

---

## Task 8: Ingestion dispatcher (skill‑based fetch)

**Files:**
- Create: `src/knowledgebase/ingest.py`
- Create: `tests/test_ingest_dispatch.py`

**Step 1: Write the failing test**

```python
# tests/test_ingest_dispatch.py
from knowledgebase.ingest import choose_ingestor


def test_choose_ingestor():
    assert choose_ingestor("youtube") == "youtube"
    assert choose_ingestor("twitter") == "twitter"
    assert choose_ingestor("pdf") == "pdf"
    assert choose_ingestor("article") == "article"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_ingest_dispatch.py::test_choose_ingestor -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/knowledgebase/ingest.py

def choose_ingestor(source_type: str) -> str:
    return source_type
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_ingest_dispatch.py::test_choose_ingestor -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/knowledgebase/ingest.py tests/test_ingest_dispatch.py
git commit -m "feat: add ingestion dispatcher"
```

---

## Task 9: Telegram router (enqueue vs query)

**Files:**
- Create: `src/knowledgebase/telegram_bot.py`
- Create: `tests/test_telegram_router.py`

**Step 1: Write the failing test**

```python
# tests/test_telegram_router.py
from knowledgebase.telegram_bot import route_message


def test_route_message_url():
    assert route_message("https://example.com")["action"] == "enqueue"

def test_route_message_query():
    assert route_message("what is rag?")["action"] == "query"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_telegram_router.py::test_route_message_url -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/knowledgebase/telegram_bot.py
import re

URL_RE = re.compile(r"https?://\S+")


def route_message(text: str):
    if URL_RE.search(text):
        return {"action": "enqueue"}
    return {"action": "query"}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_telegram_router.py::test_route_message_url -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/knowledgebase/telegram_bot.py tests/test_telegram_router.py
git commit -m "feat: add telegram routing stub"
```

---

## Task 10: QMD query stub + ranking

**Files:**
- Create: `src/knowledgebase/query.py`
- Create: `tests/test_query_rank.py`

**Step 1: Write the failing test**

```python
# tests/test_query_rank.py
from knowledgebase.query import apply_ranking


def test_apply_ranking():
    hits = [
        {"score": 0.9, "age_days": 1, "source_type": "article"},
        {"score": 0.8, "age_days": 1, "source_type": "twitter"},
    ]
    ranked = apply_ranking(hits)
    assert ranked[0]["source_type"] == "article"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_query_rank.py::test_apply_ranking -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/knowledgebase/query.py
import math

WEIGHTS = {
    "paywalled": 1.5,
    "pdf": 1.3,
    "youtube": 1.2,
    "article": 1.0,
    "twitter": 0.8,
}


def apply_ranking(hits):
    def boost(h):
        w = WEIGHTS.get(h.get("source_type"), 1.0)
        rec = math.exp(-h.get("age_days", 0) / 30)
        return h["score"] * w * rec
    return sorted(hits, key=boost, reverse=True)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_query_rank.py::test_apply_ranking -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/knowledgebase/query.py tests/test_query_rank.py
git commit -m "feat: add ranking stub"
```

---

## Task 11: Daily summary writer

**Files:**
- Create: `src/knowledgebase/summary.py`
- Create: `tests/test_summary.py`

**Step 1: Write the failing test**

```python
# tests/test_summary.py
from knowledgebase.summary import write_daily_summary


def test_write_daily_summary(tmp_path):
    path = write_daily_summary(str(tmp_path), "2026-02-20", "Summary text")
    assert path.endswith("summaries/20260220-summary.md")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_summary.py::test_write_daily_summary -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/knowledgebase/summary.py
from pathlib import Path


def write_daily_summary(vault_path: str, date: str, text: str) -> str:
    folder = Path(vault_path) / "summaries"
    folder.mkdir(parents=True, exist_ok=True)
    fname = f"{date.replace('-', '')}-summary.md"
    path = folder / fname
    path.write_text(text, encoding="utf-8")
    return str(path)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_summary.py::test_write_daily_summary -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/knowledgebase/summary.py tests/test_summary.py
git commit -m "feat: add daily summary writer"
```

---

## Task 12: System service stubs (bot/worker/api)

**Files:**
- Create: `deploy/knowledgebase-bot.service`
- Create: `deploy/knowledgebase-worker.service`
- Create: `deploy/knowledgebase-api.service`
- Create: `tests/test_service_files.py`

**Step 1: Write the failing test**

```python
# tests/test_service_files.py
from pathlib import Path

def test_service_files_exist():
    assert Path("deploy/knowledgebase-bot.service").exists()
    assert Path("deploy/knowledgebase-worker.service").exists()
    assert Path("deploy/knowledgebase-api.service").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_service_files.py::test_service_files_exist -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```
# deploy/knowledgebase-bot.service
[Unit]
Description=Knowledgebase Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/openclaw/.openclaw/workspace/projects/20260220-knowledgebase
ExecStart=/usr/bin/python -m knowledgebase.telegram_bot
Restart=always

[Install]
WantedBy=multi-user.target
```

```
# deploy/knowledgebase-worker.service
[Unit]
Description=Knowledgebase Worker
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/openclaw/.openclaw/workspace/projects/20260220-knowledgebase
ExecStart=/usr/bin/python -m knowledgebase.worker
Restart=always

[Install]
WantedBy=multi-user.target
```

```
# deploy/knowledgebase-api.service
[Unit]
Description=Knowledgebase API
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/openclaw/.openclaw/workspace/projects/20260220-knowledgebase
ExecStart=/usr/bin/python -m knowledgebase.api
Restart=always

[Install]
WantedBy=multi-user.target
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_service_files.py::test_service_files_exist -v`
Expected: PASS

**Step 5: Commit**

```bash
git add deploy/knowledgebase-bot.service deploy/knowledgebase-worker.service deploy/knowledgebase-api.service tests/test_service_files.py
git commit -m "feat: add systemd service files"
```

---

## Execution Handoff

Choose one:
1) **Subagent‑Driven (this session)** — spawn a fresh sub-agent per task, review between tasks.
2) **Parallel Session (separate)** — use executing‑plans skill with checkpoints.
