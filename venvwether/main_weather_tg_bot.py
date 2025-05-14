import asyncio
import datetime
import requests
from collections import defaultdict

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties

from config import tg_bot_token, open_weather_token

bot = Bot(
    token=tg_bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

user_mode = defaultdict(lambda: "now")  # За замовчуванням – поточна погода


@dp.message(F.text == "/start")
async def start_command(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌤 Now", callback_data="now")],
        [InlineKeyboardButton(text="📆 5-day Forecast", callback_data="week")]
    ])
    await message.answer("Hello! Choose type of weather forecast:", reply_markup=keyboard)


@dp.callback_query()
async def handle_forecast_type(callback: types.CallbackQuery):
    user_mode[callback.from_user.id] = callback.data
    await callback.message.answer("Great! Now enter the city name 🏙")
    await callback.answer()


@dp.message(F.text)
async def handle_city_input(message: Message):
    mode = user_mode[message.from_user.id]
    city = message.text.strip()

    if mode == "now":
        await send_current_weather(message, city)
    elif mode == "week":
        await send_5_day_forecast(message, city)
    else:
        await message.answer("❓ Please choose forecast type using /start")


async def send_current_weather(message: Message, city: str):
    code_to_smile = {
        "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧", "Drizzle": "🌦",
        "Thunderstorm": "⚡️", "Snow": "❄️", "Mist": "🌫"
    }

    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={open_weather_token}&units=metric",
            timeout=10
        )
        data = r.json()
        if data.get("cod") != 200:
            raise Exception("City not found")

        city_name = data["name"]
        temp = data["main"]["temp"]
        weather_description = data["weather"][0]["main"]
        wd = code_to_smile.get(weather_description, "🤷‍♂️")

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        day_length = sunset - sunrise

        await message.reply(
            f"📅 <b>{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</b>\n"
            f"📍 <b>Weather in: {city_name}</b>\n"
            f"🌡 Temperature: {temp}°C {wd}\n"
            f"💧 Humidity: {humidity}%\n"
            f"🔵 Pressure: {pressure} hPa\n"
            f"💨 Wind speed: {wind} m/s\n"
            f"🌅 Sunrise: {sunrise.strftime('%H:%M:%S')}\n"
            f"🌇 Sunset: {sunset.strftime('%H:%M:%S')}\n"
            f"🕒 Day length: {day_length}\n\n"
            f"✅ Have a nice day!"
        )

    except Exception as ex:
        print("[ERROR]", ex)
        await message.reply("⚠️ City not found or wrong input. Please try again.")


async def send_5_day_forecast(message: Message, city: str):
    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={open_weather_token}&units=metric&cnt=40",
            timeout=10
        )
        data = r.json()

        if data.get("cod") != "200":
            print("[DEBUG] API response:", data)
            await message.answer("⚠️ Forecast not available.")
            return
        
        forecast_by_day = {}
        for entry in data["list"]:
            date = entry["dt_txt"].split(" ")[0]
            temp = entry["main"]["temp"]
            desc = entry["weather"][0]["description"]
            if date not in forecast_by_day:
                forecast_by_day[date] = {
                    "temps": [],
                    "descriptions": []
                }
            forecast_by_day[date]["temps"].append(temp)
            forecast_by_day[date]["descriptions"].append(desc)

        msg = f"<b>📆 5-day forecast for {city.title()}:</b>\n\n"
        for i, (date, values) in enumerate(forecast_by_day.items()):
            if i >= 5:
                break
            avg_temp = sum(values["temps"]) / len(values["temps"])
            common_desc = max(set(values["descriptions"]), key=values["descriptions"].count).capitalize()
            dt = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%A, %d %B")
            msg += f"📅 {dt}:\n🌤 {common_desc}\n🌡 Avg Temp: {avg_temp:.1f}°C\n\n"

        await message.answer(msg)

    except Exception as ex:
        print("[ERROR forecast]", ex)
        await message.answer("❌ Failed to get forecast data.")


async def main():
    print("Bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())