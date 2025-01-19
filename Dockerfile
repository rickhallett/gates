FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p logs

# If your app needs to accept incoming traffic
EXPOSE 80

CMD ["/bin/sh", "-c", "python main.py 2>&1 | tee logs/docker.log"]