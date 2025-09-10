FROM node:22.16.0

WORKDIR /frontend

COPY package.json package-lock.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "dev" "build"]