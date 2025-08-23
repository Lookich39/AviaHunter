from aiogram import types, Router
from aiogram.filters import Command
import asyncio

from db_handlers.db_class import db
from handlers.task import user_tasks
from utils.track_flight import track_flight
from utils.airport_codes import get_airport_name
from utils.aviasales_api import CURRENCY, get_price_for_date
from utils.validators import is_valid_date

router = Router()

MAX_ACTIVE_TRACKERS = 5


@router.message(Command("track"))
async def track_command(message: types.Message):
    await db.connect()
    try:
        args = message.text.split()[1:]  # убираем /track
        if len(args) != 4:
            raise ValueError("Неверное число аргументов")

        origin = args[0].strip().upper()
        destination = args[1].strip().upper()
        dates = [d.strip() for d in args[2].split(",") if d.strip()]

        try:
            price_limit = int(args[3])
        except ValueError:
            await message.answer("❗ Неверный формат цены. Пример: 7000")
            return

        user_id = await db.add_user(message.from_user.id, message.from_user.username)
        settings = await db.get_user_settings(message.from_user.id)
        active_count = await db.count_active_trackers(user_id)
        allowed_slots = MAX_ACTIVE_TRACKERS - active_count

        if allowed_slots <= 0:
            await message.answer(
                f"⚠ У вас уже {active_count} активных отслеживаний. "
                f"Максимум разрешено {MAX_ACTIVE_TRACKERS}."
            )
            return

        origin_name = get_airport_name(origin) or origin
        destination_name = get_airport_name(destination) or destination
        await message.answer(
            f"📡 Начинаю отслеживание рейсов <b>{origin_name}</b> → <b>{destination_name}</b>\n"
            f"Даты: <b>{', '.join(dates)}</b>\n"
            f"Цена ниже <b>{price_limit} {CURRENCY.upper()}</b>"
        )

        skipped = []  # список кортежей (date, reason)

        for date in dates:
            # 1) проверка формата/прошлого времени
            if not is_valid_date(date):
                skipped.append((date, "неверная дата (формат YYYY-MM-DD или дата в прошлом)"))
                continue

            # 2) проверка наличия слотов
            if allowed_slots <= 0:
                skipped.append((date, "нет свободных слотов (достигнут лимит)"))
                continue

            # 3) проверка через API (валидность IATA + есть ли рейсы на эту дату)
            flight = await get_price_for_date(origin, destination, date, settings)
            if not flight or (isinstance(flight, dict) and flight.get("error")):
                skipped.append((date, "рейсы не найдены (проверь IATA-коды и дату)"))
                continue

            # 4) проверка дубликата в БД
            if await db.tracker_exists(user_id, origin, destination, date):
                skipped.append((date, "уже отслеживается"))
                continue

            tracker_id = await db.add_flight_tracker(user_id, origin, destination, date, price_limit)

            user_tasks.setdefault(message.from_user.id, [])
            task = asyncio.create_task(
                track_flight(
                    message.from_user.id,
                    origin,
                    destination,
                    date,
                    price_limit,
                    tracker_id,
                    settings,
                    initial_flight=flight  # если track_flight поддерживает этот параметр
                )
            )
            user_tasks[message.from_user.id].append(task)
            allowed_slots -= 1
        '''
        # Ответ пользователю: только по реально добавленным датам
        if added_dates:
            origin_name = get_airport_name(origin) or origin
            destination_name = get_airport_name(destination) or destination
            await message.answer(
                f"📡 Отслеживаю рейсы <b>{origin_name}</b> → <b>{destination_name}</b>\n"
                f"Даты: <b>{', '.join(added_dates)}</b>\n"
                f"Цена ниже <b>{price_limit} {CURRENCY.upper()}</b>"
            )
        '''
        # Сводка по пропущенным датам (если есть)
        if skipped:
            lines = [f"• {d} — {reason}" for d, reason in skipped]
            await message.answer("⚠ Пропущены даты:\n" + "\n".join(lines))

    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer(
            "❗ Формат команды:\n<code>/track LED KGD 2025-08-04,2025-08-05 7000</code>"
        )


@router.message(lambda msg: msg.text == "✈ Отслеживать")
async def track_button_handler(message: types.Message):
    await message.answer(
        "📥 Введи команду в формате:\n"
        "<code>/track &lt;код_города_вылета&gt; &lt;код_города_прилёта&gt; "
        "&lt;даты_вылета_через_запятую&gt; &lt;максимальная_цена&gt;</code>\n\n"
        "Пример:\n"
        "<code>/track LED KGD 2025-09-08,2025-09-09 7000</code>\n"
        "• LED — город вылета\n"
        "• KGD — город прилёта\n"
        "• даты через запятую\n"
        "• 7000 — максимальная цена\n\n"
    )
