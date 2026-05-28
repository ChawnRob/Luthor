# Stage 1: Build the application
FROM node:22-alpine AS builder

WORKDIR /app

# Copy package files - handle both pnpm and npm
COPY package.json ./
COPY pnpm-lock.yaml* ./
COPY package-lock.json* ./
COPY yarn.lock* ./

# Install pnpm globally
RUN npm install -g pnpm

# Install dependencies using pnpm (with fallback to npm if pnpm-lock.yaml doesn't exist)
RUN if [ -f pnpm-lock.yaml ]; then \
      pnpm install --frozen-lockfile; \
    else \
      npm install; \
    fi

# Copy source code
COPY . .

# Build the application
RUN if [ -f pnpm-lock.yaml ]; then \
      pnpm run build; \
    else \
      npm run build; \
    fi

# Stage 2: Production runtime
FROM node:22-alpine

WORKDIR /app

# Install pnpm globally
RUN npm install -g pnpm

# Copy package files from builder stage
COPY package.json ./
COPY pnpm-lock.yaml* ./
COPY package-lock.json* ./
COPY yarn.lock* ./

# Install production dependencies only
RUN if [ -f pnpm-lock.yaml ]; then \
      pnpm install --frozen-lockfile --prod; \
    else \
      npm install --production; \
    fi

# Copy built application from builder
COPY --from=builder /app/dist ./dist

# Expose port (Cloud Run uses 8080 by default)
EXPOSE 8080

# Set environment variables
ENV NODE_ENV=production
ENV PORT=8080

# Start the application
CMD ["node", "dist/index.js"]
