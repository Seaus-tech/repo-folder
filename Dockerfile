# syntax=docker/dockerfile:1

# --- 1. Base Runtime Environment ---
FROM node:20-alpine AS base
WORKDIR /app
EXPOSE 3000

# --- 2. Compilation and Dependency Layer ---
FROM base AS build
COPY package*.json ./
RUN npm ci
COPY . .

# --- 3. Final Production Package ---
FROM base AS final
USER node
COPY --from=build /app /app

CMD ["node", "index.js"]
