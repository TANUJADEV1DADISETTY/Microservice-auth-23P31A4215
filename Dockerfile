##############################################
# Stage 1 - Builder
##############################################
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt


##############################################
# Stage 2 - Runtime
##############################################
FROM python:3.11-slim

ENV TZ=UTC
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    procps \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# timezone
RUN ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# copy installed python packages
COPY --from=builder /install /usr/local

# copy application code
COPY app ./app

# correct cron folder path (important!)
COPY cron ./cron

# copy key files
COPY student_private.pem .
COPY student_public.pem .
COPY instructor_public.pem .

# folders for seed + output
RUN mkdir -p /data /cron

# install cronjob
COPY cron/cronjob /etc/cron.d/microservice-cron
RUN chmod 0644 /etc/cron.d/microservice-cron && \
    crontab /etc/cron.d/microservice-cron

EXPOSE 8080

# start cron + uvicorn
CMD ["bash", "-c", "cron -f & uvicorn app.main:app --host 0.0.0.0 --port 8080"]
