# Django image for TeamFinder.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# psycopg2-binary and Pillow ship manylinux wheels, so no build toolchain
# is needed — keeping the image small.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

# The entrypoint runs migrations, collects static and seeds demo data,
# then hands off to the CMD (gunicorn).
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "team_finder.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
