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
cp "$DEPLOYMENT_FILE" "${DEPLOYMENT_FILE}.bak"
if [ $? -ne 0 ]; then
    echo "Error: Failed to create backup file. Check permissions."
    exit 1
fi

# Replace the networks section in the docker-compose template
# We need to add the smartpay_network to the networks section and to the db-api container
sed -i 's/networks:
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
sed -i 's/networks:
      - smartpay-{store_id}
      - traefik-public/networks:
      - smartpay-{store_id}
      - traefik-public
      - smartpay_network/' "$DEPLOYMENT_FILE"

echo "Fixed deployment.py to include smartpay_network for database connectivity."
echo "Original file backed up at ${DEPLOYMENT_FILE}.bak"

# Instructions for applying the fix to existing deployments
echo ""
echo "To apply this fix to existing deployments, you need to:"
echo "1. Edit each store's docker-compose.yml file to add smartpay_network"
echo "2. Restart the containers"
echo ""
echo "For example, for store 'tiendasd3' with UUID 21e95c78-29da-4c3f-a104-5de5143bbd5b:"
echo "1. Edit /home/smartpayvps/backend-gateway-api/deployments/tiendasd3/backend-gateway-api-21e95c78-29da-4c3f-a104-5de5143bbd5b/docker-compose.yml"
echo "2. Add 'smartpay_network' to the networks section and mark it as external"
echo "3. Add 'smartpay_network' to the networks list for the smartpay-db-api container"
echo "4. Run 'docker-compose down && docker-compose up -d' in that directory"
