import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import json
import requests
from unittest.mock import patch, MagicMock, mock_open

from weather_retriever import WeatherRetriever


class TestWeatherRetriever(object):
    @pytest.fixture
    def weather_retriever(self):
        wr = WeatherRetriever(owm_api_key="mock_owm_api_key")
        return wr

    # You specify the target object to mock as a string argument.
    @patch("requests.get")
    def test_request_coord_success(self, mock_get, weather_retriever):
        # Inside this function, `requests.get` is replaced with `mock_get`.
        mock_get.return_value.json.return_value = [
            {
                "local_names": {"ko": "mock_city_ko"},
                "lat": "mock_lat",
                "lon": "mock_lon",
            }
        ]
        out = weather_retriever.owm.request_coord("mock_city")
        assert out == ("mock_city_ko", ("mock_lat", "mock_lon"))

    @patch("requests.get")
    def test_request_coord_api_failure(self, mock_get, weather_retriever):
        mock_get.side_effect = requests.exceptions.RequestException("API error")
        out = weather_retriever.owm.request_coord("mock_city")
        assert out == ("mock_city", None)

    @patch("requests.get")
    def test_request_coord_empty_result(self, mock_get, weather_retriever):
        mock_get.return_value.json.return_value = []
        out = weather_retriever.owm.request_coord("mock_city")
        assert out == ("mock_city", None)

    @patch("requests.get")
    def test_request_coord_no_local_names(self, mock_get, weather_retriever):
        mock_get.return_value.json.return_value = [
            {
                "local_names": {},
                "lat": "mock_lat",
                "lon": "mock_lon",
            }
        ]
        out = weather_retriever.owm.request_coord("mock_city")
        assert out == ("mock_city", ("mock_lat", "mock_lon"))

    @patch("requests.get")
    def test_request_5days_weather_success(self, mock_get, weather_retriever):
        mock_resp = {
            "list": [
                {
                    "dt_txt": "2024-11-01 06:00:00",
                    "weather": [{"id": 800}],
                    "main": {"temp": 15.5},
                },
                {
                    "dt_txt": "2024-11-01 15:00:00",
                    "weather": [{"id": 801}],
                    "main": {"temp": 20.1},
                },
                {
                    "dt_txt": "2024-11-01 21:00:00",
                    "weather": [{"id": 802}],
                    "main": {"temp": 13.8},
                },
            ]
        }
        mock_get.return_value.text = json.dumps(mock_resp)
        weather_dict = weather_retriever.owm.request_5days_weather((0, 0))
        assert "2024-11-01" in weather_dict
        assert "day" in weather_dict["2024-11-01"]
        assert "night" in weather_dict["2024-11-01"]
        assert weather_dict["2024-11-01"]["day"]["06:00:00"]["weather"] == 800
        assert weather_dict["2024-11-01"]["night"]["21:00:00"]["tempo"] == 13.8

    @patch("requests.get")
    def test_request_5days_weather_api_filure(self, mock_get, weather_retriever):
        mock_get.side_effect = requests.exceptions.RequestException("API error")
        weather_dict = weather_retriever.owm.request_5days_weather((0, 0))
        assert weather_dict == {}

    @pytest.fixture
    def weather_dict(self):
        return {
            "2024-11-01": {
                "day": {
                    "06:00:00": {"tempo": 15, "weather": 200},
                    "12:00:00": {"tempo": 18, "weather": 200},
                    "15:00:00": {"tempo": 20, "weather": 201},
                },
                "night": {
                    "03:00:00": {"tempo": 8, "weather": 200},
                    "21:00:00": {"tempo": 10, "weather": 201},
                },
            },
            "2024-11-03": {
                "day": {},
                "night": {},
            },
        }

    def test_average_tempos(self, weather_dict, weather_retriever):
        day, night = weather_retriever.owm.average_tempos(weather_dict, "2024-11-01")
        assert day == 18
        assert night == 9
        day, night = weather_retriever.owm.average_tempos(weather_dict, "2024-11-03")
        assert day is None
        assert night is None

    def test_get_most_common_weathers(self, weather_dict, weather_retriever):
        day, night = weather_retriever.owm.get_most_common_weathers(
            weather_dict, "2024-11-01",
        )
        assert day == "가벼운 비를 동반한 뇌우"
        assert night == "가벼운 비를 동반한 뇌우"
        day, night = weather_retriever.owm.get_most_common_weathers(
            weather_dict, "2024-11-03",
        )
        assert day is None
        assert night is None

    @patch("builtins.open", new_callable=mock_open, read_data='{"서울": [37.5665, 126.978]}')
    def test_load_city_coords_file_exists(self, mock_open, weather_retriever):
        """
        The `@patch`` decorator is used to replace the built-in `open` function with a
        `mock_open`. This mock version simulates reading a file without actually needing to
        create a physical file on the filesystem.
        """
        city_coords = weather_retriever.load_city_coords()
        assert city_coords == {"서울": [37.5665, 126.978]}
        # Asserts that `open` was called exactly once.
        mock_open.assert_called_once_with(
            weather_retriever.city_coord_path, mode="r", encoding="utf-8",
        )

    @patch("pathlib.Path.exists", return_value=False)
    def test_load_city_coords_file_not_exist(self, mock_exists, weather_retriever):
        """
        By mocking `Path.exists` to always return `False`, this test simulates the scenario
        where the city coordinates file does not exist.
        """
        city_coords = weather_retriever.load_city_coords()
        assert city_coords == {}

    @patch("requests.get")
    @patch.object(WeatherRetriever, 'save_city_coords')
    def test_get_city_coords_existing_city(self, mock_save, mock_get, weather_retriever):
        # Simulate a city that exists in city_coords
        weather_retriever.city_coords = {"mock_city": ("mock_lat", "mock_lon")}
        city_ko, coord = weather_retriever.get_city_coords("mock_city")
        assert city_ko == "mock_city"
        assert coord == ("mock_lat", "mock_lon")
        mock_save.assert_not_called()  # Ensure save is not called since city exists

    @patch("requests.get")
    def test_get_city_coords_new_city(self, mock_get, weather_retriever):
        # Simulate a new city request
        mock_get.return_value.json.return_value = [
            {
                "local_names": {"ko": "new_city_ko"},
                "lat": "new_lat",
                "lon": "new_lon",
            }
        ]
        city_ko, coord = weather_retriever.get_city_coords("new_city")
        assert city_ko == "new_city_ko"
        assert coord == ("new_lat", "new_lon")
        assert "new_city_ko" in weather_retriever.city_coords  # Ensure new city is saved

    def test_format_weather_response_same_weather(self, weather_retriever):
        date = "2024-11-01"
        city = "mock_city"
        avg_tempos = [20, 10]
        weathers = ["가벼운 비를 동반한 뇌우", "가벼운 비를 동반한 뇌우"]
        response = weather_retriever.format_weather_response(date, city, avg_tempos, weathers)
        
        assert "2024년 11월 01일" in response
        assert city in response
        assert "하루 종일" in response
        assert "평균 기온은 낮 20도, 밤 10도입니다." in response

    def test_process_weather_dates_with_invalid_dates(self, weather_retriever):
        text_dates = ["2024년 11월 1일", "2024년 11월 3일"]
        weather_dict = {}
        responses = weather_retriever.process_weather_dates(text_dates, weather_dict, "mock_city")
        assert len(responses) == 2  # One valid date and one invalid date
        assert responses[1] == "죄송합니다. 오늘로부터 최대 5일 후의 날씨만 알려드릴 수 있습니다."
