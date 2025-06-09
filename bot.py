import os
from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = os.environ.get('TELEGRAM_TOKEN')
PORT = int(os.environ.get('PORT', 5000))
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')  # твой публичный URL на Render + /webhook

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

def set_webhook():
    url = f"{TELEGRAM_API_URL}/setWebhook?url={WEBHOOK_URL}"
    resp = requests.get(url)
    print("Set webhook response:", resp.text)

@app.route('/')
def index():
    return "Hello! Bot is running."

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json

    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')

        reply_text = "Привет! Ты написал: " + text

        send_message(chat_id, reply_text)

    return {'ok': True}

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

if __name__ == '__main__':
    set_webhook()
    app.run(host='0.0.0.0', port=PORT)
