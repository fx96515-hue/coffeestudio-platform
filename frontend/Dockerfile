# syntax=docker/dockerfile:1

# =============================================================================
# Dependencies stage: Install dependencies
# =============================================================================
FROM node:20-alpine AS deps

WORKDIR /app

# Copy package files for dependency installation
COPY package.json package-lock.json ./

# Install dependencies (production + dev for build)
RUN npm ci

# =============================================================================
# Builder stage: Build the application
# =============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/package.json ./package.json
COPY --from=deps /app/package-lock.json ./package-lock.json

# Copy configuration and source files
COPY next.config.mjs ./
COPY tsconfig.json ./
COPY next-env.d.ts ./
COPY app ./app
COPY lib ./lib

# Build Next.js application
ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production

RUN npm run build

# =============================================================================
# Runtime stage: Minimal production image
# =============================================================================
FROM node:20-alpine AS runtime

WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME="0.0.0.0"

# Copy standalone server (includes minimal node_modules)
COPY --from=builder /app/.next/standalone ./

# Copy static assets (not included in standalone output)
COPY --from=builder /app/.next/static ./.next/static

# Use existing node user for security
RUN chown -R node:node /app

USER node

EXPOSE 3000

# Use standalone server directly (faster, smaller)
CMD ["node", "server.js"]
