import requests
import datetime
from config import open_weather_token


def get_weather(city):
    code_to_smile = {
        "Clear": "☀️ Clear",
        "Clouds": "☁️ Clouds",
        "Rain": "🌧️ Rain",
        "Drizzle": "🌦️ Drizzle",
        "Thunderstorm": "⚡️ Thunderstorm",
        "Snow": "❄️ Snow",
        "Mist": "🌫️ Mist"
    }

    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={open_weather_token}&units=metric",
            timeout=10
        )
        data = r.json()

        if data.get("cod") != 200:
            raise ValueError("City not found")

        city = data["name"]
        cur_weather = data["main"]["temp"]
        weather_description = data["weather"][0]["main"]
        wd = code_to_smile.get(weather_description, "Look outside!")

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        day_length = sunset - sunrise

        print(f"\n*** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} ***")
        print(f"📍 City: {city}")
        print(f"🌡 Temperature: {cur_weather}°C {wd}")
        print(f"💧 Humidity: {humidity}%")
        print(f"🔵 Pressure: {pressure} hPa")
        print(f"💨 Wind: {wind} m/s")
        print(f"🌅 Sunrise: {sunrise.strftime('%H:%M:%S')}")
        print(f"🌇 Sunset: {sunset.strftime('%H:%M:%S')}")
        print(f"🕒 Day Length: {day_length}")
        print("✅ Have a good day!")

    except Exception as ex:
        print("❌ Error:", ex)
        print("⚠️ Check the city name.")


def get_5_day_forecast(city):
    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={open_weather_token}&units=metric&cnt=40",
            timeout=10
        )
        data = r.json()

        if data.get("cod") != "200":
            print("[DEBUG] API response:", data)
            print("⚠️ Forecast not available.")
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

        print("\n📆 *** 5-Day Forecast ***")
        for i, (date, values) in enumerate(forecast_by_day.items()):
            if i >= 5:
                break
            avg_temp = sum(values["temps"]) / len(values["temps"])
            common_desc = max(set(values["descriptions"]), key=values["descriptions"].count).capitalize()
            dt = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%A, %d %B")
            print(f"{dt}: 🌤 {common_desc}, 🌡 Avg Temp: {avg_temp:.1f}°C")

    except Exception as ex:
        print("❌ Error while getting forecast:", ex)


def main():
    city = input("🌍 Enter city name: ").strip()
    if not city:
        print("⚠️ No city entered.")
        return
    print("\n📌 Current Weather:")
    get_weather(city)
    print("\n📌 5-Day Forecast:")
    get_5_day_forecast(city)

if __name__ == '__main__':
    main()