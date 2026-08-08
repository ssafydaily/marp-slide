# 토큰화 & 임베딩 정리노트

> 원본 파일: `2_1_토큰화_임베딩__Easy_.ipynb`

---

## 1. 주요 개념 요약

### 1-1. 토크나이저(Tokenizer)란?

- 문장을 **토큰 단위로 분리**하고, 각 토큰을 **정수(ID)로 변환**해주는 도구.
- 예: `"안녕하세요"` → `["안녕", "하세요"]` → `[8192, 91352]`
- 모델은 숫자만 입력받을 수 있으므로(`y = wx + b`의 `x`), 문장을 그대로 넣을 수 없어 토큰화가 필요함.
- 동작 원리
  1. 미리 학습된 **Vocabulary(사전)** 를 다운로드해서 준비 (단어/조각 ↔ Index 매핑)
  2. 입력 문장을 Vocabulary에 있는 조각들로 쪼갠 뒤 Index로 치환

### 1-2. Vocabulary 학습(Tokenizer Training) 알고리즘 2종

| 알고리즘                 | 분할 단위       | 특징                                                  | 사용 토크나이저                  |
| ------------------------ | --------------- | ----------------------------------------------------- | -------------------------------- |
| **Word Piece**     | 글자(Character) | 자주 붙어 나오는 글자 조합을 점수화해서 토큰으로 선정 | BERT 토크나이저                  |
| **Byte-Level BPE** | Byte            | 자주 붙어 나오는 Byte 조합을 빈도 기준으로 토큰화     | GPT, DeepSeek 등 최신 LLM 대부분 |

- 영어는 1글자 = 1Byte, 한글/한자/일본어는 3Byte, 이모지는 4Byte (UTF-8 기준)
- BERT 토크나이저는 영어 위주로 만들어져 한국어엔 추가 학습이 필요하지만, Byte-Level BPE는 바이트 단위라 언어에 상관없이 잘 동작 → **최신 대규모 모델은 대부분 Byte-Level BPE 사용**

### 1-3. 두 토크나이저의 출력 특징

- **BERT(WordPiece) 토크나이저**: 접두어가 아닌 조각 앞에 `##`이 붙음 (예: `##하다` → 앞에 다른 글자가 이어짐을 의미)
- **GPT2류(Byte-Level BPE) 토크나이저**: 띄어쓰기를 의미하는 `Ġ` 기호가 자주 등장. 한글은 Byte 단위로 잘게 쪼개져 사람이 읽기엔 토큰 표시가 지저분해 보임(디코딩하면 정상 복원)

### 1-4. 허깅페이스(Hugging Face)

- AI 모델·툴을 오픈소스로 공유하는 플랫폼(“AI계의 GitHub”)
- 모델 저장소(repository)에는 보통
  - `README.md` → Model Card로 표시
  - `tokenizer.json` → Vocabulary + 토큰화 설정을 모두 포함 (현재 권장 방식, 예전엔 `vocab.txt` 사용)
  - `tokenizer_config.json` → 부가 옵션 (없어도 기본값으로 동작)
  - 모델 가중치: 과거 `pytorch_model.bin` → 최근에는 `model.safetensors`(보안 강화, 악성코드 실행 방지) 권장

### 1-5. 임베딩(Embedding) 모델

- 토큰(ID)을 **"의미공간"이라는 벡터공간**으로 매핑해주는 모델.
- **비슷한 의미의 단어는 벡터공간에서 서로 가까운 위치**에 놓이도록 학습됨.
- 주로 Transformer 구조로 학습.
- 필요한 이유: 같은 뜻이라도 표현이 조금만 달라지면(오타·언어 차이 등) 모델 성능이 떨어지는 문제를, 임베딩으로 "의미가 비슷하면 벡터도 비슷하게" 만들어 해결.

### 1-6. Pooling(풀링)

- 문장 내 여러 토큰의 벡터(N개)를 **하나의 벡터로 합치는** 작업.
- 가장 흔한 방식: **Mean Pooling** (평균으로 합치기)
- 문장 임베딩 = 토큰 임베딩들의 평균 벡터

### 1-7. 코사인 유사도(Cosine Similarity)

- 두 벡터가 얼마나 비슷한 "방향"을 가지는지 측정하는 지표 (크기는 무시, 방향만 비교)
- 계산식: `cos_sim(A, B) = (A · B) / (‖A‖ × ‖B‖)`
- **L2 정규화**(벡터 크기를 1로 만듦)를 미리 해두면, 이후 코사인 유사도는 단순 내적(dot product)만으로 계산 가능
  - LLM 자체 학습에는 L2 정규화를 보통 쓰지 않음(크기 정보 손실 때문)
  - 이미지·텍스트 **검색(유사도 매칭)**에서는 크기가 방해되므로 L2 정규화를 자주 사용 (RAG 등)

