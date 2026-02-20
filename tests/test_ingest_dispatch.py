from knowledgebase.ingest import choose_ingestor


def test_choose_ingestor():
    assert choose_ingestor("youtube") == "youtube"
    assert choose_ingestor("twitter") == "twitter"
    assert choose_ingestor("pdf") == "pdf"
    assert choose_ingestor("article") == "article"
