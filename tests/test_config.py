from knowledgebase.config import load_config


def test_load_config_reads_required_fields(tmp_path, monkeypatch):
    monkeypatch.setenv("KB_VAULT_PATH", str(tmp_path / "vault"))
    monkeypatch.setenv("KB_TASKS_PATH", str(tmp_path / "tasks"))
    monkeypatch.setenv("KB_QMD_COLLECTION", "knowledgebase")
    monkeypatch.setenv("KB_TELEGRAM_BOT_TOKEN", "x")
    cfg = load_config()
    assert cfg.vault_path.endswith("vault")
    assert cfg.tasks_path.endswith("tasks")
    assert cfg.qmd_collection == "knowledgebase"
    assert cfg.telegram_bot_token == "x"
