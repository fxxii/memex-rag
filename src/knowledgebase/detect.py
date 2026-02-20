def detect_source_type(url: str) -> str:
    u = url.lower()
    if "youtu.be" in u or "youtube.com" in u:
        return "youtube"
    if "x.com" in u or "twitter.com" in u:
        return "twitter"
    if u.endswith(".pdf"):
        return "pdf"
    return "article"
