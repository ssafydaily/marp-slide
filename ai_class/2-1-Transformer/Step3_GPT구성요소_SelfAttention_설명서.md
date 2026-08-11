# Step 3. GPT 모델 구성 요소 구현 — 설명서

## 1. 이 Step에서 하는 일

GPT(Generative Pre-trained Transformer)의 4가지 핵심 구성요소를
**Attention → LayerNorm → MLP → DecoderBlock → GPT2 전체** 순서로 직접 구현합니다.

전체 흐름:

```
Config 정의 (hidden_size, num_heads 등 하이퍼파라미터)
   ↓
TODO 3: MultiHeadSelfAttention 구현  ← 이 문서의 핵심(4절)
   ↓
LayerNorm 구현
   ↓
MLP(Feed-Forward) 구현
   ↓
TODO 4: DecoderBlock 조립 (LN→Attn→Residual→LN→MLP→Residual)
   ↓
TODO 5: GPT2 전체 조립 (임베딩 + N개 DecoderBlock + 최종 LN + LM Head)
```

### 사용된 Config (셀 48)

```python
hidden_size     = 512    # H, 모델의 은닉 차원 (d_model)
ff_hidden_size  = 4*512  # MLP 내부 확장 차원
num_hidden_layers = 2    # 쌓을 DecoderBlock 개수
dropout_rate    = 0.1
vocab_size      = 10000
max_seq_len     = 128
num_heads       = 1      # attention head 개수 n_h
```

---

## 2. GPT 전체에서 사용하는 기호 정리

| 기호    | 의미                                 |
| ------- | ------------------------------------ |
| `B`   | 배치 크기 (batch size)               |
| `T`   | 시퀀스 길이 (문장의 토큰 개수)       |
| `H`   | hidden_size (모델 은닉 차원, 512)    |
| `V`   | vocab_size (어휘 사전 크기, 10000)   |
| `n_h` | num_heads (attention head 개수)      |
| `d`   | head_dim = H / n_h (head 1개당 차원) |

---

## 3. Self-Attention을 배우기 전 전체 그림

GPT 디코더 블록의 순서: **LayerNorm → Self-Attention → Residual → LayerNorm → MLP → Residual**

Self-Attention은 **"현재 토큰이 과거의 어떤 토큰 정보에 얼마나 집중(attend)할지"** 를 계산하고,
그 가중치로 Value 벡터들을 섞어 새로운 표현(context vector)을 만드는 연산입니다.

---

## 4. Self-Attention 상세 분석 (핵심)

### 4.0 입출력 크기 요약

| 텐서             | 크기                            | 의미                                                          |
| ---------------- | ------------------------------- | ------------------------------------------------------------- |
| 입력`x`        | `(B, T, H)` = `(B, T, 512)` | 각 토큰의 hidden state                                        |
| 출력`proj_out` | `(B, T, H)` = `(B, T, 512)` | attention을 거친 후 갱신된 표현 (입력과**동일한 크기**) |

Self-Attention은 **입력과 출력의 크기가 동일**하다는 것이 핵심 특징입니다 — 그래야 Residual Connection(`x + attn(x)`)으로 더할 수 있기 때문입니다.

---

### 4.1 단계 1 — Query / Key / Value 투영

```python
self.c_attn = nn.Linear(H, 3*H, bias=False)   # 가중치 W_qkv: (H, 3H)
qkv = self.c_attn(x)                          # (B, T, H) → (B, T, 3H)
q, k, v = qkv.split(H, dim=-1)                # 각각 (B, T, H)
```

