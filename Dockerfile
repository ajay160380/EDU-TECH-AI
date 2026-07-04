# Use the official Microsoft Playwright Python base image
# This image contains Python 3.11/3.12, system dependencies, and is fully configured for headless Chromium out of the box!
FROM mcr.microsoft.com/playwright/python:v1.47.0-noble

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860

# Hugging Face Spaces requires a non-root user (id 1000).
# The base image already contains a user with UID 1000, so we just switch to it.
RUN mkdir -p /app && chown -R 1000:1000 /app
USER 1000
ENV HOME=/app \
    PATH=/app/.local/bin:$PATH

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file first to take advantage of Docker layer caching
COPY --chown=1000:1000 requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download and install Chromium browser binaries locally inside Playwright
RUN playwright install chromium

# Copy the entire workspace into the container
COPY --chown=1000:1000 . /app/

# Run static files collection so that WhiteNoise can serve them efficiently
RUN python manage.py collectstatic --noinput

# Expose the default application port
EXPOSE 7860

# Command to run the production WSGI application with gunicorn
CMD python manage.py migrate --noinput && gunicorn focustube.wsgi:application --bind 0.0.0.0:$PORT
