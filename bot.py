import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import aiohttp
import json

TOKEN = os.environ.get("TOKEN", "8199308138:AAHUSipImiY_lNBtohfR9p0yBIyDEU3fxss")
WEATHER_API_KEY = "f91636e9cbe0555edad5ffa9e2680d15"

user_cities = {}

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработчик для английской команды /start (Telegram отправляет её автоматически)
@dp.message(Command("start"))
async def start_en(message: types.Message):
    await message.answer("Привет! Я погодный бот.\n\n/город (название) - установить город")

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
        await message.answer(f"✅ Город установлен: {city}\n Напиши /погода, чтобы узнать погоду на данный момент")
    else:
        await message.answer("❌ Пример: /город Москва")

@dp.message(Command("погода"))
async def get_weather(message: types.Message):
    # Проверяем, установлен ли город
    if message.from_user.id not in user_cities:
        await message.answer("❌ Сначала установи город командой /город (название)")
        return
    
    city = user_cities[message.from_user.id]
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                # Получаем текст ответа для отладки
                text_response = await response.text()
                
                if response.status == 200:
                    data = json.loads(text_response)
                    
                    # Безопасное получение каждого поля
                    temp = data.get("main", {}).get("temp", "Нет данных")
                    feels_like = data.get("main", {}).get("feels_like", "Нет данных")
                    humidity = data.get("main", {}).get("humidity", "Нет данных")
                    
                    # Ветер с проверкой
                    wind_data = data.get("wind")
                    if wind_data and isinstance(wind_data, dict):
                        wind = wind_data.get("speed", "Нет данных")
                    else:
                        wind = "Нет данных"
                    
                    # Описание погоды
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
                    answer = f"❌ Город '{city}' не найден (статус: {response.status})"
                await message.answer(answer)
        except Exception as e:
            await message.answer(f"❌ Ошибка при получении погоды: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
