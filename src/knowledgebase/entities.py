def extract_entities(text: str) -> dict[str, list[str]]:
    """Return extracted entities grouped by type."""
    return {"people": [], "companies": [], "concepts": []}
