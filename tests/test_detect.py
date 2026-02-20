from knowledgebase.detect import detect_source_type


def test_detect_source_type():
    assert detect_source_type("https://youtu.be/abc") == "youtube"
    assert detect_source_type("https://x.com/user/status/1") == "twitter"
    assert detect_source_type("https://example.com/doc.pdf") == "pdf"
    assert detect_source_type("https://example.com/article") == "article"
