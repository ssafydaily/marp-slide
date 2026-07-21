---
marp: true
theme: dark-plus-code
paginate: true
style: |
  
---

# Reshape


```python
# 이미지 데이터(MNIST): (samples, height, width, channel)
images = np.random.rand(100, 28, 28, 1)

# flatten: 완전연결층의 입력으로 변환하기
x_flat =images.reshape(100, -1)  # (100, 784)
```

---
# Transpose / Swapaxes
- (batch, height, widht, channels) => (batch, channels, height, width)
- **pytorch** 형식 변환

```python
image_torch = np.transpose(images, (0, 3, 1, 2))

print("TensorFlow 형식:", images.shape)        # (100, 28, 28, 1)
print("PyTorch 형식:", images_torch.shape)     # (100, 1, 28, 28)

# 행렬 전치
W = np.random.randn(784, 128)
W_T = W.T  # (128, 784)
```
---
# Squeeze / Expand_dims

### 불필요한 차원 제거
```python
prediction = np.random.rand(10, 1, 1)
squeezed = np.squeeze(prediction)           # (10,)
```
### 차원 추가
```python
# 차원 추가
vector = np.array([1, 2, 3, 4, 5])
col_vector = np.expand_dims(vector, axis=1)  # (5, 1)
row_vector = np.expand_dims(vector, axis=0)  # (1, 5)

print("원본:", vector.shape)
print("열벡터:", col_vector.shape)
print("행벡터:", row_vector.shape)
```
---
# indexing / slicing
### 미니 배치 추출
```python
X = np.random.randn(1000, 10)
y = np.random.randint(0, 2, 1000)

# 미니배치
batch_size = 32
start_idx = 0
X_batch = X[start_idx:start_idx + batch_size]
y_batch = y[start_idx:start_idx + batch_size]

print("배치 shape:", X_batch.shape)  # (32, 10)
```
---
# indexing / slicing

```python
# One-hot 인코딩에서 원래 레이블 복원
one_hot = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]])
labels = np.argmax(one_hot, axis=1)
print("복원된 레이블:", labels)  # [2, 0, 1]

# 다중 조건
X = np.random.randn(100, 5)
# 첫 번째 특성이 양수이고 두 번째 특성이 음수인 샘플
mask = (X[:, 0] > 0) & (X[:, 1] < 0)
filtered_X = X[mask]
```

---
# Broadcasting

### 기본 개념
```python
# 행렬 + 벡터
X = np.random.randn(100, 5)
mean = np.array([1, 2, 3, 4, 5])

# Broadcasting으로 각 샘플에 mean 더하기
X_shifted = X + mean  # mean이 (100, 5)로 자동 확장

# 스케일링
std = np.array([0.5, 1.0, 1.5, 2.0, 2.5])
X_normalized = X / std

print("Broadcasting 결과:", X_shifted.shape)
```
---
### Broadcasting 예제 : 정규화
```python
X = np.random.randn(100, 5)

# Feature-wise 정규화 (각 특성별로)
mean = X.mean(axis=0, keepdims=True)  # (1, 5)
std = X.std(axis=0, keepdims=True)    # (1, 5)
X_normalized = (X - mean) / std

print("평균 shape:", mean.shape)
print("표준편차 shape:", std.shape)
print("정규화 결과:", X_normalized.shape)

# Sample-wise 정규화 (각 샘플별로)
mean_sample = X.mean(axis=1, keepdims=True)  # (100, 1)
std_sample = X.std(axis=1, keepdims=True)    # (100, 1)
X_normalized_sample = (X - mean_sample) / std_sample
```

---
# 축 연산
### Axis 이해하기
```python
X = np.random.randn(100, 5)

# axis=0: 샘플 축 (세로 방향)
# axis=1: 특성 축 (가로 방향)

feature_means = X.mean(axis=0)    # 각 특성의 평균 (5,)
sample_means = X.mean(axis=1)     # 각 샘플의 평균 (100,)

# keepdims=True는 차원 유지 (Broadcasting용)
feature_means_kept = X.mean(axis=0, keepdims=True)  # (1, 5)
sample_means_kept = X.mean(axis=1, keepdims=True)   # (100, 1)

print("특성별 평균:", feature_means.shape)
print("샘플별 평균:", sample_means.shape)
```
---
# 축 연산
### 다양한 축 연산
```python
X = np.random.randn(100, 5)

# 통계량
print("최솟값 (특성별):", X.min(axis=0))
print("최댓값 (특성별):", X.max(axis=0))
print("표준편차 (특성별):", X.std(axis=0))
print("분산 (특성별):", X.var(axis=0))

# 누적 합
cumsum = X.cumsum(axis=0)  # (100, 5)

# argmax, argmin (인덱스 반환)
max_indices = X.argmax(axis=1)  # 각 샘플의 최대값 특성 인덱스
```

---
# 선형 대수 연산
## 행렬 곱셈
```python
# Forward pass 예제
X = np.random.randn(32, 784)    # 배치 크기 32, 입력 784
W1 = np.random.randn(784, 128)  # 첫 번째 레이어
b1 = np.zeros(128)

# 선형 변환
Z1 = X @ W1 + b1  # (32, 128)
# 또는
Z1 = np.dot(X, W1) + b1

print("Z1 shape:", Z1.shape)

# 다중 레이어
W2 = np.random.randn(128, 64)
b2 = np.zeros(64)
Z2 = Z1 @ W2 + b2  # (32, 64)
```
---
## vector 내적과 외적

---
## 내적과 외적
```python
# 코사인 유사도 계산
v1 = np.random.randn(100)
v2 = np.random.randn(100)

# 내적
dot_product = np.dot(v1, v2)

# 코사인 유사도
cosine_sim = dot_product / (np.linalg.norm(v1) * np.linalg.norm(v2))

print("코사인 유사도:", cosine_sim)

# 외적 (Outer product) - 가중치 업데이트에 사용
gradient = np.random.randn(128)
activation = np.random.randn(784)
weight_gradient = np.outer(activation, gradient)  # (784, 128)
```
---
