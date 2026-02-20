from knowledgebase.telegram_bot import route_message


def test_route_message_url():
    assert route_message("https://example.com")["action"] == "enqueue"


def test_route_message_query():
    assert route_message("what is rag?")["action"] == "query"
