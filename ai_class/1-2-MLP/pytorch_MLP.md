---
marp: true
theme: dark-plus-code
paginate: true
style: |

---

# PyTorch로 구현하는 다층 퍼셉트론 (MLP)

> 데이터셋: scikit-learn `load_digits` (8×8 손글씨 숫자 1,797장, 레이블 0–9)

---

## 학습 개요

**학습 주제**

- **PyTorch 기본 구성 요소**: 텐서(Tensor), 자동 미분(Autograd), 모듈(`nn.Module`)
- **데이터 처리**: 분할·표준화, `Dataset`과 `DataLoader`
- **모델 학습과 평가**: 학습 루프, `train()`/`eval()`, Early Stopping

**학습 목표**

1. 텐서 연산과 **Autograd**로 경사하강법의 원리를 이해한다.
2. `nn.Module`을 상속해 MLP를 정의하고 `forward`를 구현한다.
3. `TensorDataset`·`DataLoader`로 배치 파이프라인을 구성한다.
4. `CrossEntropyLoss`·`Adam`으로 학습 루프를 작성한다.
5. `train`/`eval` 전환과 Early Stopping으로 최적 모델을 저장한다.

----------

**전체 흐름**

```
텐서·Autograd  →  핵심 구성요소  →  데이터 파이프라인  →  학습·평가
   (원리)        (Module·Loss·Opt)   (Dataset·Loader)     (loop·early stop)
```

---

## Step 1 — Tensor와 Autograd

### 1.1 텐서(Tensor)

- 모든 연산의 기본 자료구조. 
- NumPy 배열과 사용법이 거의 같지만 주요한 차이가 있다.

> - **GPU 가속** — `tensor.to(device)`로 연산을 GPU에서 수행
> - **자동 미분(Autograd)** — 연산 그래프를 추적해 기울기를 자동 계산

데이터는 항상 `(N, 특성수)` 형태로 **배치 전체를 한 번에** 처리한다.

```python
import torch

a = torch.tensor([[1., 2.], [3., 4.]])   # (2, 2)
b = torch.from_numpy(np_array)            # NumPy → Tensor
c = a.cpu().numpy()                       # Tensor → NumPy
x = a.to("cuda")                          # GPU로 이동
```

--------------


### 1.2 자동 미분(Autograd)

`requires_grad=True`로 만든 텐서의 연산은 **연산 그래프(computational graph)**로 기록
- `.backward()` 로 그래프를 거꾸로 순회(역전파)하며 기울기 계산 가능

```python
x = torch.tensor([2., 3.], requires_grad=True)
y = x**2 + 3*x + 1        # y = x² + 3x + 1
z = y.sum()               # 스칼라 출력이어야 backward 가능
z.backward()              # 역전파
print(x.grad)             # dz/dx = 2x + 3 → [7., 9.]
```

---------

**함수와 도함수**:

$$
y = x^2 + 3x + 1, \qquad \frac{dy}{dx} = 2x + 3
$$

- `z = y.sum()`이므로 각 성분에 대해

$$
\frac{\partial z}{\partial x_i} = 2x_i + 3
\;\Rightarrow\;
\left[\frac{\partial z}{\partial x_1}, \frac{\partial z}{\partial x_2}\right]
= [\,2(2)+3,\; 2(3)+3\,] = [\,7,\; 9\,]
$$

> **주의** — 기울기는 **누적(accumulate)**된다. 매 반복 전에 `x.grad.zero_()`(또는 옵티마이저의 `zero_grad()`)로 비워야 한다.

----------

### 1.3 경사하강법(Gradient Descent)

- 모델 $\hat{y} = \theta x + b$, 데이터 한 점 $(x, y) = (2, 4)$, 손실은 제곱오차(MSE)라 하자.

**① 예측**

$$
\hat{y} = \theta x + b
$$

**② 손실**

$$
L = (\hat{y} - y)^2
$$

**③ 기울기(미분)** — 연쇄법칙으로

$$
\frac{\partial L}{\partial \theta} = 2(\hat{y}-y)\,x,
\qquad
\frac{\partial L}{\partial b} = 2(\hat{y}-y)
$$

---------

**④ 업데이트** — 기울기의 **반대 방향**으로 이동 ($\eta$ = 학습률)

$$
\theta \leftarrow \theta - \eta\,\frac{\partial L}{\partial \theta},
\qquad
b \leftarrow b - \eta\,\frac{\partial L}{\partial b}
$$

초기값 $\theta=3,\ b=1$로 한 스텝 따라가 보면:

$$
\hat{y} = 3(2)+1 = 7,\quad
L = (7-4)^2 = 9,\quad
\frac{\partial L}{\partial \theta}=2(3)(2)=12,\quad
\frac{\partial L}{\partial b}=2(3)=6
$$

