# daou-mail-agent2

다우오피스 메일/일정/할 일 브리핑을 위한 업무 비서 프로젝트입니다.

## 주요 기능
- 다우오피스 IMAP 기반 메일 조회
- 최근 메일 / 안 읽은 메일 / 키워드 메일 조회
- 메일 요약 / 상세 보기 / 답장 초안
- 답장 필요한 메일 브리핑
- 오늘 일정 / 오늘 할 일 / 오늘 업무 브리핑
- 텔레그램 메일 봇 응답
- 브리핑 내 권장 다음 액션 생성

## 현재 반영 상태
- 메일 수집/분류/요약/상세/답장 초안 동작
- 일정/할 일/업무 브리핑 동작
- 제안/승인/실행 기본 흐름 복원
- 메일 봇 HTML 브리핑/버튼 UX 기본 복원
- 최근 메일 조회 로직 보정
  - 다우오피스 IMAP 응답 형식 대응
  - 날짜 파싱 기반 최신순 정렬
  - 최근 메일은 INBOX 마지막 시퀀스 기준 조회

## 실행 예시
```bash
python3 telegram_mail_agent.py '최근 메일 5개 보여줘'
python3 telegram_mail_agent.py '3번 메일 자세히 보여줘'
python3 telegram_mail_agent.py '답장 필요한 메일 브리핑해줘'
python3 telegram_mail_agent.py '오늘 업무 브리핑해줘'
python3 telegram_mail_agent.py '오늘 일정 뭐야?'
python3 telegram_mail_agent.py '전체 할 일 보여줘'
```

## 환경 변수
`.env.example`를 참고해 `.env`를 준비하면 실제 메일/텔레그램 연결이 가능합니다.

기본 예시는 아래와 같습니다.
- IMAP: `imap.daouoffice.com:993`
- SMTP: `smtp.daouoffice.com:465`

필수 항목:
- `IMAP_HOST`
- `IMAP_PORT`
- `SMTP_HOST`
- `SMTP_PORT`
- `EMAIL_ADDRESS`
- `EMAIL_PASSWORD`
- `TELEGRAM_MAIL_BOT_TOKEN`
- `TELEGRAM_MAIL_BOT_CHAT_ID`

## 참고 사항
- 최근 메일 조회와 안 읽은 메일 조회는 서로 다른 기준으로 동작합니다.
- 일부 HTML 메일은 본문 요약이 제한될 수 있습니다.
- 업무 브리핑은 메일/일정/할 일 상태를 함께 묶어 보여주며, 하단에 다음 액션을 함께 제안합니다.
