import openai


def read_api_key():
    api_key_path = "/Users/jongbeomkim/Desktop/workspace/weather_api/resources/openai_api_key.txt"
    with open(api_key_path, mode="r") as f:
        api_key = f.read().strip()
    return api_key

openai_api_key = read_api_key()
client = openai.OpenAI(api_key=openai_api_key)
completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
    {"role": "system", "content": "너는 시인이야. 사용자가 요청하는 주제로 아름다운 시를 써줘"},
    {"role": "user", "content": "달빛, 사랑, 토끼, 주전자"}
]
)
print(completion.choices[0].message)