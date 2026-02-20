from knowledgebase.queue import parse_task_line


def test_parse_task_line():
    line = "- [ ] 2026-02-20 https://example.com"
    task = parse_task_line(line)
    assert task["status"] == "pending"
    assert task["date"] == "2026-02-20"
    assert task["url"] == "https://example.com"
