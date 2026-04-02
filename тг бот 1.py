import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import aiohttp

TOKEN = "8199308138:AAHUSipImiY_lNBtohfR9p0yBIyDEU3fxss"
WEATHER_API_KEY = "f91636e9cbe0555edad5ffa9e2680d15"


bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет, я твой новый помощник! Напиши свой город после /setcity")
@dp.message(Command("setcity"))
async def setcity(message: types.Message):
    global CITY
    parts = message.text.split()
    if len(parts) > 1:
        CITY = parts[1]
        await message.answer(f"Город установлен: {CITY}. Узнай погоду написав /weather")
    else:
        await message.answer("Напиши город после команды. Пример: /setcity Северодвинск")

@dp.message(Command("help"))
async def help(message: types.Message):
    await message.answer('Команды:\n/weather — погода в твоём городе\n/start — приветствие\n/setcity - ввод названия твоего города')

@dp.message(Command("weather"))
async def weather(message: types.Message):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            
            if response.status == 200:
                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                description = data["weather"][0]["description"]
                humidity = data["main"]["humidity"]
                wind = data["wind"]["speed"]
                
                answer = (f"🌍 Погода в {CITY}:\n"
                          f"🌡 Температура: {temp}°C\n"
                          f"🤔 Ощущается как: {feels_like}°C\n"
                          f"☁️ {description.capitalize()}\n"
                          f"💧 Влажность: {humidity}%\n"
                          f"💨 Ветер: {wind} м/с")
            else:
                answer = "Не удалось получить погоду. Проверь город или попробуй позже."
            
            await message.answer(answer)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
