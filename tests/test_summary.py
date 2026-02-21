from pathlib import Path
from knowledgebase.summary import write_daily_summary


def test_write_daily_summary(tmp_path):
    path = write_daily_summary(str(tmp_path), "2026-02-20", "Summary text")
    assert path.endswith("summaries/20260220-summary.md")
    assert Path(path).read_text(encoding="utf-8") == "Summary text"
