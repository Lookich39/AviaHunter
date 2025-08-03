import asyncio

from aiogram import types, Router
from aiogram.filters import Command
from handlers.tasks import user_tasks

router = Router()

@router.message(Command("stop"))
async def stop_command(message: types.Message):
    chat_id = message.chat.id
    tasks = user_tasks.get(chat_id)

    if not tasks:
        await message.answer("⚠️ Нечего останавливать.")
        return

    count = 0
    for task in tasks:
        if not task.done():
            task.cancel()
            count += 1
            try:
                await task
            except asyncio.CancelledError:
                pass

    user_tasks.pop(chat_id, None)
    await message.answer(f"❌ Остановлено отслеживаний: {count}")


@router.message(lambda msg: msg.text == "❌ Остановить")
async def stop_button(message: types.Message):
    await stop_command(message)
