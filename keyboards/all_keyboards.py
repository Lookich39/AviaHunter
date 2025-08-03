from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✈ Отслеживать"),
            KeyboardButton(text="❌ Остановить"),
        ],
        [
            KeyboardButton(text="ℹ Помощь"),
            KeyboardButton(text="🌍 Коды аэропортов"),  # новая кнопка
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери действие"
)
