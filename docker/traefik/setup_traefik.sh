#!/bin/bash

# Create directories if they don't exist
mkdir -p ./data

# Create empty acme.json file with correct permissions
touch ./data/acme.json
chmod 600 ./data/acme.json

# Create traefik network if it doesn't exist
docker network create traefik-public || true

echo "Traefik setup completed. You can now run docker-compose -f docker-compose.traefik.yml up -d"
