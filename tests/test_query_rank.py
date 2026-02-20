from knowledgebase.query import apply_ranking


def test_apply_ranking():
    hits = [
        {"score": 0.9, "age_days": 1, "source_type": "article"},
        {"score": 0.8, "age_days": 1, "source_type": "twitter"},
    ]
    ranked = apply_ranking(hits)
    assert ranked[0]["source_type"] == "article"
