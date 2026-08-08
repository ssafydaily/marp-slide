# Step 2. 임베딩 벡터 변환 및 시각화 — 설명서

## 1. 이 Step에서 하는 일
Step 1에서 만든 토큰(정수 ID)을 **의미를 담은 실수 벡터(dense vector)** 로 변환하는 워드 임베딩을 다루고,
(1) 사전학습된 BERT 임베딩과 (2) 학습되지 않은 랜덤 임베딩을 3D로 시각화하여 비교합니다.

전체 흐름:
```
Dense vector vs Sparse vector 개념 정리
   ↓
BERT의 사전학습된 word_embeddings 불러오기 (30522 x 768)
   ↓
12개 단어를 token id로 변환 → 임베딩 벡터 추출 (12 x 768)
   ↓
PCA로 3차원 축소 후 구면(sphere) 위에 시각화 → 그룹별로 뭉치는지 확인
   ↓
TODO 2: nn.Embedding으로 "학습되지 않은" 임베딩 생성 (12 x 768)
   ↓
같은 방식으로 시각화 → 사전학습 임베딩과 비교
```

---

## 2. Dense Vector vs Sparse Vector

| 구분 | 설명 |
|---|---|
| Sparse vector | 대부분 0이고 일부 위치만 값이 있음 (예: one-hot `[0,0,1,0,...]`) |
| Dense vector | 모든 차원에 실수값이 채워짐 (예: `[0.23,-1.5,0.88,...]`) |

워드 임베딩은 단어를 **저차원의 dense vector**로 표현하여, 적은 차원에 더 많은 의미 정보를 압축해 담는 방식입니다.

---

## 3. 사전학습된 BERT 임베딩 확인 (셀 30~33)

```python
model = BertModel.from_pretrained("bert-base-uncased")
word_embeddings = model.embeddings.word_embeddings
print(word_embeddings.weight.shape)   # torch.Size([30522, 768])
```

- **행(30522)** = tokenizer의 vocab 크기 → 표현 가능한 토큰의 개수
- **열(768)** = 임베딩 차원(embedding_dim) → 각 단어를 표현하는 dense vector의 크기 (256×3=768, 보통 2의 제곱수 계열 사용)

즉 `word_embeddings`는 **(vocab_size × embedding_dim)** 크기의 **룩업 테이블(조회표)** 입니다.

```python
words_to_ids = {word: tokenizer.convert_tokens_to_ids(word) for word in words}
input_tensor = torch.tensor([...])          # shape: (12,)
embeddings_vector = word_embeddings(input_tensor)   # shape: (12, 768)
```
- 입력 토큰 id가 인덱스가 되어, `word_embeddings` 테이블에서 해당 행(768차원 벡터)을 그대로 가져옵니다.
- 예: id `10527`을 가진 `infant`는 테이블의 10527번째 행 벡터를 반환받음.

**embedding_dim의 트레이드오프**

| | 차원 클 때 ↑ | 차원 작을 때 ↓ |
|---|---|---|
| 표현력 | 정교한 의미 표현 가능 | 표현력 부족 가능 |
| 계산 속도/메모리 | 느림, 메모리 많이 사용 | 빠름, 메모리 효율적 |
| 과적합 | 가능성 증가 | 가능성 감소 |

---

## 4. 임베딩 시각화 (셀 36~39)

`visualize_embeddings()` 함수는:
1. 768차원 임베딩을 `PCA(n_components=3)`로 3차원으로 축소
2. 벡터를 정규화(단위벡터화)하여 단위 구(sphere) 표면 위에 투영
3. `plotly`의 `Scatter3d`로 점 + 원점→점 선을 그려 방향성을 시각적으로 강조

3개 그룹(`age`, `adult`, `royalty`)에 색을 다르게 입혀 시각화한 결과, **같은 그룹의 단어일수록 벡터의 방향이 비슷하게(같은 위치 근처에) 모입니다.**
- 임베딩 공간에서 단어 간 유사도는 **코사인 유사도(벡터 간 각도)** 로 측정하는 것이 일반적이며, 절대적인 유클리드 거리보다 **방향**이 의미상 더 중요합니다.

---

## 5. TODO 2: 학습되지 않은 임베딩 생성 (셀 41~44)

```python
embedding_layer = nn.Embedding(len(words), 768)   # (12, 768) 크기의 랜덤 초기화 테이블
```
- `nn.Embedding(num_embeddings, embedding_dim)` : `num_embeddings × embedding_dim` 크기의 학습 가능한 파라미터 행렬을 무작위로 초기화합니다.
- 여기서는 실제 vocab 대신, 실습용 12개 단어만을 대상으로 vocab을 구성(`words_to_ids = {word: i for i, word in enumerate(words)}`).
- 동일한 방식으로 12개 단어를 id로 변환 → 임베딩 조회 → `(12, 768)` 벡터 획득.

**결과 비교**
- 사전학습(BERT) 임베딩: 같은 의미 그룹끼리 뚜렷하게 군집을 이룸 (학습을 통해 문맥 정보를 담았기 때문)
- 랜덤 초기화 임베딩: 그룹 구분이 없고 무작위로 흩어짐 (아직 아무 의미도 학습하지 않았기 때문)

---

## 6. 핵심 요약
- 워드 임베딩은 **(vocab_size × embedding_dim)** 크기의 학습 가능한 조회 테이블이며, 토큰 id를 인덱스 삼아 해당 행을 꺼내오는 연산이다.
- 임베딩 벡터의 품질(의미 반영 정도)은 **학습 여부**에 달려 있다. 학습된 임베딩만이 유사한 단어를 가까운 방향에 배치한다.
- `embedding_dim`은 표현력과 계산 비용 사이의 하이퍼파라미터이며, 절대적 정답은 없다.
