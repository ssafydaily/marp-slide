# 머신러닝/딥러닝을 위한 NumPy 핵심 가이드

## 1. 배열 생성 및 초기화

### 데이터셋 형태의 배열 생성
```python
import numpy as np

# 샘플 데이터셋 (100개 샘플, 5개 특성)
X = np.random.randn(100, 5)  # 표준정규분포
y = np.random.randint(0, 2, size=100)  # 이진 레이블

# 균등분포
X_uniform = np.random.uniform(low=0, high=1, size=(100, 5))

# 특정 범위의 정수
indices = np.arange(100)  # 0부터 99까지

# 균등 간격
learning_rates = np.linspace(0.001, 0.1, 10)  # 0.001~0.1 사이 10개

print("X shape:", X.shape)  # (100, 5)
print("y shape:", y.shape)  # (100,)
```

### 가중치 초기화 전략
```python
# Xavier/Glorot 초기화
input_dim, output_dim = 784, 128
limit = np.sqrt(6 / (input_dim + output_dim))
W = np.random.uniform(-limit, limit, size=(input_dim, output_dim))

# He 초기화 (ReLU용)
W_he = np.random.randn(input_dim, output_dim) * np.sqrt(2 / input_dim)

# 편향은 0으로 초기화
b = np.zeros(output_dim)

print("가중치 W shape:", W.shape)
print("편향 b shape:", b.shape)
```

## 2. 배열 형태 변환 (Reshaping)

### Reshape - 머신러닝에서 가장 중요!
```python
# 이미지 데이터: (samples, height, width, channels)
images = np.random.rand(100, 28, 28, 1)  # MNIST 스타일

# Flatten: 완전연결층 입력으로 변환
X_flat = images.reshape(100, -1)  # (100, 784)
# -1은 자동으로 계산됨

# 또는 flatten 메서드
X_flat2 = images.reshape(images.shape[0], -1)

print("원본:", images.shape)      # (100, 28, 28, 1)
print("Flatten:", X_flat.shape)   # (100, 784)

# 배치 차원 추가/제거
single_sample = X_flat[0]  # (784,)
batched = single_sample[np.newaxis, :]  # (1, 784)
# 또는
batched = single_sample.reshape(1, -1)

print("단일 샘플:", single_sample.shape)
print("배치화:", batched.shape)
```

### Transpose와 Swapaxes
```python
# (batch, height, width, channels) -> (batch, channels, height, width)
# PyTorch 형식 변환
images_torch = np.transpose(images, (0, 3, 1, 2))

print("TensorFlow 형식:", images.shape)        # (100, 28, 28, 1)
print("PyTorch 형식:", images_torch.shape)     # (100, 1, 28, 28)

# 행렬 전치
W = np.random.randn(784, 128)
W_T = W.T  # (128, 784)
```

### Squeeze와 Expand_dims
```python
# 불필요한 차원 제거
prediction = np.random.rand(10, 1, 1)
squeezed = np.squeeze(prediction)  # (10,)

# 차원 추가
vector = np.array([1, 2, 3, 4, 5])
col_vector = np.expand_dims(vector, axis=1)  # (5, 1)
row_vector = np.expand_dims(vector, axis=0)  # (1, 5)

print("원본:", vector.shape)
print("열벡터:", col_vector.shape)
print("행벡터:", row_vector.shape)
```

## 3. 인덱싱과 슬라이싱

### 미니배치 추출
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

### 고급 인덱싱 - 매우 중요!
```python
# 불린 마스킹 (필터링)
X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
y = np.array([0, 1, 0, 1])

# 클래스 0인 샘플만 선택
X_class0 = X[y == 0]
print("클래스 0 샘플:\n", X_class0)

# 조건부 필터링
outliers = X[np.abs(X) > 5]

# 정수 배열 인덱싱 (샘플 순서 섞기)
shuffle_indices = np.random.permutation(len(X))
X_shuffled = X[shuffle_indices]
y_shuffled = y[shuffle_indices]

# 특정 인덱스 선택
selected_indices = [0, 2, 3]
X_selected = X[selected_indices]
```

### Fancy Indexing
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

## 4. Broadcasting - 핵심 개념!

### 기본 Broadcasting
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

### 실전 예제: 정규화
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

