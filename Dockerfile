FROM python:3.11-slim

# Ensure Python doesn't buffer output (for logging)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port 80 for App Runner
EXPOSE 80

# Use tee to write to both stdout and log file
CMD ["/bin/sh", "-c", "python restart_on_crash.py 2>&1 | tee logs/docker.log"]