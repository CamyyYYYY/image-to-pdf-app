FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    imagemagick \
    libmagickwand-dev \
    tk \
    tk-dev \
    python3-tk \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]