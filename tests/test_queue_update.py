from knowledgebase.queue import update_task_status


def test_update_task_status(tmp_path):
    f = tmp_path / "task-2026-02-20.md"
    f.write_text("- [ ] 2026-02-20 https://example.com\n")
    update_task_status(str(f), "https://example.com", "X")
    assert "- [X]" in f.read_text()
