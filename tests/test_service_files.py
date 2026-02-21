from pathlib import Path


def test_service_files_exist():
    assert Path("deploy/knowledgebase-bot.service").exists()
    assert Path("deploy/knowledgebase-worker.service").exists()
    assert Path("deploy/knowledgebase-api.service").exists()
