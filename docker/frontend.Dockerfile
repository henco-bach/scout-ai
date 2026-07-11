FROM node:22-slim AS base
WORKDIR /app

FROM base AS deps
COPY package.json ./
COPY apps/frontend/package.json apps/frontend/package.json
COPY packages/shared/package.json packages/shared/package.json
# No package-lock.json here on purpose: npm's minimal lockfile only records
# optional native deps (lightningcss/swc) for the platform that generated it
# (macOS), so a lockfile-bound install can't find the Linux binaries this
# container needs. Resolving fresh here picks the right platform each time.
RUN npm install

FROM base AS build
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build --workspace=frontend

FROM base AS runner
ENV NODE_ENV=production
COPY --from=build /app/apps/frontend/public ./apps/frontend/public
COPY --from=build /app/apps/frontend/.next/standalone ./
COPY --from=build /app/apps/frontend/.next/static ./apps/frontend/.next/static

EXPOSE 3000
CMD ["node", "apps/frontend/server.js"]
