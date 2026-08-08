## `LuongAttention.forward` 내부 계산 상세

```python
class LuongAttention(nn.Module):
    def __init__(self, hidden_size: int):
        super().__init__()
        self.W_a = nn.Linear(hidden_size, hidden_size, bias=False)

    def forward(self, h_t, encoder_outputs):
        Wa_ht = self.W_a(h_t)                        # 1
        attention_score = encoder_outputs @ Wa_ht.T   # 2
        attention_weights = F.softmax(attention_score, dim=-1)  # 3
        context_vector = attention_weights.T @ encoder_outputs  # 4
        return context_vector, attention_weights
```

`hidden_size=1024`, 인코더 시퀀스 길이를 `L`이라 하고 단계별로 따라가 보겠습니다. (`h_t`는 디코더 LSTM의 현재 `h_n`, shape `(1, 1024)`)

### 1단계 — `Wa_ht = W_a(h_t)`
```
h_t:    (1, 1024)
W_a:    Linear(1024 → 1024, bias=False)   # 가중치 행렬 (1024, 1024)
Wa_ht:  (1, 1024)
```
`h_t`를 학습 가능한 선형변환에 통과시켜 "쿼리(query)" 역할을 하는 새로운 벡터 `Wa_ht`를 만듭니다. shape은 바뀌지 않지만 내용이 인코더 벡터와 내적하기 좋은 형태로 재투영됩니다.

### 2단계 — `attention_score = encoder_outputs @ Wa_ht.T`
```
encoder_outputs: (L, 1024)
Wa_ht.T:         (1024, 1)
attention_score: (L, 1)   ←  각 인코더 timestep과 h_t 사이의 내적 유사도
```
행렬곱 `(L, 1024) @ (1024, 1) → (L, 1)`은 사실상 `encoder_outputs`의 각 행(=인코더의 각 timestep 은닉 벡터)과 `Wa_ht`를 하나씩 내적한 것과 같습니다. 즉 `attention_score[i]`는 "디코더 현재 상태가 인코더의 i번째 토큰과 얼마나 유사한가"를 나타내는 스칼라입니다.

### 3단계 — `attention_weights = F.softmax(attention_score, dim=-1)`
개념적으로는 이 점수들을 확률분포로 바꿔서, `L`개의 인코더 timestep 중 어디에 더 집중할지를 나타내야 합니다. 다만 실제 코드를 그대로 실행해 확인해보면:

```
attention_score shape: (5, 1)
softmax(dim=-1) 결과:  [1., 1., 1., 1., 1.]   ← 전부 1.0
```

`attention_score`의 shape이 `(L, 1)`이기 때문에 `dim=-1`(마지막 축, 크기 1)에 softmax를 걸면 원소가 자기 자신 하나뿐이라 **항상 1.0**이 나옵니다. `L`(시퀀스 길이) 방향으로 정규화하려면 `dim=0`이어야 의도한 대로 동작합니다(직접 검증 결과, `dim=0`을 쓰면 `[0.12, 0.10, 0.35, 0.12, 0.31]`처럼 합이 1인 정상적인 분포가 나옵니다). 정리해서 참고하시라고 짚어드립니다 — 학습 목적상 구조를 이해하는 데는 지장이 없지만, 실제로 의미 있는 attention weight를 얻으려면 이 부분을 주의 깊게 볼 필요가 있습니다.

### 4단계 — `context_vector = attention_weights.T @ encoder_outputs`
```
attention_weights.T: (1, L)
encoder_outputs:      (L, 1024)
context_vector:       (1, 1024)
```
`attention_weights`를 가중치 삼아 `encoder_outputs`의 각 행(인코더 timestep 벡터)을 가중합합니다. `(1, L) @ (L, 1024) → (1, 1024)`이므로, 결과적으로 인코더 전체 시퀀스의 정보가 하나의 `(1, 1024)` 벡터로 압축됩니다 — 이것이 `context_vector`입니다.

### 전체 shape 흐름 요약

| 텐서 | shape | 의미 |
|---|---|---|
| `h_t` | `(1, 1024)` | 디코더 현재 은닉 상태 (쿼리) |
| `Wa_ht` | `(1, 1024)` | 재투영된 쿼리 |
| `encoder_outputs` | `(L, 1024)` | 인코더 전체 timestep 은닉 상태 (키/값 역할) |
| `attention_score` | `(L, 1)` | 각 timestep과의 유사도 점수 |
| `attention_weights` | `(L, 1)` | 정규화된 가중치(softmax 결과) |
| `context_vector` | `(1, 1024)` | 가중합된 인코더 정보 요약 벡터 |

이렇게 만들어진 `context_vector`는 이후 `AttentionDecoder.forward`에서 `h_n`과 concat되어 `W_c` → `tanh`를 거쳐 최종 출력 예측에 반영됩니다.