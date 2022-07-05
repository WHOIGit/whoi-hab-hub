FROM node:16

RUN ["mkdir", "/install"]
ADD ["./habhub-react-frontend/package.json", "/install"]
ADD ["./habhub-react-frontend/package-lock.json", "/install"]

WORKDIR /install

RUN npm install --verbose
ENV NODE_PATH=/install/node_modules

WORKDIR /usr/src/app


