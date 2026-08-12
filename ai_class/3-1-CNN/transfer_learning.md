업로드하신 **「3-1_Transfer Learning 기반의 CNN 모델 학습」 실습 정답 Notebook**을 기준으로 정리하면, 이 실습의 핵심은 단순히 CNN을 학습하는 것이 아니라 **사전 학습 모델을 새로운 데이터셋에 어떻게 재사용하고, 입력 데이터가 모델을 거치면서 어떤 형태로 변환되는지를 이해하는 것**입니다.

특히 요청하신 내용을 중심으로 다음 순서로 설명하겠습니다.

1. 전체 실습 구조
2. 핵심 개념과 원리
3. 각 단계의 필요성 및 주의점
4. 단계별 주요 코드와 클래스/메소드/함수
5. **입력 이미지 → 텐서 → CNN → 출력까지 행렬 크기 변화**
6. Linear Probing과 Fine-tuning의 차이
7. ViT에서의 데이터 크기 변화
8. 전체 데이터 흐름 요약

---

# 1. 실습 전체 구조

Notebook은 크게 **3단계**로 구성되어 있습니다.

```text
CIFAR-10
   │
   ▼
[데이터 전처리]
Resize 32×32 → 224×224
ToTensor
Normalize
   │
   ▼
┌─────────────────────────────┐
│ Step 1. Linear Probing      │
│                             │
│ ResNet-18                   │
│ ├─ Backbone 동결            │
│ └─ FC Layer만 학습          │
└──────────────┬──────────────┘
               │
               ▼
         성능 평가
               │
               ▼
┌─────────────────────────────┐
│ Step 2. Fine-tuning         │
│                             │
│ Data Augmentation           │
│ +                           │
│ ResNet 전체 Layer 학습      │
│ +                           │
│ Learning Rate Scheduler     │
└──────────────┬──────────────┘
               │
               ▼
         성능 평가
               
               +

┌─────────────────────────────┐
│ Step 3. Vision Transformer  │
│                             │
│ CIFAR-10 이미지             │
│ → ViTImageProcessor         │
│ → ViT                       │
│ → 10개 클래스 예측          │
└─────────────────────────────┘
```

즉,

> **데이터 준비 → 전이학습 → 평가 → Fine-tuning → 평가 → ViT 추론**

이라는 전체 이미지 분류 Pipeline을 경험하는 실습입니다.

---

# 2. 가장 중요한 개념: Transfer Learning

## 2.1 전이학습이란?

전이학습(Transfer Learning)은

> **이미 다른 대규모 데이터셋으로 학습된 모델의 지식을 새로운 문제에 재사용하는 방법**

입니다.

Notebook에서는 다음 구조입니다.

```text
ImageNet
1000개 클래스
수백만 장 이미지
        │
        ▼
   ResNet-18 학습
        │
        ▼
[이미지 특징 추출 능력]
        │
        ▼
     CIFAR-10
    10개 클래스
```

예를 들어 ImageNet을 학습한 ResNet은 이미 다음과 같은 특징을 어느 정도 학습했습니다.

```text
초기 Layer
  ↓
Edge
  ↓
Line
  ↓
Texture
  ↓
Shape
  ↓
Object Feature
  ↓
분류
```

따라서 CIFAR-10을 처음부터 학습하지 않고 기존 ResNet의 특징 추출 능력을 활용합니다.

---

# 3. 왜 전이학습이 필요한가?

처음부터 CNN을 학습한다면

```text
Random Weight
      ↓
Edge 학습
      ↓
Texture 학습
      ↓
Shape 학습
      ↓
Object 학습
      ↓
Classification
```

과정을 모두 거쳐야 합니다.

반면 전이학습에서는

```text
ImageNet에서 이미 학습된
Edge / Texture / Shape
       ↓
      재사용
       ↓
CIFAR-10에 맞는
Classification만 학습
```

할 수 있습니다.

따라서 일반적으로 다음과 같은 장점이 있습니다.

* 학습 시간이 감소
* 필요한 데이터가 감소
* 초기 성능이 높음
* 적은 데이터에서도 좋은 성능
* 학습해야 하는 파라미터 감소

---

# 4. CIFAR-10 데이터

Notebook에서 사용하는 데이터는 **CIFAR-10**입니다.

10개의 클래스가 있습니다.

```text
0 airplane
1 automobile
2 bird
3 cat
4 deer
5 dog
6 frog
7 horse
8 ship
9 truck
```

데이터 크기는 다음과 같습니다.

