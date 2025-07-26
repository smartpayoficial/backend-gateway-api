#!/bin/bash

# Script to fix the database connectivity issue by adding smartpay_network to docker-compose.yml
# This script directly modifies the deployment.py file to include smartpay_network

# Path to the deployment.py file
DEPLOYMENT_FILE="/home/smartpayvps/backend-gateway-api/app/services/deployment.py"

# Check if the file exists
if [ ! -f "$DEPLOYMENT_FILE" ]; then
    echo "Error: deployment.py file not found at $DEPLOYMENT_FILE"
    exit 1
fi

# Create a backup of the original file
sudo cp "$DEPLOYMENT_FILE" "${DEPLOYMENT_FILE}.bak.$(date +%Y%m%d%H%M%S)"
if [ $? -ne 0 ]; then
    echo "Error: Failed to create backup file. Check permissions."
    exit 1
fi

# Find the networks section in the docker-compose template and add smartpay_network
sudo sed -i '/networks:/,/external: true/{s/external: true/external: true\n  smartpay_network:\n    external: true/}' "$DEPLOYMENT_FILE"

# Find the db-api container's networks section and add smartpay_network
sudo sed -i '/smartpay-db-api-{store_id}:/,/restart: unless-stopped/{s/networks:.*$/networks:\n      - smartpay-{store_id}\n      - traefik-public\n      - smartpay_network/}' "$DEPLOYMENT_FILE"

echo "Fixed deployment.py to include smartpay_network for database connectivity."
echo "Original file backed up at ${DEPLOYMENT_FILE}.bak.*"
echo "Now all new store deployments will be able to connect to the PostgreSQL database."

# Instructions for applying the fix to existing deployments
echo ""
echo "To apply this fix to existing deployments, you need to manually edit each store's docker-compose.yml file."
echo "For example, for store 'tiendasd3' with UUID 21e95c78-29da-4c3f-a104-5de5143bbd5b:"
echo ""
echo "1. Edit the docker-compose.yml file:"
echo "   sudo nano /home/smartpayvps/backend-gateway-api/deployments/tiendasd3/backend-gateway-api-21e95c78-29da-4c3f-a104-5de5143bbd5b/docker-compose.yml"
echo ""
echo "2. Add smartpay_network to the networks section:"
echo "   networks:"
echo "     smartpay-21e95c78-29da-4c3f-a104-5de5143bbd5b:"
echo "       driver: bridge"
echo "     traefik-public:"
echo "       external: true"
echo "     smartpay_network:"
echo "       external: true"
echo ""
echo "3. Add smartpay_network to the database API container's networks:"
echo "   smartpay-db-api-21e95c78-29da-4c3f-a104-5de5143bbd5b:"
echo "     # ... existing configuration ..."
echo "     networks:"
echo "       - smartpay-21e95c78-29da-4c3f-a104-5de5143bbd5b"
echo "       - traefik-public"
echo "       - smartpay_network"
echo ""
echo "4. Restart the containers:"
echo "   cd /home/smartpayvps/backend-gateway-api/deployments/tiendasd3/backend-gateway-api-21e95c78-29da-4c3f-a104-5de5143bbd5b"
echo "   sudo docker-compose down"
echo "   sudo docker-compose up -d"