```python
theta, b, lr = 3.0, 1.0, 0.1
for step in range(100):
    y_hat = theta * 2 + b
    loss  = (y_hat - 4) ** 2
    d_theta = 2 * (y_hat - 4) * 2
    d_b     = 2 * (y_hat - 4)
    theta -= lr * d_theta
    b     -= lr * d_b
```

--------------


## Step 2 — 핵심 구성요소 (Module · Loss · Optimizer)

- Step 1의 **수동** 경사하강법에서 반복되던 부분을 PyTorch가 대신 처리한다.

| 구성요소 | 역할 | 예시 |
| --- | --- | --- |
| **파라미터** | weight·bias 자동 생성·초기화 | `nn.Linear(in, out)` |
| **손실 함수** | 예측·목표 → 스칼라 손실 | `nn.MSELoss()`, `nn.CrossEntropyLoss()` |
| **옵티마이저** | 등록된 파라미터를 일괄 갱신 | `optim.SGD(...)`, `optim.Adam(...)` |

선형 계층의 연산:

$$
\mathbf{y} = \mathbf{x}\mathbf{W}^{\top} + \mathbf{b}
$$

--------------

### 2.1 학습 루프의 네 줄

```python
model     = nn.Linear(1, 1)
criterion = nn.MSELoss()
optimizer = optim.SGD(model.parameters(), lr=0.01)

optimizer.zero_grad()               # ① 기울기 초기화
loss = criterion(model(X), y)       # ② 순전파 + 손실
loss.backward()                     # ③ 역전파
optimizer.step()                    # ④ 파라미터 업데이트
```

이 네 줄이 모든 학습의 핵심이다. 옵티마이저에 등록된 **모든 파라미터**가 `step()` 한 번에 갱신된다.

-----------------

### 2.2 nn.Module로 MLP 조립

```python
class SimpleMLP(nn.Module):
    def __init__(self, in_dim, hid, out_dim):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(in_dim, hid),
            nn.ReLU(),
            nn.Linear(hid, out_dim),
        )

    def forward(self, x):
        return self.layers(x)
```

- `model(X)`를 호출하면 `__call__`이 hook 처리와 그래프 연결을 한 뒤 `forward`를 실행한다.
  → 그래서 우리는 **`forward`만 구현**하면 된다.
- **비선형성**이 없으면 층을 쌓아도 하나의 선형변환과 같다. `nn.ReLU()`가 그 역할을 한다.

$$
\mathrm{ReLU}(x) = \max(0, x)
$$

-----------------

## Step 3 — Dataset과 DataLoader

매번 인덱싱으로 배치를 꺼내는 대신, `TensorDataset`으로 묶고 `DataLoader`에 배치·셔플·병렬 로딩을 맡긴다.

### 3.1 데이터 파이프라인

```
① 원본 데이터      (1797, 64)          load_digits, 64차원 벡터로 평탄화
② 데이터 분할      1437 / 180 / 180    train_test_split ×2, stratify로 비율 유지
③ 표준화           평균 0 · 분산 1      StandardScaler (train에만 fit)
④ TensorDataset    (x, y) 튜플          from_numpy로 Tensor 변환 후 묶기
⑤ DataLoader       batch 32 · 45배치    train만 shuffle=True
```

**① 분할** — 80·10·10, 클래스 비율 유지(`stratify`)

```python
X_tr, X_tmp, y_tr, y_tmp = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)
X_va, X_te, y_va, y_te = train_test_split(
    X_tmp, y_tmp, test_size=0.5, stratify=y_tmp, random_state=42)
```

-----------------

**② 표준화** — `train`에만 `fit`해 **데이터 누수(leakage)**를 막는다

$$
x' = \frac{x - \mu_{\text{train}}}{\sigma_{\text{train}}}
$$

```python
scaler = StandardScaler().fit(X_tr)     # train 통계로만 학습
X_tr = scaler.transform(X_tr)
X_va = scaler.transform(X_va)           # valid·test에는 transform만
X_te = scaler.transform(X_te)
```

**③ Dataset·DataLoader**

```python
train_ds = TensorDataset(torch.from_numpy(X_tr).float(),
                         torch.from_numpy(y_tr).long())
train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)

train_ds[0]           # → (x, y) 한 쌍
len(train_loader)     # → 배치 개수(45), 샘플 수가 아님
for xb, yb in train_loader:
    ...               # xb: (32, 64), yb: (32,)
```

-----------------

### 3.2 Dataset vs DataLoader

| | Dataset | DataLoader |
| --- | --- | --- |
| 단위 | 단일 샘플 | 배치 |
| 인덱싱 | `ds[0]` → `(x, y)` | 불가, `for`로 순회 |
| `len()` | 전체 샘플 수 | **배치 개수** |
| 기능 | — | shuffle · 병렬 로딩 · drop_last |

