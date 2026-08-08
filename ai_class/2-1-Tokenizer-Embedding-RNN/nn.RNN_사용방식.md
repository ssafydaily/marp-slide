네. **같은 `nn.RNN`을 생성하지만 Encoder와 Decoder에서 사용하는 방식은 상당히 다릅니다.**
첨부 파일의 Step 2 코드를 보면 두 클래스 모두 다음과 같이 동일한 형태의 RNN을 생성합니다.  

```python
self.rnn = nn.RNN(
    input_size=embedding_dim,
    hidden_size=hidden_size,
    num_layers=num_layers,
    bidirectional=bidirectional,
)
```

그런데 **RNN을 호출하는 방법**이 다릅니다.

---

# 1. 핵심 차이부터

|              | Encoder                                   | Decoder                     |
| ------------ | ----------------------------------------- | --------------------------- |
| RNN 입력       | **전체 시퀀스**                                | **한 토큰씩**                   |
| 입력 형태        | `(sequence_length, batch, embedding_dim)` | `(1, batch, embedding_dim)` |
| hidden state | RNN이 초기값을 생성                              | **Encoder의 `h_n`을 전달**      |
| RNN 호출       | `self.rnn(input_embeds)`                  | `self.rnn(embedded, h_n)`   |
| 출력 사용        | `hidden_states`, `h_n` 모두                 | `h_n`만 사용                   |
| 목적           | 입력 문장 전체를 읽음                              | 다음 토큰을 하나씩 생성               |

파일의 Encoder는 실제로

```python
hidden_states, h_n = self.rnn(input_embeds)
```

를 수행합니다. 

반면 Decoder는

```python
_, h_n = self.rnn(embedded, h_n)
```

를 반복합니다. 

---

# 2. Encoder는 전체 문장을 한 번에 넣는다

예를 들어 입력 문장이 토큰 5개라고 하겠습니다.

```text
나는  학교에  간다
 ↓     ↓       ↓
ID₁   ID₂     ID₃
```

Embedding을 거치면:

```text
ID₁ ──► x₁ : 768
ID₂ ──► x₂ : 768
ID₃ ──► x₃ : 768
ID₄ ──► x₄ : 768
ID₅ ──► x₅ : 768
```

Encoder에서는 이것들을 **한꺼번에 RNN에 전달**합니다.

```python
input_embeds = self.word_embeddings(input_ids)

hidden_states, h_n = self.rnn(input_embeds)
```

즉,

```text
                Encoder RNN
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
      x₁           x₂           x₃ ... x₅
     768           768          768
       │            │            │
       ▼            ▼            ▼
      h₁ ─────────► h₂ ───────► h₃ ... h₅
```

개념적으로는 RNN이 내부에서 시간 순서대로

```text
x₁ → h₁
      ↓
x₂ → h₂
      ↓
x₃ → h₃
      ↓
...
x₅ → h₅
```

를 수행합니다.

따라서 Encoder는 **"문장을 처음부터 끝까지 읽는 역할"**입니다.

---

# 3. Encoder에서는 초기 hidden state를 주지 않는다

다음 코드를 보세요.

```python
self.rnn(input_embeds)
```

두 번째 인자인 `h_0`을 전달하지 않았습니다.

그러면 PyTorch의 `nn.RNN`이 기본적으로 **0으로 초기화된 hidden state**를 사용합니다.

개념적으로:

```text
h₀ = 0
 │
 ▼
x₁ ──► RNN ──► h₁
               │
x₂ ───────────► RNN ──► h₂
                          │
x₃ ─────────────────────► RNN ──► h₃
                                      │
                                     ...
                                      │
x₅ ──────────────────────────────────► h₅
```

최종적으로

```text
h₅ = h_n
```

을 얻습니다.

이 `h_n`이 Encoder가 읽은 문장의 정보를 압축한 **context vector**가 됩니다.

---

# 4. Decoder는 한 번에 한 토큰만 넣는다

Decoder에서는 상황이 완전히 다릅니다.

Encoder가 만든

```text
h_n
```

을 Decoder의 초기 hidden state로 사용합니다.

그리고 처음에는 `[CLS]`를 입력합니다.

```text
Encoder
   │
   │ h_n
   ▼
Decoder의 초기 hidden state
```

그리고:

```text
[CLS]
  │
  ▼
Embedding
  │
  ▼
x₁
  │
  ▼
RNN
  │
  ▼
h₁
  │
  ▼
Linear
  │
  ▼
다음 토큰
```

파일에서도 이 구조로 구현되어 있습니다.

```python
embedded = self.word_embeddings(input_token)
_, h_n = self.rnn(embedded, h_n)
```



---

# 5. Decoder의 핵심은 `h_n`을 계속 전달한다는 것

이 부분이 Encoder와 Decoder의 가장 중요한 차이입니다.

첫 번째 Decoder step:

```text
Encoder h_n
    │
    ▼
Decoder RNN
    ▲
    │
 [CLS]
    │
    ▼
   h₁
```

두 번째 step:

