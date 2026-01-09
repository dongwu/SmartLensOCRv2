#!/bin/bash
set -e

echo "=========================================="
echo "SmartLensOCR Frontend Startup"
echo "=========================================="

# Get the backend URL from environment
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

echo "Backend URL: $BACKEND_URL"
echo "Creating config.js..."

# Create config file
cat > /usr/share/nginx/html/config.js << 'CONFIGEOF'
// SmartLensOCR Runtime Configuration
// This file is generated at container startup
window.__APP_CONFIG__ = {
  API_URL: "BACKEND_URL_PLACEHOLDER"
};
console.log('SmartLensOCR Config Loaded:', window.__APP_CONFIG__);
CONFIGEOF

# Replace placeholder with actual backend URL
sed -i "s|BACKEND_URL_PLACEHOLDER|${BACKEND_URL}|g" /usr/share/nginx/html/config.js

echo ""
echo "Config file generated:"
cat /usr/share/nginx/html/config.js
echo ""
echo "Starting Nginx..."
echo "=========================================="

# Start Nginx
exec nginx -g "daemon off;"
