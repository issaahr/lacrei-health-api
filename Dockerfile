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

EXPOSE 8000

# If DJANGO_DEBUG=True → runserver, else gunicorn
CMD if [ "$DJANGO_DEBUG" = "True" ]; then \
        python manage.py runserver 0.0.0.0:8000; \
    else \
        gunicorn app.wsgi:application --bind 0.0.0.0:${PORT:-8000}; \
    fi
