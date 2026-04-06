from __future__ import annotations

from agents.advisor import suggest_next_action
from agents.classifier import classify_email
from agents.summarizer import summarize_email
from category_rules import categorize_email
from core.models import EmailItem


def format_email_detail(email: EmailItem) -> str:
    lines = [
        '📮 메일 상세',
        '━━━━━━━━━━',
        f'중요도: {classify_email(email)}',
        f'카테고리: {categorize_email(email)}',
        f'보낸 사람: {email.sender}',
        f'제목: {email.subject}',
        f'수신 시각: {email.date}',
        '',
        '본문',
        email.body.strip() or '본문이 없습니다.',
        '',
        f'권장 조치: {suggest_next_action(email)}',
        '━━━━━━━━━━',
        '바로 하기',
        '1번 메일 답장 초안 써줘',
        '1번 메일 자세히 보여줘',
    ]
    return '\n'.join(lines)


def format_email_list(emails: list[EmailItem]) -> str:
    if not emails:
        return '조건에 맞는 메일이 없습니다.'
    lines = [
        '📮 메일 요약',
        '━━━━━━━━━━',
        f'중요 메일 = {sum(1 for e in emails if classify_email(e) == "중요")}건',
        '',
    ]
    for idx, email in enumerate(emails, start=1):
        lines.append(f'{idx}. [{categorize_email(email)}] {email.subject}')
        lines.append(f'보낸 사람: {email.sender}')
        lines.append(f'요약: {summarize_email(email)}')
        lines.append('')
    return '\n'.join(lines[:-1])


def format_summary(emails: list[EmailItem]) -> str:
    if not emails:
        return '요약할 메일이 없습니다.'
    lines = [
        '📮 메일 브리핑',
        '━━━━━━━━━━',
        f'중요 메일 = {sum(1 for e in emails if classify_email(e) == "중요")}건',
        f'결재 메일 = {sum(1 for e in emails if categorize_email(e) == "결재")}건',
        f'보안 메일 = {sum(1 for e in emails if categorize_email(e) == "보안")}건',
        '',
    ]
    for idx, email in enumerate(emails[:5], start=1):
        lines.append(f'{idx}. [{classify_email(email)}/{categorize_email(email)}] {email.subject}')
        lines.append(f'보낸 사람: {email.sender}')
    lines.extend(['', '바로 하기 = 1번 메일 자세히 보여줘 / 답장 필요한 메일 브리핑해줘'])
    return '\n'.join(lines)
