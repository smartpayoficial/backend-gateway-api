#!/bin/bash

# Script to manually fix the deployment.py file to add smartpay_network

# Path to the deployment.py file
DEPLOYMENT_FILE="/home/smartpayvps/backend-gateway-api/app/services/deployment.py"

# Check if the file exists
if [ ! -f "$DEPLOYMENT_FILE" ]; then
    echo "Error: deployment.py file not found at $DEPLOYMENT_FILE"
    exit 1
fi

# Create a backup of the original file
sudo cp "$DEPLOYMENT_FILE" "${DEPLOYMENT_FILE}.bak.manual"
if [ $? -ne 0 ]; then
    echo "Error: Failed to create backup file. Check permissions."
    exit 1
fi

# Add smartpay_network to the networks section
sudo sed -i '/networks:/,/external: true/{s/external: true/external: true\n  smartpay_network:\n    external: true/}' "$DEPLOYMENT_FILE"

# Add smartpay_network to the db-api container's networks
sudo sed -i '/smartpay-db-api-{store_id}:/,/restart: unless-stopped/{s/networks:.*$/networks:\n      - smartpay-{store_id}\n      - traefik-public\n      - smartpay_network/}' "$DEPLOYMENT_FILE"

echo "Fixed deployment.py to include smartpay_network for database connectivity."
echo "Original file backed up at ${DEPLOYMENT_FILE}.bak.manual"
echo "Now all new store deployments will be able to connect to the PostgreSQL database."

# Instructions for fixing existing deployments
echo ""
echo "To fix the existing tiendasd3 deployment:"
echo ""
echo "1. Create a fix script for tiendasd3:"
echo "cat > /tmp/fix_tiendasd3.sh << 'EOF'"
echo '#!/bin/bash'
echo 'DOCKER_COMPOSE="/home/smartpayvps/backend-gateway-api/deployments/tiendasd3/backend-gateway-api-21e95c78-29da-4c3f-a104-5de5143bbd5b/docker-compose.yml"'
echo 'sudo cp "$DOCKER_COMPOSE" "${DOCKER_COMPOSE}.bak"'
echo 'sudo sed -i "s/networks:/networks:\n  smartpay_network:\n    external: true/g" "$DOCKER_COMPOSE"'
echo 'sudo sed -i "/smartpay-db-api-21e95c78-29da-4c3f-a104-5de5143bbd5b:/,/restart: unless-stopped/s/networks:.*$/networks:\n      - smartpay-21e95c78-29da-4c3f-a104-5de5143bbd5b\n      - traefik-public\n      - smartpay_network/" "$DOCKER_COMPOSE"'
echo 'cd /home/smartpayvps/backend-gateway-api/deployments/tiendasd3/backend-gateway-api-21e95c78-29da-4c3f-a104-5de5143bbd5b'
echo 'sudo docker-compose down'
echo 'sudo docker-compose up -d'
echo 'EOF'
echo ""
echo "2. Make it executable and run it:"
echo "chmod +x /tmp/fix_tiendasd3.sh"
echo "sudo /tmp/fix_tiendasd3.sh"
