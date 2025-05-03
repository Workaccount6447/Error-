# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot.py .

# Environment variables
ENV TELEGRAM_TOKEN="8123828718:AAGwah8P4HhnGz6NvBpo-UeVIEq0qjzWmZc"
ENV OPENROUTER_MODEL="openai/gpt-3.5-turbo"

# Run the bot
CMD ["python", "bot.py"]
