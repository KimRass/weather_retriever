import dateparser
import re


def ko_to_en_date_expr(text_date):
    # Convert common Korean expressions to a more recognizable format
    conversions = {
        r"(\d+)일 후": r"\1 days later", # e.g., "3일 후" -> "3 days later"
        r"(\d+)일 뒤": r"\1 days later", # e.g., "3일 뒤" -> "3 days later"
        "하루 뒤": "1 day later",
        "내일": "1 day later",
        "이틀 뒤": "2 days later",
        "모레": "2 days later",
        "내일 모레": "2 days later", # https://m.blog.naver.com/brandioco/222620900748
        "내일모레": "2 days later",
        "사흘 뒤": "3 days later",
        "글피": "3 days later",
        "저모레": "3 days later", # https://m.blog.naver.com/edu916/220208856162
        "나흘 뒤": "4 days later",
        "그글피": "4 days later",
    }
    
    # Replace Korean date expressions with English equivalents
    for pattern, replacement in conversions.items():
        text_date = re.sub(pattern, replacement, text_date)
    return text_date


def ko_date_expr_to_date(text_date):
    # Convert the Korean date expression to a recognizable format.
    converted_input = ko_to_en_date_expr(text_date)
    # Parse the natural language date
    parsed_date = dateparser.parse(converted_input)
    # Check if the parsing was successful
    if parsed_date:
        return parsed_date.date().strftime("%Y-%m-%d")  # Return only the date part
    else:
        return "Invalid date format"


def hyphen_date_to_ko(date):
    y, m, d = date.split("-")
    return f"{y}년 {m}월 {d}일"


if __name__ == "__main__":
    user_inputs = ["3일 후", "나흘 뒤", "5일 후", "5일 뒤"]
    for input_input in user_inputs:
        result = ko_date_expr_to_date(input_input)
        print(f"{input_input}  {result}")
