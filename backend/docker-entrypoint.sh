#!/bin/sh
set -eu

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
  alembic -c /app/alembic.ini upgrade head
  python -m app.db.seed
fi

exec "$@"
