FROM python:3.13-slim

WORKDIR /app

COPY requirements-production.txt ./
RUN pip install --no-cache-dir -r requirements-production.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=5000

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --threads 4 --timeout 60 wsgi:app"]
