from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

from briefing_actions import BriefingAction, build_inline_keyboard, build_reply_keyboard
from core.config import load_settings
from mail_bot_sender import answer_mail_bot_callback, send_mail_bot_message
from telegram_mail_agent import handle_message
from workday_briefing import build_workday_briefing, get_workday_next_actions

STATE_PATH = Path(__file__).resolve().parent / 'data' / 'mail_bot_state.json'


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


def _detail_action_buttons(index: int = 1) -> dict:
    return {
        'inline_keyboard': [[
            {'text': '✍️ 답장 초안', 'callback_data': f'cmd:{index}번 메일 답장 초안 써줘'},
            {'text': '📄 원문 보기', 'callback_data': f'cmd:{index}번 메일 자세히 보여줘'},
        ]]
    }


def _detail_suggestion_keyboard(index: int = 1) -> dict:
    actions = [
        BriefingAction('✍️ 답장 초안', f'{index}번 메일 답장 초안 써줘'),
        BriefingAction('📄 원문 보기', f'{index}번 메일 자세히 보여줘'),
        BriefingAction('📮 업무 브리핑', '오늘 업무 브리핑해줘'),
        BriefingAction('✅ 전체 할 일', '전체 할 일 보여줘'),
    ]
    return build_reply_keyboard(actions)


def _extract_detail_index(text: str) -> int | None:
    if '자세히' not in text and '상세' not in text and '마지막 메일' not in text and '최근 메일' not in text:
        return None
    match = re.search(r'(\d+)번', text)
    if match:
        return int(match.group(1))
    return 1


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
            if text in {'오늘 업무 브리핑해줘', '업무 브리핑 보내줘'}:
                html, buttons = _build_workday_html()
                send_mail_bot_message(html, chat_id=chat_id, parse_mode='HTML', reply_markup=buttons)
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