### Broadcasting 트릭
```python
# 거리 행렬 계산 (모든 쌍 사이의 유클리드 거리)
X = np.random.randn(100, 5)

# 방법 1: Broadcasting 활용
X_expanded = X[:, np.newaxis, :]      # (100, 1, 5)
X_transposed = X[np.newaxis, :, :]    # (1, 100, 5)
distances_sq = np.sum((X_expanded - X_transposed)**2, axis=2)
distances = np.sqrt(distances_sq)

print("거리 행렬:", distances.shape)  # (100, 100)
```

## 5. 축(Axis) 연산

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

## 6. 선형대수 연산

### 행렬 곱셈 - 가장 중요!
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

### 배치 행렬 곱셈
```python
# 3D 텐서 연산 (시퀀스 데이터)
batch_size, seq_len, input_dim = 32, 10, 50
hidden_dim = 100

X = np.random.randn(batch_size, seq_len, input_dim)
W = np.random.randn(input_dim, hidden_dim)

# 각 타임스텝에 가중치 적용
# 방법 1: Reshape 활용
X_flat = X.reshape(-1, input_dim)  # (320, 50)
Z_flat = X_flat @ W                 # (320, 100)
Z = Z_flat.reshape(batch_size, seq_len, hidden_dim)  # (32, 10, 100)

# 방법 2: einsum (고급)
Z_einsum = np.einsum('bsi,ih->bsh', X, W)

print("출력 shape:", Z.shape)
```

### 내적과 외적
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

## 7. 활성화 함수 구현

### 주요 활성화 함수
```python
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def relu(x):
    return np.maximum(0, x)

def leaky_relu(x, alpha=0.01):
    return np.where(x > 0, x, alpha * x)

def softmax(x):
    # 수치 안정성을 위해 최댓값 빼기
    exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return exp_x / np.sum(exp_x, axis=-1, keepdims=True)

def tanh(x):
    return np.tanh(x)

# 테스트
Z = np.random.randn(32, 10)
probs = softmax(Z)
print("Softmax 결과 shape:", probs.shape)
print("각 샘플의 확률 합:", probs.sum(axis=1)[:5])  # 모두 1.0
```

## 8. 손실 함수

### 주요 손실 함수
```python
def mse_loss(y_true, y_pred):
    """평균 제곱 오차"""
    return np.mean((y_true - y_pred) ** 2)

def binary_crossentropy(y_true, y_pred):
    """이진 교차 엔트로피"""
    epsilon = 1e-15  # log(0) 방지
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
    return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))

def categorical_crossentropy(y_true, y_pred):
    """다중 클래스 교차 엔트로피"""
    epsilon = 1e-15
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
    return -np.mean(np.sum(y_true * np.log(y_pred), axis=1))

# 예제
y_true = np.array([[0, 0, 1], [0, 1, 0], [1, 0, 0]])
y_pred = softmax(np.random.randn(3, 3))
loss = categorical_crossentropy(y_true, y_pred)
print("손실:", loss)
```

## 9. 그래디언트 계산

### 역전파 예제
```python
# Forward pass
X = np.random.randn(32, 10)
W = np.random.randn(10, 5)
b = np.zeros(5)

Z = X @ W + b  # (32, 5)
A = relu(Z)

# 가상의 그래디언트 (다음 레이어에서 전파됨)
dA = np.random.randn(32, 5)

# ReLU 역전파
dZ = dA * (Z > 0)  # ReLU의 미분

# 선형 레이어 역전파
dW = X.T @ dZ / X.shape[0]  # (10, 5)
db = np.mean(dZ, axis=0)     # (5,)
dX = dZ @ W.T                # (32, 10)

print("dW shape:", dW.shape)
print("db shape:", db.shape)
print("dX shape:", dX.shape)
```

## 10. 데이터 전처리

### Min-Max 스케일링
```python
def minmax_scale(X, feature_range=(0, 1)):
    """Min-Max 스케일링"""
    X_min = X.min(axis=0)
    X_max = X.max(axis=0)
    X_scaled = (X - X_min) / (X_max - X_min)
    
    # 원하는 범위로 조정
    min_val, max_val = feature_range
    X_scaled = X_scaled * (max_val - min_val) + min_val
    return X_scaled

X = np.random.randn(100, 5)
X_scaled = minmax_scale(X)
print("스케일 후 최솟값:", X_scaled.min(axis=0))
print("스케일 후 최댓값:", X_scaled.max(axis=0))
```

### 표준화 (Z-score Normalization)
```python
def standardize(X):
    """표준화"""
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    return (X - mean) / std

X_standardized = standardize(X)
print("평균:", X_standardized.mean(axis=0))  # ~0
print("표준편차:", X_standardized.std(axis=0))  # ~1
```

