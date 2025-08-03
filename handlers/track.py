from aiogram import types, Router, Dispatcher
from aiogram.filters import Command
from handlers.tasks import user_tasks
from utils.airport_codes import get_airport_name
from create_bot import bot
import asyncio
import aiohttp
import os

API_TOKEN = os.getenv("API_TOKEN")
CURRENCY = "rub"
ONE_WAY = "true"
DIRECT = "false"

router = Router()

async def get_price_for_date(origin: str, destination: str, date_str: str):
    url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
    params = {
        "origin": origin,
        "destination": destination,
        "departure_at": date_str,
        "token": API_TOKEN,
        "cy": CURRENCY,
        "one_way": ONE_WAY,
        "direct": DIRECT,
        "limit": 10,
        "page": 1,
        "sorting": "price",
        "unique": "false"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                if not data.get("success", False):
                    return None
                flights = data.get("data", [])
                return flights[0] if flights else None
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None

async def track_flights(chat_id: int, origin: str, destination: str, dates: list, price_limit: int):
    while True:
        for date in dates:
            flight = await get_price_for_date(origin, destination, date)
            if flight:
                price = flight.get("price", 0)
                if int(price) < price_limit:
                    airline = flight.get("airline", "").upper()
                    departure = flight.get("departure_at", "")
                    link = flight.get("link", "")
                    message_text = (
                        f"✈️ <b>{get_airport_name(origin.upper())} → {get_airport_name(destination.upper())}</b>\n"
                        f"📅 Дата: <b>{date}</b>\n"
                        f"Цена: <b>{price} {CURRENCY.upper()}</b>\n"
                        f"Авиакомпания: <b>{airline}</b>\n"
                        f"Вылет: {departure}\n"
                        f"<a href='https://www.aviasales.ru{link}'>🔗 Купить билет</a>"
                    )

                    try:
                        await bot.send_message(chat_id, message_text)
                    except Exception as e:
                        print(f"Ошибка Telegram: {e}")
        await asyncio.sleep(100)

@router.message(Command("track"))
async def track_command(message: types.Message):
    try:
        args = message.text.split()[1:]  # убираем /track
        if len(args) != 4:
            raise ValueError("Неверное число аргументов")
        origin = args[0].strip().upper()
        destination = args[1].strip().upper()
        dates_str = args[2].strip()
        price_limit = int(args[3])
        dates = [d.strip() for d in dates_str.split(",")]
    except Exception:
        await message.answer("❗ Формат команды:\n<code>/track LED KGD 2025-08-04,2025-08-05 7000</code>")
        return

    await message.answer(
        f"📡 Отслеживаю рейсы <b>{get_airport_name(origin.upper())}</b> → <b>{get_airport_name(destination.upper())}</b> по датам {', '.join(dates)} при цене ниже {price_limit} {CURRENCY.upper()}"
    )
    task = asyncio.create_task(
        track_flights(message.chat.id, origin, destination, dates, price_limit)
    )
    user_tasks.setdefault(message.chat.id, []).append(task)


@router.message(lambda msg: msg.text == "✈ Отслеживать")
async def track_button_handler(message: types.Message):
    await message.answer(
        "📥 Введи команду в формате:\n"
        "<code>/track &lt;код_города_вылета&gt; &lt;код_города_прилёта&gt; "
        "&lt;даты_вылета_через_запятую&gt; &lt;максимальная_цена&gt;</code>\n\n"
        "Пример:\n"
        "<code>/track LED KGD 2025-08-08,2025-08-09 7000</code>\n"
        "• LED — город вылета\n"
        "• KGD — город прилёта\n"
        "• даты через запятую\n"
        "• 7000 — максимальная цена\n\n"
    )

