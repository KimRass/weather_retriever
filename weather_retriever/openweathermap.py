import requests
import json
from collections import Counter

from weather_retriever.date import get_cur_date
from weather_retriever.weather_codes import weather_codes


class OpenWeatherMap(object):
    def __init__(self, owm_api_key):
        self.owm_api_key = owm_api_key

    def request_coord(self, city, lim=1):
        """
        References:
            https://openweathermap.org/api/geocoding-api

        Fetches the geographical coordinates for a given city.

        Args:
            city (str): Name of the city.
            lim (int): Maximum number of results to return (default is 1).

        Returns:
            tuple: The city name in Korean (if available) and a tuple of (latitude, longitude). Returns (city, None) if no results are found.
        """
        url = (
            f"http://api.openweathermap.org/geo/1.0/direct"
            f"?q={city}&limit={lim}&appid={self.owm_api_key}"
        )
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            result = resp.json()

            if result:
                city_ko = result[0]["local_names"].get("ko", city)
                return city_ko, (result[0]["lat"], result[0]["lon"])
            else:
                return city, None
        except (requests.RequestException, KeyError, ValueError) as e:
            print(f"Error fetching coordinates: {e}")
            return city, None

    def request_5days_weather(self, coord, date=None):
        """
        References:
            https://openweathermap.org/api/one-call-3

        Fetches the 5-day weather forecast for given coordinates.
        
        Args:
            coord (tuple): A tuple of (latitude, longitude).
            date (str): The date for which weather information is required (default is current date).
        
        Returns:
            dict: A nested dictionary containing weather information categorized by day/night.
        """
        if date is None:
            date = get_cur_date()

        url = (
            f"https://api.openweathermap.org/data/2.5/forecast"
            f"?lat={coord[0]}&lon={coord[1]}&appid={self.owm_api_key}&units=metric"
        )
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            result = json.loads(resp.text)

            weather_dict = {}
            for item in result.get("list", []):
                date, time = item["dt_txt"].split()
                if date not in weather_dict:
                    weather_dict[date] = {}
                if time in ["06:00:00", "09:00:00", "12:00:00", "15:00:00"]:
                    time_split = "day"
                else:
                    time_split = "night"
                if time_split not in weather_dict[date]:
                    weather_dict[date][time_split] = {}
                weather_dict[date][time_split][time] = {
                    "weather": item["weather"][0]["id"], "tempo": item["main"]["temp"],
                }
            # 낮에는 `"06:00:00"`, `"09:00:00"`, `"12:00:00"`, `"15:00:00"` 순서로,
            # 밤에는 `"00:00:00"`, `"03:00:00"`, `"18:00:00"`, `"21:00:00"` 순서로 
            # 구성됩니다.
            return weather_dict
        except (requests.RequestException, KeyError, ValueError) as e:
            print(f"Error fetching weather data: {e}")
            return {}

    @staticmethod
    def average_tempos(weather_dict, date):
        """
        Calculates the average temperature for day and night periods.
        
        Args:
            weather_dict (dict): Weather data dictionary.
            date (str): The date to calculate averages for.
        
        Returns:
            tuple: Rounded average temperatures for day and night.
        """
        def average(ls):
            return sum(ls) / len(ls) if ls else None

        day_tempos = [
            time["tempo"] for time in weather_dict.get(date, {}).get("day", {}).values()
        ]
        night_tempos = [
            time["tempo"] for time in weather_dict.get(date, {}).get("night", {}).values()
        ]
        avg_day_tempo = average(day_tempos)
        avg_night_tempo = average(night_tempos)
        return (
            round(avg_day_tempo) if avg_day_tempo is not None else None,
            round(avg_night_tempo) if avg_night_tempo is not None else None,
        )

    @staticmethod
    def get_most_common_weathers(weather_dict, date):
        """
        Determines the most common weather conditions for day and night periods.
        
        Args:
            weather_dict (dict): Weather data dictionary.
            date (str): The date to determine the weather for.
        
        Returns:
            tuple: Translations of the most common weather conditions for day and night.
        """
        def get_most_common_elem(ls):
            return Counter(ls).most_common(1)[0][0] if ls else None

        day_weathers = [
            time["weather"]
            for time in weather_dict.get(date, {}).get("day", {}).values()
        ]
        night_weathers = [
            time["weather"]
            for time in weather_dict.get(date, {}).get("night", {}).values()
        ]
        return (
            weather_codes.get(
                get_most_common_elem(day_weathers), {},
            ).get("translation", None),
            weather_codes.get(
                get_most_common_elem(night_weathers), {},
            ).get("translation", None),
        )
