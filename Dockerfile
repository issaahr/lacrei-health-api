FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# System deps for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root

# Copy source code
COPY . .

# Collect static files (dummy env vars for build only)
RUN POSTGRES_DB=x POSTGRES_USER=x POSTGRES_PASSWORD=x DATABASE_HOST=x DATABASE_PORT=5432 \
    python manage.py collectstatic --noinput

EXPOSE 8000

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