### One-Hot 인코딩
```python
def one_hot_encode(y, num_classes=None):
    """One-hot 인코딩"""
    if num_classes is None:
        num_classes = y.max() + 1
    
    one_hot = np.zeros((len(y), num_classes))
    one_hot[np.arange(len(y)), y] = 1
    return one_hot

y = np.array([0, 2, 1, 2, 0])
y_one_hot = one_hot_encode(y, num_classes=3)
print("One-hot:\n", y_one_hot)
```

## 11. 배치 처리 및 데이터 로더

### 미니배치 생성기
```python
def batch_generator(X, y, batch_size=32, shuffle=True):
    """미니배치 생성기"""
    n_samples = X.shape[0]
    indices = np.arange(n_samples)
    
    if shuffle:
        np.random.shuffle(indices)
    
    for start_idx in range(0, n_samples, batch_size):
        end_idx = min(start_idx + batch_size, n_samples)
        batch_indices = indices[start_idx:end_idx]
        
        yield X[batch_indices], y[batch_indices]

# 사용 예제
X = np.random.randn(1000, 10)
y = np.random.randint(0, 2, 1000)

for X_batch, y_batch in batch_generator(X, y, batch_size=32):
    print("배치 shape:", X_batch.shape, y_batch.shape)
    break  # 첫 배치만 출력
```

### Train/Validation Split
```python
def train_test_split(X, y, test_size=0.2, random_state=None):
    """데이터 분할"""
    if random_state is not None:
        np.random.seed(random_state)
    
    n_samples = X.shape[0]
    indices = np.random.permutation(n_samples)
    
    test_samples = int(n_samples * test_size)
    test_indices = indices[:test_samples]
    train_indices = indices[test_samples:]
    
    return X[train_indices], X[test_indices], y[train_indices], y[test_indices]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
print("Train set:", X_train.shape)
print("Test set:", X_test.shape)
```

## 12. 유용한 NumPy 트릭

### Concatenation과 Stacking
```python
# 수평 결합 (특성 추가)
X1 = np.random.randn(100, 5)
X2 = np.random.randn(100, 3)
X_combined = np.concatenate([X1, X2], axis=1)  # (100, 8)

# 또는
X_combined = np.hstack([X1, X2])

# 수직 결합 (샘플 추가)
X_batch1 = np.random.randn(32, 10)
X_batch2 = np.random.randn(32, 10)
X_all = np.concatenate([X_batch1, X_batch2], axis=0)  # (64, 10)

# 또는
X_all = np.vstack([X_batch1, X_batch2])

# Stacking (새 차원 추가)
embeddings = [np.random.randn(100, 50) for _ in range(10)]
stacked = np.stack(embeddings, axis=0)  # (10, 100, 50)
```

### 벡터화 연산 (Vectorization)
```python
# 느린 방법: for 루프
def euclidean_distance_slow(x, y):
    distances = []
    for i in range(len(x)):
        dist = 0
        for j in range(len(x[i])):
            dist += (x[i, j] - y[j]) ** 2
        distances.append(np.sqrt(dist))
    return np.array(distances)

# 빠른 방법: 벡터화
def euclidean_distance_fast(x, y):
    return np.sqrt(np.sum((x - y) ** 2, axis=1))

X = np.random.randn(1000, 50)
y = np.random.randn(50)

# 속도 비교
import time

start = time.time()
_ = euclidean_distance_fast(X, y)
print(f"벡터화: {time.time() - start:.4f}초")
```

### 조건부 연산
```python
# np.where: 조건부 선택
X = np.random.randn(100, 5)

# 음수는 0으로, 양수는 그대로 (ReLU)
X_relu = np.where(X > 0, X, 0)

# 복잡한 조건
# 값이 -1과 1 사이면 그대로, 아니면 클리핑
X_clipped = np.where(X > 1, 1, np.where(X < -1, -1, X))

# np.select: 여러 조건
conditions = [X < -1, (X >= -1) & (X <= 1), X > 1]
choices = [-1, X, 1]
X_clipped2 = np.select(conditions, choices)
```

### 메모리 뷰와 복사
```python
# 뷰 (메모리 공유)
X = np.random.randn(100, 10)
X_view = X[:50]  # 뷰
X_view[0, 0] = 999
print("원본도 변경됨:", X[0, 0])  # 999

# 복사 (독립적)
X_copy = X[:50].copy()
X_copy[0, 0] = -999
print("원본은 유지됨:", X[0, 0])  # 999
```

