#!/bin/bash
set -e

# Configuration
IMAGE_NAME="codelens-backend"
CONTAINER_NAME="codelens-backend"
PORT=8080

echo "🚀 Starting EC2 Backend Update..."

# 1. Pull latest changes
echo "📥 Pulling latest code..."
git pull origin master

# 2. Build Docker Image
echo "🔨 Building Docker image ($IMAGE_NAME)..."
# Using sudo if user is not in docker group, typically needed on EC2 unless configured
sudo docker build -t $IMAGE_NAME .

# 3. Stop and Remove Old Container
# 3. Stop and Remove Old Container (and any port hog)
echo "🛑 Stopping running containers..."

# Find if any container is using our PORT and stop it
PORT_HOG_ID=$(sudo docker ps -q --filter "publish=$PORT")
if [ -n "$PORT_HOG_ID" ]; then
    echo "⚠️  Found container ($PORT_HOG_ID) using port $PORT. Stopping it..."
    sudo docker stop $PORT_HOG_ID
    sudo docker rm $PORT_HOG_ID
fi

# Also ensure our named container is gone (in case it wasn't the one hogging port but still exists)
if [ "$(sudo docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
    sudo docker rm -f $CONTAINER_NAME
    echo "✅ Old container instance removed."
else
    echo "ℹ️ No stopped/running container found with name $CONTAINER_NAME."
fi

# 4. cleanup old images (optional)
echo "🧹 Cleaning up dangling images..."
sudo docker image prune -f

# 5. Run New Container
echo "▶️  Starting new container..."
# Using --restart unless-stopped to ensure it restarts on reboot
sudo docker run -d \
    --name $CONTAINER_NAME \
    --restart unless-stopped \
    -p $PORT:8080 \
    -e AWS_EXECUTION_ENV=true \
    -e AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-ap-south-1} \
    $IMAGE_NAME

echo "🎉 Update Complete! Backend is running."
sudo docker ps | grep $CONTAINER_NAME
