import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-5-nano"),
)

# 도구 1: 날씨 (mock 데이터 — 실제 API 연동은 다음 시간에)
@tool
def get_weather(city: str) -> str:
    """지정한 도시의 현재 날씨를 조회한다."""
    fake_data = {
        '서울': '맑음, 기온 22°C',
        '부산': '흐림, 기온 24°C',
        '제주': '비, 기온 20°C',
    }
    return fake_data.get(city, f'{city}의 날씨 데이터를 찾을 수 없습니다.')


# 도구 2: 교통 (mock 데이터)
@tool
def get_traffic(city: str) -> str:
    """도시 이름을 받아 현재 교통 상황을 알려준다."""
    return f"{city} 시내 교통은 보통 수준입니다."

agent = create_agent(model=llm, tools=[get_weather, get_traffic])

for result in agent.stream(
    {"messages": [{"role": "user", "content": "오늘 서울 날씨와 교통 상황 알려줘"}]}
):
    print(result)
