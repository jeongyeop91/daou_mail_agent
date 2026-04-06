from __future__ import annotations

from core.proposals import create_proposal, list_proposals, update_proposal_status


def propose_action(title: str, payload: dict) -> str:
    proposal = create_proposal(title, payload)
    return (
        f"제안 #{proposal['id']} 생성\n"
        f"- 제목: {proposal['title']}\n"
        "다음 단계\n"
        f"1) 메일 제안 {proposal['id']} 승인\n"
        f"2) 메일 제안 {proposal['id']} 실행\n"
        f"취소: 메일 제안 {proposal['id']} 거절"
    )


def list_pending_proposals() -> str:
    items = list_proposals('pending')
    if not items:
        return '대기 중인 제안이 없습니다.'
    lines = ['대기 중인 제안']
    for item in items:
        lines.append(f"- #{item['id']} {item['title']}")
    return '\n'.join(lines)


def handle_proposal_action(proposal_id: int, action: str) -> str:
    status_map = {'승인': 'approved', '거절': 'rejected'}
    if action not in status_map:
        return '지원하지 않는 제안 처리입니다.'
    updated = update_proposal_status(proposal_id, status_map[action])
    if not updated:
        return '해당 제안을 찾지 못했습니다.'
    return f"제안 #{proposal_id}을(를) {action} 처리했습니다."
