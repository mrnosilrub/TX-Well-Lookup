FROM node:20-slim
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
    elif [ -f pnpm-lock.yaml ]; then corepack enable && pnpm i --frozen-lockfile; \
    else npm ci; fi
COPY . .
# default to preview; docker-compose overrides with `npm run dev`
RUN npm run build || true
EXPOSE 4321
CMD ["npm","run","preview","--","--host","0.0.0.0","--port","4321"]