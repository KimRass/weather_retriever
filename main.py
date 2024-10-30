# References:
    # https://openweathermap.org/api/one-call-3
    # https://openweathermap.org/weather-conditions

import requests
import json
from datetime import datetime
from collections import defaultdict, Counter
import xmltodict
from weather_codes import weather_codes, weather_translations


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


def get_avg_tempos(weather_dict, date):
    day_tempos = [v["tempo"] for _, v in weather_dict[date]["day"].items()]
    night_tempos = [v["tempo"] for _, v in weather_dict[date]["night"].items()]
    return round(sum(day_tempos) / len(day_tempos), 1), round(sum(night_tempos) / len(night_tempos), 1)


def get_most_common_weathers(weather_dict, date):
    day_weathers = [v["weather"] for _, v in weather_dict[date]["day"].items()]
    night_weathers = [v["weather"] for _, v in weather_dict[date]["night"].items()]
    return (
        weather_translations[weather_codes[Counter(day_weathers).most_common(1)[0][0]]],
        weather_translations[weather_codes[Counter(night_weathers).most_common(1)[0][0]]],
    )


if __name__ == "__main__":
    city = "Seoul"
    city_ko, coord = request_loc(city)
    cur_weather = request_cur_weather(coord)
    cur_weather
    weather_dict = request_5days_weather(coord)
    date = "2024-11-02"
    day_tempo, night_tempo = get_avg_tempos(weather_dict, date=date)
    day_weather, night_weather = get_most_common_weathers(weather_dict, date=date)
    f"{date}의 {city_ko}의 날씨를 말씀 드리겠습니다. 낮에는 평균 기온 {day_tempo}도의 {day_weather} 날씨가 되겠고, 밤에는 평균 기온 {night_tempo}도의 {night_weather} 날씨가 되겠습니다."
