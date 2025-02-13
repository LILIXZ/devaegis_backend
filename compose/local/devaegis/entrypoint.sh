#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

echo "starting devaegis backend service"
gunicorn 'app:create_app()' \
    --reload \
    --timeout 180 \
    --workers 6 \
    --bind 0.0.0.0:7999 \
    --limit-request-line 0
