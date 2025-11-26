# Use official Python image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_COLLECTSTATIC=0

# Install system dependencies for mysqlclient and others
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    libssl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

# Copy project files
COPY . /app/

# Expose port your Django app runs on
EXPOSE 8000

# Run migrations before starting Gunicorn (optional, adjust if you run migrations elsewhere)
CMD ["sh", "-c", "python manage.py migrate && gunicorn status_monitor.wsgi:application --bind 0.0.0.0:8000 --workers 4"]
