FROM python:latest

# Set the working directory
WORKDIR /opt/project

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .
ENV PICBUDGET_SETTING_IN_DOCKER true


RUN pip install --upgrade pip

# Copy and Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the project
COPY ["Makefile","./"]
COPY picbudget picbudget
COPY local local

# Expose the port
EXPOSE 8000

# Set up the entrypoint
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]