FROM node:15

WORKDIR /usr/src/app

# Copies package.json and package-lock.json to Docker environment
COPY ./react-frontend/package.json /usr/src/app

# Install all node packages
RUN yarn install
