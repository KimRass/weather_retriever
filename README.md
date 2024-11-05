# Weather-Retriever

**Weather-Retriever** is a Python package that allows users to retrieve and format weather information in natural language, specifically tailored for Korean speakers. It leverages data from [OpenWeatherMap](https://openweathermap.org/) and incorporates natural language processing (NLP) techniques to extract temporal and location information from user queries. The package presents weather forecasts in a user-friendly format, accommodating Korean-language date expressions and appropriate word forms.

## Features
- Retrieve real-time weather data from OpenWeatherMap.
- Understand and process natural language queries in Korean.
- Cache city coordinates for efficient API usage.
- Format weather forecasts in an easily readable manner.

## Building the Package
1. Prepare for Packaging:
    - Ensure the city coordinate file is saved correctly in '~/.weather-retriever'.
2. Create a Distribution:
    - Build the package using `setuptools`:
    ```bash
    # pip install setuptools wheel
    python setup.py sdist bdist_wheel
    ```
3. Publish to PyPI:
    - Use `twine` to upload the package:
    ```bash
    # pip install twine
    python -m twine upload dist/*
    ```

## Installation
You can install WeatherRetriever in two ways:
1. Install via PyPI:
    ```bash
    # https://pypi.org/project/weather-retriever/0.1.1/
    pip install weather-retriever
    ```
    - This method allows you to install the package directly from PyPI.
2. Install from GitHub:
    ```bash
    git clone https://github.com/KimRass/weather-retriever
    cd weather-retriever
    pip install .
    ```
    - This method is useful if you want to access the latest code or contribute to the project.

## Usage
```python
from weather_retriever import WeatherRetriever

# The OpenWeatherMap API key must be provided when initializing `WeatherRetriever`.
owm_api_key = "YOUR_OPENWEATHERMAP_API_KEY"
wr = WeatherRetriever(owm_api_key)

query = "YOUR_QUERY"
# Ensure network access is available to retrieve real-time weather data.
response = wr.query(query)
print(response)
```
- The package also includes intelligent caching of city coordinates to minimize redundant API calls.

### Query Examples
- "내일 서울 날씨는 어때?"
- "사흘 뒤의 상하이 날씨 어때?"
- "2024년 11월 6일의 런던 날씨는 어떻습니까?"
- "내일 오전 워싱턴 날씨는?"
- "내일과 2024년 11월 8일의 부산 날씨는 어떻습니까?"
- "뉴욕 날씨를 알려주세요. 내일과 모레에 대해서."

### File Handling
- The package saves city coordinate data in '~/.weather-retriever/city_coords.json' to cache information for efficient lookups.
- The `pathlib` library is used for managing file and directory operations.

## Testing
- To run the tests, you can use Python's built-in unittest framework or pytest. To execute the tests, simply run:
    ```bash
    pytest
    ```

## License
- This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for more details.
