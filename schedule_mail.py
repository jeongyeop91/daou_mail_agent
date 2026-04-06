from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from agents.collector import fetch_recent_emails
from proposals.approval_loop import propose_action
from core.models import EmailItem
from core.session_store import get_email_by_index, save_last_results

CALENDAR_ID = 'primary'
DEFAULT_DURATION_MINUTES = 60
KST = timezone(timedelta(hours=9))


@dataclass
class ScheduleCandidate:
    title: str
    start_at: datetime
    end_at: datetime
    description: str
    location: str
    source_email: EmailItem
    action: str = 'create'


def _extract_datetime(text: str) -> datetime | None:
    patterns = [
        r'(20\d{2}-\d{2}-\d{2})\s*\([^)]*\)?\s*(\d{1,2}:\d{2})',
        r'(20\d{2}[./-]\d{1,2}[./-]\d{1,2})\s*(\d{1,2}:\d{2})',
        r'(\d{1,2})/(\d{1,2})\s*(\d{1,2})시',
        r'(\d{1,2})월\s*(\d{1,2})일\s*(\d{1,2})시(?:\s*(\d{1,2})분)?',
    ]
    now = datetime.now()
    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue
        try:
            if len(match.groups()) == 2:
                date_part = match.group(1).replace('.', '-').replace('/', '-')
                time_part = match.group(2)
                return datetime.fromisoformat(f'{date_part} {time_part}')
            if pattern.startswith(r'(\d{1,2})/(\d{1,2})'):
                month, day, hour = map(int, match.groups())
                return datetime(now.year, month, day, hour, 0)
            month, day, hour, minute = match.groups()
            return datetime(now.year, int(month), int(day), int(hour), int(minute or 0))
        except Exception:
            continue
    return None


def _extract_title(subject: str) -> str:
    title = re.sub(r'^\s*(re:|fwd:)\s*', '', subject, flags=re.IGNORECASE)
    title = re.sub(r'\[일정등록\]\s*', '', title)
    title = re.sub(r'\[[^\]]+\]\s*', '', title)
    title = re.sub(r'\(20\d{2}-\d{2}-\d{2}[^)]*\)', '', title)
    title = re.sub(r'\(\d{1,2}/\d{1,2}[^)]*\)', '', title)
    title = re.sub(r'\b\d{1,2}:\d{2}\)?$', '', title)
    title = re.sub(r'\s{2,}', ' ', title)
    return title.strip(' -') or subject.strip()


