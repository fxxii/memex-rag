import math

WEIGHTS = {
    "paywalled": 1.5,
    "pdf": 1.3,
    "youtube": 1.2,
    "article": 1.0,
    "twitter": 0.8,
}


def apply_ranking(hits):
    def boost(h):
        w = WEIGHTS.get(h.get("source_type"), 1.0)
        rec = math.exp(-h.get("age_days", 0) / 30)
        return h["score"] * w * rec

    return sorted(hits, key=boost, reverse=True)
