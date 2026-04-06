#!/bin/zsh
set -e
python3 telegram_mail_agent.py '마지막 메일이 뭐야?'
printf '\n---\n'
python3 telegram_mail_agent.py '답장 필요한 메일 브리핑해줘'
