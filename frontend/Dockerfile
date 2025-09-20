# The docker-compose.[environment].yaml file used will determine
# which of these stages are built and run, based on the 
# "build target" setting for the web service.

# Base: Install dependencies and copy code -----------------------
FROM node:22.16.0-alpine AS base

# Set working directory
WORKDIR /frontend

# Install Node dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy frontend Node/React code
COPY . .


# Local/Development ONLY: Run the dev server ---------------------
FROM base AS local

# Expose the web server port
EXPOSE 3000

# Run the development web server and enable it to 
# accept requests from outside the container (via localhost)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]



# Production ONLY: Build the application and run via nginx -------
FROM base AS build

# Runs the Vite build script (in package.json),
# which builds the optimized production files.
RUN npm run build


# Nginx for serving static files
FROM nginx:stable-alpine AS production

# Copy built frontend files to nginx html folder
COPY --from=build /frontend/dist /usr/share/nginx/html

# Replace default nginx config.
# This enables the nginx to handle React routing
# and reverse proxy rules for the backend API.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose the web server port
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
