# Frontend Dockerfile - build React/Vite app and serve static files
FROM node:18-alpine AS build

WORKDIR /app

# Copy package and install
COPY package.json package-lock.json* ./
RUN npm ci --silent

# Copy rest of frontend and build
COPY . .
RUN npm run build

FROM node:18-alpine AS runtime
WORKDIR /app

# Install a small static server
RUN npm install -g serve

COPY --from=build /app/dist ./dist

EXPOSE 8080
CMD ["serve", "-s", "dist", "-l", "8080"]
