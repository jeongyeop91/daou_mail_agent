from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_env_file() -> dict[str, str]:
    env_path = Path(__file__).resolve().parent.parent / '.env'
    values: dict[str, str] = {}
    if not env_path.exists():
        return values
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        values[k.strip()] = v.strip().strip('"').strip("'")
    return values


@dataclass
class Settings:
    imap_host: str = ''
    imap_port: int = 993
    email_address: str = ''
    email_password: str = ''
    telegram_mail_bot_token: str = ''
    telegram_mail_bot_chat_id: str = ''


def load_settings() -> Settings:
    env = _load_env_file()
    return Settings(
        imap_host=env.get('IMAP_HOST') or os.getenv('IMAP_HOST', ''),
        imap_port=int(env.get('IMAP_PORT') or os.getenv('IMAP_PORT', '993')),
        email_address=env.get('EMAIL_ADDRESS') or os.getenv('EMAIL_ADDRESS', ''),
        email_password=env.get('EMAIL_PASSWORD') or os.getenv('EMAIL_PASSWORD', ''),
        telegram_mail_bot_token=env.get('TELEGRAM_MAIL_BOT_TOKEN') or os.getenv('TELEGRAM_MAIL_BOT_TOKEN', ''),
        telegram_mail_bot_chat_id=env.get('TELEGRAM_MAIL_BOT_CHAT_ID') or os.getenv('TELEGRAM_MAIL_BOT_CHAT_ID', ''),
    )
