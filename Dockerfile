# --- Stage 1: Build Frontend ---
FROM node:20 as frontend-builder
# Force update for node 20
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Backend ---
FROM python:3.11-slim

# Install system dependencies (Docker CLI, git, etc.)
RUN apt-get update && apt-get install -y \
    docker.io \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies FIRST (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# THEN copy the rest of the code
COPY . .

# Copy Built Frontend Assets from Stage 1
COPY --from=frontend-builder /app/frontend/out ./dist

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Run the application
ENTRYPOINT ["/app/entrypoint.sh"]
