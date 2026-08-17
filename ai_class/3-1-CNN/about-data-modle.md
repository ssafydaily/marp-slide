
네. 이 주제는 **"CIFAR-10으로 ResNet18을 직접 학습하는 경우"** 와 **"ImageNet으로 미리 학습된 ResNet18을 PyTorch에서 가져와 사용하는 경우"** 를 구분해서 이해하는 것이 중요합니다.

특히 교육 관점에서는 다음 흐름으로 이해하면 좋습니다.

> **CIFAR-10 → 작은 이미지 → ResNet18 구조를 직접 학습**
> **ImageNet → 대규모 이미지 → 미리 학습된 ResNet18 → 전이학습(Transfer Learning)**
> **torchvision → 이미 학습된 ResNet18을 쉽게 가져다 사용**

---

# 1. CIFAR-10이란?

CIFAR-10은 이미지 분류 모델을 학습할 때 매우 많이 사용하는 대표적인 데이터셋입니다.

CIFAR-10은 다음과 같은 특징을 갖습니다.

| 항목       | 내용          |
| -------- | ----------- |
| 이미지 개수   | 60,000장     |
| 학습 데이터   | 50,000장     |
| 테스트 데이터  | 10,000장     |
| 이미지 크기   | **32 × 32** |
| 색상       | RGB 3채널     |
| 클래스      | **10개**     |
| 클래스당 이미지 | 6,000장      |
| 데이터 형태   | 자연 이미지      |

10개 클래스는 다음과 같습니다.

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

공식 데이터셋 설명에서도 60,000개의 32×32 컬러 이미지가 10개 클래스로 구성되며, 50,000개가 학습용, 10,000개가 테스트용이라고 설명합니다. ([토론토대 컴퓨터과학부][1])

즉 한 장의 데이터는 대략

```text
이미지 : 32 × 32 × 3
정답   : 0 ~ 9
```

형태입니다.

---

# 2. ImageNet은 무엇인가?

ImageNet은 CIFAR-10과 비교할 수 없을 정도로 큰 이미지 데이터셋입니다.

일반적으로 ResNet에서 이야기하는 **ImageNet-1K**는 약 1,000개의 클래스를 대상으로 합니다.

개념적으로 비교하면:

```text
CIFAR-10
 ├─ 이미지 크기 : 32 × 32
 ├─ 클래스 : 10
 └─ 이미지 : 60,000장

ImageNet-1K
 ├─ 이미지 크기 : 일반적으로 224 × 224 입력으로 사용
 ├─ 클래스 : 1,000
 └─ 매우 많은 대규모 이미지
```

그래서 학습 난이도와 모델의 표현 학습 수준이 상당히 다릅니다.

---

# 3. ResNet이란?

ResNet은 **Residual Network**의 약자입니다.

핵심 아이디어는 **Residual Connection**, 즉 **Skip Connection**입니다.

일반적인 신경망은

```text
x
 ↓
Layer
 ↓
Layer
 ↓
Layer
 ↓
F(x)
```

처럼 데이터를 계속 변환합니다.

ResNet은 여기에 원래 입력 `x`를 직접 더합니다.

```text
             ┌──────────────┐
             │              ↓
x ───────────┼──────────→ (+) ──→ 출력
             │              ↑
             ↓              │
        Conv → BN → ReLU → Conv
             │
             └──────── F(x) ─┘
```

즉,

[
y = F(x) + x
]

입니다.

여기서

* `x` : 원래 입력
* `F(x)` : 여러 층을 거쳐 학습한 변화량
* `F(x) + x` : 최종 출력

입니다.

이 구조 덕분에 매우 깊은 네트워크에서도 학습이 훨씬 안정적으로 이루어질 수 있습니다.

---

# 4. ResNet18에서 18은 무엇인가?

ResNet에는 여러 버전이 있습니다.

```text
ResNet18
ResNet34
ResNet50
ResNet101
ResNet152
```

숫자는 대략적인 **네트워크 깊이**를 의미합니다.

즉,

```text
ResNet18 < ResNet34 < ResNet50 < ResNet101 < ResNet152
```

순서로 깊어집니다.

