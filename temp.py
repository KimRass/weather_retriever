import requests
from datetime import datetime
import xmltodict


def get_cur_date():
    cur_date = datetime.now().date()
    return cur_date.strftime("%Y%m%d")


def get_cur_hour():
    now = datetime.now()
    return datetime.now().strftime("%H%M")


int_to_weather = {
    "0": "맑음",
    "1": "비",
    "2": "비/눈",
    "3": "눈",
    "5": "빗방울",
    "6": "빗방울눈날림",
    "7": "눈날림"
}

def forecast(params):
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst" # 초단기예보
    resp = requests.get(url=url, params=params)
    xml_data = resp.text
    dict_data = xmltodict.parse(xml_data) # XML to dictionary
    # dict_data["response"]["body"].keys()
    for item in dict_data["response"]["body"]["items"]["item"]:
        if item["category"] == "T1H":
            tempo = item["obsrValue"]
        # 강수형태: 없음(0), 비(1), 비/눈(2), 눈(3), 빗방울(5), 빗방울눈날림(6), 눈날림(7)
        if item["category"] == "PTY":
            sky = item["obsrValue"]
            
    sky = int_to_weather[sky]
    
    return tempo, sky


if __name__ == "__main__":
    keys = "ZiVxPJ+vI7xgAFhr3EIUYpBxNr58xMheGfLNtbxGye5KLHVHt7jCTOORf2ix2cKYu+YYHnmsO9DOWbtuL1sC2Q=="
    params ={
        "serviceKey" : keys,
        "pageNo" : "1",
        "numOfRows" : "10",
        "dataType" : "XML",
        "base_date" : get_cur_date(),
        # "base_date" : "20241105",
        "base_time" : get_cur_hour(),
        "nx" : "100",
        "ny" : "127",
    }

    forecast(params)
