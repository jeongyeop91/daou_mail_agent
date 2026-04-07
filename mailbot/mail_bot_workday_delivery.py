from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from mailbot.mail_bot_sender import send_mail_bot_message
from briefings.workday_briefing import build_workday_briefing


def send_workday_briefing_to_mail_bot() -> str:
    return send_mail_bot_message(build_workday_briefing())


if __name__ == '__main__':
    print(send_workday_briefing_to_mail_bot())