```text
Train : 50,000장
Test  : 10,000장
```

원본 이미지 크기는

```text
32 × 32 × 3
```

입니다.

여기서

* 32 = Height
* 32 = Width
* 3 = RGB Channel

입니다.

---

# 5. 첫 번째 중요한 행렬 크기

Notebook에서 다음 코드가 있습니다.

```python
print(trainset.data.shape, testset.data.shape)
```

CIFAR-10 원본 데이터는 대략 다음 형태입니다.

```text
Train

(50000, 32, 32, 3)
```

즉,

```text
50,000 × 32 × 32 × 3
```

입니다.

여기서 중요한 점은 **PyTorch CNN 입력 형식과 다르다**는 것입니다.

CIFAR-10 원본:

```text
[N, H, W, C]
```

PyTorch CNN:

```text
[N, C, H, W]
```

입니다.


Flowers102 데이터셋의 공식 분할 방식입니다.

| split | 샘플 수 | 용도 |
|-------|---------|------|
| `"train"` | 1,020장 | 학습용 |
| `"val"` | 1,020장 | 검증용 |
| `"test"` | 6,149장 | 최종 평가용 |

특이한 점은 **train이 test보다 적다**는 것입니다. 원 논문에서 의도적으로 설계한 방식으로, 적은 데이터로 학습하고 많은 데이터로 평가하는 **소량 학습(few-shot) 시나리오**를 가정합니다. 그래서 이 데이터셋은 Transfer Learning 효과를 검증하기에 적합합니다.

CIFAR-10은 `train=True/False` 불리언을 썼지만, Flowers102처럼 3개 이상의 분할이 있는 데이터셋은 `split` 문자열 인자를 사용합니다.

---

# 6. 왜 이미지 크기를 224×224로 변경하는가?

Notebook에서는 다음과 같이 처리합니다.

```python
transforms.Resize((224, 224))
```

원래:

```text
32 × 32 × 3
```

에서

```text
224 × 224 × 3
```

으로 변경됩니다.

그 이유는 **ImageNet으로 사전 학습된 ResNet-18의 입력 크기에 맞추기 위해서**입니다.

즉,

```text
CIFAR-10
32×32
   ↓
Resize
   ↓
224×224
   ↓
ImageNet pretrained ResNet-18
```

입니다.

### 중요한 점

Resize는 이미지의 **해상도를 증가**시키는 것이지 새로운 정보를 만들어내는 것은 아닙니다.

```text
32×32
 ↓ Resize
224×224
```

이므로 픽셀 수는 증가하지만 원본 이미지가 가지고 있던 정보의 양 자체가 증가하는 것은 아닙니다.

따라서 CIFAR-10처럼 원본이 32×32인 데이터에서는 **224×224로 확대하는 것이 실습상 사전학습 모델의 입력 규격을 맞추기 위한 것**이라고 이해하는 것이 좋습니다.

```python
# 변환을 위한 평균/표준편차 계산 (배치, 높이, 너비 차원에 대해)
mean = torch.mean(data_tensor.float() / 255.0, dim=(0, 1, 2))
std = torch.std(data_tensor.float() / 255.0, dim=(0, 1, 2))
```

`dim=(0, 1, 2)`는 **평균을 계산할 축(axis)** 을 지정합니다.

Flowers102의 raw 데이터 형태가 `(N, H, W, 3)` — (샘플수, 높이, 너비, 채널) 이라면:

```
dim 0 → 샘플 축  (N개)
dim 1 → 높이 축  (H개)
dim 2 → 너비 축  (W개)
dim 3 → 채널 축  (R, G, B)
```

`dim=(0, 1, 2)`로 평균을 내면 **0·1·2 축을 전부 합쳐서 평균**을 냅니다.

```python
(N, H, W, 3)  →  (3,)
                   ↑
              R평균, G평균, B평균
```

즉 전체 이미지의 모든 픽셀을 채널별로 모아서, **R 전체 평균 / G 전체 평균 / B 전체 평균** 3개 값을 구하는 것입니다.

만약 `dim=(0,)`만 썼다면 `(H, W, 3)` 형태로 남고, `dim=(0,1,2,3)` 전부 썼다면 스칼라 하나만 남았을 것입니다.


---

# 7. Transform의 역할

Notebook에서는 다음 코드가 핵심입니다.

```python
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean, std)
])
```

`Compose`는 여러 전처리 과정을 하나의 Transform pipeline으로 묶어줍니다.

