import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Константы из переменных окружения
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
PORT = int(os.environ.get('PORT', 5000))
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
FLOWISE_API_URL = os.environ.get('FLOWISE_API_URL')  # если есть

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
        text = update['message'].get('text', '').strip()

        if text.startswith("/start"):
            reply_text = "Добро пожаловать! Я Telegram-бот, подключённый к Flowise. Напиши что-нибудь."
        elif text.startswith("/help"):
            reply_text = "Список команд:\n/start — запуск\n/help — помощь"
        else:
            reply_text = generate_flowise_response(text)

        send_message(chat_id, reply_text)

    return {'ok': True}

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

def generate_flowise_response(user_input):
    if not FLOWISE_API_URL:
        return "Flowise API не подключен."

    try:
        response = requests.post(
            FLOWISE_API_URL,
            json={"question": user_input},
            timeout=10
        )
        if response.ok:
            data = response.json()
            return data.get("answer", "Нет ответа от Flowise.")
        else:
            return "Ошибка при обращении к Flowise."
    except Exception as e:
        return f"Ошибка: {e}"

if __name__ == '__main__':
    set_webhook()
    app.run(host='0.0.0.0', port=PORT)

