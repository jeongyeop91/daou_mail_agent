from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Intent:
    action: str = 'list'
    keyword: str = ''
    limit: int = 10
    reference_index: int | None = None
    date_filter: str = ''
    important_only: bool = False


def parse_intent(command: str) -> Intent:
    text = command.strip().lower()
    intent = Intent()

    if '답장 필요한 메일' in text or '회신 필요한 메일' in text:
        intent.action = 'reply_briefing'
    elif '브리핑' in text or '요약' in text:
        intent.action = 'summary'
    elif '자세히' in text or '상세' in text or '마지막 메일' in text or '가장 최근 메일' in text:
        intent.action = 'detail'
    elif '답장' in text or '회신' in text:
        intent.action = 'draft'
    else:
        intent.action = 'list'

    if '중요' in text:
        intent.important_only = True
    if '오늘' in text:
        intent.date_filter = 'today'

    match = re.search(r'(\d+)번', text)
    if match:
        intent.reference_index = int(match.group(1))
        if intent.action == 'list':
            intent.action = 'detail'

    count = re.search(r'(\d+)\s*개', text)
    if count:
        intent.limit = int(count.group(1))
    elif '마지막 메일' in text or '가장 최근 메일' in text:
        intent.limit = 1
        intent.reference_index = 1

    for keyword in ['결재', '견적', '보안', '회의', '검토', '요청']:
        if keyword in command:
            intent.keyword = keyword
            break

    return intent
