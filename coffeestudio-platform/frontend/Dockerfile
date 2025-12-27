FROM node:20-slim

WORKDIR /app

COPY package.json /app/package.json
COPY tsconfig.json /app/tsconfig.json
COPY next.config.mjs /app/next.config.mjs
COPY next-env.d.ts /app/next-env.d.ts

RUN npm install

COPY . /app

RUN npm run build

EXPOSE 3000
