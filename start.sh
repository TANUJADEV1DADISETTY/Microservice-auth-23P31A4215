#!/bin/bash

# Start cron in the background
service cron start

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8080
