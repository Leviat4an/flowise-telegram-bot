import os
from flask import Flask, request
import requests
from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
FLOWISE_API_URL = os.getenv("FLOWISE_API_URL")

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
        message = update['message']
        chat_id = message['chat']['id']

        # Текстовое сообщение
        if 'text' in message:
            text = message['text']

            if text == '/start':
                send_message(chat_id, "Привет! Я бот, помогу с ЖКХ, штрафами и госуслугами.")
                send_main_buttons(chat_id)
            elif text == '/pdf':
                send_message(chat_id, "Отправь текст, и я сгенерирую PDF.")
            elif text.startswith("PDF: "):
                content = text[5:]
                filepath = generate_pdf(content, chat_id)
                send_document(chat_id, filepath)
            else:
                reply = ask_flowise(text)
                send_message(chat_id, reply)

        # Загруженный документ
        elif 'document' in message:
            file_id = message['document']['file_id']
            filename = message['document']['file_name']
            download_document(file_id, filename)
            send_message(chat_id, f"Файл {filename} загружен успешно.")

    return {'ok': True}

def generate_pdf(text, chat_id):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    path = f"{chat_id}_document.pdf"
    pdf.output(path)
    return path

def send_document(chat_id, filepath):
    url = f"{TELEGRAM_API_URL}/sendDocument"
    with open(filepath, 'rb') as doc:
        requests.post(url, data={"chat_id": chat_id}, files={"document": doc})

def download_document(file_id, filename):
    file_info = requests.get(f"{TELEGRAM_API_URL}/getFile?file_id={file_id}").json()
    file_path = file_info["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    response = requests.get(file_url)
    with open(filename, "wb") as f:
        f.write(response.content)

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def send_main_buttons(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": " M-  ЖКХ", "callback_data": "jkh"}],
            [{"text": " ~T Штрафы", "callback_data": "fines"}],
            [{"text": " ~B Госуслуги", "callback_data": "gosuslugi"}]
        ]
    }
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "Выберите категорию:",
        "reply_markup": keyboard
    }
    requests.post(url, json=payload)

def ask_flowise(text):
    response = requests.post(FLOWISE_API_URL, json={"question": text})
    return response.json().get("text", "Нет ответа от Flowise.")
