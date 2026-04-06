from __future__ import annotations

from mail_bot_sender import send_mail_bot_message
from workday_briefing import build_workday_briefing


def send_workday_briefing_to_mail_bot() -> str:
    return send_mail_bot_message(build_workday_briefing())


if __name__ == '__main__':
    print(send_workday_briefing_to_mail_bot())
