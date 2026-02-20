from pathlib import Path
from knowledgebase.queue import append_task


def test_append_task(tmp_path):
    tasks_file = tmp_path / "task-2026-02-20.md"
    append_task(str(tasks_file), "2026-02-20", "https://example.com")
    content = tasks_file.read_text()
    assert content == "- [ ] 2026-02-20 https://example.com\n"
