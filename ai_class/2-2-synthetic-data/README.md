"합성데이터 - 실습" 노트북은 **LLM을 활용해 합성 데이터를 생성하고, 그 품질을 자동으로 평가하는 파이프라인**을 구축하는 실습입니다. 

## 전체 구조 한눈에 보기

이 실습은 4단계로 구성되어 있습니다.

1. **Step 1**: 환경 설정 및 API 호출 인프라 구축
2. **Step 2**: 프롬프팅 기법(Zero-shot / Few-shot / CoT) 비교
3. **Step 3**: 구조화된(JSON) 합성 데이터 생성
4. **Step 4**: LLM as Judge로 생성된 데이터 품질 평가

---

## 사용된 주요 라이브러리

| 라이브러리              | 역할                                                                                                                                                                                                                                                 |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **openai**        | OpenAI 호환 API 클라이언트.`OpenAI(api_key, base_url)`로 클라이언트를 만들고 `client.chat.completions.create()`로 LLM을 호출. `base_url`을 바꾸면 OpenAI가 아닌 다른 제공사(여기선 GMS라는 프록시 서버)의 모델도 동일한 인터페이스로 호출 가능 |
| **python-dotenv** | `.env` 파일에 저장한 비밀 값(API 키)을 `load_dotenv()`로 환경 변수에 로드. 코드에 키를 직접 하드코딩하지 않기 위한 보안 장치                                                                                                                     |
| **os**            | `os.getenv("GMS_KEY")`로 환경 변수 값을 읽어옴                                                                                                                                                                                                     |
| **json**          | LLM이 문자열로 반환한 응답에서 JSON 부분을 파싱(`json.loads`)하거나, dict를 문자열로 직렬화(`json.dumps`)                                                                                                                                        |
| **pandas**        | 최종 평가 결과를 표(DataFrame) 형태로 정리                                                                                                                                                                                                           |
| **pprint**        | 딕셔너리/리스트를 보기 좋게 출력                                                                                                                                                                                                                     |

---

## Step 1: 환경 설정 및 API 기본 호출

**핵심 개념**

- **환경 변수**: API 키 같은 민감정보를 코드가 아니라 OS 레벨(또는 `.env` 파일)에 저장해서, 코드를 깃허브 등에 올려도 키가 유출되지 않도록 하는 방법. `.env`는 `.gitignore`에 등록해 버전관리에서 제외
- **OpenAI 호환 API**: `OpenAI` SDK는 표준 인터페이스이며, `base_url`만 바꾸면 다른 벤더의 모델도 동일 코드로 호출 가능 (여기서는 `https://gms.ssafy.io/gmsapi/api.openai.com/v1/`라는 프록시를 사용)

**코드 흐름**

```python
load_dotenv(".env")              # .env 파일 로드
GMS_KEY = os.getenv("GMS_KEY")   # 환경변수에서 키 추출

client = OpenAI(api_key=GMS_KEY, base_url="...")  # 클라이언트 생성

def chat_completion(prompt, system_prompt=None, model="solar-pro3"):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content
```

→ 이후 모든 단계에서 이 `chat_completion` 함수를 재사용해서 LLM을 호출합니다. `system` 메시지는 모델의 역할/말투/제약을 규정하고, `user` 메시지는 실제 질문입니다.

---

## Step 2: 프롬프팅 기법 비교

**핵심 개념** — 동일한 "스릴러 영화 추천"이라는 작업을 세 가지 방식으로 요청해 결과 차이를 비교합니다.

| 기법                             | 방식                                                                                              | 특징                                               |
| -------------------------------- | ------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| **Zero-shot**              | 예시 없이 바로 질문 (`zero_shot_prompt = user_query`)                                           | 간단하지만 출력 형식이 들쭉날쭉할 수 있음          |
| **Few-shot**               | 로맨스/코미디 추천 예시 2개를 프롬프트 안에 넣고 마지막에 실제 질문                               | 예시의 패턴(제목/연도/이유 형식)을 모방하게 유도   |
| **CoT (Chain-of-Thought)** | "1단계: 장르 요소 정의 → 2단계: 후보 나열 → 3단계: 최종 선택"처럼 단계별 추론을 명시적으로 지시 | 논리적 근거를 거쳐 답을 내므로 정확도·설득력 향상 |

세 프롬프트 모두 같은 `SYSTEM_PROMPT`(역할: 영화 전문가 '시네마스터')와 같은 `chat_completion` 함수를 사용해서, **프롬프트 설계만 다르게 했을 때 응답이 어떻게 달라지는지** 관찰하는 것이 목적입니다.

---

## Step 3: 구조화된 합성 데이터 생성

**핵심 개념**

