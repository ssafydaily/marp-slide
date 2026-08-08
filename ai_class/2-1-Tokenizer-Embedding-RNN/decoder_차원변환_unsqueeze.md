```python
# 2. 위에서 만든 은닉벡터를 `nn.Linear`를 거쳐 토큰을 예측하여 `logit`을 만들어줍니다.
logit = self.fully_connected_layer(h_n) # (1, vocab_size)
logit = logit.squeeze()
logits.append(logit)

# 3. `logit`을 기반으로 예측된 토큰인 `output_token`을 `argmax`를 통해 찾아줍니다.
output_token = torch.argmax(logit, dim=-1).unsqueeze(0)
output_token_ids.append(output_token.item())
```

네. 이 부분은 **RNN의 출력 Tensor 차원을 추적하면 `squeeze()`와 `unsqueeze()`를 왜 사용하는지 아주 명확하게 이해할 수 있습니다.**

특히 핵심은:

> **`squeeze()`는 계산하기 편한 형태로 차원을 없애고, `unsqueeze()`는 다음 RNN 입력에 맞게 차원을 다시 추가하는 역할**입니다.

---

# 1. 먼저 전체 흐름

해당 코드를 차원 변화 중심으로 보면 다음과 같습니다.

```text
h_n
(1, 1024)
   │
   │ nn.Linear
   ▼
logit
(1, vocab_size)
   │
   │ squeeze()
   ▼
logit
(vocab_size)
   │
   │ argmax()
   ▼
token_id
()
   │
   │ unsqueeze(0)
   ▼
output_token
(1,)
```

예를 들어 `vocab_size = 30,000`이라면:

```text
(1, 1024)
     │
     ▼
(1, 30000)
     │
 squeeze()
     ▼
(30000)
     │
 argmax()
     ▼
()
     │
 unsqueeze(0)
     ▼
(1)
```

입니다.

---

# 2. 먼저 `h_n`의 크기

Decoder의 RNN 부분을 다시 보면:

```python
_, h_n = self.rnn(embedded, h_n)
```

이때 실습 코드에서는

```text
batch_first = False
```

이므로 RNN의 hidden state는 일반적으로

```text
(num_layers * num_directions, batch_size, hidden_size)
```

형태입니다.

현재 실습에서는

```text
num_layers = 1
num_directions = 1
batch_size = 1
hidden_size = 1024
```

이므로:

```text
h_n
 ↓
(1, 1, 1024)
```

가 될 수 있습니다.

다만 파일의 구현/출력 맥락에서는 `h_n`을 Linear에 넣어 결과를 `(1, vocab_size)` 형태로 다루고 있습니다.

개념적으로 중요한 것은 **마지막 두 차원에서 `1024 → vocab_size`가 변한다는 것**입니다.

---

# 3. `nn.Linear`를 통과하면

코드는:

```python
logit = self.fully_connected_layer(h_n)
```

입니다.

Linear가

```python
nn.Linear(hidden_size, vocab_size)
```

이므로

```text
1024 → 30,000
```

으로 변환합니다.

예를 들어:

```text
h_n
[1, 1024]
     │
     │ Linear
     ▼
logit
[1, 30000]
```

입니다.

여기서 `logit`은

> **30,000개의 vocabulary 각각에 대한 예측 점수**

입니다.

---

# 4. 왜 `squeeze()`를 하는가?

코드:

```python
logit = logit.squeeze()
```

입니다.

현재:

```text
logit
(1, 30000)
```

인데 첫 번째 차원의 크기가 `1`입니다.

`torch.squeeze()`는 **크기가 1인 차원을 제거**합니다.

따라서:

```text
(1, 30000)
      │
   squeeze()
      │
      ▼
(30000)
```

이 됩니다.

---

# 5. 왜 `(1, 30000)`보다 `(30000)`이 편한가?

이제 다음 코드가 실행됩니다.

```python
output_token = torch.argmax(logit, dim=-1)
```

현재 `logit`이

```text
(30000)
```

이므로:

```text
logit
│
├── ID 0      점수
├── ID 1      점수
├── ID 2      점수
├── ...
└── ID 29999  점수
```

가 됩니다.

`argmax(dim=-1)`을 하면

```text
30000개의 점수
       │
       ▼
가장 큰 값의 위치
       │
       ▼
하나의 정수
```

가 됩니다.

예를 들어:

```text
logit =
[-1.2, 0.5, 3.8, ..., 1.1]

argmax
   ↓

2
```

즉,

```text
(30000)
   │
 argmax
   ▼
스칼라
```

입니다.

---

# 6. 그런데 왜 다시 `unsqueeze(0)`을 하는가?

바로 다음 코드입니다.

```python
output_token = torch.argmax(logit, dim=-1).unsqueeze(0)
```

먼저 `argmax()`만 수행하면:

```text
logit
(30000)
   │
   ▼
argmax
   │
   ▼
2
```

즉 **스칼라 Tensor**가 됩니다.

그런데 Decoder는 다음 단계에서 이 값을 다시 Embedding에 넣어야 합니다.

```python
embedded = self.word_embeddings(input_token)
```

