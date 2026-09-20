FROM node:22-alpine AS dependencies
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup -S flowgard && adduser -S flowgard -G flowgard
COPY --from=builder --chown=flowgard:flowgard /app/package.json /app/package-lock.json ./
COPY --from=builder --chown=flowgard:flowgard /app/node_modules ./node_modules
COPY --from=builder --chown=flowgard:flowgard /app/.next ./.next
COPY --from=builder --chown=flowgard:flowgard /app/public ./public
USER flowgard
EXPOSE 3000
CMD ["npm", "run", "start", "--", "-H", "0.0.0.0"]
