# Build
FROM node:22-slim AS builder

WORKDIR /app

COPY package*.json ./

RUN apt-get update -y && apt-get install -y openssl

RUN npm ci

COPY . .

RUN npx svelte-kit sync

RUN npx prisma generate

RUN npm run build
RUN npm prune --production


# Last stage
FROM node:22-slim

WORKDIR /app

RUN apt-get update -y && apt-get install -y openssl

COPY --from=builder /app/prisma prisma/

COPY --from=builder /app/build build/
COPY --from=builder /app/node_modules node_modules/
COPY package.json .

RUN npx prisma generate

ENV NODE_ENV=production

EXPOSE 3000

CMD ["node", "build"]