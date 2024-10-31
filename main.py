import re
from collections import defaultdict, Counter

from ner import NER
from openweathermap import get_cur_date, request_loc, request_5days_weather
from weather_codes import weather_codes, weather_translations
from date import parse_date


def get_dates_and_cities(ner_out):
    word = ""
    words = []
    for token in ner_out:
        subword = token["word"]
        pref, suff = token["entity"].split("-")
        if suff not in ["DT", "LC"]:
            continue

        if pref == "I" and words:
            word, prev_suff = words.pop()
            if suff != prev_suff:
                continue

            if re.match(r"##(?!##)\S+", subword):
                word += f"{subword[2:]}"
            else:
                word += f" {subword}"
        elif pref == "B":
            word = subword
        words.append((word, suff))

    dates = []
    cities = []
    for word, entity in words:
        if entity == "DT":
            dates.append(word)
        else:
            cities.append(word)
    return dates, cities


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

date_dict = {
    
}


if __name__ == "__main__":
    ner = NER()
    text = "3일 후 시드니 날씨 알려줘."
    ner_out = ner(text)
    # ner_out = [{'entity': 'B-DT', 'score': 0.9855451, 'index': 1, 'word': '3', 'start': 0, 'end': 1}, {'entity': 'I-DT', 'score': 0.9825005, 'index': 2, 'word': '##일', 'start': 1, 'end': 2}, {'entity': 'I-DT', 'score': 0.97232145, 'index': 3, 'word': '후', 'start': 3, 'end': 4}, {'entity': 'B-LC', 'score': 0.9674333, 'index': 4, 'word': '시드니', 'start': 5, 'end': 8}]

    cur_date = get_cur_date()
    dates, cities = get_dates_and_cities(ner_out)
    for city in cities:
        city_ko, coord = request_loc(city)
        weather_dict = request_5days_weather(coord)
        for date in dates:
            date = parse_date(date)
            day_tempo, night_tempo = get_avg_tempos(weather_dict, date=date)
            day_weather, night_weather = get_most_common_weathers(weather_dict, date=date)
            f"{date}의 {city_ko}의 날씨를 말씀 드리겠습니다. 낮에는 평균 기온 {day_tempo}도의 {day_weather} 날씨가 되겠고, 밤에는 평균 기온 {night_tempo}도의 {night_weather} 날씨가 되겠습니다."
