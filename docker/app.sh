#!/bin/bash

echo "Waiting for PostgreSQL..."
until PGPASSWORD=$DB_PASS psql -h db -U postgres -d documents_db -c '\q'; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

alembic upgrade head

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload