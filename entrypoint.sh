#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting server..."
exec gunicorn app.wsgi:application --bind 0.0.0.0:${PORT:-8000}