PyTorch torchvision의 ResNet18은 약 **1,169만 개의 파라미터**를 가지고 있으며 약 **1.81 GFLOPS**의 계산량을 갖습니다. ImageNet-1K에서 제공되는 가중치의 Top-1 정확도는 약 69.76%입니다. ([PyTorch Docs][2])

---

# 5. 그런데 CIFAR-10용 ResNet18과 ImageNet용 ResNet18은 다르다

이 부분이 **가장 중요합니다.**

같은 `ResNet18`이라는 이름을 사용하더라도 **입력 이미지 크기와 학습 목적에 따라 구조를 수정해서 사용하는 경우가 많습니다.**

## ImageNet용 ResNet18

일반적인 ImageNet ResNet18은 처음에 대략 다음과 같습니다.

```text
224 × 224 × 3
       ↓
7×7 Conv, stride=2
       ↓
112 × 112
       ↓
3×3 MaxPool, stride=2
       ↓
56 × 56
       ↓
Residual Blocks
       ↓
...
       ↓
1000 classes
```

반면 CIFAR-10은

```text
32 × 32 × 3
```

밖에 안 됩니다.

여기서 ImageNet용 구조를 그대로 적용하면 초기에

```text
32
 ↓ stride 2
16
 ↓ max pooling
8
 ↓
...
```

처럼 공간 크기가 너무 빠르게 감소합니다.

그래서 CIFAR 계열에서는 일반적으로 첫 번째 `7×7 stride=2 convolution`을 `3×3 stride=1`로 바꾸고 초기 MaxPool을 제거하는 방식이 사용됩니다. 이러한 수정은 작은 32×32 이미지에 대한 ResNet 계열 실험에서도 널리 사용됩니다. ([arXiv][3])

---

# 6. CIFAR-10용 ResNet18

개념적으로는 다음과 같습니다.

```text
CIFAR-10
32×32×3
    ↓
3×3 Conv
    ↓
Residual Block × 여러 개
    ↓
Residual Block × 여러 개
    ↓
Residual Block × 여러 개
    ↓
Residual Block × 여러 개
    ↓
Global Average Pooling
    ↓
FC
    ↓
10
```

마지막 출력이

```text
10
```

인 이유는 CIFAR-10의 클래스가 10개이기 때문입니다.

예를 들어 출력이

```text
[-1.2, 0.3, 4.5, 0.2, ...]
```

라면 가장 큰 값의 인덱스가 예측 클래스입니다.

```python
pred = output.argmax(dim=1)
```

---

# 7. ImageNet을 학습한 ResNet18

반면 PyTorch에서 제공하는 ResNet18의 `DEFAULT` 가중치는 ImageNet-1K로 학습된 가중치입니다.

```python
from torchvision.models import resnet18, ResNet18_Weights

weights = ResNet18_Weights.DEFAULT

model = resnet18(weights=weights)
```

현재 torchvision에서는 예전의

```python
resnet18(pretrained=True)
```

방식보다

```python
resnet18(weights=ResNet18_Weights.DEFAULT)
```

방식을 사용하는 것이 권장됩니다. `pretrained` 방식은 deprecated 상태입니다. ([PyTorch Docs][2])

---

# 8. ImageNet pretrained ResNet18의 출력은 1,000개

이 모델은 ImageNet의 1,000개 클래스를 학습했습니다.

따라서

```python
output = model(x)

print(output.shape)
```

결과는

```text
torch.Size([batch_size, 1000])
```

입니다.

예를 들어

```text
이미지
 ↓
ResNet18
 ↓
[1000개의 점수]
 ↓
가장 높은 점수
 ↓
ImageNet class
```

입니다.

---

# 9. PyTorch에서 가장 간단한 사용법

```python
import torch
from torchvision.models import resnet18, ResNet18_Weights

# 1. ImageNet pretrained model
weights = ResNet18_Weights.DEFAULT
model = resnet18(weights=weights)

# 2. 평가 모드
model.eval()

# 3. 전처리
preprocess = weights.transforms()

# 4. 이미지 전처리
image = ...
x = preprocess(image)

# 5. batch 차원 추가
x = x.unsqueeze(0)

# 6. 추론
with torch.no_grad():
    output = model(x)

# 7. 확률
prob = output.softmax(dim=1)

# 8. 가장 높은 클래스
class_id = prob.argmax(dim=1).item()

# 9. 클래스 이름
class_name = weights.meta["categories"][class_id]

print(class_name)
```

