#!/usr/bin/env bash

set -e

RUN_MANAGE_PY = "python -m picbudget.manage"

echo "Collecting static files"
$RUN_MANAGE_PY collectstatic --noinput

echo "Running migrations..."
$RUN_MANAGE_PY migrate --noinput

exec daphne picbudget.project.asgi:application --port 8000 --bind 0.0.0.0