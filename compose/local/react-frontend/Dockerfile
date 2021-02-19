FROM node:15

WORKDIR /usr/src/app

# Copy package.json to Docker environment
COPY ./habhub-react-frontend/package.json /usr/src/app
COPY ./habhub-react-frontend/yarn.lock /usr/src/app

# Install all node packages
RUN yarn
