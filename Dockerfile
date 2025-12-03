##############################################
# Stage 1 - Builder
##############################################
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirement file
COPY requirements.txt .

# Install Python dependencies to /install
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt


##############################################
# Stage 2 - Runtime
##############################################
FROM python:3.11-slim

ENV TZ=UTC

WORKDIR /app

# Install cron + timezone data
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Configure UTC timezone
RUN ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# Copy installed dependencies from builder image
COPY --from=builder /install /usr/local

# Copy application code
COPY app ./app
COPY cron ./cron

# Copy key files
COPY student_private.pem .
COPY student_public.pem .
COPY instructor_public.pem .

# Create mount folders
RUN mkdir -p /data /cron

# Install cron job
COPY cron/cronjob /etc/cron.d/microservice-cron
RUN chmod 0644 /etc/cron.d/microservice-cron && \
    crontab /etc/cron.d/microservice-cron

# Expose port
EXPOSE 8080

# Start cron + API server
CMD cron && uvicorn app.main:app --host 0.0.0.0 --port 8080
