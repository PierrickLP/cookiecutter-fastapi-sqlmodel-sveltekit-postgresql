# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:19-alpine as build-stage

WORKDIR /app

COPY package*.json /app/

RUN npm install

COPY ./ /app/

ARG FRONTEND_ENV=production

ENV VITE_APP_ENV=${FRONTEND_ENV}

# Comment out the next line to disable tests
#RUN npm run test:unit

RUN npm run build


# Stage 1, based on Node, to have only the compiled app
FROM node:19-alpine

WORKDIR /app
COPY --from=build-stage /app .

RUN npm install dotenv

ENV PORT=80
CMD ["node", "-r", "dotenv/config", "build"]
