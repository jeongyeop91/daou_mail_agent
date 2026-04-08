from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

from briefing_actions import BriefingAction, build_inline_keyboard
from agents.drafter import draft_reply
from briefings.operations_briefing import build_mailbot_commands_help
from briefings.response_formatter import format_email_detail
from core.config import load_settings
from core.models import EmailItem
from core.session_store import get_email_by_index, get_email_by_token, save_button_target
from mailbot.mail_bot_sender import answer_mail_bot_callback, send_mail_bot_message
from schedule_mail import extract_schedule_candidate, propose_schedule_cancel_for_email, propose_schedule_create_for_email, propose_schedule_update_for_email
from telegram_mail_agent import handle_message
from briefings.workday_briefing import build_workday_briefing, get_workday_next_actions

STATE_PATH = Path(__file__).resolve().parent.parent / 'data' / 'mail_bot_state.json'


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {'last_update_id': None}
    try:
        return json.loads(STATE_PATH.read_text())
    except Exception:
        return {'last_update_id': None}


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def _fetch_updates(offset: int | None = None) -> list[dict]:
    settings = load_settings()
    token = settings.telegram_mail_bot_token
    if not token:
        raise RuntimeError('메일 봇 토큰이 설정되지 않았습니다.')
    url = f'https://api.telegram.org/bot{token}/getUpdates'
    if offset is not None:
        url += f'?offset={offset}'
    with urllib.request.urlopen(url, timeout=20) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    return data.get('result', []) if data.get('ok') else []


def _load_email(index: int) -> EmailItem | None:
    saved = get_email_by_index(index)
    if not saved:
        return None
    return EmailItem(**saved)


def _detail_action_buttons(index: int = 1) -> dict:
    email = _load_email(index)
    if not email:
        actions = [
            BriefingAction('✍️ 답장 초안', f'{index}번 메일 답장 초안 써줘'),
            BriefingAction('📄 원문 보기', f'{index}번 메일 자세히 보여줘'),
            BriefingAction('📮 업무 브리핑', '오늘 업무 브리핑해줘'),
        ]
        return build_inline_keyboard(actions, row_size=2)

    token = save_button_target(email)
    actions = [
        BriefingAction('✍️ 답장 초안', f'@mailtoken:{token}:draft'),
        BriefingAction('📄 원문 보기', f'@mailtoken:{token}:detail'),
    ]
    schedule_candidate = extract_schedule_candidate(email)
    if schedule_candidate:
        if schedule_candidate.action == 'create':
            actions.append(BriefingAction('📅 일정 제안', f'@mailtoken:{token}:schedule_create'))
        elif schedule_candidate.action == 'update':
            actions.append(BriefingAction('🛠 일정 수정 제안', f'@mailtoken:{token}:schedule_update'))
        elif schedule_candidate.action == 'cancel':
            actions.append(BriefingAction('🗑 일정 취소 제안', f'@mailtoken:{token}:schedule_cancel'))
    actions.append(BriefingAction('📮 업무 브리핑', '오늘 업무 브리핑해줘'))
    return build_inline_keyboard(actions, row_size=2)


def _handle_mail_token_command(command: str) -> tuple[str, dict | None]:
    if not command.startswith('@mailtoken:'):
        return handle_message(command), None
    try:
        _, token, action = command.split(':', 2)
    except ValueError:
        return '메일 버튼 정보를 해석하지 못했습니다.', None
    saved = get_email_by_token(token)
    if not saved:
        return '참조할 메일을 찾지 못했습니다. 다시 목록에서 선택해 주세요.', None
    email = EmailItem(**saved)
    if action == 'detail':
        return format_email_detail(email), build_inline_keyboard([
            BriefingAction('✍️ 답장 초안', f'@mailtoken:{token}:draft'),
            BriefingAction('📄 원문 보기', f'@mailtoken:{token}:detail'),
            BriefingAction('📮 업무 브리핑', '오늘 업무 브리핑해줘'),
        ], row_size=2)
    if action == 'draft':
        return draft_reply(email), build_inline_keyboard([
            BriefingAction('📄 원문 보기', f'@mailtoken:{token}:detail'),
            BriefingAction('📮 업무 브리핑', '오늘 업무 브리핑해줘'),
        ], row_size=2)
    if action == 'schedule_create':
        return propose_schedule_create_for_email(email), None
    if action == 'schedule_update':
        return propose_schedule_update_for_email(email), None
    if action == 'schedule_cancel':
        return propose_schedule_cancel_for_email(email), None
    return '지원하지 않는 메일 버튼 동작입니다.', None


def _extract_detail_index(text: str) -> int | None:
    if '자세히' not in text and '상세' not in text and '마지막 메일' not in text and '최근 메일' not in text:
        return None
    match = re.search(r'(\d+)번', text)
    if match:
        return int(match.group(1))
    return 1


