FROM node:15

WORKDIR /usr/src/app

# Copy package.json to Docker environment
COPY ./react-frontend/package.json /usr/src/app
COPY ./react-frontend/yarn.lock /usr/src/app

# Install all node packages
RUN yarn
