from dataclasses import dataclass
import os


@dataclass
class Config:
    vault_path: str
    tasks_path: str
    qmd_collection: str
    telegram_bot_token: str


def load_config() -> Config:
    return Config(
        vault_path=os.environ["KB_VAULT_PATH"],
        tasks_path=os.environ["KB_TASKS_PATH"],
        qmd_collection=os.environ["KB_QMD_COLLECTION"],
        telegram_bot_token=os.environ["KB_TELEGRAM_BOT_TOKEN"],
    )
