import json
from pathlib import Path

from src.ner import NER
from src.openweathermap import OpenWeatherMap
from src.date import ko_date_expr_to_date, hyphen_date_to_ko
from src.hangul import has_batchim, replace_time_words


class WeatherRetriever(object):
    def __init__(self, owm_api_key, city_coord_path=None):
        if city_coord_path is None:
            city_coord_path = Path(__file__).parent.parent/"resources/city_coords.json"
        self.city_coord_path = city_coord_path
        with open(self.city_coord_path, mode="r", encoding="utf-8") as f:
            self.city_coord = json.load(f)
        self.ner = NER()
        self.owm = OpenWeatherMap(owm_api_key=owm_api_key)

    def query(self, query):
        def weather_to_text(date, city, avg_tempos, weathers):
            ko_date = hyphen_date_to_ko(date)
            jugyeokjosa1 = "이" if has_batchim(weathers[0][-1]) else "가"
            if weathers[0] == weathers[1]:
                return f"{ko_date} {city}의 날씨입니다: 하루 종일 {weathers[0]}{jugyeokjosa1} 예상되며, 평균 기온은 낮 {avg_tempos[0]}도, 밤 {avg_tempos[1]}도입니다."
            else:
                jugyeokjosa2 = "이" if has_batchim(weathers[1][-1]) else "가"
                return f"{ko_date} {city}의 날씨입니다: 낮에는 {weathers[0]}{jugyeokjosa1}, 밤에는 {weathers[1]}{jugyeokjosa2} 예상됩니다. 평균 기온은 낮 {avg_tempos[0]}도, 밤 {avg_tempos[1]}도입니다."

        answer = []
        query = replace_time_words(query)
        ner_out = self.ner(query)
        text_dates, cities = self.ner.parse(ner_out)
        if not text_dates:
            return "죄송합니다. 언제를 말씀하시는 건지 모르겠습니다."
        if not cities:
            return"죄송합니다. 어느 지역을 말씀하시는 건지 모르겠습니다."
        for city in cities:
            if city in self.city_coord:
                coord = self.city_coord[city]
                city_ko = city
            else:
                city_ko, coord = self.owm.request_coord(city)
                if not coord:
                    answer.append(
                        f"죄송합니다. '{city_ko}'을 찾을 수 없습니다."
                    )
                    continue
                else:
                    self.city_coord[city_ko] = coord
                    with open(self.city_coord_path, mode="w") as f:
                        json.dump(self.city_coord, f, ensure_ascii=False, indent=4)

            weather_dict = self.owm.request_5days_weather(coord)
            for text_date in text_dates:
                date = ko_date_expr_to_date(text_date)
                if date not in weather_dict:
                    answer.append(
                        f"죄송합니다. 오늘로부터 최대 5일 후의 날씨만 알려드릴 수 있습니다."
                    )
                    continue

                avg_tempos = self.owm.average_tempos(
                    weather_dict, date=date,
                )
                weathers = self.owm.get_most_common_weathers(
                    weather_dict, date=date,
                )
                answer.append(
                    weather_to_text(
                        date=date, city=city_ko, avg_tempos=avg_tempos, weathers=weathers,
                    )
                )
        return "\n".join(answer)
