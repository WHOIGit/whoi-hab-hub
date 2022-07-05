FROM node:16

WORKDIR /usr/src/app

# To Fix Permissions for Packages
RUN npm config set unsafe-perm true

# Copy package.json to Docker environment
COPY ./habhub-react-frontend/package.json /usr/src/app
COPY ./habhub-react-frontend/package-lock.json /usr/src/app

# Install all node packages
RUN npm install
RUN mkdir -p node_modules/.cache && chmod -R 777 node_modules/.cache