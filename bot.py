import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import aiohttp

TOKEN = os.environ.get("TOKEN", "8199308138:AAHUSipImiY_lNBtohfR9p0yBIyDEU3fxss")
WEATHER_API_KEY = "f91636e9cbe0555edad5ffa9e2680d15"

user_cities = {}

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("старт"))
async def start(message: types.Message):
    await message.answer("Привет! Я погодный бот.\n\n/город (название) - установить город")

@dp.message(Command("помощь"))
async def help(message: types.Message):
    await message.answer("Команды:\n/старт - приветствие\n/город (название) - установить город\n/погода - показать погоду")

@dp.message(Command("город"))
async def set_city(message: types.Message):
    parts = message.text.split()
    if len(parts) > 1:
        city = parts[1]
        user_cities[message.from_user.id] = city
        await message.answer(f"✅ Город установлен: {city}")
    else:
        await message.answer("❌ Пример: /город Москва")

@dp.message(Command("погода"))
async def get_weather(message: types.Message):
    city = user_cities.get(message.from_user.id, "Severodvinsk")
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    temp = data["main"]["temp"]
                    feels_like = data["main"]["feels_like"]
                    description = data["weather"][0]["description"]
                    humidity = data["main"]["humidity"]
                    wind = data["main"]["wind"]["speed"]
                    
                    answer = (f"🌍 Погода в {city}:\n\n"
                              f"🌡 {temp}°C (ощущается как {feels_like}°C)\n"
                              f"☁️ {description.capitalize()}\n"
                              f"💧 Влажность: {humidity}%\n"
                              f"💨 Ветер: {wind} м/с")
                else:
                    answer = f"❌ Город '{city}' не найден"
                await message.answer(answer)
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
