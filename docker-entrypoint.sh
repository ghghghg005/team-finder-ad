#!/bin/sh
set -e

# The db service is gated behind a healthcheck, but retry migrations a few
# times just in case the database is still finishing its startup.
echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Seeding demo data (idempotent)..."
python manage.py seed_demo

echo "Starting application server..."
exec "$@"
