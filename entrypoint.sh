#!/bin/sh
set -e

# Default to port 8080 if not set
PORT=${PORT:-8080}

echo "Starting Private AI-CI on port $PORT..."

# Run Gunicorn with the dynamic port
exec gunicorn -w 1 -b 0.0.0.0:$PORT app.main:app --timeout 600