PyTorch 공식 문서에서도 `weights.transforms()`를 이용하여 해당 가중치에 맞는 전처리를 수행하는 방식을 권장합니다. ([PyTorch Docs][4])

---

# 10. 전처리가 굉장히 중요하다

여기서 초보자가 가장 많이 실수합니다.

ImageNet ResNet18의 기본 inference transform은 현재 torchvision 문서 기준으로

```text
Resize → 256
Center Crop → 224
[0, 1] 변환
Normalize
```

를 수행합니다.

정규화 값은

```python
mean = [0.485, 0.456, 0.406]
std  = [0.229, 0.224, 0.225]
```

입니다. ([PyTorch Docs][2])

즉 단순히

```python
image → Tensor → model
```

하면 안 됩니다.

반드시

```text
원본 이미지
   ↓
Resize
   ↓
Center Crop
   ↓
Tensor
   ↓
Normalize
   ↓
ResNet18
```

과정을 맞춰줘야 합니다.

특히 pretrained model은 **학습할 때 사용한 전처리와 추론할 때 사용하는 전처리가 맞아야 합니다.** PyTorch 문서도 pretrained model에서 올바른 preprocessing을 사용하는 것이 매우 중요하다고 명시합니다. ([PyTorch Docs][4])

---

# 11. CIFAR-10을 PyTorch로 가져오기

`torchvision`에는 CIFAR-10 Dataset이 제공됩니다.

```python
from torchvision import datasets, transforms

transform = transforms.Compose([
    transforms.ToTensor()
])

train_dataset = datasets.CIFAR10(
    root="./data",
    train=True,
    download=True,
    transform=transform
)

test_dataset = datasets.CIFAR10(
    root="./data",
    train=False,
    download=True,
    transform=transform
)
```

그리고 DataLoader를 사용합니다.

```python
from torch.utils.data import DataLoader

train_loader = DataLoader(
    train_dataset,
    batch_size=64,
    shuffle=True
)

test_loader = DataLoader(
    test_dataset,
    batch_size=64,
    shuffle=False
)
```

`torchvision`의 Dataset들은 `torch.utils.data.Dataset`을 기반으로 하기 때문에 DataLoader와 함께 사용할 수 있습니다. ([PyTorch Docs][5])

---

# 12. CIFAR-10용 ResNet18을 직접 학습한다면

가장 중요한 것은 **마지막 출력층**입니다.

ImageNet용:

```python
1000 classes
```

CIFAR-10:

```python
10 classes
```

따라서 마지막 `fc`를 변경해야 합니다.

```python
import torch.nn as nn
from torchvision.models import resnet18

model = resnet18(weights=None)

model.fc = nn.Linear(
    model.fc.in_features,
    10
)
```

그러면

```text
ResNet18
   ↓
Feature
   ↓
FC
   ↓
10개 클래스
```

가 됩니다.

---

# 13. ImageNet pretrained ResNet18을 CIFAR-10에 사용한다면?

이 경우가 **전이학습(Transfer Learning)**의 대표적인 예입니다.

```python
from torchvision.models import resnet18, ResNet18_Weights
import torch.nn as nn

weights = ResNet18_Weights.DEFAULT

model = resnet18(weights=weights)

model.fc = nn.Linear(
    model.fc.in_features,
    10
)
```

그러면

```text
ImageNet에서 학습
       ↓
ResNet18
       ↓
이미 학습된 특징 추출 능력
       ↓
마지막 FC 교체
       ↓
CIFAR-10 10개 클래스
       ↓
Fine-tuning
```

이라는 과정이 됩니다.

---

# 14. 그런데 CIFAR-10에 ImageNet ResNet18을 그대로 넣으면?

여기서 주의해야 합니다.

ImageNet pretrained ResNet18은 기본적으로

```text
224 × 224
```

크기의 입력을 기준으로 학습되었습니다.

CIFAR-10은

```text
32 × 32
```

입니다.

따라서 다음 두 가지 접근이 가능합니다.

