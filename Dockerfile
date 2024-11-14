FROM python:3.9-slim

WORKDIR /app

# Instalacja wymaganych zależności systemowych
RUN apt-get update && apt-get install -y \
    gcc \
    libsndfile1-dev \
    && rm -rf /var/lib/apt/lists/*

# Skopiuj plik requirements.txt i zainstaluj zależności Pythona
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod aplikacji
COPY . .

# Ustaw punkt wejścia
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
