# daou-mail-agent2

재구축 중인 Daou Mail Agent 프로젝트.

## 목표
- 다우오피스 메일 조회
- 자연어 메일/일정/할 일 비서
- 텔레그램 메일 봇 응답
- 브리핑/요약/답장 초안/승인 흐름

## 현재 복원 상태
- 기본 메일 수집/요약/상세/답장 초안 복원
- 일정/할 일/업무 브리핑 복원
- 제안/승인/실행 기본 흐름 복원
- 메일 봇 HTML 브리핑/버튼 UX 기본 복원
- mail-agent 전용 persona 파일(`AGENTS.md`, `SOUL.md`, `STYLE.md`) 추가

## 실행 예시
- `python3 telegram_mail_agent.py '마지막 메일이 뭐야?'`
- `python3 telegram_mail_agent.py '답장 필요한 메일 브리핑해줘'`
- `python3 telegram_mail_agent.py '오늘 업무 브리핑해줘'`
- `python3 mail_bot_workday_delivery.py`
- `python3 mail_bot_router.py`

## 환경 변수
`.env.example`를 참고해 `.env`를 준비하면 실제 메일/텔레그램 연결이 가능하다.
