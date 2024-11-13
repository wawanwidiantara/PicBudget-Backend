FROM python:latest

# Set the working directory
WORKDIR /opt/project

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .
ENV PICBUDGET_SETTING_IN_DOCKER true

# Expose the port
EXPOSE 8000

RUN pip install --upgrade pip

# Copy and Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the project
COPY ["Makefile","./"]

# Set up the entrypoint
COPY scripts/run-django.sh ./
RUN chmod a+x ./run-django.sh

# Set up the celery worker
COPY scripts/run-celery.sh ./
RUN chmod a+x ./run-celery.sh

COPY picbudget picbudget
COPY local local