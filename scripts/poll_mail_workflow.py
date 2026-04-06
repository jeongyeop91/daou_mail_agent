from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agents.collector import fetch_recent_emails
from important_mail_briefing import build_important_mail_briefing, mark_important_notified
from mail_bot_sender import send_mail_bot_message
from mail_cache import purge_old_cache
from reply_needed_briefing import build_reply_needed_briefing, mark_reply_briefed
from schedule_recommendation import build_schedule_recommendation, mark_schedule_recommendation_sent

POLL_MINUTES = 30
RETENTION_DAYS = 180


def main() -> None:
    purged = purge_old_cache(RETENTION_DAYS)
    print(f'PURGED={purged}')
    fetched = fetch_recent_emails(limit=10)
    print(f'FETCHED={len(fetched)}')

    important_text, important_emails, important_buttons = build_important_mail_briefing(limit=5, unnotified_only=True)
    if important_emails:
        important_result = send_mail_bot_message(important_text, reply_markup=important_buttons)
        print(important_result)
        marked = 0
        if '전송 완료' in important_result:
            marked = mark_important_notified(important_emails)
        print(f'IMPORTANT_NOTIFY={len(important_emails)}')
        print(f'IMPORTANT_MARKED={marked}')
    else:
        print('IMPORTANT_NOTIFY=0')
        print(important_text)

    reply_text, reply_emails, reply_buttons = build_reply_needed_briefing(limit=5)
    if reply_emails:
        reply_result = send_mail_bot_message(reply_text, reply_markup=reply_buttons)
        print(reply_result)
        marked = 0
        if '전송 완료' in reply_result:
            marked = mark_reply_briefed(reply_emails)
        print('REPLY_BRIEFED=1')
        print(f'REPLY_MARKED={marked}')
    else:
        print('REPLY_BRIEFED=0')
        print(reply_text)

    schedule_text, schedule_emails, schedule_buttons = build_schedule_recommendation(limit=3)
    if schedule_emails:
        schedule_result = send_mail_bot_message(schedule_text, reply_markup=schedule_buttons)
        print(schedule_result)
        marked = 0
        if '전송 완료' in schedule_result:
            marked = mark_schedule_recommendation_sent(schedule_emails)
        print('SCHEDULE_RECOMMENDED=1')
        print(f'SCHEDULE_MARKED={marked}')
    else:
        print('SCHEDULE_RECOMMENDED=0')
        print(schedule_text)

    print(f'INTERVAL_MINUTES={POLL_MINUTES}')
    print(f'RETENTION_DAYS={RETENTION_DAYS}')


if __name__ == '__main__':
    main()
