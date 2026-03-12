# ============================================================
# Telegram Signal Listener - Configurazione
# ============================================================
# Modifica questo file per aggiungere/rimuovere canali,
# cambiare il webhook URL o aggiornare le credenziali Telegram.
# ============================================================

# Credenziali Telegram API (da https://my.telegram.org)
API_ID = 33227823
API_HASH = "9037fa7b7aed573b844a8ca19bf55876"

# URL del webhook n8n dove inviare i messaggi
WEBHOOK_URL = "https://automation.growbe.cloud/webhook/telegram-signal-trading"

# Lista dei canali Telegram da monitorare
# Aggiungi gli username con @ davanti
CANALI = [
    "@FXNLofficial",
]

# Nome del file di sessione Pyrogram (senza estensione)
SESSION_NAME = "sessions/telegram_listener"

# Timeout per le richieste HTTP al webhook (secondi)
WEBHOOK_TIMEOUT = 30

# Numero massimo di tentativi per il webhook in caso di errore
WEBHOOK_MAX_RETRIES = 3

# Pausa tra i tentativi di retry (secondi)
WEBHOOK_RETRY_DELAY = 5
