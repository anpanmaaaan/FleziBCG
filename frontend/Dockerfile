ARG NODE_IMAGE=node:20-alpine
ARG NGINX_IMAGE=nginx:alpine

# Build stage
FROM ${NODE_IMAGE} AS build
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Serve stage
FROM ${NGINX_IMAGE}

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]