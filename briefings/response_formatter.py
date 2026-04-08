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
        '아래 버튼에서 답장 초안 또는 메일 상세 보기를 실행할 수 있습니다.',
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
        '요약',
        f'중요 메일 {sum(1 for e in emails if classify_email(e) == "중요")}건',
        f'결재 메일 {sum(1 for e in emails if categorize_email(e) == "결재")}건',
        f'보안 메일 {sum(1 for e in emails if categorize_email(e) == "보안")}건',
        '',
        '주요 메일',
    ]
    for idx, email in enumerate(emails[:5], start=1):
        lines.append(f'{idx}. [{classify_email(email)}/{categorize_email(email)}] {email.subject}')
        lines.append(f'보낸 사람: {email.sender}')
        lines.append('우선 확인 후 필요 시 상세 보기나 회신 초안 작성으로 이어가실 수 있습니다.')
        lines.append('')
    if lines[-1] == '':
        lines.pop()
    lines.extend(['', '바로 하기', '아래 버튼이나 후속 명령으로 상세 보기 또는 답장 필요 브리핑을 이어갈 수 있습니다.'])
    return '\n'.join(lines)
