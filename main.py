import asyncio
import logging
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
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Подключение к базе данных
    await db.connect()
    
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
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 Бот остановлен")
