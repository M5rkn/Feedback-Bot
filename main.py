import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config.settings import settings
from database.connection import db
from handlers import user, admin


async def main():
    """Запуск бота"""

    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )

    # Подключение к базе данных
    try:
        await db.connect()
    except Exception as e:
        logging.error(f"Не удалось подключиться к базе данных: {e}")
        sys.exit(1)

    # Инициализация бота
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Инициализация диспетчера
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(user.router)
    dp.include_router(admin.router)

    # Удаление вебхука и запуск polling
    await bot.delete_webhook(drop_pending_updates=True)
    
    logging.info("🚀 Бот запущен...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await db.disconnect()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 Бот остановлен")
