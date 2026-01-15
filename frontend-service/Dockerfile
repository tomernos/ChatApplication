# Multi-stage Dockerfile for React Frontend
# Stage 1: Build the React app
# Stage 2: Serve with Nginx

# ============================================
# STAGE 1: Build Stage
# ============================================
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Accept build arguments for React environment variables
# These are used at BUILD TIME (not runtime) because React is compiled to static files
# Defaults are set for local development - override in CI/CD for production
ARG REACT_APP_OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4318
ARG REACT_APP_OTEL_SERVICE_NAME=chatapp-frontend
ARG REACT_APP_OTEL_SERVICE_NAMESPACE=chatapp-dev
ARG REACT_APP_API_URL=/api

# Set as environment variables for npm build
ENV REACT_APP_OTEL_EXPORTER_OTLP_ENDPOINT=$REACT_APP_OTEL_EXPORTER_OTLP_ENDPOINT
ENV REACT_APP_OTEL_SERVICE_NAME=$REACT_APP_OTEL_SERVICE_NAME
ENV REACT_APP_OTEL_SERVICE_NAMESPACE=$REACT_APP_OTEL_SERVICE_NAMESPACE
ENV REACT_APP_API_URL=$REACT_APP_API_URL

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build production-ready React app
# Creates optimized bundle in /app/build directory
# Environment variables are baked into the build at this step
RUN npm run build

# ============================================
# STAGE 2: Production Stage
# ============================================
FROM nginx:alpine

# Copy built React app from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx template and startup script
COPY nginx.conf.template /etc/nginx/conf.d/default.conf.template
COPY docker-entrypoint.sh /docker-entrypoint.sh

# Make entrypoint script executable
RUN chmod +x /docker-entrypoint.sh

# Expose port 80
EXPOSE 80

# Use custom entrypoint that processes template and starts nginx
ENTRYPOINT ["/docker-entrypoint.sh"]

# Why multi-stage build?
# - Stage 1 builds the app (needs Node.js and all dev dependencies)
# - Stage 2 only needs the built files (static HTML/CSS/JS)
# - Final image is much smaller (only Nginx + built files, no Node.js!)
# - Production image: ~25MB vs ~300MB if we kept Node.js