```text
PIL Image
   ↓
Resize
   ↓
ToTensor
   ↓
Normalize
   ↓
Tensor
```

---

# 8. `Resize`

```python
transforms.Resize((224, 224))
```

### 역할

이미지 크기를

```text
32 × 32
```

에서

```text
224 × 224
```

로 변경합니다.

### 필요성

ResNet-18의 사전 학습 환경에 맞추기 위해 사용합니다.

---

# 9. `ToTensor()`

```python
transforms.ToTensor()
```

이미지를 PyTorch Tensor로 변환합니다.

원래 이미지:

```text
H × W × C
```

예:

```text
224 × 224 × 3
```

PyTorch Tensor:

```text
C × H × W
```

즉,

```text
3 × 224 × 224
```

이 됩니다.

그리고 일반적으로 픽셀값

```text
0 ~ 255
```

를

```text
0.0 ~ 1.0
```

범위로 변환합니다.

---

# 10. Normalize

Notebook에서는 먼저 평균과 표준편차를 계산합니다.

```python
data_tensor = torch.from_numpy(trainset.data)

mean = torch.mean(
    data_tensor.float() / 255.0,
    dim=(0, 1, 2)
)

std = torch.std(
    data_tensor.float() / 255.0,
    dim=(0, 1, 2)
)
```

RGB 각각에 대해 평균과 표준편차를 계산합니다.

개념적으로:

```text
R → 평균, 표준편차
G → 평균, 표준편차
B → 평균, 표준편차
```

그리고

```python
transforms.Normalize(mean, std)
```

를 적용합니다.

정규화는 일반적으로

[
x' = \frac{x-\mu}{\sigma}
]

형태입니다.

즉 픽셀값의 분포를 적절하게 조정합니다.

### 왜 필요한가?

신경망 학습에서 입력값의 스케일이 지나치게 다르면 최적화가 불안정해질 수 있습니다.

따라서 입력 데이터의 분포를 적절하게 정규화하여 학습을 안정적으로 만드는 것입니다.

---

# 11. DataLoader

Notebook에서는 다음과 같이 사용합니다.

```python
trainloader = torch.utils.data.DataLoader(
    trainset,
    batch_size=256,
    shuffle=True,
    pin_memory=True,
    num_workers=8
)
```

`DataLoader`의 핵심 역할은

> **전체 데이터를 미니배치 단위로 나누어 모델에 공급하는 것**

입니다.

전체 데이터:

```text
50,000장
```

을 한 번에 넣지 않고

```text
256장
256장
256장
...
```

형태로 제공합니다.

---

# 12. 왜 Batch가 필요한가?

50,000장의 이미지를 한꺼번에 GPU에 넣으면 메모리가 많이 필요합니다.

따라서

```text
50,000장
   ↓
Batch
   ↓
256장
   ↓
256장
   ↓
...
```

형태로 학습합니다.

여기서 모델 입력의 대표적인 크기는

```text
256 × 3 × 224 × 224
```

입니다.

즉,

```text
[N, C, H, W]
```

입니다.

---

# 13. ResNet-18 준비

Notebook에서는

```python
model = torchvision.models.resnet18(pretrained=True)
```

를 사용합니다.

여기서 중요한 것은

```python
pretrained=True
```

입니다.

이는 **ImageNet으로 학습된 가중치를 사용하는 것**을 의미합니다.

---

# 14. ResNet-18의 기본 구조

개념적으로 다음과 같습니다.

```text
Input
  │
  ▼
Conv
  │
  ▼
BatchNorm
  │
  ▼
ReLU
  │
  ▼
Residual Blocks
  │
  ▼
Feature Map
  │
  ▼
Global Average Pooling
  │
  ▼
512 features
  │
  ▼
Fully Connected
  │
  ▼
1000 classes
```

원래 ResNet-18은 ImageNet용이므로

```text
512 → 1000
```

출력을 만듭니다.

---

# 15. 왜 마지막 FC Layer를 바꾸는가?

CIFAR-10은 클래스가 10개입니다.

기존 모델:

```text
512 → 1000
```

새로운 문제:

```text
512 → 10
```

따라서 Notebook에서는

```python
model.fc = nn.Linear(
    model.fc.in_features,
    10
)
```

으로 교체합니다.

### `nn.Linear`

PyTorch의 Fully Connected Layer입니다.

수학적으로는

[
y = Wx+b
]

를 수행합니다.

여기서

```text
입력 feature = 512
출력 = 10
```

이므로

```text
512 → 10
```

