#!/bin/zsh
set -e
cd "$(dirname "$0")/.."
python3 mail_bot_workday_delivery.py
