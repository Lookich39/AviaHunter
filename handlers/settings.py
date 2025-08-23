from aiogram import Router, types
from db_handlers.db_class import db
from keyboards.all_keyboards import settings_menu, main_menu, transfers_keyboard
from aiogram import F

router = Router()

@router.message(lambda msg: msg.text == "⚙️ Настройки")
async def settings_menu_handler(message: types.Message):
    await message.answer(
        "Выберите настройку:",
        reply_markup=settings_menu
    )
@router.message(lambda msg: msg.text == "🔄 Пересадки: Да / Нет")
async def transfers_settings(message: types.Message):
    user_id = message.from_user.id
    settings = await db.get_user_settings(user_id)
    is_enabled = settings.get("transfers", True)

    text = f"Настройка пересадок: сейчас {'разрешены' if is_enabled else 'запрещены'}"
    if not is_enabled:
        text += "\n\n✈️ Вы выбрали билеты без пересадок, но если таких нет, показываем с пересадками 🔄"

    await message.answer(
        text,
        reply_markup=transfers_keyboard(is_enabled)
    )


@router.message(lambda msg: msg.text == "🔙 Назад")
async def back_to_main(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_menu)

@router.callback_query(F.data == "toggle_transfers")
async def toggle_transfers_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    settings = await db.get_user_settings(user_id)
    new_value = not settings.get("transfers", True)
    await db.update_user_setting(user_id, "transfers_allowed", new_value)

    base_text = f"Настройка пересадок: сейчас {'разрешены' if new_value else 'запрещены'}"
    if not new_value:  # если пересадки запрещены
        base_text += "\n\n✈️ Вы выбрали билеты без пересадок, но если таких нет, показываем с пересадками 🔄"

    await callback.message.edit_text(
        base_text,
        reply_markup=transfers_keyboard(new_value)
    )
    await callback.answer()
