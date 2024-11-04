import pytest
import json
import requests
from unittest.mock import patch
from src import WeatherRetriever


class TestOpenWeatherMap(object):
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
