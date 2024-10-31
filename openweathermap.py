# References:
    # https://openweathermap.org/api/one-call-3
    # https://openweathermap.org/weather-conditions

import requests
import json
from datetime import datetime, timedelta

today = datetime.now()
date_after_3_days = today + timedelta(days=3)
date_after_3_days.strftime("%Y-%m-%d")


def get_cur_date():
    cur_date = datetime.now().date()
    return cur_date.strftime("%Y-%m-%d")


def read_api_key():
    api_key_path = "/Users/jongbeomkim/Desktop/workspace/weather_api/resources/openweather_api_key.txt"
    with open(api_key_path, mode="r") as f:
        api_key = f.read().strip()
    return api_key


def request_loc(city, api_key=None, lim=1):
    """
    References:
        https://openweathermap.org/api/geocoding-api
    """
    if api_key is None:
        api_key = read_api_key()

    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit={lim}&appid={api_key}"
    resp = requests.get(url)
    result = json.loads(resp.text)
    return result[0]["local_names"]["ko"], (result[0]["lat"], result[0]["lon"])


def request_cur_weather(coord, api_key=None):
    if api_key is None:
        api_key = read_api_key()


    # lang = "kr"
    units = "metric"
    
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={coord[0]}&lon={coord[1]}&appid={api_key}&units={units}"
    resp = requests.get(url)
    return json.loads(resp.text)


def request_5days_weather(coord, date=None, api_key=None):
    if date is None:
        date = get_cur_date()
    if api_key is None:
        api_key = read_api_key()

    # lang = "kr"
    units = "metric"

    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={coord[0]}&lon={coord[1]}&appid={api_key}&units={units}"
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


# if __name__ == "__main__":
#     city = "Seoul"
#     city_ko, coord = request_loc(city)
#     cur_weather = request_cur_weather(coord)
#     cur_weather
#     weather_dict = request_5days_weather(coord)
