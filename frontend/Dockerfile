FROM node:22.16.0-alpine

# Set working directory
WORKDIR /frontend

# Install Node dependencies
COPY package*.json ./
RUN npm install

# Copy frontend Node/React code
COPY . .

# Expose the web server port
EXPOSE 3000

# Run the development web server and enable it to 
# accept requests from outside the container (via localhost)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
