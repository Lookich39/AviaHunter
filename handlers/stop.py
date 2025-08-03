from aiogram import types, Router
from aiogram.filters import Command
from handlers.tasks import user_tasks

router = Router()

@router.message(Command("stop"))
async def stop_command(message: types.Message):
    chat_id = message.chat.id
    task = user_tasks.get(chat_id)
    if task and not task.done():
        task.cancel()
        await message.answer("❌ Отслеживание остановлено.")
    else:
        await message.answer("⚠️ Нечего останавливать.")
    user_tasks.pop(chat_id, None)

@router.message(lambda msg: msg.text == "❌ Остановить")
async def stop_button(message: types.Message):
    await stop_command(message)
