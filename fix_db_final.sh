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
sudo cp "$DEPLOYMENT_FILE" "${DEPLOYMENT_FILE}.bak.final"
if [ $? -ne 0 ]; then
    echo "Error: Failed to create backup file. Check permissions."
    exit 1
fi

# Create a temporary sed script file
sudo bash -c "cat > /tmp/db_network_fix.sed << 'EOF'
# Add smartpay_network to the networks section
/networks:/,/external: true/ {
  /external: true/ a\\
  smartpay_network:\\
    external: true
}

# Add smartpay_network to the db-api container's networks list
/smartpay-db-api-{store_id}:/,/restart: unless-stopped/ {
  /networks:/ {
    c\\
    networks:\\
      - smartpay-{store_id}\\
      - traefik-public\\
      - smartpay_network
  }
}

# Fix Traefik entrypoints from https to websecure
s/entrypoints=https/entrypoints=websecure/g
EOF"

# Apply the sed script
sudo sed -i -f /tmp/db_network_fix.sed "$DEPLOYMENT_FILE"

echo "Fixed deployment.py to include smartpay_network for database connectivity."
echo "Also fixed Traefik entrypoints from 'https' to 'websecure'."
echo "Original file backed up at ${DEPLOYMENT_FILE}.bak.final"
echo "Now all new store deployments will be able to connect to the PostgreSQL database."
