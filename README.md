# daou-mail-agent2

다우오피스 메일/일정/할 일 브리핑을 위한 업무 비서 프로젝트입니다.

## 프로젝트 개요
이 프로젝트는 아래 흐름을 하나로 묶는 업무 비서입니다.
- 다우오피스 메일 조회 및 분류
- 중요 메일 / 답장 필요 메일 / 일정 메일 브리핑
- Google Calendar 일정 등록/수정/취소 제안
- Telegram 메일봇 응답 및 버튼 UX
- 로컬 SQLite 캐시 기반 상태 관리
- 예약 브리핑 및 폴링 스크립트 운영

## 현재 주요 기능
- IMAP 기반 최근 메일 / 안 읽은 메일 조회
- 메일 상세 보기 / 요약 / 답장 초안
- 중요 메일 알림
- 답장 필요한 메일 브리핑
- 일정 메일 감지 및 일정 등록 제안
- Google Calendar 등록 실동작
- 제안 / 승인 / 실행 흐름
- Telegram 메일봇 inline button UX
- SQLite 메일 캐시 및 상태 추적
  - `notified_at`
  - `briefed_at`
  - `schedule_proposed_at`
- 캐시 180일 보관 정책

## 현재 폴더 구조
```text
daou-mail-agent2/
├─ agents/        # 메일 수집/분류/요약/답장 핵심 로직
├─ briefings/     # 업무/메일/일정/운영 브리핑 생성
├─ core/          # 공통 모델/설정/세션/제안 저장
├─ mailbot/       # Telegram 메일봇 라우팅/전송
├─ proposals/     # 제안 승인/실행 흐름
├─ storage/       # SQLite 캐시 접근
├─ scripts/       # 실행용 스크립트
├─ data/          # 로컬 캐시/운영 데이터
└─ memory/        # 작업 메모
```

## 주요 엔트리포인트
### 사용자 명령 처리
- `telegram_mail_agent.py`
- 자연어 메일/브리핑/제안 명령 처리 진입점

### 메일봇 라우팅
- `mailbot/mail_bot_router.py`
- Telegram bot update 처리

### 브리핑 생성
- `briefings/workday_briefing.py`
- `briefings/important_mail_briefing.py`
- `briefings/reply_needed_briefing.py`
- `briefings/schedule_recommendation.py`
- `briefings/operations_briefing.py`

### 일정 메일 처리
- `schedule_mail.py`
- 일정 후보 탐지 / 일정 제안 / Google Calendar 등록 연동

### 저장소
- `storage/mail_cache.py`
- SQLite 기반 메일 캐시 및 상태 필드 관리

## 실행 예시
```bash
python3 telegram_mail_agent.py '최근 메일 5개 보여줘'
python3 telegram_mail_agent.py '3번 메일 자세히 보여줘'
python3 telegram_mail_agent.py '답장 필요한 메일 브리핑해줘'
python3 telegram_mail_agent.py '오늘 업무 브리핑해줘'
python3 telegram_mail_agent.py '일정 메일 브리핑해줘'
python3 telegram_mail_agent.py '1번 메일 일정등록 제안해줘'
python3 telegram_mail_agent.py '메일 통계 보여줘'
python3 telegram_mail_agent.py '제안 히스토리 보여줘'
```

## 운영 스크립트
- `scripts/send_workday_briefing.py`
  - 종합 업무 브리핑 전송
- `scripts/send_mail_briefing.py`
  - 중요 메일 / 답장 필요 / 일정 추천 브리핑 전송
- `scripts/poll_mail_workflow.py`
  - 주기 점검용 메일 폴링 워크플로
- `scripts/update_briefing_cron.py`
  - 예약 브리핑용 crontab 내용 생성/갱신 지원

## 환경 변수
`.env.example`를 참고해 `.env`를 준비하면 실제 메일/텔레그램 연결이 가능합니다.

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
- 일정 메일 등록은 현재 정규식 기반 후보 추출을 사용합니다.
- 수정/취소 일정 흐름은 구현되어 있으며, 실메일 기준 추가 검증 대상이 남아 있습니다.
- 로컬 캐시/로그/DB 파일은 저장소 커밋 대상이 아닙니다.
