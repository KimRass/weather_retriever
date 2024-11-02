import re


def has_batchim(char):
    # 한글 음절인지 확인.
    if "가" <= char <= "힣":
        code = ord(char) - ord("가")
        return code % 28 != 0 # 28로 나눈 나머지가 0이 아닐 경우 받침이 있음.
    return False  # 한글이 아닐 경우.


def replace_time_words(text):
    pattern = r"지금|현재"
    return re.sub(pattern, "오늘", text)
