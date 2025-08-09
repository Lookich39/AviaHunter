from aiogram import types, Router
from aiogram.filters import Command
from keyboards.all_keyboards import main_menu  # клавиатура
from db_handlers.db_class import db

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message):
    await db.connect()
    user_id = await db.add_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "👋 Привет! Я бот для отслеживания дешёвых авиабилетов.\n\n"
        "✈ Используй кнопки ниже или команду:\n"
         "<code>/track &lt;код_города_вылета&gt; &lt;код_города_прилёта&gt; "
        "&lt;даты_вылета_через_запятую&gt; &lt;максимальная_цена&gt;</code>\n\n"
        "Пример:\n"
        "<code>/track LED KGD 2025-09-08,2025-09-09 7000</code>",
        reply_markup=main_menu
    )
