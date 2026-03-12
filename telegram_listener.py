#!/usr/bin/env python3
"""
Telegram Signal Listener
========================
Ascolta messaggi in tempo reale da canali Telegram pubblici
e li inoltra via HTTP POST a un webhook n8n.

Usa Pyrogram (client MTProto) per ricevere messaggi come utente,
non come bot. Richiede autenticazione interattiva al primo avvio.

Autore: Dario
"""

import asyncio
import json
import logging
import sys
from datetime import datetime

import httpx
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    FloodWait,
    ConnectionError as PyrogramConnectionError,
)

from config import (
    API_ID,
    API_HASH,
    WEBHOOK_URL,
    CANALI,
    SESSION_NAME,
    WEBHOOK_TIMEOUT,
    WEBHOOK_MAX_RETRIES,
    WEBHOOK_RETRY_DELAY,
)

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("TelegramListener")

# ── Pyrogram Client ──────────────────────────────────────────
# Rimuovi @ dai nomi dei canali per i filtri Pyrogram
channel_usernames = [ch.lstrip("@") for ch in CANALI]

app = Client(
    name=SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
)


# ── Webhook sender con retry ────────────────────────────────
async def send_to_webhook(payload: dict) -> bool:
    """
    Invia il payload JSON al webhook n8n.
    Ritenta fino a WEBHOOK_MAX_RETRIES volte in caso di errore.
    Ritorna True se il POST ha avuto successo, False altrimenti.
    """
    for attempt in range(1, WEBHOOK_MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=WEBHOOK_TIMEOUT) as client:
                response = await client.post(WEBHOOK_URL, json=payload)

            if response.status_code < 400:
                logger.info(
                    f"✅ Webhook POST riuscito (HTTP {response.status_code}) "
                    f"| Tentativo {attempt}/{WEBHOOK_MAX_RETRIES}"
                )
                return True
            else:
                logger.warning(
                    f"⚠️  Webhook ha risposto HTTP {response.status_code} "
                    f"| Tentativo {attempt}/{WEBHOOK_MAX_RETRIES}"
                )
        except httpx.TimeoutException:
            logger.warning(
                f"⏱️  Webhook timeout dopo {WEBHOOK_TIMEOUT}s "
                f"| Tentativo {attempt}/{WEBHOOK_MAX_RETRIES}"
            )
        except httpx.ConnectError as e:
            logger.warning(
                f"🔌 Connessione al webhook fallita: {e} "
                f"| Tentativo {attempt}/{WEBHOOK_MAX_RETRIES}"
            )
        except Exception as e:
            logger.error(
                f"❌ Errore webhook inaspettato: {e} "
                f"| Tentativo {attempt}/{WEBHOOK_MAX_RETRIES}"
            )

        if attempt < WEBHOOK_MAX_RETRIES:
            logger.info(f"⏳ Retry tra {WEBHOOK_RETRY_DELAY}s...")
            await asyncio.sleep(WEBHOOK_RETRY_DELAY)

    logger.error(
        f"💀 Webhook POST fallito dopo {WEBHOOK_MAX_RETRIES} tentativi! "
        f"Messaggio perso: channel={payload.get('channel')}, "
        f"message_id={payload.get('message_id')}"
    )
    return False


# ── Serializzazione messaggio ────────────────────────────────
def serialize_message(message: Message) -> dict:
    """
    Converte un oggetto Message di Pyrogram in un dict JSON-serializzabile.
    Pyrogram's str(message) restituisce una rappresentazione JSON valida.
    """
    try:
        return json.loads(str(message))
    except (json.JSONDecodeError, TypeError):
        # Fallback: ritorna solo i campi essenziali
        return {
            "id": message.id,
            "date": message.date.isoformat() if message.date else None,
            "text": message.text or message.caption or "",
        }


# ── Handler messaggi ────────────────────────────────────────
@app.on_message(filters.chat(channel_usernames))
async def on_new_message(client: Client, message: Message):
    """
    Handler chiamato per ogni nuovo messaggio nei canali monitorati.
    Estrae i dati rilevanti e li invia al webhook n8n.
    """
    # Identifica il canale
    channel = (
        f"@{message.chat.username}"
        if message.chat.username
        else str(message.chat.id)
    )

    # Estrai il testo (può essere in text o caption per i media)
    text = message.text or message.caption or ""

    # Log del messaggio ricevuto
    preview = text[:80].replace("\n", " ") if text else "[media/no text]"
    logger.info(
        f"📩 Nuovo messaggio | Canale: {channel} | ID: {message.id} | "
        f"Preview: {preview}"
    )

    # Prepara il payload per il webhook
    payload = {
        "channel": channel,
        "message_id": message.id,
        "text": text,
        "date": message.date.isoformat() if message.date else None,
        "raw": serialize_message(message),
    }

    # Invia al webhook
    await send_to_webhook(payload)


# ── Evento connessione ──────────────────────────────────────
@app.on_connect()
async def on_connect(client: Client):
    logger.info("🔗 Connesso a Telegram!")


@app.on_disconnect()
async def on_disconnect(client: Client):
    logger.warning("🔌 Disconnesso da Telegram. Pyrogram tenterà la riconnessione automatica...")


# ── Main ─────────────────────────────────────────────────────
def main():
    """Punto di ingresso principale."""
    logger.info("=" * 60)
    logger.info("🚀 Telegram Signal Listener - Avvio")
    logger.info(f"📡 Canali monitorati ({len(CANALI)}):")
    for ch in CANALI:
        logger.info(f"   • {ch}")
    logger.info(f"🌐 Webhook: {WEBHOOK_URL}")
    logger.info(f"📁 Sessione: {SESSION_NAME}.session")
    logger.info("=" * 60)

    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("👋 Arresto manuale (Ctrl+C)")
    except Exception as e:
        logger.critical(f"💀 Errore fatale: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