### 방법 A — CIFAR 이미지를 224×224로 확대

```python
transforms.Resize((224, 224))
```

그리고 ImageNet pretrained ResNet18을 그대로 사용합니다.

장점:

* torchvision pretrained 모델을 그대로 사용 가능
* 구현이 매우 간단
* 전이학습 실습에 좋음

단점:

* 원본이 32×32인데 224×224로 확대
* 새로운 정보가 생기는 것은 아님
* CIFAR-10에 최적화된 구조라고 보기는 어려움

---

### 방법 B — ResNet 구조를 CIFAR에 맞게 수정

```text
7×7 Conv
   ↓
3×3 Conv

MaxPool
   ↓
제거
```

등으로 변경합니다.

이 방법은 CIFAR-10 자체를 연구하거나 작은 이미지에 맞는 CNN 구조를 학습할 때 더 적절합니다.

---

# 15. 두 가지 ResNet18을 구분하면 이해가 쉽다

| 구분                      | CIFAR-10 ResNet18 | ImageNet pretrained ResNet18 |
| ----------------------- | ----------------- | ---------------------------- |
| 학습 데이터                  | CIFAR-10          | ImageNet-1K                  |
| 입력                      | 32×32             | 일반적으로 224×224                |
| 클래스                     | 10                | 1,000                        |
| 목적                      | CIFAR 분류          | 일반적인 이미지 특징 학습               |
| 마지막 FC                  | 10                | 1,000                        |
| pretrained              | 직접 학습             | 이미 학습됨                       |
| 전이학습                    | 가능                | 대표적인 용도                      |
| torchvision 기본 ResNet18 | 그대로 사용하기 어려움      | 바로 사용 가능                     |

---

# 16. 왜 ImageNet pretrained 모델을 사용하는가?

핵심은 **이미 유용한 특징을 학습했기 때문**입니다.

예를 들어 ResNet18이 ImageNet을 학습하면서

```text
초기 Layer
↓
Edge
Line
Color

중간 Layer
↓
Texture
Shape
Pattern

후반 Layer
↓
Object parts
Object features
```

같은 특징을 학습합니다.

이러한 특징은 CIFAR-10에서도 어느 정도 활용할 수 있습니다.

따라서

```text
처음부터 학습

Random Weight
     ↓
학습
     ↓
학습
     ↓
학습
```

보다

```text
ImageNet pretrained Weight
          ↓
       CIFAR-10
          ↓
      Fine-tuning
```

으로 시작할 수 있습니다.

이것이 **Transfer Learning**입니다.

---

# 17. Fine-tuning에는 두 가지 대표적인 방법이 있다

## 방법 1. 마지막 FC만 학습

```python
for param in model.parameters():
    param.requires_grad = False

model.fc = nn.Linear(
    model.fc.in_features,
    10
)
```

이렇게 하면 기존 ResNet은 고정하고 마지막 분류기만 학습합니다.

```text
ImageNet Feature Extractor
          ↓
        고정
          ↓
     CIFAR classifier
          ↓
        학습
```

데이터가 적을 때 유용합니다.

---

## 방법 2. 전체 모델 Fine-tuning

처음에는 FC만 학습하다가 이후 전체 네트워크를 학습할 수도 있습니다.

```text
1단계

ResNet
 ↓
Freeze
 ↓
FC만 학습


2단계

ResNet
 ↓
Unfreeze
 ↓
전체 Fine-tuning
```

이 경우 일반적으로 pretrained weight를 망가뜨리지 않도록 **학습률을 작게** 설정하는 것이 중요합니다.

---

# 18. `weights=None`과 `weights=DEFAULT`의 차이

매우 중요한 개념입니다.

### 처음부터 학습

```python
model = resnet18(weights=None)
```

```text
Random Initialization
       ↓
CIFAR-10
       ↓
처음부터 학습
```

### ImageNet pretrained

```python
model = resnet18(
    weights=ResNet18_Weights.DEFAULT
)
```

```text
ImageNet pretrained weights
          ↓
CIFAR-10
          ↓
Fine-tuning
```

둘은 전혀 다른 학습 방식입니다.

---

# 19. `model.train()`과 `model.eval()`도 주의

