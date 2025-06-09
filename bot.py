import os
from flask import Flask, request
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
FLOWISE_API_URL = os.environ.get('FLOWISE_API_URL')

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

def set_webhook():
    url = f"{TELEGRAM_API_URL}/setWebhook?url={WEBHOOK_URL}"
    resp = requests.get(url)
    print("Set webhook response:", resp.text)

@app.route('/')
def index():
    return "Бот запущен."

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')

        if text == '/start':
            send_message(chat_id, " ~K Привет! Я AI-помощник по ЖКХ, штрафам и госуслугам.\n\n\nВыбери тему или задай свой вопрос.")
            send_main_buttons(chat_id)

        elif text == '/шаблоны':
            send_message(chat_id, " ~D Вот некоторые шаблоны:\n\n\n1. Жалоба в управляющую компанию\n2. Запрос в МФЦ\n3. Объяснение по штрафу\n\n(в будущем сюда можно прикрутить PDF/Word генератор)")

        else:
            reply = ask_flowise(text)
            send_message(chat_id, reply)

    elif 'callback_query' in update:
        query = update['callback_query']
        chat_id = query['message']['chat']['id']
        data = query['data']

        if data == 'jkh':
            send_message(chat_id, "🏠 Вопрос по ЖКХ? Напиши его.")
        elif data == 'fines':
            send_message(chat_id, "💸 Вопрос по штрафам? Напиши его.")
        elif data == 'gosuslugi':
            send_message(chat_id, "🛂 Что интересует по Госуслугам? Я постараюсь помочь.")

    return {'ok': True}

def send_main_buttons(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "🏠 ЖКХ", "callback_data": "jkh"}],
            [{"text": "💸 Штрафы", "callback_data": "fines"}],
            [{"text": "🛂 Госуслуги", "callback_data": "gosuslugi"}]
        ]
    }
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "Выберите тему:",
        "reply_markup": keyboard
    }
    requests.post(url, json=payload)

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

def ask_flowise(question):
    headers = {"Content-Type": "application/json"}
    payload = {"question": question}
    response = requests.post(FLOWISE_API_URL, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get('text', 'Нет ответа от Flowise.')
    return 'Ошибка при запросе к Flowise.'
