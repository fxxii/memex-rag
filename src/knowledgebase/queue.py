import re
from pathlib import Path

TASK_RE = re.compile(r"^- \[(?P<status>[^\]]+)\] (?P<date>\d{4}-\d{2}-\d{2}) (?P<url>\S+)")


def parse_task_line(line: str):
    m = TASK_RE.match(line.strip())
    if not m:
        return None
    raw = m.group("status")
    status = "pending" if raw == " " else ("done" if raw == "X" else ("failed" if raw == "F" else "retry"))
    return {"status": status, "date": m.group("date"), "url": m.group("url"), "raw_status": raw}


def append_task(tasks_file: str, date: str, url: str):
    Path(tasks_file).parent.mkdir(parents=True, exist_ok=True)
    with open(tasks_file, "a", encoding="utf-8") as f:
        f.write(f"- [ ] {date} {url}\n")


def update_task_status(tasks_file: str, url: str, new_status: str):
    lines = Path(tasks_file).read_text().splitlines()
    out = []
    for line in lines:
        if url in line:
            out.append(
                line.replace("- [ ]", f"- [{new_status}]")
                .replace("- [F]", f"- [{new_status}]")
                .replace("- [X]", f"- [{new_status}]")
            )
        else:
            out.append(line)
    Path(tasks_file).write_text("\n".join(out) + "\n")
