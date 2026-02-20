import re

TASK_RE = re.compile(r"^- \[(?P<status>[^\]]+)\] (?P<date>\d{4}-\d{2}-\d{2}) (?P<url>\S+)")


def parse_task_line(line: str):
    m = TASK_RE.match(line.strip())
    if not m:
        return None
    raw = m.group("status")
    status = "pending" if raw == " " else ("done" if raw == "X" else ("failed" if raw == "F" else "retry"))
    return {"status": status, "date": m.group("date"), "url": m.group("url"), "raw_status": raw}
