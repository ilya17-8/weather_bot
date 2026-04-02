import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import aiohttp
import json

TOKEN = os.environ.get("TOKEN", "8199308138:AAHUSipImiY_lNBtohfR9p0yBIyDEU3fxss")
WEATHER_API_KEY = "f91636e9cbe0555edad5ffa9e2680d15"

user_cities = {}
user_zodiac = {}

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработчик для английской команды /start (Telegram отправляет её автоматически)
@dp.message(Command("start"))
async def start_en(message: types.Message):
    await message.answer("Привет! Я погодный бот.\n\n Напиши /помощь, чтобы узнать что я умею")

@dp.message(Command("старт"))
async def start(message: types.Message):
    await message.answer("Привет, я твой новый помощник.\n\n Напиши /помощь, чтобы узнать что я умею")

@dp.message(Command("помощь"))
async def help(message: types.Message):
    await message.answer("Команды:\n/старт - приветствие\n/город (название) - установить город\n/погода - показать погоду\n/зодиак (знак) - установить знак зодиака\n/гороскоп - показать гороскоп")

@dp.message(Command("город"))
async def set_city(message: types.Message):
    parts = message.text.split()
    if len(parts) > 1:
        city = parts[1:]
        user_cities[message.from_user.id] = city
        await message.answer(f"✅ Город установлен: {city}\nНапиши /погода, чтобы узнать погоду")
    else:
        await message.answer("❌ Пример: /город Москва")

@dp.message(Command("погода"))
async def get_weather(message: types.Message):
    if message.from_user.id not in user_cities:
        await message.answer("❌ Сначала установи город командой /город (название)")
        return
    
    city = user_cities[message.from_user.id]
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                text_response = await response.text()
                
                if response.status == 200:
                    data = json.loads(text_response)
                    
                    temp = data.get("main", {}).get("temp", "Нет данных")
                    feels_like = data.get("main", {}).get("feels_like", "Нет данных")
                    humidity = data.get("main", {}).get("humidity", "Нет данных")
                    
                    wind_data = data.get("wind")
                    if wind_data and isinstance(wind_data, dict):
                        wind = wind_data.get("speed", "Нет данных")
                    else:
                        wind = "Нет данных"
                    
                    weather_list = data.get("weather")
                    if weather_list and len(weather_list) > 0:
                        description = weather_list[0].get("description", "неизвестно")
                    else:
                        description = "неизвестно"
                    
                    answer = (f"🌍 Погода в {city}:\n\n"
                              f"🌡 Температура: {temp}°C\n"
                              f"🤔 Ощущается как: {feels_like}°C\n"
                              f"☁️ {description.capitalize()}\n"
                              f"💧 Влажность: {humidity}%\n"
                              f"💨 Ветер: {wind} м/с")
                else:
                    answer = f"❌ Город '{city}' не найден"
                await message.answer(answer)
        except Exception as e:
            await message.answer(f"❌ Ошибка при получении погоды: {str(e)}")

@dp.message(Command("зодиак"))
async def set_zodiac(message: types.Message):
    parts = message.text.split()
    if len(parts) > 1:
        zodiac = parts[1].lower()
        user_zodiac[message.from_user.id] = zodiac
        await message.answer(f"✅ Знак зодиака установлен: {zodiac.capitalize()}\nНапиши /гороскоп, чтобы узнать гороскоп")
    else:
        await message.answer("❌ Пример: /зодиак рак")

@dp.message(Command("гороскоп"))
async def get_horoscope(message: types.Message):
    if message.from_user.id not in user_zodiac:
        await message.answer("❌ Сначала установи знак зодиака командой /зодиак (название)\nПример: /зодиак рак")
        return
    
    zodiac = user_zodiac[message.from_user.id]
    
    url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={zodiac}&day=today"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    horoscope_text = data["data"]["horoscope_data"]
                    await message.answer(f"🔮 Гороскоп для {zodiac.capitalize()} на сегодня:\n\n{horoscope_text}")
                else:
                    await message.answer("❌ Не удалось получить гороскоп. Попробуй позже.")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

from aiohttp import web

async def health(request):
    return web.Response(text="OK")

async def run_web():
    app = web.Application()
    app.router.add_get('/', health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")
    await asyncio.Event().wait()

async def main():
    await asyncio.gather(
        dp.start_polling(bot),
        run_web()
    )

if __name__ == "__main__":
    asyncio.run(main())
