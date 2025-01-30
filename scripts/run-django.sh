#!/bin/bash

set -e

RUN_MANAGE_PY="python -m picbudget.manage"

if [ "$DEBUG" = "False" ]; then
    echo 'Production mode: Collecting static files and running migrations...'
    $RUN_MANAGE_PY collectstatic --no-input
    $RUN_MANAGE_PY migrate --no-input

    exec daphne picbudget.project.asgi:application --port 8000 --bind 0.0.0.0
else
    echo 'Development mode: Skipping collectstatic & migrations'
    echo 'Running Django development server...'

    exec python -m picbudget.manage runserver 0.0.0.0:8000
fi