### 1-8. 임베딩 모델 활용 구조

- 감정 분류 등 응용 모델을 만들 때, **임베딩 모델을 앞단(입력 전처리)** 로 두고 그 출력(문장 벡터)을 본 모델의 입력으로 사용하는 구조가 일반적.
- 학습 순서(일반적 패턴)
  1. 임베딩 모델을 범용으로 먼저 학습(또는 사전학습 모델 사용)
  2. 임베딩 모델 뒤에 원하는 태스크용 레이어(본 모델) 추가
  3. 임베딩 모델 파라미터는 고정(freeze)
  4. 본 모델만 학습

---

## 2. 사용된 코드와 라이브러리 설명

### 2-1. 핵심 라이브러리

| 라이브러리                               | 역할                                                                                                       |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `transformers` (Hugging Face)          | 토크나이저·모델 다운로드 및 추론.`AutoTokenizer`, `AutoModel` 등 제공                                 |
| `torch` (PyTorch)                      | 텐서 연산, 모델 추론(`torch.no_grad()` 등)                                                               |
| `sentence-transformers`                | `transformers`를 감싸서 문장 임베딩(코사인 유사도, 정규화, Pooling)을 더 쉽게 처리해주는 상위 라이브러리 |
| `plotly`                               | 인터랙티브 시각화 (임베딩 벡터를 3D로 축소해 시각화)                                                       |
| `sklearn.decomposition.PCA`            | 고차원 임베딩 벡터(384차원 등)를 3차원으로 축소(주성분분석)                                                |
| `numpy` / `seaborn` / `matplotlib` | 수치 연산 및 히트맵 등 일반 시각화                                                                         |

### 2-2. 코드 흐름별 설명

**(1) BERT 계열 토크나이저 사용 (WordPiece)**

```python
from transformers import AutoTokenizer

model_id = "google-bert/bert-base-multilingual-cased"
tokenizer = AutoTokenizer.from_pretrained(model_id)

tokens_kor = tokenizer.tokenize(korean)          # 문장 → 토큰 리스트
ids_kor = tokenizer.convert_tokens_to_ids(tokens_kor)  # 토큰 → ID 리스트
```

- `AutoTokenizer.from_pretrained(model_id)`로 모델 ID(허깅페이스 저장소 경로)에 해당하는 사전 학습 토크나이저를 다운로드/로드.
- 결과는 `~/.cache/huggingface/hub` 아래에 캐시됨.

**(2) ID → 문자열 복원**

```python
token = tokenizer.decode([19865])
```

- ID 리스트를 다시 사람이 읽을 수 있는 문자열로 복원.

**(3) GPT2(Byte-Level BPE) 토크나이저**

```python
model_id = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokens_eng = tokenizer.tokenize(english)
```

- 동일한 `AutoTokenizer` 인터페이스로 다른 알고리즘의 토크나이저도 동일하게 사용 가능(추상화의 장점).

**(4) 로컬 폴더에서 토크나이저 불러오기**

```python
tokenizer = AutoTokenizer.from_pretrained("./tokenizer_deepseek")
```

- 허깅페이스 모델 ID 대신 로컬 경로를 넣으면, 해당 폴더 안의 `tokenizer.json`(+ `tokenizer_config.json`)을 읽어 토크나이저를 구성.

**(5) 임베딩 모델로 벡터 뽑고 Mean Pooling**

```python
from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained("intfloat/e5-small-v2")
model = AutoModel.from_pretrained("intfloat/e5-small-v2")

tokens = tokenizer(words, padding=True, return_tensors='pt')

with torch.no_grad():
    outputs = model(**tokens)
    embeddings = outputs.last_hidden_state.mean(dim=1)  # Mean Pooling
    result = embeddings.tolist()
```

- `padding=True`: 배치 내 문장 길이를 맞추기 위해 짧은 문장 뒤를 0으로 채움(모델 입력은 동일 shape 필요).
- `return_tensors='pt'`: 결과를 PyTorch 텐서로 반환.
- `model(**tokens)`: 토큰화 결과 딕셔너리를 그대로 모델에 입력(`input_ids`, `attention_mask` 등 자동 매핑).
- `outputs.last_hidden_state`: 모델의 마지막 레이어 은닉 상태, shape = (문장 수, 토큰 수, 은닉 차원).
- `.mean(dim=1)`: 토큰 축(문장 내 위치)을 기준으로 평균 → 문장 벡터 하나로 축소(Mean Pooling).
- `torch.no_grad()`: 추론 시 그래디언트 계산을 끄고 메모리·속도 절약.

