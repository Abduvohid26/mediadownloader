#!/bin/sh

echo "Waiting for PostgreSQL to start..."

# PostgreSQL serveri ishga tushgunicha kutish
while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL is up and running!"

# Alembic migratsiyalarini bajarish
echo "Running Alembic migrations..."
# alembic revision --autogenerate -m "Initial migration"
# alembic upgrade head

# Asosiy ilovani ishga tushirish
echo "Starting the application..."
exec "$@"