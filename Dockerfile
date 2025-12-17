# ---------- Build stage ----------
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Install frontend deps
COPY frontend/package*.json ./
RUN npm ci

# Copy the rest of the frontend source
COPY frontend/ ./

# Build a static export (Next.js)
#   - `next build` creates .next
#   - `next export` writes a static site to ./out
RUN npx next build && npx next export

# ---------- Backend stage ----------
FROM python:3.11-slim

# System deps (already present, keep as‑is)
RUN apt-get update && apt-get install -y \
    docker.io \
    git \
    curl \
    build-essential \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Python deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY . /app

# ---- Copy the built frontend into Flask's static folder ----
# The Flask app expects static files at /app/dist
# The export from the previous stage lives in /app/frontend/out
COPY --from=frontend-builder /app/frontend/out /app/dist

# Expose the port used by Flask
EXPOSE 8080

# Run the app
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "app.main:app", "--timeout", "600"]