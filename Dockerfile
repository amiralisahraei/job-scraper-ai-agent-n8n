# Base image
FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl unzip gnupg wget \
    chromium-driver \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Set work directory
WORKDIR /app

# Copy project files
COPY ./requirements.txt  .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/ .

# Expose Flask port
EXPOSE 5000

# Run Flask app
CMD ["python", "app.py"]
