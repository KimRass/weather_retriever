# References:
    # https://openweathermap.org/api/one-call-3
    # https://openweathermap.org/weather-conditions

import requests
import json
from datetime import datetime
import xmltodict


def get_cur_date():
    cur_date = datetime.now().date()
    return cur_date.strftime("%Y-%m-%d")


def read_api_key():
    api_key_path = "/Users/jongbeomkim/Desktop/workspace/weather_api/resources/api_key.txt"
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
    return result[0]["lat"], result[0]["lon"]


def request_cur_weather(coord, api_key=None):
    if api_key is None:
        api_key = read_api_key()


    lang = "kr"
    units = "metric"
    
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={coord[0]}&lon={coord[1]}&appid={api_key}&units={units}"
    resp = requests.get(url)
    return json.loads(resp.text)


def request_5days_weather(coord, date=None, api_key=None):
    if date is None:
        date = get_cur_date()
    if api_key is None:
        api_key = read_api_key()

    lang = "kr"
    units = "metric"

    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={coord[0]}&lon={coord[1]}&appid={api_key}&units={units}"
    resp = requests.get(url)
    result = json.loads(resp.text)
    return [
        (i["weather"][0]["main"], i["main"]["temp"], i["main"]["feels_like"])
        for i in result["list"] if i["dt_txt"].startswith(date)
    ]


if __name__ == "__main__":
    city = "Seoul"
    coord = request_loc(city)
    cur_weather = request_cur_weather(coord)
    cur_weather
    future_weather = request_5days_weather(coord)
    future_weather

    # clouds.all: Cloudiness, %
    print(cur_weather)
    cur_weather["main"]["temp"]
    cur_weather["main"]["feels_like"]
    cur_weather["main"]["humidity"]
    cur_weather["weather"][0]["id"]
    cur_weather["weather"][0]["main"]
