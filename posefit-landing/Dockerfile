FROM node:20-alpine

WORKDIR /app

# Set environment variables
ENV NEXT_PUBLIC_ASSISTANT_URL=http://posefit-assistant:3000
ENV NEXT_PUBLIC_TRAINER_URL=http://posefit-trainer:3000
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
ENV NEXT_FONT_GOOGLE_MOCKED=true

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the application
RUN npm run build

# Expose the port the app runs on
EXPOSE 3000

# Command to run the application
CMD ["npm", "start"] 