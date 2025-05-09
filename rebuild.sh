#!/bin/bash

# Stop and remove all containers
docker compose down -v

# Remove all unused Docker resources
docker system prune -af --volumes

# Build the assistant service with the correct environment variables
cd PoseFit_assistant
docker build --no-cache \
  --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_Y29tcG9zZWQtc2N1bHBpbi02MC5jbGVyay5hY2NvdW50cy5kZXYk \
  --build-arg CLERK_SECRET_KEY=sk_test_fLtgeNhSLuo1ZYP6zr9walZaQKo8wGwLGtIGoVZyQv \
  --build-arg NEXT_PUBLIC_CONVEX_URL=https://benevolent-cow-710.convex.cloud \
  -t posefit-assistant .

cd ..

# Start all services
docker compose up -d 