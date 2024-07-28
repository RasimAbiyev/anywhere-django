# Docker
FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV NAME=World
RUN adduser --disabled-password --gecos '' celeryuser
WORKDIR /code
COPY requirements.txt /code/
COPY . .
RUN python manage.py collectstatic --noinput
RUN chown -R celeryuser:celeryuser /code
COPY requirements.txt /code/
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r requirements.txt
ENV PATH="/venv/bin:$PATH"
EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=myproject.settings
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]