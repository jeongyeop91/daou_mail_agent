from __future__ import annotations

import sys

from approval_loop import handle_proposal_action, list_pending_proposals, propose_action
from command_router import run_command
from core.session_store import save_last_results
from intent_parser import parse_intent
from operations_briefing import build_mail_stats, build_mailbot_commands_help, build_proposal_history
from proposal_executor import execute_approved_proposal
from reply_needed_briefing import build_reply_needed_briefing
from response_formatter import format_email_detail, format_email_list, format_summary
from schedule_mail import build_schedule_mail_briefing, propose_email_calendar_cancel, propose_email_calendar_update, propose_email_to_google_calendar, register_email_to_google_calendar


def handle_message(message: str) -> str:
    text = message.strip()
    if text in {'마지막 메일이 뭐야?', '가장 최근 메일이 뭐야?', '방금 온 메일 뭐야?'}:
        text = '최근 메일 1개 보여줘'
    if text in {'오늘 업무 브리핑해줘', '오늘 전체 브리핑해줘'}:
        from workday_briefing import build_workday_briefing
        return build_workday_briefing()
    if text in {'일정 메일 브리핑해줘', '스케줄 메일 브리핑해줘'}:
        return build_schedule_mail_briefing()
    if text in {'메일 제안 보여줘', '메일 대기 제안 보여줘'}:
        return list_pending_proposals()
    if text in {'제안 히스토리 보여줘', '메일 제안 히스토리 보여줘'}:
        return build_proposal_history()
    if text in {'메일 통계 보여줘', '알림 통계 보여줘'}:
        return build_mail_stats()
    if text in {'메일봇 명령 보여줘', '사용 가능한 명령 보여줘', '도움말'}:
        return build_mailbot_commands_help()
    if text.startswith('메일 제안 ') and text.endswith(' 승인'):
        return handle_proposal_action(int(text.removeprefix('메일 제안 ').removesuffix(' 승인').strip()), '승인')
    if text.startswith('메일 제안 ') and text.endswith(' 거절'):
        return handle_proposal_action(int(text.removeprefix('메일 제안 ').removesuffix(' 거절').strip()), '거절')
    if text.startswith('메일 제안 ') and text.endswith(' 실행'):
        return execute_approved_proposal(int(text.removeprefix('메일 제안 ').removesuffix(' 실행').strip()))
    if text in {'오늘 일정 뭐야?', '오늘 일정 보여줘'}:
        from calendar_briefing import build_calendar_briefing
        return build_calendar_briefing('today')
    if text in {'내일 일정 뭐야?', '내일 일정 보여줘'}:
        from calendar_briefing import build_calendar_briefing
        return build_calendar_briefing('tomorrow')
    if text in {'이번 주 일정 뭐야?', '이번 주 일정 보여줘'}:
        from calendar_briefing import build_calendar_briefing
        return build_calendar_briefing('week')
    if text in {'오늘 할 일 뭐야?', '오늘 할 일 보여줘'}:
        from tasks_briefing import build_tasks_briefing
        return build_tasks_briefing('today')
    if text in {'전체 할 일 보여줘', '할 일 브리핑해줘'}:
        from tasks_briefing import build_tasks_briefing
        return build_tasks_briefing('all')
    if text.startswith('할 일 추가해줘 '):
        from task_actions import add_task
        payload = text.removeprefix('할 일 추가해줘 ').strip()
        parts = [p.strip() for p in payload.split('|')]
        return add_task(parts[0], parts[1] if len(parts) > 1 else None, parts[2] if len(parts) > 2 else '')
    if text.startswith('할 일 ') and text.endswith(' 완료해줘'):
        from task_actions import complete_task_by_index
        body = text.removeprefix('할 일 ').removesuffix(' 완료해줘').strip().removesuffix('번')
        return complete_task_by_index(int(body))
    if text.startswith('할 일 ') and ' 미뤄줘' in text:
        from task_actions import postpone_task_by_index
        body = text.removeprefix('할 일 ')
        left, right = body.split(' 미뤄줘', 1)
        return postpone_task_by_index(int(left.strip().removesuffix('번')), right.strip())
    if text.startswith('할 일 ') and text.endswith(' 삭제해줘'):
        from task_actions import delete_task_by_index
        body = text.removeprefix('할 일 ').removesuffix(' 삭제해줘').strip().removesuffix('번')
        return delete_task_by_index(int(body))
    if text.startswith('번 메일 구글일정 등록해줘'):
        return '참조 번호 형식이 올바르지 않습니다.'
    if text.endswith('번 메일 일정등록 제안해줘'):
        import re
        match = re.search(r'(\d+)번 메일 일정등록 제안해줘$', text)
        if match:
            return propose_email_to_google_calendar(int(match.group(1)))
    if text.endswith('번 메일 일정수정 제안해줘'):
        import re
        match = re.search(r'(\d+)번 메일 일정수정 제안해줘$', text)
        if match:
            return propose_email_calendar_update(int(match.group(1)))
    if text.endswith('번 메일 일정취소 제안해줘'):
        import re
        match = re.search(r'(\d+)번 메일 일정취소 제안해줘$', text)
        if match:
            return propose_email_calendar_cancel(int(match.group(1)))
    if text.endswith('번 메일 구글일정 등록해줘'):
        import re
        match = re.search(r'(\d+)번 메일 구글일정 등록해줘$', text)
        if match:
            return register_email_to_google_calendar(int(match.group(1)))
    if text.startswith('일정 등록해줘 '):
        from calendar_actions import create_calendar_event
        parts = [p.strip() for p in text.removeprefix('일정 등록해줘 ').split('|')]
        return create_calendar_event(parts[0], parts[1], parts[2], parts[3] if len(parts) > 3 else '')
    if text.startswith('일정 수정해줘 '):
        from calendar_actions import update_calendar_event, update_calendar_event_by_index
        parts = [p.strip() for p in text.removeprefix('일정 수정해줘 ').split('|')]
        first = parts[0]
        if first.endswith('번'):
            return update_calendar_event_by_index(int(first.removesuffix('번')), parts[1], parts[2], parts[3], parts[4] if len(parts) > 4 else None)
        return update_calendar_event(first, parts[1], parts[2], parts[3], parts[4] if len(parts) > 4 else None)
    if text.startswith('일정 취소해줘 ') or text.startswith('일정 삭제해줘 '):
        from calendar_actions import delete_calendar_event, delete_calendar_event_by_index
        payload = text.removeprefix('일정 취소해줘 ').removeprefix('일정 삭제해줘 ').strip()
        if payload.endswith('번'):
            return delete_calendar_event_by_index(int(payload.removesuffix('번')))
        return delete_calendar_event(payload)

    intent = parse_intent(text)
    if intent.action == 'reply_briefing':
        reply_text, _emails, _buttons = build_reply_needed_briefing(intent.limit)
        return reply_text

    result = run_command(intent)
    if isinstance(result, str):
        return result

    if intent.action == 'draft' and result:
        return str(result)

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
