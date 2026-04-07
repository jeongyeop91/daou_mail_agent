from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from briefings.daily_briefing import build_daily_briefing
from mailbot.mail_bot_sender import send_mail_bot_message


def send_daily_briefing_to_mail_bot() -> str:
    text = build_daily_briefing()
    return send_mail_bot_message(text)


if __name__ == '__main__':
    print(send_daily_briefing_to_mail_bot())
