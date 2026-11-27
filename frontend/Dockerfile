FROM node:26-alpine AS build

WORKDIR /workspace

COPY frontend/package.json ./package.json
RUN npm install --no-audit --no-fund

COPY frontend/ ./
RUN npm run build

FROM nginx:stable-alpine3.24

COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /workspace/dist /usr/share/nginx/html

EXPOSE 80
