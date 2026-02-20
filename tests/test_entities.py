from knowledgebase.entities import extract_entities


def test_extract_entities():
    text = "Elon Musk founded Tesla"
    entities = extract_entities(text)
    assert "people" in entities
    assert "companies" in entities
    assert "concepts" in entities
