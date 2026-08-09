확인해보니 OpenAI가 최근 **Responses API**(`client.responses.create`)를 새로운 표준으로 권장하고 있고, 기존 Chat Completions API(`client.chat.completions.create`)는 계속 지원되지만 새 프로젝트에는 Responses API 사용을 권장하고 있습니다.Chat Completions는 계속 지원되지만, 새 프로젝트에는 Responses API가 권장됩니다.

주요 변경점:
- `messages` 배열 대신 `input`(문자열 또는 메시지 리스트) 사용
- 시스템 프롬프트는 `instructions` 파라미터로 분리
- 응답은 `response.choices[0].message.content` 대신 `response.output_text`로 바로 접근

```python
from openai import OpenAI

# 1. OpenAI 클라이언트 생성
client = OpenAI(
    api_key=GMS_KEY,
    base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1/"
)

# 2. chat_completion 함수를 완성 (Responses API 방식으로 변경)
def chat_completion(prompt: str,
                    system_prompt: str = None,
                    model: str = "gpt-5-mini") -> str:
    """
    LLM을 호출하여 응답을 반환하는 함수 (Responses API 사용)

    Args:
        prompt: 사용자 메시지
        system_prompt: 시스템 메시지 (선택) - instructions 파라미터로 전달됨
        model: 사용할 모델명

    Returns:
        LLM의 응답 텍스트
    """
    # Responses API에서는 system_prompt를 instructions로 별도 전달합니다.
    # 대화의 스타일, 성격, 제약 조건 등을 결정하는 역할은 동일합니다.
    kwargs = {
        "model": model,
        "input": prompt,
    }
    if system_prompt:
        kwargs["instructions"] = system_prompt

    response = client.responses.create(**kwargs)

    # Chat Completions의 response.choices[0].message.content 대신
    # Responses API는 output_text로 바로 텍스트를 제공합니다.
    return response.output_text


# 잘 작동하는지 테스트해볼까요?
test_response = chat_completion("안녕하세요! 간단한 인사말을 해주세요.")
print("테스트 응답:")
print(test_response)
```

**참고사항:**
- 멀티턴 대화가 필요하면 `input`에 메시지 리스트(`[{"role": "user", "content": "..."}]`) 형태도 그대로 넣을 수 있고, `store=True` + `previous_response_id`로 이전 대화 맥락을 서버 측에서 이어갈 수도 있습니다 (매번 전체 히스토리를 다시 보낼 필요 없음).Stateful context: store: true를 사용해 턴 간 상태를 유지하고, 이전 대화의 추론 및 도구 컨텍스트를 보존합니다.
- reasoning 모델(GPT-5 계열) 사용 시 Chat Completions보다 성능/캐시 효율이 더 좋다고 알려져 있습니다.추론 모델(GPT-5 등)을 Responses와 함께 사용하면 Chat Completions 대비 더 나은 모델 지능을 얻을 수 있습니다.
- 다만 `gms.ssafy.io`처럼 OpenAI 호환 프록시를 쓰는 경우, 해당 프록시가 `/v1/responses` 엔드포인트를 지원하지 않을 수도 있으니 먼저 확인이 필요합니다. 지원하지 않는다면 기존 `chat.completions.create` 방식을 그대로 써도 무방합니다.