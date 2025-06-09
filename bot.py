import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# Получаем токены из переменных окружения (рекомендуется)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот с OpenAI. Напиши мне что-нибудь.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # Запрос к OpenAI
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=user_text,
        max_tokens=150,
        temperature=0.7,
    )

    reply_text = response.choices[0].text.strip()
    await update.message.reply_text(reply_text)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.T_
