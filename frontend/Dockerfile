FROM node:18-bullseye-slim AS build

WORKDIR /app

COPY package.json ./
RUN npm install --silent

COPY . .
RUN npm run build

FROM node:18-bullseye-slim AS runtime
WORKDIR /app

RUN npm install -g serve

COPY --from=build /app/dist ./dist

EXPOSE 8080 
CMD ["serve", "-s", "dist", "-l", "8080"]