입니다.

---

# 16. Linear Probing

첫 번째 학습 방법이 **Linear Probing**입니다.

핵심은

```text
ResNet Backbone
      │
      │ Freeze
      ▼
Feature Extraction
      │
      ▼
FC Layer
      │
      │ Train
      ▼
10 classes
```

입니다.

Notebook에서는

```python
for name, param in model.named_parameters():
    if "fc" not in name:
        param.requires_grad = False
```

입니다.

---

# 17. `requires_grad=False`의 의미

```python
param.requires_grad = False
```

는 해당 파라미터에 대한 gradient를 학습에 사용하지 않겠다는 의미입니다.

즉,

```text
Conv Layer
requires_grad=False
        ↓
업데이트 안 됨

FC Layer
requires_grad=True
        ↓
업데이트 됨
```

입니다.

### 중요한 오해

`requires_grad=False`는 **forward 계산을 하지 않는다는 의미가 아닙니다.**

여전히 입력 이미지는

```text
Conv → Pooling → ...
```

을 모두 통과합니다.

단지 해당 가중치를 업데이트하지 않는 것입니다.

---

# 18. Linear Probing의 데이터 흐름

대표적인 Batch 하나를 생각해보겠습니다.

### 입력

```text
X
[256, 3, 224, 224]
```

↓

### ResNet Backbone

이미지의 특징을 추출합니다.

최종적으로

```text
[256, 512]
```

형태의 feature가 만들어집니다.

↓

### FC

```text
[256, 512]
      ×
[512, 10]
      ↓
[256, 10]
```

최종 출력:

```text
[256, 10]
```

입니다.

---

# 19. `[256, 10]`의 의미

여기서 매우 중요합니다.

```text
256 = Batch Size
10  = CIFAR-10 클래스 수
```

따라서

```text
outputs.shape
```

은

```text
(256, 10)
```

이 됩니다.

예를 들어 한 이미지의 출력이

```text
[-1.2, 0.5, 2.7, ...]
```

라면 10개의 클래스에 대한 **logit**입니다.

---

# 20. Logit이란?

`CrossEntropyLoss`에 전달되는 값은 일반적으로 확률이 아니라 **logit**입니다.

```text
outputs
[256, 10]
```

각 행:

```text
이미지 1 → 10개 클래스의 점수
이미지 2 → 10개 클래스의 점수
...
이미지 256 → 10개 클래스의 점수
```

가장 큰 값을 가진 인덱스를 선택하면 예측 클래스가 됩니다.

```python
_, predicted = torch.max(outputs.data, 1)
```

또는

```python
predicted = outputs.argmax(dim=1)
```

와 같은 방식입니다.

결과:

```text
[256]
```

입니다.

---

# 21. CrossEntropyLoss

Notebook:

```python
criterion = nn.CrossEntropyLoss()
```

입니다.

역할은

> 모델이 출력한 10개 클래스의 점수와 실제 정답을 비교하여 손실을 계산

하는 것입니다.

입력:

```text
outputs : [256, 10]
labels  : [256]
```

출력:

```text
loss : scalar
```

즉 행렬이 하나의 숫자로 축약됩니다.

```text
[256,10]
   +
[256]
   ↓
loss
   ↓
하나의 값
```

---

# 22. 왜 Softmax를 직접 사용하지 않는가?

초보자가 흔히 다음과 같이 생각합니다.

```python
outputs = model(x)
outputs = softmax(outputs)
loss = criterion(outputs, y)
```

하지만 `CrossEntropyLoss`는 내부적으로 LogSoftmax와 NLLLoss 계열 계산을 처리합니다.

따라서 일반적인 PyTorch 분류 학습에서는

```python
outputs = model(x)
loss = criterion(outputs, y)
```

처럼 사용하는 것이 맞습니다.

---

# 23. SGD

Notebook:

```python
optimizer = optim.SGD(
    model.fc.parameters(),
    lr=0.001
)
```

여기서는 FC Layer만 optimizer에 전달합니다.

즉,

```text
Optimizer
   │
   └── model.fc.parameters()
```

입니다.

따라서 Linear Probing에서는 실제로 FC Layer의 파라미터만 업데이트됩니다.

---

# 24. 학습 루프의 핵심

Notebook의 학습 과정은 매우 중요합니다.

```python
optimizer.zero_grad()

outputs = model(xb)

loss = criterion(outputs, yb)

loss.backward()

optimizer.step()
```

이 5줄을 반드시 이해해야 합니다.

---

