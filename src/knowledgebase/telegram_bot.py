import re

URL_RE = re.compile(r"https?://\S+")


def route_message(text: str):
    if URL_RE.search(text):
        return {"action": "enqueue"}
    return {"action": "query"}