def _extract_location(text: str) -> str:
    patterns = [
        r'(?:장소|위치)\s*[:：]\s*([^\n<]+)',
        r'(Conference Room[^\n<]*)',
        r'(서울사옥[^\n<]*)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ''


def _detect_schedule_action(email: EmailItem) -> str:
    text = f'{email.subject} {email.body}'.lower()
    if any(token in text for token in ['취소', '삭제', 'cancel']):
        return 'cancel'
    if any(token in text for token in ['변경', '수정', '연기', 'reschedule', 'update']):
        return 'update'
    return 'create'


def extract_schedule_candidate(email: EmailItem) -> ScheduleCandidate | None:
    text = f'{email.subject}\n{email.body}'
    if not any(token in text for token in ['일정', '미팅', '회의', '면담', '방문']):
        return None
    start_at = _extract_datetime(email.subject) or _extract_datetime(email.body)
    if not start_at:
        return None
    title = _extract_title(email.subject)
    description = (email.body or '').strip()[:2000]
    location = _extract_location(email.body or '')
    if start_at.tzinfo is None:
        start_at = start_at.replace(tzinfo=KST)
    end_at = start_at + timedelta(minutes=DEFAULT_DURATION_MINUTES)
    return ScheduleCandidate(title=title, start_at=start_at, end_at=end_at, description=description, location=location, source_email=email, action=_detect_schedule_action(email))


def list_schedule_candidate_emails(limit: int = 10) -> list[EmailItem]:
    emails = fetch_recent_emails(limit=max(limit, 10))
    candidates = [email for email in emails if extract_schedule_candidate(email)]
    save_last_results('일정 메일 브리핑해줘', candidates[:limit])
    return candidates[:limit]


def build_schedule_mail_briefing(limit: int = 10) -> str:
    emails = list_schedule_candidate_emails(limit)
    if not emails:
        return '일정으로 등록할 만한 메일이 없습니다.'
    lines = ['📅 일정 메일 브리핑', '━━━━━━━━━━', f'일정 후보 = {len(emails)}건', '']
    for idx, email in enumerate(emails, start=1):
        candidate = extract_schedule_candidate(email)
        if not candidate:
            continue
        action_label = {'create': '등록', 'update': '수정', 'cancel': '취소'}.get(candidate.action, '등록')
        lines.append(f'{idx}. [{action_label}] {candidate.title}')
        lines.append(f'일정: {candidate.start_at.strftime("%Y-%m-%d %H:%M")} ~ {candidate.end_at.strftime("%H:%M")}')
        if candidate.location:
            lines.append(f'장소: {candidate.location}')
        lines.append(f'보낸 사람: {email.sender}')
        if candidate.action == 'update':
            lines.append(f'바로 하기: {idx}번 메일 일정수정 제안해줘')
        elif candidate.action == 'cancel':
            lines.append(f'바로 하기: {idx}번 메일 일정취소 제안해줘')
        else:
            lines.append(f'바로 하기: {idx}번 메일 일정등록 제안해줘')
        lines.append('')
    return '\n'.join(lines[:-1])


def _find_matching_event(candidate: ScheduleCandidate) -> dict | None:
    cmd = [
        'gog', 'calendar', 'events', CALENDAR_ID,
        '--from', (candidate.start_at - timedelta(days=1)).isoformat(),
        '--to', (candidate.end_at + timedelta(days=1)).isoformat(),
        '--json',
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads((result.stdout or '').strip() or '{}')
        events = data.get('events', []) if isinstance(data, dict) else []
    except Exception:
        return None
    normalized = candidate.title.strip().lower()
    for event in events:
        summary = str(event.get('summary', '')).strip().lower()
        if normalized and (summary == normalized or normalized in summary or summary in normalized):
            return event
    return None


def _find_duplicate_event(candidate: ScheduleCandidate) -> bool:
    return _find_matching_event(candidate) is not None


def propose_email_to_google_calendar(index: int) -> str:
    saved = get_email_by_index(index)
    if not saved:
        return '참조할 일정 메일을 찾지 못했습니다. 먼저 일정 메일 브리핑을 조회해 주세요.'
    email = EmailItem(**saved)
    candidate = extract_schedule_candidate(email)
    if not candidate:
        return '해당 메일에서 일정 정보를 추출하지 못했습니다.'
    if candidate.action != 'create':
        return '신규 일정 등록 메일이 아닙니다. 수정/취소 전용 제안을 사용해 주세요.'
    if _find_duplicate_event(candidate):
        return '같은 제목과 시간대의 일정이 이미 구글 캘린더에 있어 등록을 보류했습니다.'
    payload = {
        'kind': 'calendar_register',
        'title': candidate.title,
        'start_at': candidate.start_at.isoformat(),
        'end_at': candidate.end_at.isoformat(),
        'description': candidate.description,
        'location': candidate.location,
    }
    return propose_action(f'구글 일정 등록: {candidate.title}', payload)


def propose_email_calendar_update(index: int) -> str:
    saved = get_email_by_index(index)
    if not saved:
        return '참조할 일정 메일을 찾지 못했습니다. 먼저 일정 메일 브리핑을 조회해 주세요.'
    email = EmailItem(**saved)
    candidate = extract_schedule_candidate(email)
    if not candidate:
        return '해당 메일에서 일정 정보를 추출하지 못했습니다.'
    event = _find_matching_event(candidate)
    if not event:
        return '수정할 기존 구글 일정을 찾지 못했습니다.'
    payload = {
        'kind': 'calendar_update',
        'event_id': event.get('id'),
        'title': candidate.title,
        'start_at': candidate.start_at.isoformat(),
        'end_at': candidate.end_at.isoformat(),
        'description': candidate.description,
        'location': candidate.location,
    }
    return propose_action(f'구글 일정 수정: {candidate.title}', payload)


def propose_email_calendar_cancel(index: int) -> str:
    saved = get_email_by_index(index)
    if not saved:
        return '참조할 일정 메일을 찾지 못했습니다. 먼저 일정 메일 브리핑을 조회해 주세요.'
    email = EmailItem(**saved)
    candidate = extract_schedule_candidate(email)
    if not candidate:
        return '해당 메일에서 일정 정보를 추출하지 못했습니다.'
    event = _find_matching_event(candidate)
    if not event:
        return '취소할 기존 구글 일정을 찾지 못했습니다.'
    payload = {
        'kind': 'calendar_cancel',
        'event_id': event.get('id'),
        'title': candidate.title,
    }
    return propose_action(f'구글 일정 취소: {candidate.title}', payload)


def register_email_to_google_calendar(index: int) -> str:
    saved = get_email_by_index(index)
    if not saved:
        return '참조할 일정 메일을 찾지 못했습니다. 먼저 일정 메일 브리핑을 조회해 주세요.'
    email = EmailItem(**saved)
    candidate = extract_schedule_candidate(email)
    if not candidate:
        return '해당 메일에서 일정 정보를 추출하지 못했습니다.'

    cmd = [
        'gog', 'calendar', 'create', CALENDAR_ID,
        '--summary', candidate.title,
        '--from', candidate.start_at.isoformat(),
        '--to', candidate.end_at.isoformat(),
    ]
    if candidate.description:
        cmd.extend(['--description', candidate.description])
    if candidate.location:
        cmd.extend(['--location', candidate.location])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        message = (e.stderr or e.stdout or '').strip()
        return f'구글 일정 등록에 실패했습니다: {message or e.returncode}'

    raw = (result.stdout or '').strip()
    event_id = ''
    try:
        parsed = json.loads(raw) if raw.startswith('{') else {}
        event_id = parsed.get('id', '') if isinstance(parsed, dict) else ''
    except Exception:
        event_id = ''
    return (
        '구글 일정에 등록했습니다.\n'
        f'- 제목: {candidate.title}\n'
        f'- 일정: {candidate.start_at.strftime("%Y-%m-%d %H:%M")} ~ {candidate.end_at.strftime("%H:%M")}\n'
        f'- 이벤트 ID: {event_id or "(응답 확인 필요)"}'
    )
