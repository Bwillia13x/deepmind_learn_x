#!/usr/bin/env bash
set -e

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Start infrastructure
make up

# Wait for services
echo "Waiting for PostgreSQL..."
sleep 3

# Start API
make api
