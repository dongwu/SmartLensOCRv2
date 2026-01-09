# SmartLensOCR Frontend - Multi-stage Docker build
# Stage 1: Build React app with Vite
# Stage 2: Serve with Nginx and inject runtime configuration

# ============================================================================
# STAGE 1: Builder
# ============================================================================
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
# Default to production build; can be overridden with --build-arg
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# ============================================================================
# STAGE 2: Runtime (Nginx)
# ============================================================================
FROM nginx:alpine

# Install bash for startup script
RUN apk add --no-cache bash

# Copy nginx configuration (pre-created file)
COPY frontend_nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy startup script that generates runtime configuration
COPY frontend_config.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start with configuration script that injects backend URL at runtime
ENTRYPOINT ["/docker-entrypoint.sh"]
