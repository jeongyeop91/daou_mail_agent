from __future__ import annotations

from daily_briefing import build_daily_briefing
from mailbot.mail_bot_sender import send_mail_bot_message


def send_daily_briefing_to_mail_bot() -> str:
    text = build_daily_briefing()
    return send_mail_bot_message(text)


if __name__ == '__main__':
    print(send_daily_briefing_to_mail_bot())
