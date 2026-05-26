# Use the official Microsoft Playwright Python base image
# This image contains Python 3.11/3.12, system dependencies, and is fully configured for headless Chromium out of the box!
FROM mcr.microsoft.com/playwright/python:v1.44.0-noble

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file first to take advantage of Docker layer caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download and install Chromium browser binaries locally inside Playwright
RUN playwright install chromium

# Copy the entire workspace into the container
COPY . /app/

# Run static files collection so that WhiteNoise can serve them efficiently
RUN python manage.py collectstatic --noinput

# Expose the default application port
EXPOSE 8000

# Command to run the production WSGI application with gunicorn
CMD gunicorn focustube.wsgi:application --bind 0.0.0.0:$PORT
