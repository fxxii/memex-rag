from pathlib import Path
import re
import yaml


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "note"


def write_note(
    vault_path: str,
    source_type: str,
    title: str,
    date: str,
    content: str,
    metadata: dict,
    entities: dict,
) -> str:
    date_compact = date.replace("-", "")
    fname = f"{date_compact}-{slugify(title)}.md"
    folder = Path(vault_path) / source_type
    folder.mkdir(parents=True, exist_ok=True)
    front = {**metadata, "entities": entities}
    body = f"---\n{yaml.safe_dump(front)}---\n\n# {title}\n\n{content}\n"
    path = folder / fname
    path.write_text(body, encoding="utf-8")
    return str(path)
