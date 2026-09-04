FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including ffmpeg for video rendering and fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run the bot under a production WSGI server.
# One worker so the webhook is registered exactly once; threads handle concurrent Telegram updates.
CMD gunicorn bot:app --bind 0.0.0.0:${PORT:-5000} --workers 1 --threads 8 --timeout 120 --access-logfile -
