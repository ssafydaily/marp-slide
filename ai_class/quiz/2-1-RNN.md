# Kahoot 퀴즈: 자연어 처리 기본 (토큰화 · 워드 임베딩 · RNN · LSTM · Transformer)

- 형식: 4지 선다형 (Kahoot Quiz)
- 문항 수: 총 10문제 (단답형 지문 6문제 + 문장형 지문 4문제)
- 출제 범위: 「2-1_자연어_처리_기본」 강의자료 기반 (토큰화, 원-핫 인코딩, 워드 임베딩, RNN, LSTM, Transformer)
- 각 문항은 정답(✅ 표시)과 간단한 해설을 포함합니다. Kahoot 문항 입력 시 해설은 제외하고 질문/보기 4개/정답만 입력하면 됩니다.

---

## [단답형 지문] 문제 1~6

### 1. 토큰화(Tokenization)
**Q1. 자연어 문장을 단어, 형태소 등 처리 가능한 최소 단위로 나누는 과정을 무엇이라 하는가?**

- A. 토큰화(Tokenization) ✅
- B. 임베딩(Embedding)
- C. 정규화(Normalization)
- D. 인코딩(Encoding)

> 해설: 토큰화는 문장을 단어·서브워드·형태소 등 의미 있는 최소 단위(토큰)로 분리하는 자연어 처리의 가장 첫 단계이다.

---

### 2. 원-핫 인코딩
**Q2. 단어 집합(사전)의 크기만큼 차원을 가지며, 해당 단어의 위치만 1이고 나머지는 모두 0으로 표현하는 방식은?**

- A. 워드 임베딩
- B. 원-핫 인코딩 ✅
- C. Skip-gram
- D. Self-Attention

> 해설: 원-핫 인코딩은 단어를 어휘 수만큼의 차원을 가진 희소 벡터로 표현하며, 단어 간 의미적 관계는 반영하지 못한다.

---

### 3. 워드 임베딩 대표 모델
**Q3. 단어를 저차원의 밀집 벡터로 학습시켜, 단어 간 의미적 유사성을 벡터 공간에 반영하는 대표적인 모델은?**

- A. Word2Vec ✅
- B. One-Hot Encoding
- C. LSTM
- D. Transformer

> 해설: Word2Vec은 Skip-gram, CBOW 방식을 통해 단어를 저차원 밀집 벡터(임베딩)로 학습하는 대표적인 워드 임베딩 기법이다.

---

### 4. RNN 핵심 개념
**Q4. RNN이 이전 시점의 정보를 현재 시점의 연산에 전달하기 위해 사용하는 값은?**

- A. Attention Score
- B. Hidden State ✅
- C. Gradient
- D. Embedding Vector

> 해설: RNN은 순환 구조를 통해 이전 시점의 hidden state를 현재 시점 계산에 반영하여 순차적 데이터를 처리한다.

---

### 5. LSTM 게이트
**Q5. LSTM에서 이전 cell state의 정보 중 불필요한 부분을 얼마나 잊을지 결정하는 게이트는?**

- A. Input Gate
- B. Output Gate
- C. Forget Gate ✅
- D. Update Gate

> 해설: Forget Gate는 이전 cell state 정보 중 유지할 부분과 버릴 부분을 시그모이드 함수로 결정한다.

---

### 6. Transformer 핵심 개념
**Q6. Transformer의 Self-Attention에서 단어 간 연관성(유사도)을 계산할 때 사용하는 세 가지 벡터는?**

- A. Query, Key, Value ✅
- B. Encoder, Decoder, Attention
- C. Hidden, Cell, Gate
- D. Input, Output, Forget

> 해설: Self-Attention은 각 단어의 Query와 다른 모든 단어의 Key를 비교해 가중치를 구하고, 이를 Value에 곱해 문맥 정보를 반영한다.

---

## [문장형 지문] 문제 7~10

### 7. Skip-gram
**Q7. Skip-gram의 예측 방식으로 가장 적절한 것은?**

- A. 중심 단어로 주변 단어 예측 ✅
- B. 주변 단어로 중심 단어 예측
- C. 문장 전체를 한 번에 예측
- D. 이전 단어로 다음 단어만 예측

> 해설: Skip-gram은 중심 단어를 입력으로 주변 단어들을 예측한다. 반대로 CBOW는 주변 단어로 중심 단어를 예측한다.

---

### 8. LSTM vs RNN
**Q8. LSTM이 RNN과 다른 가장 큰 특징은?**

- A. cell state와 게이트 구조 추가 ✅
- B. 순환 구조를 완전히 제거함
- C. 병렬 처리만 가능함
- D. 이미지 데이터만 처리 가능

> 해설: LSTM은 cell state와 forget/input/output 게이트를 추가해 RNN의 기울기 소실 문제를 완화한 구조이다.

---

### 9. Transformer 구조
**Q9. Transformer의 특징으로 가장 적절한 것은?**

- A. 단어를 순차적으로 하나씩 입력받음
- B. Self-Attention으로 병렬 계산함 ✅
- C. CNN 필터만으로 문맥 파악
- D. Positional Encoding이 불필요함

> 해설: Transformer는 순환 구조 없이 Self-Attention으로 단어 관계를 병렬 계산하며, 순서 정보 보완을 위해 Positional Encoding을 사용한다.

---

### 10. 워드 임베딩
**Q10. 워드 임베딩의 특징으로 가장 적절한 것은?**

- A. 고차원 희소 벡터로 표현됨
- B. 의미적 유사성을 벡터에 반영 ✅
- C. 차원이 항상 고정되어 있음
- D. 사전 크기와 차원이 반드시 동일

> 해설: 워드 임베딩은 학습을 통해 단어를 저차원 밀집 벡터로 표현하며, 벡터 공간상에서 의미적 유사성을 반영한다.

---

## 정답 요약표

| 번호 | 주제 | 정답 |
|---|---|---|
| 1 | 토큰화 | A |
| 2 | 원-핫 인코딩 | B |
| 3 | 워드 임베딩(Word2Vec) | A |
| 4 | RNN | B |
| 5 | LSTM 게이트 | C |
| 6 | Transformer (Q,K,V) | A |
| 7 | Skip-gram vs CBOW | B |
| 8 | RNN vs LSTM | A |
| 9 | Transformer 구조 | B |
| 10 | 워드 임베딩 vs 원-핫 인코딩 | B |

## Kahoot 입력 팁
- Kahoot Classic 문제 만들기 화면에서 "Quiz" 유형 선택 후 위 문항을 순서대로 입력하면 됩니다.
- 문항(Question)은 120자, 보기(Answer)는 75자 이내 제한이 있으므로 위 문항은 모두 해당 기준에 맞게 작성되었습니다.
- 제한시간은 개념 이해도를 묻는 문제이므로 20~30초를 권장합니다.
