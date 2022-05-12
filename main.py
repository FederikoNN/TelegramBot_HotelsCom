# from aiogram import executor
import logging

from aiogram.utils.executor import start_webhook

from botrequests import *
import log_and_errors
from loader import dp, db, bot, SSL_CERTIFICATE, ssl_context
from config import WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Устанавливаем webhook
    await bot.set_webhook(url=WEBHOOK_URL, certificate=SSL_CERTIFICATE)
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)
    # Уведомляет про запуск
    await on_startup_notify(dispatcher)
    # Создаем таблицы в БД
    try:
        db.create_table_users()
        db.create_table_history()
    except Exception as e:
        logging.exception(e)


if __name__ == '__main__':
    # executor.start_polling(dp, on_startup=on_startup)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
        ssl_context=ssl_context
    )
