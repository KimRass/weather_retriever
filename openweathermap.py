import requests
import json
from collections import Counter

from date import get_cur_date
from weather_codes import weather_codes


class OpenWeatherMap(object):
    def __init__(self, api_key_path="./resources/openweathermap_api_key.txt"):
        self.api_key_path = api_key_path

    def read_api_key(self):
        with open(self.api_key_path, mode="r") as f:
            api_key = f.read().strip()
        return api_key

    def request_coord(self, city, api_key=None, lim=1):
        """
        References:
            https://openweathermap.org/api/geocoding-api
        """
        if api_key is None:
            api_key = self.read_api_key()

        url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit={lim}&appid={api_key}"
        resp = requests.get(url)
        result = json.loads(resp.text)
        if result:
            if "ko" in result[0]["local_names"]:
                city_ko = result[0]["local_names"]["ko"]
            else:
                city_ko = city
            return city_ko, (result[0]["lat"], result[0]["lon"])
        else:
            return city, None

    def request_5days_weather(self, coord, date=None, api_key=None):
        """
        References:
            https://openweathermap.org/api/one-call-3
        """
        if date is None:
            date = get_cur_date()
        if api_key is None:
            api_key = self.read_api_key()

        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={coord[0]}&lon={coord[1]}&appid={api_key}&units=metric"
        resp = requests.get(url)
        result = json.loads(resp.text)

        weather_dict = {}
        for i in result["list"]:
            date, time = i["dt_txt"].split()
            if date not in weather_dict:
                weather_dict[date] = dict()
            if time in ["06:00:00", "09:00:00", "12:00:00", "15:00:00"]:
                time_split = "day"
            else:
                time_split = "night"
            if time_split not in weather_dict[date]:
                weather_dict[date][time_split] = dict()
            weather_dict[date][time_split][time] = {
                "weather": i["weather"][0]["id"], "tempo": i["main"]["temp"],
            }
        return weather_dict

    @staticmethod
    def average_tempos(weather_dict, date):
        def average(ls):
            return sum(ls) / len(ls)

        day_tempos = [v["tempo"] for _, v in weather_dict[date]["day"].items()]
        night_tempos = [v["tempo"] for _, v in weather_dict[date]["night"].items()]
        return round(average(day_tempos)), round(average(night_tempos))

    @staticmethod
    def get_most_common_weathers(weather_dict, date):
        def get_most_common(ls):
            return Counter(ls).most_common(1)[0][0]

        day_weathers = [v["weather"] for _, v in weather_dict[date]["day"].items()]
        night_weathers = [v["weather"] for _, v in weather_dict[date]["night"].items()]
        return (
            weather_codes[get_most_common(day_weathers)]["translation"],
            weather_codes[get_most_common(night_weathers)]["translation"],
        )
