import json
from typing import Any

import requests

from langflow.custom import Component
from langflow.inputs import DropdownInput, MultilineInput, SecretStrInput, StrInput, MessageInput
from langflow.io import Output
from langflow.schema import Data

class GetWeatherComponent(Component):
    display_name = "Get Weather"
    description = "Get Weather"
    icon = "thermometer-sun"
    name = "GetWeather"
    # legacy = True

    inputs = [
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            info="Your WeatherAPI.com API key",
            advanced=False,
            value="api_key",
            required=True,
        ),
        MessageInput(
            name="city",
            display_name="City",
            info="Specify the name of the city.",
            value="",
            tool_mode=True,
            advanced=False,
        ),
    ]

    outputs=[
        Output(display_name="Data", name="weather", method="get_weather"),
    ]

    async def get_weather(self) -> Data:
        url = f"https://api.weatherapi.com/v1/current.json?key={self.api_key}&q={self.city}&aqi=no"
        print(f"getting weather from {url}")
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            location = data["location"]["name"]
            country = data["location"]["country"]
            condition = data["current"]["condition"]["text"]
            temp_c = data["current"]["temp_c"]
            feels_like = data["current"]["feelslike_c"]
            wind_kph = data["current"]["wind_kph"]
            humidity = data["current"]["humidity"]

            result: dict[str, Any] = {
                "location": location,
                "country": country,
                "condition": condition,
                "temp_c": temp_c,
                "feels_like": feels_like,
                "humidity": humidity,
                "wind_kph": wind_kph
            }
            self.status = result
            return Data(data=result)
        else:
            result: dict[str, Any] = {
                "error": "Please try again later."
            }
            self.status = result
            return Data(data=result)