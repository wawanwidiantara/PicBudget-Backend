#!/usr/bin/env bash

exec celery -A picbudget.project worker -l INFO