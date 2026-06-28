#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py seed_plans

exec gunicorn hrms.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout 120 \
  --max-requests 1000 \
  --max-requests-jitter 50
