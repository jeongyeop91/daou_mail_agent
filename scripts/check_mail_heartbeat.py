from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agents.collector import fetch_recent_emails
from briefings.important_mail_briefing import build_important_mail_briefing
from mailbot.mail_bot_sender import send_mail_bot_message
from storage.mail_cache import mark_notified

POLL_MINUTES = 10


def main() -> None:
    fetched = fetch_recent_emails(limit=10)
    print(f'FETCHED={len(fetched)}')
    text, emails = build_important_mail_briefing(limit=5, unnotified_only=True)
    if not emails:
        print('NOTIFY=0')
        print(text)
        return
    result = send_mail_bot_message(text)
    print(result)
    marked = 0
    if '전송 완료' in result:
        marked = mark_notified(emails)
    print(f'NOTIFY={len(emails)}')
    print(f'MARKED={marked}')
    print(f'INTERVAL_MINUTES={POLL_MINUTES}')


if __name__ == '__main__':
    main()