## ① `zero_grad()`

```python
optimizer.zero_grad()
```

이전 Batch에서 계산된 gradient를 제거합니다.

PyTorch의 gradient는 기본적으로 누적되기 때문입니다.

---

## ② Forward

```python
outputs = model(xb)
```

입력:

```text
[256,3,224,224]
```

↓

ResNet

↓

출력:

```text
[256,10]
```

---

## ③ Loss

```python
loss = criterion(outputs, yb)
```

```text
[256,10]
      +
[256]
      ↓
   Loss
```

---

## ④ Backward

```python
loss.backward()
```

Loss를 기준으로 각 학습 가능한 파라미터의 gradient를 계산합니다.

```text
Loss
 ↓
Gradient
 ↓
FC weight
FC bias
```

Linear Probing에서는 Backbone이 동결되어 있으므로 FC 관련 파라미터만 학습됩니다.

---

## ⑤ Parameter Update

```python
optimizer.step()
```

SGD가 gradient를 이용하여 가중치를 업데이트합니다.

개념적으로

[
w_{new}=w_{old}-\eta\frac{\partial L}{\partial w}
]

입니다.

---

# 25. 모델 평가

Notebook에서는

```python
model.eval()
```

을 사용합니다.

학습 모드:

```python
model.train()
```

평가 모드:

```python
model.eval()
```

입니다.

특히 BatchNorm과 Dropout이 포함된 모델에서는 둘의 차이가 중요합니다.

---

# 26. `torch.no_grad()`

평가할 때

```python
with torch.no_grad():
```

를 사용합니다.

이유는 평가할 때는 gradient가 필요하지 않기 때문입니다.

따라서

* 메모리 절약
* 계산량 감소
* 추론 속도 향상

효과가 있습니다.

---

# 27. Accuracy 계산

예측:

```python
predicted = torch.max(outputs.data, 1)
```

실제 정답:

```text
yb
```

비교:

```python
predicted == yb
```

결과는 Boolean Tensor입니다.

예:

```text
[True, False, True, True, ...]
```

그리고

```python
.sum()
```

으로 맞춘 개수를 계산합니다.

최종적으로

```python
accuracy = 100 * correct / total
```

입니다.

---

# 28. Step 2 — Fine-tuning

Linear Probing의 문제는

> 기존 ResNet의 특징 추출기가 CIFAR-10에 최적화되어 있지 않을 수 있다

는 것입니다.

따라서 두 번째 단계에서는 Backbone도 학습합니다.

```text
Image
 ↓
ResNet Backbone
 ↓
Feature
 ↓
FC
 ↓
10 classes

↑
전체 파라미터 학습
```

---

# 29. Fine-tuning에서는 왜 Learning Rate를 낮추는가?

Notebook에서는

```python
optimizer = optim.SGD(
    model.parameters(),
    lr=0.0005
)
```

를 사용합니다.

Linear Probing:

```text
0.001
```

Fine-tuning:

```text
0.0005
```

입니다.

이미 사전 학습된 좋은 가중치를 가지고 있기 때문에 너무 큰 학습률을 사용하면 기존에 학습된 유용한 특징을 크게 훼손할 수 있습니다.

즉,

```text
Pretrained knowledge
       ↓
조금씩 수정
       ↓
CIFAR-10에 적응
```

하는 것입니다.

---

# 30. Data Augmentation

Notebook에서는

```python
transforms.RandomCrop(32, padding=4)
```

와

```python
transforms.RandomHorizontalFlip(p=0.5)
```

를 사용합니다.

전체 과정은

```text
원본 이미지
   ↓
RandomCrop
   ↓
RandomHorizontalFlip
   ↓
Resize(224,224)
   ↓
ToTensor
   ↓
Normalize
```

입니다.

---

# 31. RandomCrop

```python
transforms.RandomCrop(32, padding=4)
```

먼저 주변에 4픽셀 padding을 추가하고 무작위로 32×32 영역을 선택합니다.

개념적으로

```text
32×32
 ↓
Padding
 ↓
40×40
 ↓
Random Crop
 ↓
32×32
```

입니다.

이를 통해 동일한 이미지라도 매번 조금씩 다른 위치의 이미지가 만들어집니다.

---

# 32. RandomHorizontalFlip

```python
transforms.RandomHorizontalFlip(p=0.5)
```

50% 확률로 좌우 반전합니다.

따라서 하나의 이미지가

```text
원본
```

또는

```text
좌우 반전
```

된 형태로 모델에 들어갑니다.

