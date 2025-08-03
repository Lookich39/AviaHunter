import asyncio
from aiogram import Dispatcher
from create_bot import bot
from handlers import register_handlers


async def main():
    dp = Dispatcher()
    register_handlers(dp)
    await dp.start_polling(bot)  # <<< Важно

if __name__ == '__main__':
    asyncio.run(main())  # <<< Запуск asyncio-цикла
