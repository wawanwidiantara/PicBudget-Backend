# Base image
FROM python:3.12.8

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .
ENV PICBUDGET_SETTING_IN_DOCKER true

# Set working directory
WORKDIR /opt/project

# Expose the application port
EXPOSE 8000

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install system dependencies
RUN pip install --upgrade pip

# Copy and Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application files
COPY ["Makefile", "./"]
COPY scripts/run-django.sh ./run-django.sh
RUN chmod +x ./run-django.sh

COPY scripts/run-celery.sh ./run-celery.sh
RUN chmod +x ./run-celery.sh

COPY picbudget picbudget
COPY local local