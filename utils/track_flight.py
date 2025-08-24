import asyncio
import datetime

from exceptions.all_exceptions import PastDateError, APIError, NoFlightsError
from exceptions.error_handlers import handle_past_date_error, handle_api_error, handle_no_flight_error
from utils.aviasales_api import get_price_for_date, CURRENCY
from utils.airport_codes import get_airport_name
from create_bot import bot
from db_handlers.db_class import db


async def track_flight(
    telegram_id: int,
    origin: str,
    destination: str,
    date: str,
    price_limit: int,
    tracker_id: int,
    settings: dict,
    initial_flight: dict = None,
    check_interval: int = 100
):
    first = True
    while True:
        try:
            # Проверка — дата уже прошла
            flight_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            today = datetime.date.today()

            if today > flight_date:
                raise PastDateError(date, origin, destination)

            # Получаем данные
            if first and initial_flight:
                flight = initial_flight
                first = False
            else:
                flight = await get_price_for_date(origin, destination, date, settings)
            # Проверка на ошибки API
            if not flight or (isinstance(flight, dict) and flight.get("error")):
                await bot.send_message(
                    telegram_id,
                    f"❗ Ошибка получения данных для {get_airport_name(origin)} → {get_airport_name(destination)} на {date}."
                )
                await asyncio.sleep(check_interval)
                continue

            # Цена
            #ВОЗМОЖНО НАДО УБРАТЬ ТК НАХОДИТСЯ В ЦИКЛЕ ТРЕК, А НЕ В ВВОДЕ
            price = flight.get("price")
            if not price or int(price) == 0:
                await bot.send_message(
                    telegram_id,
                    f"❗ Рейсов {get_airport_name(origin)} → {get_airport_name(destination)} на {date} не найдено."
                )
                await asyncio.sleep(check_interval)
                continue

            price = int(price)

            # Получаем предыдущую цену из БД
            last_price = await db.get_last_price(tracker_id)

            # Если цена изменилась — сохраняем и проверяем лимит
            if last_price is None or price != last_price:
                await db.update_last_price(tracker_id, price)

                if price < price_limit:
                    airline = flight.get("airline", "").upper()
                    departure = flight.get("departure_at", "")
                    link = flight.get("link", "")

                    message_text = (
                        f"✈️ <b>{get_airport_name(origin)}</b> → <b>{get_airport_name(destination)}</b>\n"
                        f"📅 Дата: <b>{date}</b>\n"
                        f"Цена: <b>{price} {CURRENCY.upper()}</b>\n"
                        f"Авиакомпания: <b>{airline}</b>\n"
                        f"Вылет: {departure}\n"
                        f"<a href='https://www.aviasales.ru{link}'>🔗 Купить билет</a>"
                    )
                    await bot.send_message(telegram_id, message_text)
        except PastDateError as e:
            await handle_past_date_error(e, telegram_id, tracker_id)
            break

        except APIError as e:
            await handle_api_error(e, telegram_id)
            break

        except NoFlightsError as e:
            await handle_no_flight_error(e, telegram_id)
            break

        except Exception as e:
            print(f"Ошибка в track_flight: {e}")

        await asyncio.sleep(check_interval)