### 주의점

모든 이미지에서 좌우 반전이 의미 있는 것은 아닙니다.

예를 들어 자동차나 동물처럼 좌우 반전이 비교적 자연스러운 경우와 달리, 숫자나 방향성이 중요한 데이터에서는 주의해야 합니다.

---

# 33. 데이터 증강은 왜 Training에만 사용하는가?

Notebook에서도 테스트 데이터에는 증강을 적용하지 않습니다.

학습:

```text
RandomCrop
RandomFlip
```

평가:

```text
Resize
ToTensor
Normalize
```

입니다.

이유는 평가할 때는 **실제 데이터 분포에 대해 일관된 성능을 측정해야 하기 때문**입니다.

---

# 34. Fine-tuning의 행렬 흐름

입력:

```text
[256, 3, 224, 224]
```

↓

ResNet

↓

Feature:

```text
[256, 512]
```

↓

FC:

```text
[256, 10]
```

↓

Loss:

```text
scalar
```

입니다.

Linear Probing과 **행렬 크기 자체는 동일**합니다.

차이는 **어떤 파라미터를 업데이트하느냐**입니다.

---

# 35. Linear Probing vs Fine-tuning 핵심 비교

| 항목            | Linear Probing | Fine-tuning     |
| ------------- | -------------- | --------------- |
| Backbone      | 동결             | 학습              |
| FC            | 학습             | 학습              |
| 학습 파라미터       | 적음             | 많음              |
| 학습 속도         | 빠름             | 느림              |
| 과적합 위험        | 낮음             | 상대적으로 높음        |
| Learning Rate | 상대적으로 높음       | 낮게 사용           |
| 특징 추출기 변화     | 없음             | CIFAR-10에 맞게 변화 |
| 목적            | 빠른 적응          | 성능 극대화          |

---

# 36. Learning Rate Scheduler

Notebook에서는

```python
scheduler = optim.lr_scheduler.StepLR(
    optimizer,
    step_size=5,
    gamma=0.1
)
```

을 사용합니다.

그리고 Epoch가 끝날 때

```python
scheduler.step()
```

을 호출합니다.

의미는

```text
5 epoch마다
learning rate × 0.1
```

입니다.

예를 들어 시작이

```text
0.0005
```

라면

```text
Epoch 1~5 : 0.0005
Epoch 6~10: 0.00005
...
```

형태로 감소합니다.

---

# 37. 왜 Learning Rate를 감소시키는가?

초기에는

```text
큰 변화
```

가 필요합니다.

후반에는

```text
작은 변화
```

로 세밀하게 최적화하는 것이 유리할 수 있습니다.

즉,

```text
초기
큰 Step
 ↓
빠른 탐색
 ↓
Learning Rate 감소
 ↓
작은 Step
 ↓
세밀한 최적화
```

입니다.

---

# 38. Step 3 — Vision Transformer

세 번째 단계에서는 CNN이 아니라 **Vision Transformer(ViT)**를 사용합니다.

핵심 차이는

```text
CNN
이미지 → Convolution

ViT
이미지 → Patch → Token → Transformer
```

입니다.

---

# 39. ViT에서 이미지가 어떻게 변하는가?

Notebook에서 사용하는 모델은

```text
vit-base-patch16-224-cifar10
```

입니다.

입력:

```text
224 × 224 × 3
```

입니다.

Patch 크기는

```text
16 × 16
```

입니다.

따라서 가로 방향:

```text
224 / 16 = 14
```

세로 방향:

```text
224 / 16 = 14
```

입니다.

총 Patch 수:

```text
14 × 14 = 196
```

입니다.

---

# 40. ViT의 핵심 행렬 변화

```text
이미지
224 × 224 × 3
       │
       ▼
16 × 16 Patch
       │
       ▼
14 × 14 = 196 patches
       │
       ▼
Patch Embedding
       │
       ▼
196개의 Token
       │
       ▼
Transformer Encoder
       │
       ▼
Classification
       │
       ▼
10 classes
```

즉 CNN과 달리 **이미지를 Patch들의 Sequence로 변환**합니다.

---

# 41. `ViTImageProcessor`

Notebook:

```python
image_processor = ViTImageProcessor.from_pretrained(
    model_name
)
```

이 객체는 ViT가 기대하는 이미지 입력 형식으로 변환하는 역할을 합니다.

다음 코드를 보겠습니다.

```python
inputs = image_processor(
    images=sample_images,
    return_tensors="pt"
)
```

