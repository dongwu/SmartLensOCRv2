#!/bin/sh
# Frontend Runtime Configuration Script
# This script generates a JavaScript file with the API configuration
# The backend URL is read from environment variable BACKEND_URL
# If not provided, defaults to window.location.origin (same host)

BACKEND_URL="${BACKEND_URL:-${WINDOW_LOCATION_ORIGIN}}"

# If BACKEND_URL is still empty, derive from current host
if [ -z "$BACKEND_URL" ]; then
  BACKEND_URL=""  # Will use window.location.origin on client side
fi

# Create config file
cat > /usr/share/nginx/html/config.js << 'CONFIG_EOF'
// Runtime configuration injected at container startup
window.__APP_CONFIG__ = {
  API_URL: "BACKEND_URL_PLACEHOLDER"
};
CONFIG_EOF

# Replace placeholder with actual backend URL
if [ -n "$BACKEND_URL" ]; then
  sed -i "s|BACKEND_URL_PLACEHOLDER|$BACKEND_URL|g" /usr/share/nginx/html/config.js
else
  # Use relative path to same host (works when frontend and backend are on same domain)
  sed -i "s|BACKEND_URL_PLACEHOLDER|${RELATIVE_BACKEND_PATH:-http://localhost:8000}|g" /usr/share/nginx/html/config.js
fi

echo "Configuration file generated:"
cat /usr/share/nginx/html/config.js

# Start nginx
exec nginx -g "daemon off;"
