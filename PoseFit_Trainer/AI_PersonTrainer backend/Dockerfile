FROM python:3.9-slim

WORKDIR /app

# Install system dependencies required for OpenCV, MediaPipe
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    ffmpeg \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories with proper permissions
RUN mkdir -p temp_videos static templates user_profiles saved_workouts && \
    chmod -R 755 /app && \
    chown -R nobody:nogroup /app

# Copy env.example file first
COPY env.example .
COPY generate_key.py .

# Generate a secure key for the container if not provided externally
RUN chmod +x generate_key.py && python generate_key.py

# Copy the rest of the application
COPY . .

# Set proper permissions for all files
RUN chmod -R 755 /app && \
    chown -R nobody:nogroup /app

# Expose the port the app runs on
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=180s --retries=5 \
    CMD curl -f http://localhost:8002/health || exit 1

# Switch to non-root user
USER nobody

# Command to run the application
CMD ["python", "api_server.py"] 