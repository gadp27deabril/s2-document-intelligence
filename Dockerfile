# S2 Document Intelligence - Community Edition
# Docker image for easy deployment

FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 5000

# Set environment variables
ENV PORT=5000
ENV HOST=0.0.0.0
ENV LOG_LEVEL=INFO

# Run application
CMD ["python", "main.py"]
