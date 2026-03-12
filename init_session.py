#!/usr/bin/env python3
"""
Inizializzazione sessione Pyrogram
===================================
Esegui questo script UNA SOLA VOLTA per autenticarti su Telegram
e creare il file .session. Dopo l'autenticazione, il file .session
viene salvato e il listener può partire automaticamente.

Uso:
    python init_session.py

Ti verrà chiesto:
  1. Il tuo numero di telefono Telegram
  2. Il codice OTP ricevuto su Telegram
  3. (Opzionale) La password 2FA se attivata
"""

from pyrogram import Client
from config import API_ID, API_HASH, SESSION_NAME

print("=" * 50)
print("🔐 Inizializzazione sessione Pyrogram")
print("=" * 50)
print()
print("Questo script crea il file di sessione necessario")
print("per il Telegram Signal Listener.")
print()
print("Ti verrà chiesto il numero di telefono e il codice OTP.")
print()

with Client(
    name=SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
) as app:
    me = app.get_me()
    print()
    print(f"✅ Autenticazione riuscita!")
    print(f"👤 Utente: {me.first_name} {me.last_name or ''}")
    print(f"📱 Username: @{me.username or 'N/A'}")
    print(f"📁 Sessione salvata: {SESSION_NAME}.session")
    print()
    print("Ora puoi avviare il listener con:")
    print("   python telegram_listener.py")
