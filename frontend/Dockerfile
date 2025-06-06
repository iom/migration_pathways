FROM node:20-alpine as build

WORKDIR /app

# Copy package.json
COPY package.json ./

# Install dependencies with npm install instead of npm ci
# since package-lock.json might not exist
RUN npm install

# Copy the rest of the application code
COPY . .

# Create .env file with API URL
RUN echo "VITE_BACKEND_URL = \"/api\"" > .env

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy the build output to replace the default nginx contents
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Add a default favicon to prevent 404 errors
RUN mkdir -p /usr/share/nginx/html/assets
RUN echo "" > /usr/share/nginx/html/favicon.ico

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]