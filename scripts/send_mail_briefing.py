from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from briefings.important_mail_briefing import build_important_mail_briefing, mark_important_notified
from mailbot.mail_bot_sender import send_mail_bot_message
from briefings.reply_needed_briefing import build_reply_needed_briefing, mark_reply_briefed
from briefings.schedule_recommendation import build_schedule_recommendation, mark_schedule_recommendation_sent


def main() -> None:
    important_text, important_emails, important_buttons = build_important_mail_briefing(limit=5, unnotified_only=True)
    if important_emails:
        result = send_mail_bot_message(important_text, reply_markup=important_buttons)
        print(result)
        if '전송 완료' in result:
            print(f'IMPORTANT_MARKED={mark_important_notified(important_emails)}')
    else:
        print('IMPORTANT=0')

    reply_text, reply_emails, reply_buttons = build_reply_needed_briefing(limit=5)
    if reply_emails:
        result = send_mail_bot_message(reply_text, reply_markup=reply_buttons)
        print(result)
        if '전송 완료' in result:
            print(f'REPLY_MARKED={mark_reply_briefed(reply_emails)}')
    else:
        print('REPLY=0')

    schedule_text, schedule_emails, schedule_buttons = build_schedule_recommendation(limit=3)
    if schedule_emails:
        result = send_mail_bot_message(schedule_text, reply_markup=schedule_buttons)
        print(result)
        if '전송 완료' in result:
            print(f'SCHEDULE_MARKED={mark_schedule_recommendation_sent(schedule_emails)}')
    else:
        print('SCHEDULE=0')


if __name__ == '__main__':
    main()
