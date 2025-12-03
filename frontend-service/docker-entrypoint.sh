#!/bin/sh
# Startup script for nginx with environment variable substitution

# Set default if not provided
export BACKEND_URL=${BACKEND_URL:-http://backend-api:5000}

echo "Substituting BACKEND_URL=${BACKEND_URL} in nginx.conf"

# Replace ${BACKEND_URL} in the template and output to actual nginx.conf
envsubst '${BACKEND_URL}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

echo "Generated nginx configuration:"
cat /etc/nginx/conf.d/default.conf

# Start nginx
echo "Starting nginx"
nginx -g 'daemon off;'
