FROM node:16

WORKDIR /usr/src/app
RUN useradd worker

# Copy package.json to Docker environment
COPY ./habhub-react-frontend/package.json /usr/src/app
COPY ./habhub-react-frontend/package-lock.json /usr/src/app

# Install all node packages
RUN npm install

RUN chown -R worker /usr/src/app
USER worker
