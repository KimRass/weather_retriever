import json

from ner import NER
from openweathermap import (
    request_coord,
    request_5days_weather,
    average_tempos,
    get_most_common_weathers,
)
from date import ko_date_expr_to_date, hyphen_date_to_ko
from korean import has_batchim


class WeatherRetrieval(object):
    def __init__(self, city_coord_path="./resources/city_coords.json"):
        self.ner = NER()
        self.city_coord_path = city_coord_path
        with open(self.city_coord_path, mode="r", encoding="utf-8") as f:
            self.city_coord = json.load(f)

    def __call__(self, query):
        def weather_to_text(date, city, avg_tempos, weathers):
            ko_date = hyphen_date_to_ko(date)
            jugyeokjosa1 = "이" if has_batchim(weathers[0][-1]) else "가"
            if weathers[0] == weathers[1]:
                return f"{ko_date} {city}의 날씨입니다: 하루 종일 {weathers[0]}{jugyeokjosa1} 예상되며, 평균 기온은 낮 {avg_tempos[0]}도, 밤 {avg_tempos[1]}도입니다."
            else:
                jugyeokjosa2 = "이" if has_batchim(weathers[1][-1]) else "가"
                return f"{ko_date} {city}의 날씨입니다: 낮에는 {weathers[0]}{jugyeokjosa1}, 밤에는 {weathers[1]}{jugyeokjosa2} 예상됩니다. 평균 기온은 낮 {avg_tempos[0]}도, 밤 {avg_tempos[1]}도입니다."

        answer = []
        ner_out = self.ner(query)
        text_dates, cities = self.ner.parse(ner_out)
        if not cities:
            answer.append(
                f"죄송합니다. 말씀하신 문장에서 지역을 찾을 수 없습니다."
            )
        for city in cities:
            if city in self.city_coord:
                coord = self.city_coord[city]
                city_ko = city
            else:
                city_ko, coord = request_coord(city)
                if not coord:
                    answer.append(
                        f"죄송합니다. '{city_ko}'을 찾을 수 없습니다."
                    )
                    continue
                else:
                    self.city_coord[city_ko] = coord
                    with open(self.city_coord_path, mode="w") as f:
                        json.dump(self.city_coord, f, ensure_ascii=False, indent=4)

            weather_dict = request_5days_weather(coord)
            for text_date in text_dates:
                date = ko_date_expr_to_date(text_date)
                avg_tempos = average_tempos(weather_dict, date=date)
                weathers = get_most_common_weathers(
                    weather_dict, date=date,
                )
                answer.append(
                    weather_to_text(
                        date=date, city=city_ko, avg_tempos=avg_tempos, weathers=weathers,
                    )
                )
        return "\n".join(answer)


if __name__ == "__main__":
    weather_retrieval = WeatherRetrieval()
    # query = "모레 서울 날씨 말해 줘."
    # query = "내일과 모레 부산 날씨 말해 줘."
    query = "내일과 모레 런던 날씨 말해 줘."
    answer = weather_retrieval(query)
    print(answer)
