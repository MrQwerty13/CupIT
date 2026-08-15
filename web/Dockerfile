FROM node:24-alpine AS build
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci --ignore-scripts
COPY web/ ./
RUN npm run build

FROM node:24-alpine
WORKDIR /web
ENV NODE_ENV=production
COPY --from=build /web /web
RUN addgroup -S cupit && adduser -S cupit -G cupit && chown -R cupit:cupit /web
USER cupit
EXPOSE 3000
CMD ["npm", "run", "start", "--", "--host", "0.0.0.0"]
