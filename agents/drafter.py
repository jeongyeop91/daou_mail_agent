from __future__ import annotations

from core.models import EmailItem


def draft_reply(email: EmailItem) -> str:
    return (
        f"안녕하세요. {email.sender.split('<')[0].strip()}님.\n\n"
        f"보내주신 메일 잘 확인했습니다.\n"
        f"'{email.subject}' 관련 내용은 검토 후 다시 안내드리겠습니다.\n\n"
        "감사합니다."
    )