-----------------

## Step 4 — MLP 학습과 평가

### 4.1 MLP 구조 (64 → 128 → 64 → 10)

| 층 | 연산 | 출력 shape | 파라미터 |
| --- | --- | --- | --- |
| 입력 | 64차원 벡터로 평탄화 | `(N, 64)` | — |
| 은닉 1 | `Linear` → `ReLU` → `Dropout(0.2)` | `(N, 128)` | 8,320 |
| 은닉 2 | `Linear` → `ReLU` → `Dropout(0.2)` | `(N, 64)` | 8,256 |
| 출력 | `Linear` | `(N, 10)` | 650 |

-----------------

- 전체 학습 파라미터는 약 **17,000개**. 출력은 클래스 0–9에 대한 **logit**이다.

```python
class MLP(nn.Module):
    def __init__(self, in_dim=64, num_classes=10, p=0.2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 128), nn.ReLU(), nn.Dropout(p),
            nn.Linear(128, 64),     nn.ReLU(), nn.Dropout(p),
            nn.Linear(64, num_classes),
        )

    def forward(self, x):
        return self.net(x)
```

-----------------

### 4.2 손실 함수 — CrossEntropy

다중 분류에는 `CrossEntropyLoss`를 쓴다. 내부에서 **softmax + 음의 로그가능도**를 함께 계산하므로,
모델은 softmax 없이 **logit을 그대로** 출력하면 된다.

$$
\hat{p}_k = \frac{e^{z_k}}{\sum_{j} e^{z_j}},
\qquad
L = -\sum_{k} y_k \log \hat{p}_k = -\log \hat{p}_{\text{정답}}
$$

-----------------

### 4.3 train()과 eval()

`train()`/`eval()`은 파라미터가 아니라 **레이어의 동작 모드**를 바꾼다. 추론 전에는 반드시 `eval()` + `no_grad()`.

| | `model.train()` | `model.eval()` |
| --- | --- | --- |
| Dropout | 일부 뉴런을 확률 $p$로 0 | 모든 뉴런 사용 |
| BatchNorm | 현재 배치 통계 | 학습된 running 통계 |
| 기울기 | 추적 (backward 준비) | `no_grad`로 비활성화 |
| 사용 시점 | 학습 루프 | 검증 · 테스트 |

-----------------

### 4.4 학습 함수

```python
def train_one_epoch(model, loader, optimizer, device):
    model.train()
    for xb, yb in loader:
        xb, yb = xb.to(device), yb.to(device)
        optimizer.zero_grad()
        logits = model(xb)
        loss = F.cross_entropy(logits, yb)
        loss.backward()
        optimizer.step()
```

-----------------

### 4.5 평가 함수

```python
@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    correct = total = 0
    for xb, yb in loader:
        xb, yb = xb.to(device), yb.to(device)
        preds = model(xb).argmax(dim=1)
        correct += (preds == yb).sum().item()
        total   += yb.size(0)
    return correct / total          # 정확도
```

정확도:

$$
\text{Accuracy} = \frac{\text{맞힌 샘플 수}}{\text{전체 샘플 수}}
$$

-----------------

### 4.6 Early Stopping

검증 성능이 개선될 때만 체크포인트를 저장하고, `patience` 동안 개선이 없으면 조기 종료한다.

```python
best_acc, no_improve, patience = 0.0, 0, 5

for epoch in range(max_epochs):
    train_one_epoch(model, train_loader, optimizer, device)
    val_acc = evaluate(model, val_loader, device)

    if val_acc > best_acc:                       # 개선됨
        best_acc = val_acc
        torch.save(model.state_dict(), "best.pt")
        no_improve = 0
    else:
        no_improve += 1
        if no_improve >= patience:               # 조기 종료
            break

model.load_state_dict(torch.load("best.pt"))     # best 모델 복원
test_acc = evaluate(model, test_loader, device)
```

-----------------

## 핵심 요약

| 단계 | 무엇을 | 핵심 API |
| --- | --- | --- |
| 1 | 텐서 연산·자동 미분 | `torch.Tensor`, `requires_grad`, `.backward()`, `.grad` |
| 2 | 모델·손실·최적화 | `nn.Module`, `nn.Linear/ReLU/Sequential`, `optim.Adam` |
| 3 | 데이터 배치 처리 | `train_test_split`, `StandardScaler`, `TensorDataset`, `DataLoader` |
| 4 | 학습·평가 | `train()/eval()`, `F.cross_entropy`, `no_grad`, `state_dict`, Early Stopping |

> 한 문장 요약 — **텐서에서 시작해 구성요소로 자동화하고, 데이터를 배치로 흘려, 학습하고 평가한다.**
