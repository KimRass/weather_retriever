import json
from pathlib import Path

from weather_retriever.ner import NER
from weather_retriever.openweathermap import OpenWeatherMap
from weather_retriever.date import ko_date_expr_to_date, hyphen_to_ko_date_expr
from weather_retriever.hangul import has_batchim, replace_time_words


class WeatherRetriever(object):
    def __init__(self, owm_api_key):
        self.city_coord_path = Path.home()/".weather-retriever/city_coords.json"
        self.city_coords = self.load_city_coords()
        self.ner = NER()
        self.owm = OpenWeatherMap(owm_api_key=owm_api_key)

    def load_city_coords(self):
        """
        Load city coordinates from JSON file or return an empty dict.
        """
        if self.city_coord_path.exists():
            with open(self.city_coord_path, mode="r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_city_coords(self):
        """
        Save the city coordinates to a JSON file.
        """
        self.city_coord_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.city_coord_path, mode="w") as f:
            json.dump(self.city_coords, f, ensure_ascii=False, indent=4)

    def get_city_coords(self, city):
        """
        Retrieve the coordinates for a given city.
        """
        if city in self.city_coords:
            return city, self.city_coords[city]
        city_ko, coord = self.owm.request_coord(city)
        if coord:
            self.city_coords[city_ko] = coord
            self.save_city_coords()
        return city_ko, coord

    def format_weather_response(self, date, city, avg_tempos, weathers):
        """
        Format the weather response text.
        """
        ko_date = hyphen_to_ko_date_expr(date)
        jugyeokjosa1 = "이" if has_batchim(weathers[0][-1]) else "가"
        
        if weathers[0] == weathers[1]:
            return (
                f"{ko_date} {city}의 날씨입니다: 하루 종일 {weathers[0]}{jugyeokjosa1} 예상되며, "
                f"평균 기온은 낮 {avg_tempos[0]}도, 밤 {avg_tempos[1]}도입니다."
            )

        jugyeokjosa2 = "이" if has_batchim(weathers[1][-1]) else "가"
        return (
            f"{ko_date} {city}의 날씨입니다: 낮에는 {weathers[0]}{jugyeokjosa1}, "
            f"밤에는 {weathers[1]}{jugyeokjosa2} 예상됩니다. "
            f"평균 기온은 낮 {avg_tempos[0]}도, 밤 {avg_tempos[1]}도입니다."
        )

    def process_weather_dates(self, text_dates, weather_dict, city_ko):
        """
        Process weather information for each date and return formatted strings.
        """
        responses = []
        for text_date in text_dates:
            date = ko_date_expr_to_date(text_date)
            if date not in weather_dict:
                responses.append(
                    "죄송합니다. 오늘로부터 최대 5일 후의 날씨만 알려드릴 수 있습니다."
                )
                continue

            avg_tempos = self.owm.average_tempos(weather_dict, date=date)
            weathers = self.owm.get_most_common_weathers(weather_dict, date=date)
            responses.append(self.format_weather_response(date, city_ko, avg_tempos, weathers))
        return responses

    def query(self, query, print_ner_output=False):
        """
        Process the weather query and return a formatted response.
        """
        query = replace_time_words(query)
        ner_out = self.ner(query)
        if print_ner_output:
            print(ner_out)
        text_dates, cities = self.ner.parse(ner_out)

        if not text_dates:
            return "죄송합니다. 언제를 말씀하시는 건지 모르겠습니다."
        if not cities:
            return "죄송합니다. 어느 지역을 말씀하시는 건지 모르겠습니다."

        answers = []
        for city in cities:
            city_ko, coord = self.get_city_coords(city)
            if not coord:
                mokjeokgyeokjosa = "을" if has_batchim(city_ko[-1]) else "를"
                answers.append(f"죄송합니다. '{city_ko}'{mokjeokgyeokjosa} 찾을 수 없습니다.")
                continue

            weather_dict = self.owm.request_5days_weather(coord)
            answers.extend(self.process_weather_dates(text_dates, weather_dict, city_ko))
        return "\n".join(answers)
