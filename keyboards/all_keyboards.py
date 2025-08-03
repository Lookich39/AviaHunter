# keyboards/all_keyboards.py

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✈ Отслеживать")],
        [KeyboardButton(text="❌ Остановить"), KeyboardButton(text="ℹ Помощь")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери действие"
)
