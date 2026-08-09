좋습니다. `chat.completions.create` → `responses.create`로 변경할 때 핵심 차이는:

- `messages` → `input`
- `response_format` → `text={"format": ...}`
- 결과 파싱: `response.choices[0].message.content` → `response.output_text`

또한 **`response_format`의 스키마 형태 자체도 살짝 다릅니다.** `chat.completions`에서는 보통 아래처럼 `json_schema` 키 아래에 중첩되어 있습니다:

```python
translation_response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "translation",
        "schema": {...}
    }
}
```

반면 `responses.create`의 `text.format`은 중첩 없이 평평한 구조를 기대합니다:

```python
{
    "type": "json_schema",
    "name": "translation",
    "schema": {...},
    "strict": True
}
```

따라서 기존 `translation_response_format`이 `chat.completions`용으로 정의되어 있다면, `json_schema` 안의 내용을 꺼내서 평평하게 만들어줘야 합니다.

## 변환된 코드

```python
# 1. Zero-shot 시스템 프롬프트
ZERO_SHOT_PROMPT = """다음 영어 문장을 한국어로 번역해주세요.
원문의 의미를 정확히 전달하면서 자연스러운 한국어로 번역하세요."""

# translation_response_format이 chat.completions용 구조라면 변환 필요
# 예: translation_response_format["json_schema"] 안에 name, schema가 있는 경우
translation_text_format = {
    "type": "json_schema",
    "name": translation_response_format["json_schema"]["name"],
    "schema": translation_response_format["json_schema"]["schema"],
    "strict": translation_response_format["json_schema"].get("strict", True),
}

# 2. 첫 번째 샘플 번역
test_question = dataset_10[0]["question"]
print(f"원문: {test_question}")

response = client.responses.create(
    model="gpt-5-mini",
    input=[
        {"role": "system", "content": ZERO_SHOT_PROMPT},
        {"role": "user", "content": test_question}
    ],
    text={"format": translation_text_format}
)

zero_shot_result = json.loads(response.output_text)
print(f"Zero-shot 번역: {zero_shot_result['korean']}")
```

### 참고
- 만약 `translation_response_format`이 이미 `{"type": "json_schema", "name": ..., "schema": ...}` 형태로 평평하게 정의되어 있다면 위 변환 단계(`translation_text_format` 생성 부분) 없이 그대로 `text={"format": translation_response_format}`로 넣으면 됩니다.
- `response.output_text`는 SDK에서 제공하는 편의 속성으로, 텍스트 출력 콘텐츠를 자동으로 합쳐줍니다. 만약 사용 중인 SDK 버전에 없다면 `response.output[0].content[0].text`로 접근하시면 됩니다.

혹시 `translation_response_format`의 실제 정의 코드를 보여주시면, 정확히 어떤 형태인지 확인하고 변환 코드를 더 정확하게 맞춰드릴 수 있습니다.