from knowledgebase.obsidian import write_note


def test_write_note(tmp_path):
    path = write_note(
        vault_path=str(tmp_path),
        source_type="article",
        title="Hello",
        date="2026-02-20",
        content="Body",
        metadata={"source_url": "https://example.com"},
        entities={"people": [], "companies": [], "concepts": []},
    )
    assert path.endswith("article/20260220-hello.md")
