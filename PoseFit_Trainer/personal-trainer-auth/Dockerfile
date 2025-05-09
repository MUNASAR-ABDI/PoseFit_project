FROM node:18-alpine

WORKDIR /app

# Copy package.json and package-lock.json before other files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy prisma schema
COPY prisma ./prisma/

# Copy environment variables if they exist
COPY .env* ./

# Generate Prisma Client
RUN npx prisma generate

# Copy all files
COPY . .

# Build app
RUN npm run build

# Expose the listening port
EXPOSE 3000

# Run npm start script when container starts
CMD ["npm", "run", "dev"] 