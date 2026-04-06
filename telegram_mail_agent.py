from __future__ import annotations

import sys

from command_router import run_command
from core.session_store import save_last_results
from intent_parser import parse_intent
from reply_needed_briefing import build_reply_needed_briefing
from response_formatter import format_email_detail, format_email_list, format_summary


def handle_message(message: str) -> str:
    text = message.strip()
    if text in {'마지막 메일이 뭐야?', '가장 최근 메일이 뭐야?', '방금 온 메일 뭐야?'}:
        text = '최근 메일 1개 보여줘'
    if text in {'오늘 업무 브리핑해줘', '오늘 전체 브리핑해줘'}:
        text = '오늘 중요 메일 브리핑해줘'

    intent = parse_intent(text)
    if intent.action == 'reply_briefing':
        return build_reply_needed_briefing(intent.limit)

    result = run_command(intent)
    if isinstance(result, str):
        return result

    if intent.action in {'list', 'summary', 'detail'}:
        save_last_results(text, result)

    if intent.action == 'detail':
        return format_email_detail(result[0]) if result else '메일이 없습니다.'
    if intent.action == 'summary':
        return format_summary(result)
    return format_email_list(result)


def main() -> None:
    if len(sys.argv) < 2:
        print("사용법: python3 telegram_mail_agent.py '마지막 메일이 뭐야?'")
        return
    print(handle_message(' '.join(sys.argv[1:])))


if __name__ == '__main__':
    main()