```text
      h₁
       │
       ▼
Decoder RNN
    ▲
    │
  "나는"
    │
    ▼
   h₂
```

세 번째:

```text
      h₂
       │
       ▼
Decoder RNN
    ▲
    │
  "학교"
    │
    ▼
   h₃
```

즉,

[
h_t = RNN(x_t,h_{t-1})
]

입니다.

---

# 6. 그래서 Decoder 코드가 이렇게 생겼다

파일의 코드를 다시 보면:

```python
for _ in range(max_len):

    embedded = self.word_embeddings(input_token)

    _, h_n = self.rnn(embedded, h_n)

    logit = self.fully_connected_layer(h_n)
```



이것을 그림으로 바꾸면:

```text
                ┌─────────────────────┐
                │     Decoder RNN     │
                └─────────────────────┘
                     ▲           │
                     │           ▼
                   h₀│          h₁
                     │           │
                   [CLS]         │
                     │           │
                  Embedding       │
                     │           │
                     ▼           │
                    x₁           │
                                  │
                     ┌────────────┘
                     ▼
                  Linear
                     │
                     ▼
                다음 Token
                     │
                     │
                     ▼
                  Embedding
                     │
                     ▼
                    x₂
                     │
                     ▼
                ┌─────────┐
              h₁│   RNN   │
                └────┬────┘
                     │
                     ▼
                    h₂
                     │
                    ...
```

즉 Decoder는 **RNN을 한 번 호출하고 끝나는 것이 아니라, 토큰을 생성할 때마다 RNN을 반복 호출**합니다.

---

# 7. `nn.RNN` 객체는 하나인데 어떻게 반복해서 사용할 수 있는가?

여기가 상당히 중요한 개념입니다.

```python
self.rnn = nn.RNN(...)
```

은 **RNN의 가중치를 가진 하나의 RNN 객체**를 만드는 것입니다.

Decoder에서는 이 동일한 객체를 반복 사용합니다.

```python
self.rnn(embedded, h_n)
```

↓

```python
self.rnn(embedded, h_n)
```

↓

```python
self.rnn(embedded, h_n)
```

↓

```python
...
```

이때 **RNN의 가중치는 동일합니다.**

```text
               동일한 RNN 가중치
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
        Step 1      Step 2     Step 3
          │          │          │
        RNN         RNN        RNN
          │          │          │
         h₁         h₂         h₃
```

따라서 이것을 **RNN의 시간축을 직접 하나씩 실행한다**고 생각하면 됩니다.

---

# 8. Encoder와 Decoder의 차이를 가장 직관적으로 비교

### Encoder

```text
입력 문장

x₁   x₂   x₃   x₄   x₅
│    │    │    │    │
└────┴────┴────┴────┴────► RNN

             ↓

h₁   h₂   h₃   h₄   h₅

                  ↓
                 h_n
```

**전체 입력 시퀀스를 처리**

---

### Decoder

```text
          h_n
           │
           ▼
[CLS] ──► RNN ──► h₁ ──► Linear ──► ID₁
                                      │
                                      ▼
                                    RNN
                                      │
                                      ▼
                                     h₂
                                      │
                                      ▼
                                   Linear
                                      │
                                      ▼
                                     ID₂
                                      │
                                     ...
```

**한 토큰씩 처리하면서 hidden state를 다음 단계로 전달**

---

# 9. 그런데 `nn.RNN`의 생성 방식 자체가 다른 것은 아니다

이 부분도 중요합니다.

Encoder와 Decoder가 **서로 다른 종류의 RNN을 사용하는 것은 아닙니다.**

둘 다:

```python
nn.RNN(
    input_size=embedding_dim,
    hidden_size=hidden_size,
    ...
)
```

입니다.  

차이는 **RNN 객체의 사용 방법**입니다.

```text
                nn.RNN
                  │
       ┌──────────┴──────────┐
       │                     │
    Encoder                Decoder
       │                     │
전체 sequence 입력        1 token 입력
       │                     │
h₀는 기본값(0)           h₀ = Encoder h_n
       │                     │
전체 sequence 처리       한 step씩 반복
       │                     │
h₁...hₙ 생성             h₁ → h₂ → h₃...
```

---

## 10. 한 문장으로 정리하면

> **Encoder의 `nn.RNN`은 입력 문장의 모든 임베딩 시퀀스를 한 번에 받아 전체 문장을 순차적으로 처리하고, Decoder의 `nn.RNN`은 Encoder의 마지막 `h_n`을 초기 hidden state로 받아 한 토큰씩 입력하면서 생성된 hidden state를 다음 step으로 계속 전달합니다.**

따라서 코드에서 가장 중요한 차이는 사실 **`nn.RNN`을 어떻게 생성했느냐보다 `self.rnn()`을 어떻게 호출했느냐**입니다.

```python
# Encoder
hidden_states, h_n = self.rnn(input_embeds)
```

vs.

```python
# Decoder
_, h_n = self.rnn(embedded, h_n)
```

이 두 줄의 차이를 이해하면 **Seq2Seq에서 Encoder와 Decoder의 역할 차이**가 거의 완전히 이해됩니다.  