def _build_main_menu() -> tuple[str, dict]:
    text = '\n'.join([
        '🤖 메일봇 메뉴',
        '━━━━━━━━━━',
        '자주 쓰는 기능을 아래 버튼으로 바로 실행할 수 있습니다.',
        '',
        '구성',
        '- 메일 조회',
        '- 업무 브리핑',
        '- 일정 메일',
        '- 운영 조회',
    ])
    buttons = build_inline_keyboard([
        BriefingAction('📮 최근 메일', '최근 메일 5개 보여줘'),
        BriefingAction('📄 메일 상세', '1번 메일 자세히 보여줘'),
        BriefingAction('🧭 업무 브리핑', '오늘 업무 브리핑해줘'),
        BriefingAction('📅 일정 메일', '일정 메일 브리핑해줘'),
        BriefingAction('📊 메일 통계', '메일 통계 보여줘'),
        BriefingAction('🧾 제안 히스토리', '제안 히스토리 보여줘'),
    ], row_size=2)
    return text, buttons


def _build_workday_html() -> tuple[str, dict]:
    text = build_workday_briefing()
    actions = get_workday_next_actions(
        has_important_mail='🔴 중요 메일 0건' not in text,
        has_events='🔵 오늘 일정 0건' not in text,
        has_tasks='🟡 오늘 할 일 0건' not in text,
    )
    html = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '\n')
    html = html.replace('📮 오늘 업무 브리핑', '<b>📮 오늘 업무 브리핑</b>')
    html = html.replace('한눈 요약', '<b>한눈 요약</b>')
    html = html.replace('현재 상태', '<b>현재 상태</b>')
    html = html.replace('우선 확인 메일', '<b>우선 확인 메일</b>')
    html = html.replace('오늘 일정', '<b>오늘 일정</b>')
    html = html.replace('오늘 할 일', '<b>오늘 할 일</b>')
    html = html.replace('권장 다음 액션', '<b>권장 다음 액션</b>')
    html = html.replace('━━━━━━━━━━', '━━━━━━━━━━')
    html = html.replace('\n', '\n')
    inline = build_inline_keyboard(actions)
    return html, inline


def process_mail_bot_updates() -> str:
    state = _load_state()
    offset = (state.get('last_update_id') + 1) if isinstance(state.get('last_update_id'), int) else None
    updates = _fetch_updates(offset)
    if not updates:
        return '새 메일 봇 메시지가 없습니다.'
    handled = 0
    for item in updates:
        update_id = item.get('update_id')
        callback = item.get('callback_query') or {}
        if callback:
            data = (callback.get('data') or '').strip()
            chat_id = str(((callback.get('message') or {}).get('chat') or {}).get('id') or '')
            if data.startswith('cmd:') and chat_id:
                command = data.removeprefix('cmd:').strip()
                if command.startswith('@mailtoken:'):
                    reply, buttons = _handle_mail_token_command(command)
                    send_mail_bot_message(reply, chat_id=chat_id, reply_markup=buttons)
                else:
                    reply = handle_message(command)
                    idx = _extract_detail_index(command)
                    if idx is not None:
                        send_mail_bot_message(reply, chat_id=chat_id, reply_markup=_detail_action_buttons(idx))
                    else:
                        send_mail_bot_message(reply, chat_id=chat_id)
                answer_mail_bot_callback(callback.get('id'), '실행했습니다')
                handled += 1
            state['last_update_id'] = update_id
            continue

        msg = item.get('message') or {}
        text = (msg.get('text') or '').strip()
        chat_id = str((msg.get('chat') or {}).get('id') or '')
        if text and chat_id:
            if text in {'/menu', '메뉴 보여줘', '메일봇 메뉴 보여줘'}:
                menu_text, menu_buttons = _build_main_menu()
                send_mail_bot_message(menu_text, chat_id=chat_id, reply_markup=menu_buttons)
                handled += 1
            elif text in {'오늘 업무 브리핑해줘', '업무 브리핑 보내줘'}:
                html, buttons = _build_workday_html()
                send_mail_bot_message(html, chat_id=chat_id, parse_mode='HTML', reply_markup=buttons)
                handled += 1
            elif text in {'도움말', '메일봇 명령 보여줘'}:
                help_text = build_mailbot_commands_help()
                menu_text, menu_buttons = _build_main_menu()
                send_mail_bot_message(help_text, chat_id=chat_id)
                send_mail_bot_message(menu_text, chat_id=chat_id, reply_markup=menu_buttons)
                handled += 1
            else:
                reply = handle_message(text)
                idx = _extract_detail_index(text)
                if idx is not None:
                    send_mail_bot_message(reply, chat_id=chat_id, reply_markup=_detail_action_buttons(idx))
                else:
                    send_mail_bot_message(reply, chat_id=chat_id)
                handled += 1
        state['last_update_id'] = update_id
    _save_state(state)
    return f'메일 봇 메시지 처리 완료: {handled}건'


if __name__ == '__main__':
    print(process_mail_bot_updates())
