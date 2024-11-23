from src import WeatherRetriever


if __name__ == "__main__":
    wr = WeatherRetriever("c7f820e3c14576722c87304f460a0e2b")
    while True:
        query = input("날씨를 묻는 문장을 입력하세요 (종료하려면 'exit' 입력): ")
        if query.lower() == "exit":
            print("프로그램을 종료합니다.")
            break
        answer = wr.query(query)
        print(answer)
