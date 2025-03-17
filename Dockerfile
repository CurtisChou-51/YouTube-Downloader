FROM python:3.9-slim

WORKDIR /app

COPY "src/requirements.txt" .

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY "src/" .

EXPOSE 5000

CMD ["python", "app.py"]