**(6) 코사인 유사도 (직접 계산)**

```python
embeddings = embeddings / embeddings.norm(dim=1, keepdim=True)  # L2 정규화
cos_sim_matrix = torch.matmul(embeddings, embeddings.T).numpy() # 정규화 후엔 내적=코사인유사도
```

- `.norm(dim=1, keepdim=True)`: 각 벡터의 L2 크기(유클리드 노름) 계산.
- 정규화된 벡터끼리 내적(`matmul`)하면 곧 코사인 유사도.

**(7) sentence-transformers로 더 간단히**

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")

query_embeddings = model.encode(queries, prompt_name="query")
document_embeddings = model.encode(documents)

similarity = model.similarity(query_embeddings, document_embeddings)
max_index = torch.argmax(similarity, dim=1).tolist()
```

- `SentenceTransformer(model_id)`: Pooling·정규화·유사도 계산까지 자동 처리해주는 상위 래퍼.
- `model.encode(texts, prompt_name=...)`: 문장 리스트를 임베딩 벡터로 변환. `prompt_name="query"`는 Qwen3 계열 모델이 "이 입력은 질의문이다"라는 문맥을 알려주기 위한 프롬프트 프리셋(질문/문서를 구분해 성능을 높임).
- `model.similarity(A, B)`: 두 임베딩 집합 간 코사인 유사도 행렬(A개수 × B개수)을 자동 계산.
- `torch.argmax(similarity, dim=1)`: 각 질의(query)마다 가장 유사도가 높은 문서의 인덱스를 반환.

---

## 3. 함수/메소드별 매개변수·반환값 정리

| 함수(메소드)                                            | 주요 매개변수                                                                                    | 반환값                                                                 |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| `AutoTokenizer.from_pretrained(model_id)`             | `model_id`: 허깅페이스 모델 ID 또는 로컬 경로                                                  | 해당 모델용 토크나이저 객체                                            |
| `AutoModel.from_pretrained(model_id)`                 | `model_id`: 허깅페이스 모델 ID                                                                 | 사전학습된 모델 객체(nn.Module)                                        |
| `tokenizer.tokenize(text)`                            | `text`: 입력 문자열                                                                            | 토큰(문자열 조각) 리스트                                               |
| `tokenizer.convert_tokens_to_ids(tokens)`             | `tokens`: 토큰 리스트                                                                          | 각 토큰에 대응하는 정수 ID 리스트                                      |
| `tokenizer.decode(ids)`                               | `ids`: 정수 ID 리스트                                                                          | 복원된 문자열                                                          |
| `tokenizer(texts, padding=True, return_tensors='pt')` | `texts`: 문자열(리스트), `padding`: 길이 맞춤 여부, `return_tensors`: `'pt'`(PyTorch) 등 | `input_ids`, `attention_mask` 등을 담은 딕셔너리(배치 인코딩 객체) |
| `model(**tokens)`                                     | 토큰화 딕셔너리(언패킹)                                                                          | 모델 출력 객체(`last_hidden_state` 등 포함)                          |
| `outputs.last_hidden_state.mean(dim=1)`               | `dim=1`: 평균낼 축(토큰 축)                                                                    | 문장 단위로 pooling된 임베딩 텐서                                      |
| `tensor.norm(dim=1, keepdim=True)`                    | `dim`: 계산 축, `keepdim`: 차원 유지 여부                                                    | 각 벡터의 L2 노름(크기)                                                |
| `torch.matmul(A, B)`                                  | `A`, `B`: 텐서                                                                               | 행렬곱 결과 텐서                                                       |
| `torch.no_grad()`                                     | (컨텍스트 매니저, 매개변수 없음)                                                                 | 그래디언트 계산 비활성화 컨텍스트                                      |
| `SentenceTransformer(model_id)`                       | `model_id`: 허깅페이스 모델 ID                                                                 | Sentence-Transformers 모델 객체                                        |
| `model.encode(texts, prompt_name=None)`               | `texts`: 문장(리스트), `prompt_name`: 프롬프트 프리셋 이름(예: `"query"`)                  | 문장 임베딩 벡터(넘파이 배열 또는 텐서)                                |
| `model.similarity(A, B)`                              | `A`, `B`: 임베딩 벡터 집합                                                                   | 코사인 유사도 행렬                                                     |
| `torch.argmax(tensor, dim=1)`                         | `dim`: 최댓값을 찾을 축                                                                        | 최댓값의 인덱스 텐서                                                   |

---

## 4. 반드시 알아야 할 내용 · 주의사항

1. **BERT는 언어모델이지 토크나이저가 아님** — "BERT 토크나이저"는 BERT가 학습에 사용한 WordPiece 기반 토크나이저를 가리키는 것이며, 오늘날 BERT 자체나 BERT 토크나이저는 실무에서 거의 쓰이지 않는다. 현재 주류는 Byte-Level BPE 계열.
2. **"BPE"라는 용어의 혼동 주의** — Character-Level BPE와 Byte-Level BPE는 서로 다르다. 그냥 "BPE"라고만 하면 어느 쪽인지 불명확하므로 Byte-Level BPE(BBPE)처럼 명시하는 것이 안전.
3. **Byte-Level BPE의 깨져 보이는 출력은 정상** — 토큰 문자열이 이상한 기호로 보이는 것은 내부적으로 커스텀 문자코드(예: Latin-1 유사 매핑)를 쓰기 때문이며, `tokenizer.decode()`로 복원하면 정상적으로 보인다. 다만 한글처럼 여러 Byte로 나뉘는 문자는 토큰 하나만 디코딩하면 깨질 수 있다(전체 시퀀스를 디코딩해야 정상 복원).
4. **모델 파일 포맷 보안 이슈** — `.bin`(pickle 기반) 파일은 악성코드 실행 위험이 있어, 허깅페이스는 2023년 이후 `.safetensors` 포맷을 권장한다.
5. **`vocab.txt` vs `tokenizer.json`** — 예전에는 `vocab.txt`만으로 충분했지만, 지금은 토큰화 설정까지 포함한 `tokenizer.json` 사용이 표준이다. 구버전 호환을 위해 `vocab.txt`가 같이 있는 경우도 있다.
6. **Padding과 배치 처리** — 여러 문장을 한 번에 토큰화할 때 `padding=True`가 없으면 문장 길이가 달라 텐서로 묶을 수 없다. 짧은 문장은 뒤에 0(패딩 토큰)으로 채워지고, 이는 `attention_mask`로 실제 유효 토큰과 구분된다.
7. **L2 정규화는 상황에 따라 사용 여부가 다름** — LLM 학습 자체에서는 벡터의 크기 정보도 의미가 있어 정규화를 잘 쓰지 않지만, 유사도 검색(RAG 등)에서는 방향(의미)만 비교하면 되므로 정규화를 널리 사용한다.
8. **코사인 유사도 값의 범위 특성** — 실제 임베딩끼리 비교하면 이론상 -1~1 범위지만, 실무에서는 대체로 0.5~0.9 사이 값이 나오는 경우가 많다(모델·데이터 특성에 따라 다름). 철자가 비슷한 단어(cat/car 등)도 의미와 무관하게 유사도가 높게 나올 수 있음에 유의.
9. **차원 축소 시각화는 정보 손실을 동반** — 384차원 등 고차원 임베딩을 PCA로 3차원까지 축소해 시각화하면 직관적으로 보기엔 좋지만, 실제 유사도 순위와는 차이가 날 수 있다(원본 고차원에서 코사인 유사도를 계산하는 것이 더 정확).
10. **Qwen3 등 최신 임베딩 모델의 `prompt_name`** — 질의문(query)과 문서(document)를 구분해 프롬프트를 다르게 주면 검색 성능이 향상된다. 실습에서는 `model.encode(queries, prompt_name="query")`처럼 질의에만 프리셋을 지정하고 문서는 기본값을 사용했다.
11. **모델 다운로드 관련 실습 환경 주의** — Colab 등에서 대용량 모델(수백 MB~1GB 이상)을 다운로드할 때 런타임 연결이 끊기거나 재실행이 필요할 수 있다. 첫 다운로드가 완료되면 캐시(`~/.cache/huggingface/hub`)를 재사용하므로 이후 실행은 빨라진다.
12. **임베딩 모델은 사실상 필수 요소** — 2018년 이후 대부분의 LLM 파이프라인이 임베딩(및 Transformer 구조)을 기반으로 하고 있어, 토크나이저·임베딩 개념은 이후 모든 LLM 실습의 기초가 된다.

---

## 5. 전체 학습 흐름 요약

```
문장 입력
   ↓ (토크나이저: WordPiece 또는 Byte-Level BPE)
토큰 ID 리스트
   ↓ (임베딩 모델, 예: AutoModel / SentenceTransformer)
토큰별 벡터 (last_hidden_state)
   ↓ (Pooling, 보통 Mean Pooling)
문장 벡터 (하나의 벡터로 압축)
   ↓ (필요 시 L2 정규화 → 코사인 유사도 계산)
문장 간 유사도 비교 / 후속 모델(분류기 등)의 입력으로 활용
```
