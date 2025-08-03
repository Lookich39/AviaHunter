from aiogram import types, Router
from aiogram.filters import Command
from keyboards.all_keyboards import main_menu  # клавиатура

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для отслеживания дешёвых авиабилетов.\n\n"
        "✈ Используй кнопки ниже или команду:\n"
         "<code>/track &lt;код_города_вылета&gt; &lt;код_города_прилёта&gt; "
        "&lt;даты_вылета_через_запятую&gt; &lt;максимальная_цена&gt;</code>\n\n"
        "Пример:\n"
        "<code>/track LED KGD 2025-08-08,2025-08-09 7000</code>",
        reply_markup=main_menu
    )
