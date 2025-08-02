import requests
import time
import schedule
from datetime import datetime
import os
from dotenv import load_dotenv

# === Настройки API ===
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
ORIGIN = "LED"
DESTINATION = "KGD"
CURRENCY = "rub"
DATES = ["2025-08-08", "2025-08-09"]
ONE_WAY = "true"
DIRECT = "false"

# === Настройки Telegram ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, data=payload)
        if r.status_code != 200:
            print("⚠️ Ошибка Telegram:", r.text)
    except Exception as e:
        print("⚠️ Telegram отправка не удалась:", e)

def get_price_for_date(date_str):
    url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
    params = {
        "origin": ORIGIN,
        "destination": DESTINATION,
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

    print(f"\n📅 Дата вылета: {date_str}")
    response = requests.get(url, params=params)

    try:
        data = response.json()
    except Exception as e:
        print("❌ Ошибка JSON:", e)
        print(response.text[:500])
        return

    if not data.get("success", False):
        print("❌ API-ошибка:", data)
        return

    flights = data.get("data", [])
    if not flights:
        print("⚠️ Билеты не найдены.")
        return

    # Находим самый дешёвый билет
    cheapest = flights[0]
    price = cheapest["price"]
    airline = cheapest["airline"]
    departure = cheapest["departure_at"]
    link = cheapest.get("link", "")
    message = (
        f"✈️ <b>{date_str}</b>\n"
        f"Цена: <b>{price} {CURRENCY.upper()}</b>\n"
        f"Авиакомпания: <b>{airline.upper()}</b>\n"
        f"Вылет: {departure}\n"
        f"<a href='https://www.aviasales.ru{link}'>🔗 Купить билет</a>"
    )
    if int(price) < 4000:
        print("✅ Отправка уведомления в Telegram...")
        send_telegram_message(message)

def job():
    print(f"\n=== Запуск парсера {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    for date in DATES:
        get_price_for_date(date)

# Планировщик: каждые 5 минут
schedule.every(5).minutes.do(job)

print("🚀 Парсер Aviasales API с Telegram запущен")
job()

while True:
    schedule.run_pending()
    time.sleep(1)