입력:

```text
PIL Image
```

출력:

```text
PyTorch Tensor
```

입니다.

그리고 여러 이미지를 넣었기 때문에 Batch가 됩니다.

예를 들어 5개 이미지를 넣으면 개념적으로

```text
[5, 3, 224, 224]
```

형태의 `pixel_values`가 만들어집니다.

---

# 42. ViT 모델 호출

Notebook:

```python
outputs = vit_model(**inputs)
```

여기서

```python
**inputs
```

는 딕셔너리를 함수의 keyword argument로 풀어주는 Python 문법입니다.

예를 들어

```python
inputs = {
    "pixel_values": tensor
}
```

라면

```python
vit_model(
    pixel_values=tensor
)
```

와 같은 의미가 됩니다.

---

# 43. ViT 출력

Notebook:

```python
outputs.logits
```

의 형태는

```text
[5, 10]
```

과 같이 됩니다.

의미는

```text
이미지 1 → 10개 클래스 점수
이미지 2 → 10개 클래스 점수
...
이미지 5 → 10개 클래스 점수
```

입니다.

그리고

```python
outputs.logits.argmax(dim=1)
```

을 사용하면

```text
[5]
```

형태의 예측 클래스 인덱스를 얻습니다.

---

# 44. 클래스 인덱스 → 클래스 이름

Notebook:

```python
labels = dataset.features['label'].names
```

를 사용합니다.

예:

```text
0 → airplane
1 → automobile
2 → bird
...
```

따라서

```python
predicted_labels = [
    labels[idx]
    for idx in predicted_class_idxs
]
```

를 사용하면

```text
[2, 3, 0, 8, 5]
```

같은 숫자 결과를

```text
['bird', 'cat', 'airplane', 'ship', 'dog']
```

처럼 사람이 읽을 수 있는 결과로 변환할 수 있습니다.

---

# 45. Pipeline

마지막에는 HuggingFace의

```python
pipeline(
    task="image-classification",
    model=model_name,
    device=device
)
```

를 사용합니다.

이것은 앞서 직접 작성한

```text
Image
 ↓
ImageProcessor
 ↓
Tensor
 ↓
Model
 ↓
Logits
 ↓
Prediction
 ↓
Label
```

과정을 하나의 편리한 API로 묶은 것입니다.

---

# 46. 전체 행렬 크기 변화 — ResNet

이 부분을 가장 중요하게 기억하시면 됩니다.

CIFAR-10 이미지 한 장:

```text
32 × 32 × 3
```

↓

Resize:

```text
224 × 224 × 3
```

↓

ToTensor:

```text
3 × 224 × 224
```

↓

Batch:

```text
256 × 3 × 224 × 224
```

↓

ResNet Backbone

```text
256 × 512
```

↓

FC:

```text
256 × 10
```

↓

예측:

```text
256
```

즉,

```text
[N,H,W,C]
   ↓
[N,C,H,W]
   ↓
[N,C,H,W]
   ↓
[N,512]
   ↓
[N,10]
   ↓
[N]
```

입니다.

---

# 47. 전체 행렬 크기 변화 — ViT

ViT에서는

```text
CIFAR-10
32 × 32 × 3
```

↓

ImageProcessor

```text
224 × 224 × 3
```

↓

Tensor

```text
3 × 224 × 224
```

↓

Batch 5개

```text
5 × 3 × 224 × 224
```

↓

Patch 분할

```text
14 × 14
```

↓

```text
196 patches
```

↓

Patch Embedding

```text
196 × embedding_dimension
```

↓

Transformer

```text
Token sequence
```

↓

Classification Head

```text
5 × 10
```

↓

`argmax`

```text
5
```

입니다.

---

# 48. CNN과 ViT의 데이터 처리 차이

가장 중요한 차이를 그림으로 보면 다음과 같습니다.

### ResNet

```text
Image
  │
  ▼
Convolution
  │
  ▼
Feature Map
  │
  ▼
Pooling
  │
  ▼
Feature
  │
  ▼
FC
  │
  ▼
Class
```

### ViT

```text
Image
  │
  ▼
Patch
  │
  ▼
Patch Embedding
  │
  ▼
Token Sequence
  │
  ▼
Transformer
  │
  ▼
Classification Head
  │
  ▼
Class
```

따라서 이 실습은 단순한 Transfer Learning 실습을 넘어

> **CNN 기반 전이학습과 Transformer 기반 이미지 분류의 입력 처리 방식 차이**

