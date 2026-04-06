from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from core.proposals import list_proposals
from mail_cache import _connect, init_mail_cache
from proposal_executor import _load_execs


def build_proposal_history(limit: int = 10) -> str:
    proposals = list_proposals()
    executions = _load_execs()
    if not proposals and not executions:
        return '제안 이력이 없습니다.'
    lines = ['🧾 제안 히스토리', '━━━━━━━━━━', f'전체 제안 = {len(proposals)}건', '']
    for item in sorted(proposals, key=lambda x: x.get('id', 0), reverse=True)[:limit]:
        lines.append(f"#{item.get('id')} [{item.get('status')}] {item.get('title')}")
        lines.append(f"생성: {item.get('created_at', '-')}")
        if item.get('updated_at'):
            lines.append(f"변경: {item.get('updated_at')}")
        lines.append('')
    if executions:
        lines.append('최근 실행')
        for item in executions[-5:]:
            lines.append(f"- #{item.get('proposal_id')} {item.get('title')}")
            lines.append(f"  결과: {item.get('result')}")
    return '\n'.join(lines[:-1] if lines and lines[-1] == '' else lines)


def build_mail_stats() -> str:
    init_mail_cache()
    with _connect() as conn:
        total = conn.execute('SELECT COUNT(*) AS c FROM messages').fetchone()['c']
        important = conn.execute('SELECT COUNT(*) AS c FROM messages WHERE is_important = 1').fetchone()['c']
        reply_needed = conn.execute('SELECT COUNT(*) AS c FROM messages WHERE needs_reply = 1').fetchone()['c']
        notified = conn.execute('SELECT COUNT(*) AS c FROM messages WHERE notified_at IS NOT NULL').fetchone()['c']
        briefed = conn.execute('SELECT COUNT(*) AS c FROM messages WHERE briefed_at IS NOT NULL').fetchone()['c']
        proposed = conn.execute('SELECT COUNT(*) AS c FROM messages WHERE schedule_proposed_at IS NOT NULL').fetchone()['c']
        categories = conn.execute('SELECT classification, COUNT(*) AS c FROM messages GROUP BY classification').fetchall()
    lines = [
        '📊 메일/알림 통계',
        '━━━━━━━━━━',
        f'- 캐시 메일: {total}건',
        f'- 중요 메일: {important}건',
        f'- 답장 필요: {reply_needed}건',
        f'- 알림 완료: {notified}건',
        f'- 브리핑 완료: {briefed}건',
        f'- 일정 추천 완료: {proposed}건',
        '',
        '분류별 현황',
    ]
    for row in categories:
        lines.append(f"- {row['classification'] or '미분류'}: {row['c']}건")
    return '\n'.join(lines)


def build_mailbot_commands_help() -> str:
    return '\n'.join([
        '🤖 메일봇 사용 명령',
        '━━━━━━━━━━',
        '메일 조회',
        '- 최근 메일 5개 보여줘',
        '- 3번 메일 자세히 보여줘',
        '- 답장 필요한 메일 브리핑해줘',
        '',
        '업무 브리핑',
        '- 오늘 업무 브리핑해줘',
        '- 오늘 일정 뭐야?',
        '- 전체 할 일 보여줘',
        '',
        '일정 메일',
        '- 일정 메일 브리핑해줘',
        '- 1번 메일 일정등록 제안해줘',
        '- 메일 제안 보여줘',
        '- 메일 제안 n 승인',
        '- 메일 제안 n 실행',
        '',
        '운영 조회',
        '- 제안 히스토리 보여줘',
        '- 메일 통계 보여줘',
        '- 메일봇 명령 보여줘',
    ])
