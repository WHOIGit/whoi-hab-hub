# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:14 AS builder

LABEL maintainer="Ethan Andrews <eandrews@whoi.edu>"

WORKDIR /app

COPY ./habhub-react-frontend /app

# Install all node packages
RUN npm install && npm run build

# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:alpine

# Set working directory to nginx asset directory
WORKDIR /usr/share/nginx/html

# Remove default nginx static assets
RUN rm -rf ./*

# Copy static assets from builder stage
COPY --from=builder /app/build .

# Copy nginx conf file to
COPY ./compose/production/react-frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Containers run nginx with global directives and daemon off
ENTRYPOINT ["nginx", "-g", "daemon off;"]
