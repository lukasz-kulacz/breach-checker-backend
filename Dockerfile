FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# --- Etap 2: obraz finalny ---
FROM python:3.12-slim

# Użytkownik non-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

RUN echo "API_KEY=sekret123" > /tmp/klucz.txt
RUN rm /tmp/klucz.txt

# Kopiujemy tylko zainstalowane pakiety, nie cały builder
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["python", "-m", "gunicorn", "-b", "0.0.0.0:5000", "app:app"]