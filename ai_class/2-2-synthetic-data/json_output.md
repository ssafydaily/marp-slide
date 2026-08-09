OpenAI API에서 JSON 형식 응답을 요청하는 방법을 체계적으로 정리해드리겠습니다.

## 1. 방식 개요 (3가지 레벨)

| 방식                                 | 보장 수준 | 특징                                      |
| ------------------------------------ | --------- | ----------------------------------------- |
| 프롬프트로만 요청                    | 낮음      | JSON이 아닐 수도 있음                     |
| `json_object` 모드                 | 중간      | 유효한 JSON은 보장, 구조(스키마)는 미보장 |
| `json_schema` (Structured Outputs) | 높음      | 지정한 스키마를 100% 준수                 |

실무에서는 **3번(json_schema)**을 쓰는 게 가장 안전합니다.

---

## 2. `chat.completions.create` 방식

### (1) json_object 모드 — 구조 보장 X

```python
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[
        {"role": "system", "content": "응답을 JSON 형식으로만 출력하세요."},
        {"role": "user", "content": "..."}
    ],
    response_format={"type": "json_object"}
)
```

- 시스템 프롬프트에 **"JSON으로 응답하라"는 문구가 반드시 포함**되어야 함 (없으면 에러 발생 가능)
- 키 이름, 자료형까지는 강제하지 않음

### (2) json_schema 모드 — 구조까지 보장 O

```python
translation_response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "translation",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "korean": {"type": "string"}
            },
            "required": ["korean"],
            "additionalProperties": False
        }
    }
}

response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[...],
    response_format=translation_response_format
)

result = json.loads(response.choices[0].message.content)
```

---

## 3. `responses.create` 방식 (신규 API)

구조는 같지만 **키 위치가 한 단계 평평(flat)** 해집니다.

```python
translation_text_format = {
    "type": "json_schema",
    "name": "translation",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "korean": {"type": "string"}
        },
        "required": ["korean"],
        "additionalProperties": False
    }
}

response = client.responses.create(
    model="gpt-5-mini",
    input=[...],
    text={"format": translation_text_format}
)

result = json.loads(response.output_text)
```

> 차이 요약: `response_format={"type":"json_schema","json_schema":{...}}` → `text={"format":{"type":"json_schema", ...}}` (한 겹 벗겨짐)

---

## 4. Structured Outputs(`json_schema`) 작성 규칙

`strict: True`를 쓸 경우 JSON Schema 작성에 몇 가지 **필수 규칙**이 있습니다:

1. **`additionalProperties: False`** 반드시 명시
2. **`required`에 모든 프로퍼티 이름 포함** (선택적 필드도 required에 넣고, null 허용은 `type: ["string","null"]`로 표현)
3. 지원되는 타입: `string`, `number`, `boolean`, `integer`, `object`, `array`, `enum`, `anyOf` 등
4. 중첩 객체/배열도 가능, 재귀 스키마도 지원

### 예시 (필드가 여러 개일 때)

```python
schema = {
    "type": "object",
    "properties": {
        "korean": {"type": "string"},
        "confidence": {"type": "number"},
        "notes": {"type": ["string", "null"]}
    },
    "required": ["korean", "confidence", "notes"],
    "additionalProperties": False
}
```

---

## 5. Pydantic으로 스키마 관리 (권장)

스키마를 손으로 짜는 대신 Pydantic 모델로 정의하면 더 안전합니다.

```python
from pydantic import BaseModel

class Translation(BaseModel):
    korean: str

# chat.completions
response = client.chat.completions.parse(
    model="gpt-5-mini",
    messages=[...],
    response_format=Translation
)
result = response.choices[0].message.parsed  # 이미 Translation 객체

# responses
response = client.responses.parse(
    model="gpt-5-mini",
    input=[...],
    text_format=Translation
)
result = response.output_parsed
```

`.parse()`를 쓰면 `json.loads()` 없이 바로 Pydantic 객체로 받을 수 있어 가장 안전하고 편리합니다.

---

## 6. 실무 체크리스트

- [ ] `strict: True`로 스키마 강제 준수 여부 확인
- [ ] `additionalProperties: False` 누락 여부 확인
- [ ] `required`에 모든 키 포함했는지 확인
- [ ] 가능하면 Pydantic + `.parse()`로 파싱 에러 리스크 제거
- [ ] `chat.completions` vs `responses`에 따라 `response_format` vs `text.format` 키 위치 구분

필요하시면 지금 쓰고 계신 `translation_response_format`을 Pydantic 모델 방식으로도 변환해드릴 수 있습니다.