- 수식: $[Q', K', V'] = X W_{qkv}$, $X \in \mathbb{R}^{B\times T\times H}$, $W_{qkv}\in\mathbb{R}^{H\times 3H}$
- **의미**: 입력 `x`를 3개의 서로 다른 선형변환($W_Q, W_K, W_V$가 합쳐진 형태)에 동시에 통과시켜, "질문(Query)", "특징표(Key)", "실제 내용(Value)" 3가지 관점의 벡터를 만듭니다. 하나의 큰 선형층으로 한 번에 처리하는 것은 계산 효율을 위한 구현상의 트릭입니다.

**Multi-head로 reshape**

```python
q = q.view(B, T, n_h, d).transpose(1, 2)   # (B, T, H) → (B, T, n_h, d) → (B, n_h, T, d)
k, v 도 동일하게 처리
```

- `(B, T, H)` → `(B, n_h, T, d)` (단, `n_h × d = H`)
- **의미**: 하나의 큰 표현(H차원)을 `n_h`개의 더 작은 부분공간(d차원)으로 쪼개, 각 head가 서로 다른 "관점"에서 독립적으로 attention을 계산하게 합니다. (이 노트북에서는 `num_heads=1`이라 `d = H = 512`)

| 텐서                       | 크기                    |
| -------------------------- | ----------------------- |
| `qkv`                    | `(B, T, 3H)`          |
| `q, k, v` (분리 직후)    | `(B, T, H)` 각각      |
| `q, k, v` (head 분리 후) | `(B, n_h, T, d)` 각각 |

---

### 4.2 단계 2 — Scaled Dot-Product Attention Score

```python
attn_scores = (q @ k.transpose(-2, -1)) / math.sqrt(d)
```

- `q`: `(B, n_h, T, d)`, `k.transpose(-2,-1)`: `(B, n_h, d, T)`
- 행렬곱 결과: `(B, n_h, T, d) @ (B, n_h, d, T) → (B, n_h, T, T)`
- 수식: $S_h = \dfrac{Q_h K_h^\top}{\sqrt{d}} \in \mathbb{R}^{T\times T}$ (head별)

**의미**

- `attn_scores[b, h, i, j]` 는 "**i번째 토큰의 Query**가 **j번째 토큰의 Key**와 얼마나 유사한가(내적)"를 나타냅니다.
- Query = "지금 내가 필요한 정보가 무엇인가", Key = "내가 가진 정보의 특징표" 라고 직관적으로 이해할 수 있습니다. 내적이 클수록 두 토큰이 서로 관련이 크다는 뜻입니다.
- $\sqrt{d}$로 나누는 이유: 차원 `d`가 커질수록 내적 값의 분산이 커져 softmax가 한쪽으로 극단적으로 쏠리는(gradient가 매우 작아지는) 문제를 방지하기 위한 스케일링입니다.

| 텐서            | 크기                                                                                     |
| --------------- | ---------------------------------------------------------------------------------------- |
| `attn_scores` | `(B, n_h, T, T)` — **T×T 정사각 행렬**, "토큰 i가 토큰 j를 얼마나 보는가"의 표 |

---

### 4.3 단계 3 — Causal Mask (미래 차단)

```python
causal_mask = torch.tril(torch.ones(T, T)).view(1, 1, T, T)   # (T,T) → (1,1,T,T)
attn_scores = attn_scores.masked_fill(causal_mask == 0, float('-inf'))
```

- `tril`(하삼각행렬)로 만든 `(T, T)` 마스크를 `(1, 1, T, T)`로 reshape 후 `(B, n_h, T, T)`의 `attn_scores`에 브로드캐스트하여 적용.
- 수식: $M_{ij} = 1 \text{ if } i \ge j \text{ else } 0$
- **의미**: GPT는 autoregressive(자기회귀) 모델이므로, `i`번째 위치는 자기 자신(`j=i`)과 그 이전 토큰(`j<i`)만 볼 수 있고, 미래 토큰(`j>i`)은 볼 수 없어야 합니다. 마스크가 0인 위치(미래)에 `-inf`를 채워 다음 softmax에서 확률이 정확히 0이 되도록 만듭니다.

| 텐서            | 크기                                                           | 비고                   |
| --------------- | -------------------------------------------------------------- | ---------------------- |
| `causal_mask` | `(1, 1, T, T)` → 브로드캐스트되어 `(B, n_h, T, T)`에 적용 | 값이 0/1인 하삼각 행렬 |

---

### 4.4 단계 4 — Softmax & Dropout

```python
attn_probs = F.softmax(attn_scores, dim=-1)   # (B, n_h, T, T)
attn_probs = self.attn_dropout(attn_probs)
```

- `dim=-1`(마지막 축, 즉 `j` 방향)을 기준으로 softmax를 적용 → **각 행(i번째 토큰)의 합이 1이 되는 확률 분포**로 변환.
- 수식: $A_h = \text{softmax}(S_h^{masked})$
- **의미**: `attn_probs[b,h,i,:]`는 "i번째 토큰이 과거(및 자기 자신) 토큰들 각각에 얼마나 집중(가중치)할지"를 나타내는 확률 분포입니다. `-inf`였던 미래 위치는 softmax 후 정확히 0이 됩니다. Dropout은 학습 시 일부 attention 연결을 무작위로 끊어 과적합을 방지합니다.

| 텐서           | 크기                                                                  |
| -------------- | --------------------------------------------------------------------- |
| `attn_probs` | `(B, n_h, T, T)` — 크기는 그대로, 값이 확률(0~1, 행별 합=1)로 바뀜 |

---

### 4.5 단계 5 — Value 가중합 (Context 생성)

```python
attn_out = attn_probs @ v   # (B, n_h, T, T) @ (B, n_h, T, d) → (B, n_h, T, d)
```

- 수식: $Z_h = A_h V_h$
- **의미**: 각 토큰(행)이 가진 확률분포(attn_probs)로 Value 벡터들을 가중평균 합니다. 즉 "현재 토큰이 필요로 하는 정보를 과거 토큰들의 Value에서 골라서 섞어온 결과"가 바로 `attn_out`입니다.

| 텐서                  | 크기               |
| --------------------- | ------------------ |
| `attn_out` (head별) | `(B, n_h, T, d)` |

---

### 4.6 단계 6 — 여러 Head 결합 (Concat)

```python
attn_out = attn_out.transpose(1, 2).contiguous().view(B, T, H)
```

- `(B, n_h, T, d)` → transpose → `(B, T, n_h, d)` → view → `(B, T, H)` (`n_h × d = H`이므로 크기 복원)
- 수식: $Z = \text{Concat}(Z_1, \dots, Z_{n_h})$
- **의미**: 서로 다른 관점(head)에서 얻은 context 벡터들을 이어붙여, 다시 원래의 hidden 차원(H) 표현으로 되돌립니다.

| 텐서                   | 크기          |
| ---------------------- | ------------- |
| `attn_out` (결합 후) | `(B, T, H)` |

---

### 4.7 단계 7 — 최종 Projection & Dropout

```python
proj_out = self.c_proj(attn_out)     # (B, T, H) @ (H, H) → (B, T, H)
proj_out = self.proj_dropout(proj_out)
```

- 수식: $Y = ZW_O,\quad \tilde Y = \text{Dropout}(Y)$, $W_O \in \mathbb{R}^{H\times H}$
- **의미**: 여러 head의 정보가 단순히 이어붙여진 상태(`Z`)를 학습 가능한 선형변환 `W_O`로 다시 한 번 "잘 섞어" 최종 출력 표현을 만듭니다.

| 텐서                     | 크기                                          |
| ------------------------ | --------------------------------------------- |
| `proj_out` (최종 출력) | `(B, T, H)` — **입력과 동일한 크기** |

---

### 4.8 Self-Attention 전체 크기 변화 흐름 요약

```
x                (B, T, H)
  → c_attn       (B, T, 3H)                     [W_qkv: H×3H]
  → split        q,k,v 각 (B, T, H)
  → head reshape q,k,v 각 (B, n_h, T, d)          (d = H/n_h)
  → Q·K^T /√d    attn_scores (B, n_h, T, T)
  → causal mask  attn_scores (B, n_h, T, T)   (미래 위치 -inf)
  → softmax      attn_probs  (B, n_h, T, T)   (행별 합=1인 확률)
  → ·V           attn_out    (B, n_h, T, d)
  → concat heads attn_out    (B, T, H)
  → c_proj       proj_out    (B, T, H)         [W_O: H×H]
```

**직관 요약**: Q·Kᵀ는 "토큰끼리 서로 얼마나 관련있는지"의 T×T 유사도 표를 만들고, causal mask+softmax는 그것을 "과거만 보는 확률분포"로 바꾸며, 그 확률로 V를 가중합해 "각 토큰이 필요한 정보를 과거에서 끌어온 새 표현"을 얻습니다. 마지막 projection은 여러 head의 결과를 다시 하나로 통합합니다.

---

## 5. Layer Normalization (셀 60)

```python
mean = x.mean(dim=-1, keepdim=True)   # (B, T, 1)
std  = x.std(dim=-1, keepdim=True)    # (B, T, 1)
out  = (x - mean) / (std + eps) * gamma + beta   # (B, T, H)
```

- 입력/출력 크기: `(B, T, H)` → `(B, T, H)` (동일)
- **의미**: 배치가 아니라 **마지막 차원(H, 한 토큰의 hidden 벡터)** 단위로 평균 0, 분산 1로 정규화한 뒤, 학습 가능한 `gamma(H,)`, `beta(H,)`로 다시 스케일·이동시켜 표현력을 보존합니다. 시퀀스 길이(T)에 무관하게 동작하는 것이 BatchNorm과의 차이점입니다.
- `n.Parameter`로 감싸는 이유는 **"이 텐서는 학습(gradient descent)을 통해 값이 업데이트되어야 하는 모델의 파라미터다"라고 PyTorch에게 알려주기 위함**

---

## 6. MLP (Feed-Forward Network) (셀 62)

```python
x = c_fc(x)     # (B, T, H) → (B, T, 4H)   확장
x = GELU(x)     # (B, T, 4H)               비선형 활성화
x = c_proj(x)   # (B, T, 4H) → (B, T, H)   축소
x = dropout(x)
```

- 입력/출력 크기: `(B, T, H)` → `(B, T, H)`
- **의미**: 각 토큰(위치)마다 **독립적으로** 적용되는 2-layer 신경망입니다. H→4H로 확장했다가 다시 H로 축소하며 GELU 비선형성을 추가해, Attention이 만든 표현에 더 풍부한 표현력을 부여합니다. (Attention이 "토큰 간" 정보교환을 담당한다면, MLP는 "토큰 내부" 표현을 강화)

---

## 7. Decoder Block 조립 (TODO 4, 셀 65)

```python
x = self.ln_1(x)
x = x + self.attn(x)      # LN → Self-Attention → Residual

x = self.ln_2(x)
x = x + self.mlp(x)       # LN → MLP → Residual
```

- 수식:
  - $\text{AttnOut} = \text{MHA}(\text{LN}_1(X))$, $X' = X + \text{AttnOut}$
  - $\text{MLPOut} = \text{MLP}(\text{LN}_2(X'))$, $Y = X' + \text{MLPOut}$
- 입력/출력 크기: `(B, T, H)` → `(B, T, H)` (블록을 여러 번 쌓을 수 있는 이유)
- **Pre-Norm 구조**(정규화를 서브레이어 앞에 배치)는 깊게 쌓을 때 gradient 흐름을 안정시키는 효과가 있습니다.
- **Residual Connection**(`x + ...`)은 정보 손실 없이 원본 신호를 다음 층까지 전달해 gradient vanishing을 완화합니다.

---

## 8. GPT-2 전체 조립 (TODO 5, 셀 68)

```python
position_ids = torch.arange(T).unsqueeze(0)              # (1, T)
x = token_embed(input_ids) + position_embed(position_ids) # (B,T,H) + (1,T,H) → (B,T,H)
x = embed_dropout(x)

for layer in hidden_layers:      # DecoderBlock × num_hidden_layers
    x = layer(x)                 # (B,T,H) → (B,T,H)

x = ln_f(x)                      # (B,T,H)
logits = language_head(x)        # (B,T,H) @ (H,V) → (B,T,V)
```

| 단계                                           | 텐서 크기     | 의미                                                                       |
| ---------------------------------------------- | ------------- | -------------------------------------------------------------------------- |
| `input_ids`                                  | `(B, T)`    | 토큰 정수 ID 시퀀스                                                        |
| 토큰 임베딩 + 위치 임베딩                      | `(B, T, H)` | 단어 의미 + 순서 정보 결합                                                 |
| N개 DecoderBlock 통과 후                       | `(B, T, H)` | 문맥이 반영된 표현                                                         |
| 최종 LayerNorm 후                              | `(B, T, H)` | 분포 안정화                                                                |
| 언어 헤드(`Linear(H, V)`) 통과 후 `logits` | `(B, T, V)` | 각 위치에서 다음 토큰이 vocab의 어떤 단어일지에 대한 점수(softmax 이전 값) |

- **위치 임베딩(Position Embedding)** 이 필요한 이유: Self-Attention 자체는 순서 정보를 모릅니다(토큰의 위치가 바뀌어도 Q·Kᵀ 계산 방식은 동일). 따라서 위치 정보를 별도의 임베딩으로 더해줘야 "순서"를 모델이 인식할 수 있습니다.
- 최종 `logits`는 `(B, T, V)` 크기이며, 여기에 softmax를 적용하면 각 위치에서 다음에 올 토큰의 확률 분포가 됩니다 — 이것이 GPT가 텍스트를 생성하는 원리(autoregressive next-token prediction)입니다.

---

## 9. 핵심 요약

- **Self-Attention**은 `Q·Kᵀ`로 T×T 크기의 "토큰 간 관련도" 행렬을 만들고, causal mask+softmax로 "과거만 보는 확률분포"로 변환한 뒤, 그 확률로 V를 가중합하여 문맥이 반영된 새 표현을 만드는 연산이며, 입출력 크기는 항상 `(B,T,H)`로 동일하다.
- Multi-head는 H차원을 `n_h`개의 `d=H/n_h`차원 부분공간으로 나누어 병렬로 다른 관점의 attention을 계산한 뒤 다시 합치는 구조이다.
- LayerNorm, MLP, DecoderBlock 모두 입출력 크기가 `(B,T,H)`로 보존되기 때문에 여러 블록을 자유롭게 쌓을 수 있고, 마지막에만 `Linear(H,V)`로 vocab 차원으로 확장되어 다음 토큰 예측 로짓(B,T,V)을 만든다.