그리고 다음 단계의 `input_token`으로 사용해야 합니다.

따라서 토큰 ID를 **1차원 Tensor 형태**로 만들어줍니다.

```text
스칼라
()
 │
 │ unsqueeze(0)
 ▼
(1)
```

즉:

```text
2
 ↓
tensor(2)
 ↓ unsqueeze(0)
tensor([2])
```

가 됩니다.

---

# 7. `unsqueeze(0)`의 의미

`unsqueeze(0)`은

> **0번 위치에 크기 1인 차원을 추가한다**

는 뜻입니다.

예:

```python
x.shape
```

가

```text
()
```

라면

```python
x.unsqueeze(0).shape
```

는

```text
(1,)
```

이 됩니다.

시각적으로:

```text
Before

tensor(3421)
   shape = ()


          │
          │ unsqueeze(0)
          ▼

After

tensor([3421])
   shape = (1,)
```

---

# 8. 그런데 `output_token_ids.append(output_token.item())`은 왜 `.item()`인가?

다음 코드도 같이 보겠습니다.

```python
output_token_ids.append(output_token.item())
```

현재:

```text
output_token
    ↓
tensor([3421])
    ↓
shape = (1,)
```

입니다.

그런데 Python 리스트에는 Tensor 자체가 아니라 **일반 Python 정수**를 저장하고 싶습니다.

그래서:

```python
output_token.item()
```

을 사용합니다.

결과:

```text
tensor([3421])
      │
      │ .item()
      ▼
3421
```

따라서:

```python
output_token_ids
```

에는

```python
[3421, 527, 8921, ...]
```

같은 일반 정수 리스트가 저장됩니다.

---

# 9. 전체 과정을 연결하면

이 부분을 **Tensor의 shape 변화**로 추적해보겠습니다.

```text
             RNN Decoder
                  │
                  ▼
             h_n
           (1, 1024)
                  │
                  │ Linear
                  ▼
             logit
          (1, 30000)
                  │
                  │ squeeze()
                  ▼
             logit
            (30000)
                  │
                  │ argmax(dim=-1)
                  ▼
          token index
               ()
                  │
                  │ unsqueeze(0)
                  ▼
          output_token
              (1,)
                  │
                  ├───────────────┐
                  │               │
                  │ .item()       │ 다음 step
                  ▼               ▼
               Python int    input_token
                  │               │
                  ▼               ▼
          output_token_ids    Embedding
                               (1, 768)
```

---

# 10. 왜 `squeeze → unsqueeze`를 굳이 하는가?

처음 보면 이렇게 생각할 수 있습니다.

> "차원을 없앴다가 다시 추가하는데 왜 이렇게 하지?"

맞습니다. 이 코드는 **각 연산에서 필요한 Tensor 형태가 다르기 때문에** 이렇게 처리합니다.

### `squeeze()`

```text
(1, vocab_size)
       ↓
(vocab_size)
```

목적:

> **vocabulary별 점수 벡터를 1차원으로 만들어 `argmax`하기 편하게 한다.**

---

### `unsqueeze(0)`

```text
()
 ↓
(1,)
```

목적:

> **선택된 토큰 ID를 다음 Decoder 단계에서 사용할 Tensor 형태로 만든다.**

---

# 11. `squeeze()`와 `unsqueeze()`를 그림으로 기억하면

```text
        Linear 출력
            │
            ▼
     ┌──────────────┐
     │ 30000개의    │
     │   logits     │
     └──────────────┘
       (1, 30000)
            │
            │ squeeze()
            ▼
       (30000)
            │
            │ argmax()
            ▼
          3421
            │
            │ unsqueeze(0)
            ▼
       tensor([3421])
            │
            ▼
       다음 입력 Token
```

즉,

[
\boxed{
(1,30000)
\xrightarrow{squeeze}
(30000)
\xrightarrow{argmax}
()
\xrightarrow{unsqueeze}
(1)
}
]

입니다.

---

## 12. 한 가지 주의할 점

`logit.squeeze()`는 **모든 크기 1인 차원을 제거**합니다.

따라서 배치 크기가 1이 아닌 일반적인 상황에서는 조심해야 합니다.

예를 들어:

```text
(1, 1, 30000)
```

에 `squeeze()`를 하면:

```text
(30000)
```

이 되어 batch 차원까지 사라질 수 있습니다.

실제 딥러닝 코드에서는 이런 이유 때문에 종종

```python
logit = logit.squeeze(0)
```

처럼 **제거할 차원을 명시**하는 방법이 더 안전합니다.

---

### 핵심만 정리하면

```text
squeeze()
   ↓
불필요한 크기 1 차원 제거
   ↓
(1, vocab_size) → (vocab_size)


unsqueeze(0)
   ↓
크기 1인 차원 추가
   ↓
() → (1,)
```

그리고 이 코드에서는

> **`squeeze()`는 `argmax`를 위해, `unsqueeze()`는 선택된 토큰 ID를 다음 Decoder 단계의 입력 형태로 맞추기 위해 사용한다**

라고 이해하시면 가장 좋습니다.
