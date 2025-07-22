FROM node:24-alpine

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy the frontend app code
ADD . /app
WORKDIR /app

# Expose port
EXPOSE 3000

CMD ["npm", "run", "dev"]