학습할 때:

```python
model.train()
```

추론할 때:

```python
model.eval()
```

을 사용합니다.

특히 ResNet에는 **BatchNorm**이 있기 때문에 중요합니다.

추론할 때는

```python
model.eval()

with torch.no_grad():
    output = model(x)
```

형태로 사용하는 것이 일반적입니다.

---

# 20. 가장 흔한 실수

### 실수 1. ImageNet 모델의 FC를 그대로 사용

```python
model = resnet18(weights=...)
```

했는데 CIFAR-10을 넣고

```text
출력 = 1000
```

이 나오는 경우입니다.

CIFAR-10이면

```python
model.fc = nn.Linear(model.fc.in_features, 10)
```

으로 변경해야 합니다.

---

### 실수 2. pretrained model인데 전처리를 다르게 함

예를 들어 ImageNet pretrained ResNet18에

```python
transforms.ToTensor()
```

만 적용하는 것은 좋지 않습니다.

가장 안전한 방법은

```python
weights = ResNet18_Weights.DEFAULT

transform = weights.transforms()
```

입니다. ([PyTorch Docs][2])

---

### 실수 3. CIFAR-10 32×32 이미지를 무조건 ImageNet 모델에 그대로 넣음

ResNet의 spatial downsampling 구조를 생각해야 합니다.

```text
32×32
 ↓
stride 2
 ↓
16×16
 ↓
MaxPool
 ↓
8×8
```

처럼 너무 빠르게 공간 정보가 줄어들 수 있습니다.

---

### 실수 4. `softmax`를 학습 단계에서 무조건 사용

CrossEntropyLoss를 사용하는 경우

```python
criterion = nn.CrossEntropyLoss()

loss = criterion(output, target)
```

처럼 **모델의 raw logits를 그대로 넣는 것**이 일반적인 방식입니다.

즉 학습할 때

```python
output = model(x)

loss = criterion(output, y)
```

이고,

예측 결과를 확률로 보고 싶을 때

```python
prob = torch.softmax(output, dim=1)
```

을 사용합니다.

---

# 21. 교육용으로 가장 좋은 실습 순서

제가 추천하는 실습 순서는 다음입니다.

### 실습 1 — CIFAR-10 데이터 확인

```text
CIFAR-10
 ↓
Dataset
 ↓
DataLoader
 ↓
이미지 시각화
```

먼저

```python
print(images.shape)
print(labels.shape)
```

을 확인합니다.

예:

```text
torch.Size([64, 3, 32, 32])
torch.Size([64])
```

---

### 실습 2 — 간단한 CNN

```text
CIFAR-10
 ↓
CNN
 ↓
10 classes
```

을 직접 만들어봅니다.

---

### 실습 3 — CIFAR-10용 ResNet18

```text
CIFAR-10
 ↓
CIFAR용 ResNet18
 ↓
10 classes
 ↓
처음부터 학습
```

---

### 실습 4 — torchvision ResNet18

```python
model = resnet18(
    weights=ResNet18_Weights.DEFAULT
)
```

을 사용해봅니다.

---

### 실습 5 — ImageNet pretrained ResNet18

```text
ImageNet pretrained
       ↓
Feature extraction
       ↓
CIFAR-10
```

을 실습합니다.

---

### 실습 6 — Fine-tuning

```text
Pretrained ResNet18
       ↓
FC 교체
       ↓
10 classes
       ↓
Fine-tuning
```

까지 진행하면 **CNN → ResNet → Pretrained Model → Transfer Learning → Fine-tuning**의 흐름이 한 번에 연결됩니다.

---

# 22. PyTorch에서 제공하는 모델이란?

여기서 한 단계 더 나가면 `torchvision.models`가 중요합니다.

PyTorch의 torchvision은 ResNet뿐만 아니라 다양한 이미지 모델과 pretrained weights를 제공합니다.

예를 들어:

```text
AlexNet
VGG
ResNet
ResNeXt
DenseNet
MobileNet
EfficientNet
ConvNeXt
Vision Transformer
Swin Transformer
...
```

등이 제공됩니다. ([PyTorch Docs][4])

따라서 과거처럼

