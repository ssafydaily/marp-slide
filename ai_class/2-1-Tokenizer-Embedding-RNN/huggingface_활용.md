## Step 4: Huggingface 라이브러리 활용 정리

Step 4는 지금까지 직접 구현한 Seq2Seq(Encoder-Decoder) 구조를, 실제로 사전학습된(pre-trained) 모델을 불러와 추론에 활용하는 방식으로 전환하는 파트입니다.

### 1. Huggingface 소개

Huggingface는 최대 규모의 오픈소스 AI 모델 커뮤니티/허브입니다. 노트북에서 언급하듯 초기에는 자연어처리(NLP) 모델 위주였지만, 현재는 비전·음성·로봇 등 다양한 도메인의 사전학습 모델을 지원합니다. 핵심은 `transformers` 라이브러리를 통해 **모델 구조를 몰라도** 몇 줄의 코드로 토크나이저와 모델을 불러와 바로 추론할 수 있다는 점입니다. 이번 실습에서 직접 만들었던 `RNNEncoder`, `LSTMDecoder`, `LuongAttention` 등을 처음부터 구현하지 않아도, Huggingface Hub에 이미 학습되어 올라와 있는 모델을 그대로 가져다 쓸 수 있습니다.

### 2. 주요 클래스들 (Step 4 코드 기준)

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "Helsinki-NLP/opus-mt-ko-en"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
```

| 클래스 | 역할 |
|---|---|
| `AutoTokenizer` | 모델 이름(`model_name`)만 주면 그 모델에 맞는 토크나이저를 자동으로 찾아서 불러옵니다. 실습 초반에 직접 학습시킨 WordPiece 토크나이저와 같은 역할이지만, 이미 학습이 끝난 상태로 제공됩니다. |
| `AutoModelForSeq2SeqLM` | 번역·요약 같은 Encoder-Decoder 구조의 사전학습 모델을 자동으로 불러옵니다. 지금까지 직접 만든 `LSTMSeq2Seq`/`AttentionSeq2Seq`와 같은 역할을 하는, 학습이 완료된 완제품 모델입니다. |

`Helsinki-NLP/opus-mt-ko-en`은 한국어→영어 번역에 특화된 사전학습 모델입니다.

### 3. 사용 방법

**① 모델/토크나이저 불러오기**
```python
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
```
`from_pretrained`가 핵심 메서드로, Huggingface Hub에서 가중치와 설정 파일을 다운로드해 즉시 사용 가능한 객체로 반환합니다.

**② 모델 구조 확인 (2가지 방법)**
```python
print(model)                          # 구조를 사람이 보기 좋게 출력
for name, param in model.named_parameters():
    print(name)                       # 실제 파라미터(레이어) 이름들 나열
```
`print(model)`은 트리 구조로, `named_parameters()`는 각 가중치 텐서의 정확한 경로/이름으로 내부를 확인하는 방식입니다.

**③ 토큰화 (batch 차원 주의)**
```python
text = "나는 학교에 간다."
encoded = tokenizer(text, return_tensors="pt")
```
노트북 주석에서 강조하듯, 직접 구현한 실습 코드에서는 입력이 `[seq_len]`이었지만, Huggingface의 `tokenizer(...)`는 **항상 batch 차원을 포함**해 `[batch_size, seq_len]` 형태로 반환합니다. 문장이 하나여도 `[1, seq_len]`입니다.

**④ 추론(생성)**
```python
generated_ids = model.generate(**encoded, max_new_tokens=64)
translation = tokenizer.decode(generated_ids.squeeze(), skip_special_tokens=True)
```
- `model.generate()`: 직접 구현했던 `for _ in range(max_len): ... argmax ... break` 루프(Todo 2, 3에서 만든 디코딩 루프)를 대신 처리해주는 고수준 메서드입니다. beam search, sampling 등 다양한 디코딩 전략도 내부적으로 지원합니다.
- `tokenizer.decode(..., skip_special_tokens=True)`: 생성된 id 시퀀스를 다시 텍스트로 변환하면서 `[CLS]`, `[SEP]` 같은 특수 토큰은 자동으로 제거합니다.

### 4. 알면 좋은 점 / 주의점

- **`Auto*` 클래스의 편의성**: `AutoTokenizer`, `AutoModelForSeq2SeqLM`처럼 `Auto` 접두사가 붙은 클래스는 모델 이름만으로 내부적으로 알맞은 구체 클래스(예: MarianMT 계열)를 자동 선택합니다. 모델마다 어떤 클래스를 써야 하는지 일일이 알 필요가 없습니다.
- **직접 구현 코드와의 차이**: 실습 앞부분에서 직접 만든 모델은 학습되지 않은 랜덤 초기화 상태라 결과가 의미 없었지만(노트북 39번 셀에서 언급), Huggingface에서 불러온 모델은 이미 대규모 데이터로 학습이 끝난 상태이므로 훨씬 자연스러운 번역 결과가 나옵니다.
- **추가 의존성 필요**: 노트북 상단 안내처럼 `Helsinki-NLP/opus-mt-ko-en` 모델을 쓰려면 `sentencepiece`, `sacremoses` 패키지가 별도로 필요합니다. 모델마다 요구하는 부가 패키지가 다를 수 있어 에러 메시지를 잘 확인해야 합니다.
- **입력 shape 관례 차이**: 직접 구현 코드는 batch 없이 `(seq_len, ...)`로 다뤘지만, Huggingface 생태계 전반은 기본적으로 `(batch_size, seq_len, ...)`을 가정합니다. 다른 Huggingface 코드와 섞어 쓸 때 이 shape 차이를 항상 염두에 둬야 합니다.
- **`device` 처리**: 이 셀에서는 `.to(device)` 호출이 빠져 있는데(바로 다음 Step 5의 BERT/GPT2 예제부터는 `.to(device)`가 붙습니다), GPU를 쓰려면 모델과 입력 텐서(`encoded`) 모두 같은 device로 옮겨줘야 합니다.
- **`model.generate()`는 학습이 아니라 추론 전용**: 그래디언트 계산이 필요 없으므로 실제 서비스 코드에서는 `torch.no_grad()`(Step 5의 GPT-2 예제처럼)로 감싸 메모리/속도를 아끼는 것이 일반적입니다.