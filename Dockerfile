# ============================================================
# Telegram Signal Listener - Docker Image
# ============================================================
# Multi-purpose: usato sia per l'init della sessione sia per
# il listener in esecuzione continua.
#
# PRIMO AVVIO (autenticazione):
#   docker exec -it <container> python init_session.py
#
# ESECUZIONE NORMALE:
#   Il container parte automaticamente con telegram_listener.py
# ============================================================

FROM python:3.12-slim

# Evita output bufferizzato (logs in tempo reale)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Build tools necessari per compilare tgcrypto (estensione C)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Installa dipendenze prima (cache Docker layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Rimuovi build tools per ridurre dimensione immagine
RUN apt-get purge -y gcc python3-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copia il codice sorgente
COPY config.py .
COPY telegram_listener.py .
COPY init_session.py .

# La sessione viene salvata in /app/sessions/
# Questo path va montato come volume persistente in Coolify
RUN mkdir -p /app/sessions


# Avvio: loop infinito con riavvio automatico in caso di crash
CMD ["sh", "-c", "while true; do python telegram_listener.py; echo 'Riavvio tra 5s...'; sleep 5; done"]
