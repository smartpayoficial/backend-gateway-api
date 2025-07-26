#!/bin/bash

# Script to fix the database connectivity issue by adding smartpay_network to docker-compose.yml
# This script modifies deployment.py to include smartpay_network in the networks section

# Path to the deployment.py file
DEPLOYMENT_FILE="/home/smartpayvps/backend-gateway-api/app/services/deployment.py"

# Check if the file exists
if [ ! -f "$DEPLOYMENT_FILE" ]; then
    echo "Error: deployment.py file not found at $DEPLOYMENT_FILE"
    exit 1
fi

# Create a backup of the original file
sudo cp "$DEPLOYMENT_FILE" "${DEPLOYMENT_FILE}.bak"
if [ $? -ne 0 ]; then
    echo "Error: Failed to create backup file. Check permissions."
    exit 1
fi

# Replace the networks section in the docker-compose template
# We need to add the smartpay_network to the networks section and to the db-api container
sudo sed -i 's/networks:
  smartpay-{store_id}:
    driver: bridge
  traefik-public:
    external: true/networks:
  smartpay-{store_id}:
    driver: bridge
  traefik-public:
    external: true
  smartpay_network:
    external: true/' "$DEPLOYMENT_FILE"

# Add smartpay_network to the db-api container's networks
sudo sed -i 's/networks:
      - smartpay-{store_id}
      - traefik-public/networks:
      - smartpay-{store_id}
      - traefik-public
      - smartpay_network/' "$DEPLOYMENT_FILE"

echo "Fixed deployment.py to include smartpay_network for database connectivity."
echo "Original file backed up at ${DEPLOYMENT_FILE}.bak"
echo "Now all new store deployments will be able to connect to the PostgreSQL database."