- **합성 데이터**: 실제 수집 데이터가 아니라 LLM이 만들어낸 인공 데이터. 데이터 부족 해결, 비용 절감, 개인정보 보호 등에 활용
- **Structured Output**: 모델에게 JSON 스키마를 프롬프트로 명시해 후처리하기 쉬운 형태로 응답을 받는 기법

**코드 흐름**

1) JSON 파싱 유틸리티

```python
def json_parsing(output_text):
    if "```json" in output_text:
        # ```json ... ``` 코드블록에서 순수 JSON 문자열만 추출
        ...
    return json.loads(output_text)
```

LLM은 종종 JSON을 마크다운 코드블록(``json ... ``)으로 감싸서 반환하기 때문에, 이 껍데기를 벗겨내고 `json.loads`로 파싱합니다.

2) 구조화 생성 함수

```python
STRUCTURED_GENERATOR_SYSTEM_PROMPT = """... 
## 3. 출력 형식
{
    "movie_name": ..., "year": ..., "genre": ..., "reason": ...
}
"""

def generate_movie_recommendation(genre, temperature=1.0):
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role":"system","content":STRUCTURED_GENERATOR_SYSTEM_PROMPT},
                  {"role":"user","content":f"{genre} 영화를 추천해줘"}],
        temperature=temperature
    )
    return json_parsing(response.choices[0].message.content)
```

- **temperature**: 응답의 무작위성(다양성) 조절 파라미터. 값이 높을수록 다양하고 창의적인 응답, 낮을수록 일관되고 결정적인 응답. 여기선 `1.0`으로 설정해 장르별로 다양한 추천이 나오도록 함
- 3개 장르("공포", "SF", "액션")를 반복문으로 돌며 `synthetic_data` 리스트에 저장 → **이 리스트가 다음 단계의 평가 대상**

---

## Step 4: 합성 데이터 평가 (LLM as Judge)

**핵심 개념**

- **LLM as Judge**: 사람이 일일이 채점하는 대신 LLM에게 "평가자" 역할을 맡겨 자동으로 품질을 채점하는 방법론
- **평가자 선택 원칙**: 생성에 쓴 모델과 같은 모델을 평가자로 쓰면 자기 결과를 후하게 평가하는 편향이 생길 수 있어, 가급적 다른/더 큰 모델을 사용 (실습에서는 편의상 동일 `gpt-5-mini` 사용)
- **일관성**: 평가는 temperature를 낮게(또는 기본값) 설정해 채점 결과가 흔들리지 않도록 함
- **점수+이유 동시 생성**: 단순 점수만이 아니라 `comment`(근거)를 함께 받아 평가의 신뢰도를 높임

**코드 흐름**

```python
JUDGE_SYSTEM_PROMPT = """... 1-5점 채점 기준 정의 ... JSON으로 {"score":..., "comment":...} 출력 ..."""
JUDGE_USER_PROMPT_TEMPLATE = "- 입력 프롬프트: {instruction}\n- 모델 답변: {output}\n- 평가 기준: {criteria}"

def evaluate_with_llm(instruction, output, criteria):
    user_prompt = JUDGE_USER_PROMPT_TEMPLATE.format(...)
    response = client.chat.completions.create(model="gpt-5-mini", messages=[...])
    return json_parsing(response.choices[0].message.content)
```

이후 TODO 4에서는:

1. `criteria_list`(요청 충실도 / 추천 이유 구체성 / 정보 정확성 3가지 기준)로 **각 합성 데이터마다 3번씩 평가**를 수행해 `evaluation_results`에 저장
2. 각 데이터의 평균 점수 계산 → 전체 평균 점수 계산 → 4.0 이상/3.0 이상/미만 기준으로 "우수/보통/미흡" 등급 출력
3. 최종적으로 `pandas.DataFrame`으로 영화명, 연도, 장르, 추천 이유, 개별 점수 3개, 평균 점수를 표 형태로 정리

---

## 전체 파이프라인 요약

```
[환경설정/API 호출 함수 구축]
        ↓
[프롬프팅 기법 비교 (Zero/Few/CoT)] → 어떤 기법이 좋은 데이터를 만드는지 감 잡기
        ↓
[Few-shot/CoT 통찰을 반영한 구조화 프롬프트로 합성 데이터 생성 (JSON)]
        ↓
[LLM as Judge로 여러 기준에 대해 자동 채점]
        ↓
[평균 점수 → 품질 등급 판정 → DataFrame으로 정리]
```

즉 이 실습은 "LLM으로 데이터를 **만들고**(생성) → 그 데이터가 쓸만한지 LLM으로 **검증한다**(평가)"는, 실무에서 흔히 쓰이는 **합성 데이터 파이프라인의 축소판**을 체험하는 데 목적이 있습니다.