## 13. PyTorch/Scikit-learn과의 연동

### NumPy ↔ PyTorch
```python
# NumPy -> PyTorch (예시 코드)
"""
import torch

X_numpy = np.random.randn(100, 10)
X_torch = torch.from_numpy(X_numpy).float()

# PyTorch -> NumPy
y_torch = torch.randn(100, 5)
y_numpy = y_torch.numpy()
"""
```

### NumPy ↔ Scikit-learn
```python
# Scikit-learn은 NumPy 배열을 네이티브로 사용
"""
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

X = np.random.randn(1000, 20)
y = np.random.randint(0, 2, 1000)

# 스케일링
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # NumPy 배열 반환

# 모델 학습
model = LogisticRegression()
model.fit(X_scaled, y)

# 예측
predictions = model.predict(X_scaled)  # NumPy 배열
probabilities = model.predict_proba(X_scaled)  # NumPy 배열
"""
```

## 14. 실전 예제: 간단한 신경망 구현

```python
class SimpleNeuralNetwork:
    def __init__(self, input_dim, hidden_dim, output_dim):
        # He 초기화
        self.W1 = np.random.randn(input_dim, hidden_dim) * np.sqrt(2 / input_dim)
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, output_dim) * np.sqrt(2 / hidden_dim)
        self.b2 = np.zeros(output_dim)
    
    def relu(self, x):
        return np.maximum(0, x)
    
    def relu_derivative(self, x):
        return (x > 0).astype(float)
    
    def softmax(self, x):
        exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=-1, keepdims=True)
    
    def forward(self, X):
        # 은닉층
        self.Z1 = X @ self.W1 + self.b1
        self.A1 = self.relu(self.Z1)
        
        # 출력층
        self.Z2 = self.A1 @ self.W2 + self.b2
        self.A2 = self.softmax(self.Z2)
        
        return self.A2
    
    def backward(self, X, y, learning_rate=0.01):
        m = X.shape[0]
        
        # 출력층 그래디언트
        dZ2 = self.A2 - y
        dW2 = (self.A1.T @ dZ2) / m
        db2 = np.mean(dZ2, axis=0)
        
        # 은닉층 그래디언트
        dA1 = dZ2 @ self.W2.T
        dZ1 = dA1 * self.relu_derivative(self.Z1)
        dW1 = (X.T @ dZ1) / m
        db1 = np.mean(dZ1, axis=0)
        
        # 가중치 업데이트
        self.W2 -= learning_rate * dW2
        self.b2 -= learning_rate * db2
        self.W1 -= learning_rate * dW1
        self.b1 -= learning_rate * db1
    
    def train(self, X, y, epochs=100, batch_size=32, learning_rate=0.01):
        for epoch in range(epochs):
            # 미니배치 학습
            for X_batch, y_batch in batch_generator(X, y, batch_size):
                # Forward pass
                predictions = self.forward(X_batch)
                
                # Backward pass
                self.backward(X_batch, y_batch, learning_rate)
            
            # 에포크마다 손실 출력
            if epoch % 10 == 0:
                predictions = self.forward(X)
                loss = -np.mean(np.sum(y * np.log(predictions + 1e-15), axis=1))
                print(f"Epoch {epoch}, Loss: {loss:.4f}")

# 사용 예제
X = np.random.randn(1000, 20)
y = np.eye(3)[np.random.randint(0, 3, 1000)]  # One-hot

model = SimpleNeuralNetwork(input_dim=20, hidden_dim=50, output_dim=3)
model.train(X, y, epochs=50, batch_size=32, learning_rate=0.1)
```

## 핵심 요약

### 자주 사용하는 패턴

```python
# 1. 데이터 로드 및 전처리
X = np.load('data.npy')
X = (X - X.mean(axis=0)) / X.std(axis=0)

# 2. 배치 처리
for X_batch, y_batch in batch_generator(X, y, batch_size=32):
    # 학습 코드
    pass

# 3. Forward pass
Z = X @ W + b
A = relu(Z)

# 4. Backward pass
dZ = dA * (Z > 0)
dW = X.T @ dZ / batch_size

# 5. 가중치 업데이트
W -= learning_rate * dW
```

### 성능 최적화 팁

1. **벡터화**: 항상 for 루프 대신 NumPy 연산 사용
2. **Broadcasting**: 불필요한