까지 비교할 수 있도록 구성되어 있습니다.

---

# 49. 실습에서 특히 주의해야 할 부분

## ① Train과 Test Transform을 구분

훈련:

```text
Augmentation 적용
```

테스트:

```text
Augmentation 적용하지 않음
```

---

## ② Normalize 값은 일관성 있게 사용

학습 데이터에서 계산한

```python
mean
std
```

를 Train/Test 모두 동일하게 사용합니다.

---

## ③ Linear Probing에서는 Backbone을 동결

```python
param.requires_grad = False
```

를 확인해야 합니다.

---

## ④ Fine-tuning에서는 동결 해제

```python
for param in model.parameters():
    param.requires_grad = True
```

---

## ⑤ Fine-tuning에서는 Learning Rate를 낮게

사전 학습 가중치를 크게 훼손하지 않도록 낮은 learning rate를 사용합니다.

---

## ⑥ `train()`과 `eval()`을 구분

```python
model.train()
```

과

```python
model.eval()
```

은 서로 다른 역할을 합니다.

---

## ⑦ 추론에서는 `torch.no_grad()`

```python
with torch.no_grad():
```

를 사용하여 불필요한 gradient 계산을 방지합니다.

---

## ⑧ 출력은 확률이 아니라 Logit

```python
outputs = model(x)
```

의 결과는 일반적으로

```text
확률
```

이 아니라

```text
logit
```

입니다.

분류 클래스는

```python
outputs.argmax(dim=1)
```

으로 선택할 수 있습니다.

---

# 50. 이 실습에서 반드시 이해해야 하는 핵심 코드 10개

| 코드                          | 의미                   |
| --------------------------- | -------------------- |
| `transforms.Resize()`       | 입력 이미지 크기 변경         |
| `transforms.ToTensor()`     | 이미지 → PyTorch Tensor |
| `transforms.Normalize()`    | 입력 데이터 정규화           |
| `DataLoader()`              | Mini-batch 생성        |
| `resnet18(pretrained=True)` | 사전학습 ResNet-18 로드    |
| `nn.Linear()`               | 분류층 생성               |
| `requires_grad=False`       | 파라미터 학습 동결           |
| `CrossEntropyLoss()`        | 다중 클래스 분류 손실         |
| `optimizer.step()`          | 가중치 업데이트             |
| `scheduler.step()`          | Learning Rate 조정     |

---

# 51. 전체 Pipeline을 한 장으로 정리

```text
                 CIFAR-10
             32×32×3 이미지
                    │
                    ▼
          ┌──────────────────┐
          │ Resize(224,224)  │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │    ToTensor()    │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │   Normalize()    │
          └────────┬─────────┘
                   │
                   ▼
        [Batch, 3, 224, 224]
                   │
                   ▼
          ┌──────────────────┐
          │   ResNet-18      │
          │  Pretrained      │
          └────────┬─────────┘
                   │
                   ▼
             [Batch, 512]
                   │
                   ▼
             ┌──────────┐
             │   FC     │
             │ 512 → 10 │
             └────┬─────┘
                  │
                  ▼
             [Batch, 10]
                  │
                  ▼
              Logits
                  │
                  ▼
               argmax
                  │
                  ▼
            Predicted Class
```

그리고 학습 전략은

```text
                 ResNet-18
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
   Linear Probing          Fine-tuning
          │                     │
 Backbone Freeze          전체 학습
          │                     │
 FC만 학습               낮은 LR 사용
          │                     │
          └──────────┬──────────┘
                     ▼
                CIFAR-10
```

으로 정리할 수 있습니다.

---

## 핵심적으로 기억할 5가지

**① 전이학습**

> 이미 학습된 모델의 특징 추출 능력을 새로운 문제에 재사용한다.

**② Linear Probing**

> Backbone은 고정하고 마지막 분류층만 학습한다.

**③ Fine-tuning**

> Backbone까지 학습하여 새로운 데이터셋에 모델을 더 세밀하게 적응시킨다.

**④ 데이터 형태 변화**

```text
32×32×3
→ 224×224×3
→ 3×224×224
→ Batch×3×224×224
→ Batch×512
→ Batch×10
→ Batch
```

**⑤ 학습의 본질**

```text
Input
 ↓
Forward
 ↓
Output
 ↓
Loss
 ↓
Backward
 ↓
Gradient
 ↓
Optimizer
 ↓
Weight Update
```

이 흐름이 이 Notebook에서 가장 중요한 **PyTorch CNN 학습 원리**입니다.
