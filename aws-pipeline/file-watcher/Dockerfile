FROM node:20

# set app directory
WORKDIR /usr/src/app

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
COPY package*.json ./
RUN npm ci

# copy app source
COPY ./*.js .

EXPOSE 4000

CMD [ "node", "app.js" ]