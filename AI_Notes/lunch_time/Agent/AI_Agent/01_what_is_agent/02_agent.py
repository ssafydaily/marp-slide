import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()
# OPENAI_API_KEY를 .env에 넣어두면, 별도 설정 필요 없음.
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-5-nano"),
)

# 에이전트가 쓸 수 있는 도구 하나를 등록
@tool
def get_weather(city: str) -> str:
    """지정한 도시의 현재 날씨를 조회한다."""
    fake_data = {
        '서울': '맑음, 기온 22°C',
        '부산': '흐림, 기온 24°C',
        '제주': '비, 기온 20°C',
    }
    return fake_data.get(city, f'{city}의 날씨 데이터를 찾을 수 없습니다.')


# 모델 + 도구 -> 반복 루프를 도는 에이전트
agent = create_agent(model=llm, tools=[get_weather])

result = agent.invoke(
    {"messages": [{"role": "user", "content": "오늘 서울 날씨 알려줘"}]}
)
print(result["messages"][-1].content)


''' agent.stream() 실행 결과 예시
{'model': {'messages': [AIMessage(content='', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 471, 'prompt_tokens': 135, 'total_tokens': 606, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 448, 'rejected_prediction_tokens': 0, 'text_tokens': None}, 'prompt_tokens_details': {'audio_tokens': 0, 'cache_write_tokens': None, 'cached_tokens': 0, 'image_tokens': None, 'text_tokens': None}}, 'model_provider': 'openai', 'model_name': 'gpt-5-nano-2025-08-07', 'system_fingerprint': None, 'id': 'chatcmpl-EIjqhWDIM5inKOAd6iywurZwYXvxj', 'service_tier': 'default', 'finish_reason': 'tool_calls', 'logprobs': None}, id='lc_run--01a05524-9bc1-7be0-8e1f-9e3f879166a2-0', tool_calls=[{'name': 'get_weather', 'args': {'city': '서울'}, 'id': 'call_z0XPSDafk6il6dftLbnXQr5u', 'type': 'tool_call'}], invalid_tool_calls=[], usage_metadata={'input_tokens': 135, 'output_tokens': 471, 'total_tokens': 606, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 448}})]}}
{'tools': {'messages': [ToolMessage(content='맑음, 기온 22°C', name='get_weather', id='b1cc2254-26b3-4f47-94df-ed254c9b5303', tool_call_id='call_z0XPSDafk6il6dftLbnXQr5u')]}}
{'model': {'messages': [AIMessage(content='오늘 서울 날씨는 맑고 기온은 약 22°C입니다.\n\n외출 시 가벼운 옷차림에 자외선 차단제나 선글라스도 챙기시면 좋습니다. 시간대별 예보나 주간 예보가 필요하시면 알려드릴게요.', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 589, 'prompt_tokens': 172, 'total_tokens': 761, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 512, 'rejected_prediction_tokens': 0, 'text_tokens': None}, 'prompt_tokens_details': {'audio_tokens': 0, 'cache_write_tokens': None, 'cached_tokens': 0, 'image_tokens': None, 'text_tokens': None}}, 'model_provider': 'openai', 'model_name': 'gpt-5-nano-2025-08-07', 'system_fingerprint': None, 'id': 'chatcmpl-EIjqketA5YhKpre5NL4dAvcgaD9HY', 'service_tier': 'default', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--01a05524-a77c-7712-ae7b-b7ac977311e4-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 172, 'output_tokens': 589, 'total_tokens': 761, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 512}})]}}
'''
# stream()을 쓰면, 에이전트가 중간에 도구를 호출하고, 그 결과를 받아서 최종 답변을 생성하는 과정을 실시간으로 확인할 수 있음.
for result in agent.stream(
    {"messages": [{"role": "user", "content": "오늘 서울 날씨 알려줘"}]}
):
    print(result)
