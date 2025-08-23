from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✈ Отслеживать"),
            KeyboardButton(text="❌ Остановить"),
        ],
        [
            KeyboardButton(text="📋 Мои отслеживания"),
        ],
        [
            KeyboardButton(text="ℹ Помощь"),
            KeyboardButton(text="🌍 Коды аэропортов"),
            KeyboardButton(text="⚙️ Настройки"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери действие"
)

settings_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔄 Пересадки: Да / Нет")],
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Настрой параметры отслеживания"
)

def transfers_keyboard(is_enabled: bool) -> InlineKeyboardMarkup:
    text = "Да" if is_enabled else "Нет"
    toggle_text = "Отключить" if is_enabled else "Включить"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"Пересадки: {text}", callback_data=f"toggle_transfers")],
        ]
    )
