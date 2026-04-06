from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

from core.config import load_settings


def send_mail_bot_message(text: str, chat_id: str | None = None, parse_mode: str | None = None) -> str:
    settings = load_settings()
    token = settings.telegram_mail_bot_token
    chat_id = chat_id or settings.telegram_mail_bot_chat_id
    if not token or not chat_id:
        return '메일 봇 토큰 또는 chat_id가 설정되지 않았습니다.'
    body = {'chat_id': chat_id, 'text': text}
    if parse_mode:
        body['parse_mode'] = parse_mode
    payload = urllib.parse.urlencode(body).encode('utf-8')
    req = urllib.request.Request(f'https://api.telegram.org/bot{token}/sendMessage', data=payload, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return f'메일 봇 메시지 전송 실패: HTTP {e.code}'
    except Exception as e:
        return f'메일 봇 메시지 전송 실패: {type(e).__name__}'
    if not data.get('ok'):
        return f"메일 봇 메시지 전송 실패: {data.get('description', 'unknown error')}"
    return f"메일 봇 메시지 전송 완료: message_id={data.get('result', {}).get('message_id')}"
