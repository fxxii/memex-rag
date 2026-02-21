from pathlib import Path


def write_daily_summary(vault_path: str, date: str, text: str) -> str:
    folder = Path(vault_path) / "summaries"
    folder.mkdir(parents=True, exist_ok=True)
    fname = f"{date.replace('-', '')}-summary.md"
    path = folder / fname
    path.write_text(text, encoding="utf-8")
    return str(path)
