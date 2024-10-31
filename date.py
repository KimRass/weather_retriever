import dateparser
import re

def convert_korean_date_expression(user_input):
    # Convert common Korean expressions to a more recognizable format
    conversions = {
        r"(\d+)일 후": r"\1 days later", # e.g., "3일 후" -> "3 days later"
        r"(\d+)일 뒤": r"\1 days later", # e.g., "3일 뒤" -> "3 days later"
        r"하루 뒤": "1 day later",
        r"이틀 뒤": "2 days later",
        r"사흘 뒤": "3 days later",
        r"나흘 뒤": "4 days later",
    }
    
    # Replace Korean date expressions with English equivalents
    for pattern, replacement in conversions.items():
        user_input = re.sub(pattern, replacement, user_input)
    
    return user_input


def parse_date(user_input):
    # Convert the Korean date expression to a recognizable format
    converted_input = convert_korean_date_expression(user_input)
    
    # Parse the natural language date
    parsed_date = dateparser.parse(converted_input)

    # Check if the parsing was successful
    if parsed_date:
        return parsed_date.date().strftime("%Y-%m-%d")  # Return only the date part
    else:
        return "Invalid date format"


if __name__ == "__main__":
    user_inputs = ["3일 후", "나흘 뒤", "5일 후", "5일 뒤"]
    for input_input in user_inputs:
        result = parse_date(input_input)
        print(f"{input_input}  {result}")
