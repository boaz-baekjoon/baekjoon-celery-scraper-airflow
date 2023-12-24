#!/bin/bash

# Command to run in the container
COMMAND="python crawler_process.py beakjoon_user_detail"

# Build the Docker image
echo "Building Docker image..."
docker build -t baekjoon_scraper .

# Run the Docker container with the specified command
echo "Running Docker container with command: ${COMMAND}"
docker run -it --rm baekjoon_scraper $COMMAND