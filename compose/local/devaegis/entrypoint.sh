#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

echo "starting devaegis backend service"
gunicorn 'devaegis.app:create_app()' \
    --reload \
    --timeout 180 \
    --workers 6 \
    --bind 0.0.0.0:8000 \
    --limit-request-line 0