```text
논문 읽기
 ↓
모델 직접 구현
 ↓
가중치 다운로드
 ↓
전처리 구현
```

을 모두 할 필요가 없습니다.

예를 들어

```python
from torchvision.models import resnet18

model = resnet18(
    weights="DEFAULT"
)
```

처럼 사용할 수 있습니다.

---

# 23. PyTorch pretrained model의 핵심 구조

앞으로 torchvision 모델을 사용할 때는 다음 4가지만 기억하면 상당히 편합니다.

```text
① Model
   ↓
② Weights
   ↓
③ Transforms
   ↓
④ Categories
```

예를 들어:

```python
from torchvision.models import resnet18, ResNet18_Weights

weights = ResNet18_Weights.DEFAULT

model = resnet18(weights=weights)

preprocess = weights.transforms()

categories = weights.meta["categories"]
```

각각의 역할은:

```text
weights
   → 학습된 가중치

model
   → 신경망 구조

transforms
   → 입력 이미지 전처리

categories
   → 출력 클래스 이름
```

입니다. `weights.meta["categories"]`를 통해 pretrained 모델의 클래스 이름도 가져올 수 있습니다. ([PyTorch Docs][4])

---

# 24. 핵심적으로 기억할 것

종윤님이 AI/CNN 교육에서 설명하신다면 저는 다음 그림을 핵심 개념으로 잡는 것을 추천합니다.

```text
                    ImageNet
                약 1,000 classes
                       │
                       ▼
                ┌────────────┐
                │  ResNet18  │
                │ pretrained │
                └────────────┘
                       │
              일반적인 이미지 특징
                       │
              ┌────────┴────────┐
              ▼                 ▼
       ImageNet 분류        Transfer Learning
          1000 classes             │
                                   ▼
                              CIFAR-10
                              10 classes
                                   │
                                   ▼
                              FC 교체
                                   │
                                   ▼
                            Fine-tuning
```

그리고 **CIFAR-10용 ResNet18을 처음부터 학습하는 경우**에는 별도로:

```text
CIFAR-10
32×32×3
   │
   ▼
CIFAR용 ResNet18
   │
   ├─ 초기 7×7 Conv 수정
   ├─ 초기 MaxPool 제거
   │
   ▼
Feature Extraction
   │
   ▼
FC
   │
   ▼
10 classes
```

로 설명하면 좋습니다.

### 한 문장으로 정리하면

> **CIFAR-10은 32×32의 작은 10개 클래스 이미지 데이터셋이고, ImageNet pretrained ResNet18은 대규모 ImageNet에서 이미 이미지 특징을 학습한 모델이므로, CIFAR-10에 적용할 때는 입력 크기·전처리·마지막 FC·학습 방식(Fine-tuning)을 반드시 구분해야 합니다.**

특히 **`resnet18(weights=ResNet18_Weights.DEFAULT)`은 "CIFAR-10을 학습한 ResNet18"이 아니라 "ImageNet-1K를 학습한 ResNet18"**이라는 점이 가장 중요한 포인트입니다. ([PyTorch Docs][2])

원하시면 다음 단계로 **① CIFAR-10용 ResNet18을 PyTorch로 직접 구현 → ② 학습 → ③ ImageNet pretrained ResNet18과 비교 → ④ Transfer Learning/Fine-tuning → ⑤ 정확도와 Confusion Matrix 비교**까지 하나의 실습 코드로 연결할 수 있습니다.

[1]: https://www.cs.toronto.edu/~kriz/cifar.html?trk=public_post_comment-text&utm_source=chatgpt.com "CIFAR-10 and CIFAR-100 datasets"
[2]: https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.resnet18.html?utm_source=chatgpt.com "resnet18 — Torchvision 0.28 documentation"
[3]: https://arxiv.org/pdf/2002.05709?utm_source=chatgpt.com "A Simple Framework for Contrastive Learning of Visual Representations"
[4]: https://docs.pytorch.org/vision/stable/models.html?highlight=resnet18&utm_source=chatgpt.com "Models and pre-trained weights — Torchvision 0.28 documentation"
[5]: https://docs.pytorch.org/vision/stable/datasets.html?utm_source=chatgpt.com "Datasets — Torchvision 0.28 documentation"
