#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="$(command -v python3)"
LOG_DIR="$ROOT/data"
LOG_FILE="$LOG_DIR/briefing_cron.log"
mkdir -p "$LOG_DIR"

WORKDAY_LINE="0 9 * * * cd $ROOT && $PYTHON_BIN scripts/send_workday_briefing.py >> $LOG_FILE 2>&1"
MAIL_AM_LINE="0 11 * * * cd $ROOT && $PYTHON_BIN scripts/send_mail_briefing.py >> $LOG_FILE 2>&1"
MAIL_PM_LINE="0 16 * * * cd $ROOT && $PYTHON_BIN scripts/send_mail_briefing.py >> $LOG_FILE 2>&1"

EXISTING="$(crontab -l 2>/dev/null || true)"
UPDATED="$(printf '%s\n' "$EXISTING" | grep -v 'scripts/poll_mail_workflow.py' | grep -v 'scripts/send_workday_briefing.py' | grep -v 'scripts/send_mail_briefing.py' || true)"
{
  if [ -n "$UPDATED" ]; then
    printf '%s\n' "$UPDATED"
  fi
  printf '%s\n' "$WORKDAY_LINE"
  printf '%s\n' "$MAIL_AM_LINE"
  printf '%s\n' "$MAIL_PM_LINE"
} | crontab -

echo "Installed cron lines:"
echo "$WORKDAY_LINE"
echo "$MAIL_AM_LINE"
echo "$MAIL_PM_LINE"
