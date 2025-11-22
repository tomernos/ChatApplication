# Multi-stage Dockerfile for React Frontend
# Stage 1: Build the React app
# Stage 2: Serve with Nginx

# ============================================
# STAGE 1: Build Stage
# ============================================
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build production-ready React app
# Creates optimized bundle in /app/build directory
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
