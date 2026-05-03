import os

import httpx
from langchain.tools import Tool

_OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY", "")
_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def _get_weather(location: str) -> str:
    if not _OPENWEATHER_KEY:
        return (
            "Weather service is not configured. "
            "Please set the OPENWEATHER_KEY environment variable."
        )
    try:
        response = httpx.get(
            _BASE_URL,
            params={
                "q": location,
                "appid": _OPENWEATHER_KEY,
                "units": "metric",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        city = data["name"]
        country = data["sys"]["country"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"].capitalize()
        wind_speed = data["wind"]["speed"]

        return (
            f"Weather in {city}, {country}:\n"
            f"  Condition: {description}\n"
            f"  Temperature: {temp}°C (feels like {feels_like}°C)\n"
            f"  Humidity: {humidity}%\n"
            f"  Wind speed: {wind_speed} m/s"
        )
    except httpx.HTTPStatusError as exc:
        return f"Could not retrieve weather for '{location}': HTTP {exc.response.status_code}."
    except Exception as exc:
        return f"Weather lookup failed: {exc}"


weather_tool = Tool(
    name="get_weather",
    func=_get_weather,
    description=(
        "Get the current weather for a given city or location. "
        "Input should be a city name, optionally with a country code "
        "(e.g. 'London' or 'Paris, FR'). "
        "Returns temperature, humidity, wind speed, and conditions."
    ),
)
