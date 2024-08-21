# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-alpine3.19 AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    build-base \
    linux-headers \
    libffi-dev

# Upgrade pip
RUN python -m pip install --upgrade pip==24.0

# Copy the requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Copy the source code into the container
COPY app.py .

# Expose the port that the application listens on.
EXPOSE 8080

# Switch to the non-privileged user to run the application.
USER appuser

# Run the application with gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--access-logfile", "-", "--error-logfile", "-"]
