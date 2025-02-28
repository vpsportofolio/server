import streamlit as st
import requests


TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]


def send_telegram_message(message: str):
    """
    Sends a message to the configured Telegram group/chat.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}

    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"⚠️ Failed to send message: {response.text}")
    else:
        print("✅ Telegram alert sent successfully!")
