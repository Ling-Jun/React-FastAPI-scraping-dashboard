# Dockerfile for Redis + Celery Worker + Celery Beat
FROM python:3.11-slim

# Install Redis
RUN apt-get update && apt-get install -y redis && apt-get clean

# Set the working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Redis port
EXPOSE 6379

# Default command (can be overridden in the docker-compose file)
CMD ["sh", "-c", "redis-server & celery -A celery_app worker --loglevel=info & celery -A celery_app beat --loglevel=info"]
