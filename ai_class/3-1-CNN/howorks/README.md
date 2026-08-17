업로드하신 **「3-1_Transfer Learning 기반의 CNN 모델 학습」 실습 노트북**을 기준으로, 학습자가 실습을 따라가면서 이해할 수 있도록 다음과 같은 흐름으로 정리할 수 있습니다.

# 1. 실습 전체 흐름 요약

이 실습의 핵심은 **사전 학습된 ResNet-18을 Flowers102 데이터셋에 맞게 재활용하고, 일부 레이어만 학습하면서 Optimizer와 Scheduler에 따른 성능 차이를 비교하는 것**입니다.

전체 흐름은 다음과 같습니다.

```text
환경 설정
   ↓
Flowers102 데이터셋 로드
   ↓
이미지 전처리 및 DataLoader 생성
   ↓
ImageNet 사전학습 ResNet-18 로드
   ↓
FC Layer를 102개 클래스에 맞게 교체
   ↓
Backbone 일부 레이어 동결
   ↓
Layer4 + FC만 학습
   ↓
① SGD + Momentum + StepLR
   ↓
Baseline 성능 측정
   ↓
모델을 초기 상태로 복원
   ↓
② Adam + ReduceLROnPlateau
   ↓
성능 측정
   ↓
Loss Curve 비교
   ↓
수렴 속도 / 최종 성능 / 안정성 분석
```

즉, 단순히 CNN 모델을 학습하는 것이 아니라,

> **"이미 학습된 모델을 어떻게 새로운 문제에 활용할 것인가?"**

를 실험하는 것이 핵심입니다.

---

# 2. 주요 개념 및 원리 정리

## 2.1 Transfer Learning

**전이 학습(Transfer Learning)**은 이미 다른 데이터로 학습된 모델의 지식을 새로운 문제에 활용하는 방법입니다.

이번 실습에서는

```text
ImageNet
   ↓
ResNet-18 사전 학습
   ↓
일반적인 이미지 특징 학습
   ↓
Flowers102에 재사용
```

이라는 구조를 사용합니다.

ResNet-18은 이미 ImageNet에서 다양한 이미지의

* Edge
* Texture
* Shape
* Object 특징

등을 학습했기 때문에 처음부터 CNN을 학습할 필요가 없습니다.

---

## 2.2 Backbone과 Head

모델을 크게 두 부분으로 생각하면 이해하기 쉽습니다.

```text
입력 이미지
    ↓
[Backbone]
특징 추출
    ↓
[Head]
분류
    ↓
102개 꽃 클래스
```

### Backbone

이미지에서 특징을 추출합니다.

```text
Image
 ↓
Edge
 ↓
Texture
 ↓
Shape
 ↓
High-level feature
```

### Head

추출된 특징을 이용하여 최종적으로 어떤 클래스인지 판단합니다.

ImageNet의 ResNet-18은 **1000개 클래스**를 대상으로 학습되어 있습니다.

하지만 Flowers102는 **102개 클래스**입니다.

따라서 마지막 `fc`를 변경해야 합니다.

---

# 3. 왜 레이어를 동결하는가?

이번 실습에서는 다음과 같이 구성합니다.

```text
conv1       ── Freeze
layer1      ── Freeze
layer2      ── Freeze
layer3      ── Freeze
layer4      ── Train
fc          ── Train
```

즉,

> **Layer4 + FC만 학습**

합니다.

초기 레이어는 일반적인 특징을 학습하고 있기 때문에 그대로 사용하는 것입니다.

반면 Layer4는 상대적으로 고수준의 특징을 가지고 있으므로 꽃이라는 새로운 데이터셋에 맞게 조금 수정할 필요가 있습니다.

---

# 4. Linear Probing과 Partial Fine-tuning

실습에서는 두 개념을 비교해서 이해하는 것이 중요합니다.

| 방법                  | 학습하는 부분     | 특징              |
| ------------------- | ----------- | --------------- |
| Linear Probing      | FC만         | 빠르고 안정적         |
| Partial Fine-tuning | Layer4 + FC | 새로운 데이터에 더 잘 적응 |
| Full Fine-tuning    | 전체          | 많은 데이터와 계산량 필요  |

이번 과제에서는 **Partial Fine-tuning**을 사용합니다.

Flowers102는 학습 데이터가 1,020개로 상대적으로 작기 때문에 전체 모델을 학습시키는 것보다 일부 레이어만 학습하는 전략을 사용하는 것입니다.

---

# 5. Step 1 — 데이터 준비 및 전처리

## 5.1 데이터셋 로드

Flowers102를 다음과 같이 세 부분으로 나눕니다.

```text
Train       1,020
Validation  1,020
Test        6,149
```

코드에서는

```python
datasets.Flowers102(
    root=data_root,
    split="train",
    download=True
)
```

와 같이 `split`을 지정합니다.

---

# 6. 왜 Transform이 필요한가?

사전 학습된 ResNet-18은 ImageNet 데이터에 맞춰 학습되었습니다.

따라서 입력 데이터도 모델이 학습했던 환경과 비슷하게 만들어 주어야 합니다.

이번 실습에서 사용하는 값은

```python
mean = [0.485, 0.456, 0.406]
std = [0.229, 0.224, 0.225]
```

입니다.

전처리 과정은

```text
원본 이미지
   ↓
Resize(224, 224)
   ↓
ToTensor()
   ↓
Normalize(mean, std)
   ↓
ResNet-18
```

입니다.

### 왜 224×224인가?

ImageNet에서 학습된 ResNet-18의 대표적인 입력 크기가 224×224이기 때문입니다.

### 왜 Normalize 하는가?

입력 데이터의 분포를 사전 학습 모델이 학습했던 입력 분포에 맞추기 위해서입니다.

---

# 7. TODO 1에서 학습자가 해야 할 내용

학습자는 다음 네 가지를 직접 구현합니다.

### ① Train Transform

```python
transforms.Resize((224, 224))
transforms.ToTensor()
transforms.Normalize(mean, std)
```

### ② Test Transform

테스트 데이터에는 학습용 데이터 증강을 넣지 않습니다.

```text
Resize
→ ToTensor
→ Normalize
```

### ③ Dataset 생성

각각의 Transform을 train/val/test 데이터셋에 연결합니다.

### ④ DataLoader 생성

```python
batch_size=64
```

를 사용합니다.

---

# 8. 왜 학습자가 직접 작성하게 하는가?

단순히 완성된 코드를 보여주면

> `transforms.Compose()`가 무엇인지 모르고 복사해서 사용할 가능성이 있습니다.

TODO 방식으로 만들면 학습자는

```text
데이터
 ↓
Transform
 ↓
Dataset
 ↓
DataLoader
 ↓
Batch
 ↓
Model
```

이라는 데이터 처리 흐름을 직접 경험하게 됩니다.

즉, **코드를 외우는 것보다 딥러닝 데이터 파이프라인의 구조를 이해하도록 하기 위한 것**입니다.

---

# 9. Step 2 — ResNet-18 모델 준비

다음 단계에서는 ImageNet으로 사전 학습된 ResNet-18을 가져옵니다.

핵심은 다음 세 가지입니다.

```text
① Pretrained ResNet-18 로드
② FC Layer 교체
③ 일부 Layer Freeze
```

---

# 10. FC Layer를 왜 교체하는가?

기존 ResNet-18은

```text
ImageNet
→ 1000개 클래스
```

를 분류하도록 만들어져 있습니다.

하지만 현재 문제는

```text
Flowers102
→ 102개 클래스
```

입니다.

따라서

```python
model.fc = nn.Linear(..., 102)
```

형태로 변경합니다.

이것이 전이 학습에서 매우 중요한 부분입니다.

> **사전 학습 모델의 출력 구조를 새로운 문제의 출력 구조에 맞게 변경한다.**

---

# 11. `requires_grad`의 의미

다음 코드가 핵심입니다.

```python
param.requires_grad = False
```

이것은 해당 파라미터의 gradient를 계산하지 않도록 설정합니다.

즉,

```text
requires_grad=False
→ 학습하지 않음

requires_grad=True
→ 학습 가능
```

입니다.

이번 실습에서는

```text
layer1 → False
layer2 → False
layer3 → False
layer4 → True
fc     → True
```

가 되어야 합니다.

---

# 12. TODO 2에서 학습자가 해야 할 내용

학습자가 해야 할 작업은 다음과 같습니다.

### ① Pretrained ResNet-18 로드

```python
torchvision.models.resnet18(...)
```

### ② FC 변경

```python
model.fc = ...
```

### ③ 레이어 동결

```python
for name, param in model.named_parameters():
    ...
```

여기에서 `layer4`와 `fc`만 학습하도록 설정합니다.

### ④ GPU 이동

```python
model = model.to(device)
```

---

# 13. 왜 모델을 GPU로 이동하는가?

GPU가 있다면 CNN의 대규모 행렬 연산을 병렬적으로 처리할 수 있기 때문에 학습 속도가 크게 향상됩니다.

코드에서는

```python
device = torch.device(
    'cuda' if torch.cuda.is_available() else 'cpu'
)
```

로 실행 환경을 결정합니다.

그리고

```python
xb = xb.to(device)
yb = yb.to(device)
model = model.to(device)
```

처럼 **데이터와 모델이 같은 device에 있어야 합니다.**

---

# 14. TODO 3 — Baseline 학습

첫 번째 실험에서는

```text
Loss
CrossEntropyLoss

Optimizer
SGD + Momentum

Scheduler
StepLR
```

을 사용합니다.

구조를 그림으로 표현하면

```text
SGD + Momentum
       ↓
   학습률 관리
       ↑
     StepLR
```

입니다.

---

# 15. CrossEntropyLoss

다중 클래스 분류 문제에서 대표적으로 사용하는 손실 함수입니다.

이번 문제는

```text
102개의 꽃 클래스 중
하나를 선택
```

하는 문제이므로

```python
criterion = nn.CrossEntropyLoss()
```

를 사용합니다.

---

# 16. 학습 루프의 핵심

TODO 3에서 가장 중요한 부분입니다.

딥러닝 학습은 기본적으로 다음 순서입니다.

```text
1. Gradient 초기화
       ↓
2. Forward
       ↓
3. Loss 계산
       ↓
4. Backward
       ↓
5. Parameter Update
```

코드로 표현하면

```python
optimizer.zero_grad()

outputs = model(xb)

loss = criterion(outputs, yb)

loss.backward()

optimizer.step()
```

입니다.

이 5줄은 **PyTorch 학습 코드에서 반드시 이해해야 하는 핵심 코드**입니다.

---

# 17. SGD + Momentum

SGD는 기본적으로

```text
현재 Gradient
      ↓
가중치 업데이트
```

를 수행합니다.

Momentum은 이전 업데이트 방향도 어느 정도 반영합니다.

따라서

> 학습 과정의 진동을 줄이고 보다 안정적으로 최적점을 찾아가는 데 도움을 줍니다.

---

# 18. StepLR

StepLR은 일정한 epoch마다 learning rate를 감소시킵니다.

이번 설정은

```python
step_size=5
gamma=0.1
```

입니다.

개념적으로

```text
Epoch 1~5
lr = 0.001

Epoch 6~10
lr = 0.0001
```

과 같은 방식으로 감소합니다.

따라서 처음에는 비교적 빠르게 학습하고 후반에는 작은 학습률로 세밀하게 조정할 수 있습니다.

---

# 19. 왜 Baseline을 먼저 만드는가?

첫 번째 실험은 **기준선(Baseline)**입니다.

이 기준이 있어야 이후에

```text
SGD + StepLR
        VS
Adam + ReduceLROnPlateau
```

를 비교할 수 있습니다.

예를 들어 두 번째 실험의 정확도가 높아졌다고 하더라도

> 무엇 때문에 좋아졌는가?

를 판단하려면 기존 결과가 필요합니다.

따라서 실험에서는 **Baseline → 변경 → 비교**가 중요합니다.

---

# 20. TODO 4 — Adam + ReduceLROnPlateau

두 번째 실험에서는 학습 전략을 변경합니다.

```text
첫 번째
SGD + Momentum
StepLR

        VS

두 번째
Adam
ReduceLROnPlateau
```

즉, **Optimizer와 Scheduler의 차이를 실험**하는 것입니다.

---

# 21. Adam Optimizer

Adam은 Gradient의 평균적인 방향과 크기 정보를 이용해서 각 파라미터의 학습률을 적응적으로 조정합니다.

이번 설정은

```python
lr=0.001
betas=(0.9, 0.999)
```

입니다.

간단하게 이해하면

> **파라미터마다 학습 상황에 따라 업데이트 크기를 조절하는 Optimizer**

라고 이해하면 됩니다.

---

# 22. ReduceLROnPlateau

StepLR과 가장 큰 차이는 **성능을 보고 학습률을 변경한다는 것**입니다.

StepLR:

```text
5 epoch 지나면
→ 무조건 LR 감소
```

ReduceLROnPlateau:

```text
Validation Loss 관찰
       ↓
개선되고 있는가?
       ↓
개선되지 않음
       ↓
Learning Rate 감소
```

이번 설정은

```text
mode='min'
factor=0.1
patience=2
min_lr=1e-6
```

입니다.

---

# 23. TODO 4에서 특히 중요한 부분

두 번째 실험에서는 학습뿐 아니라 **Validation**을 사용합니다.

전체 구조는

```text
Training
   ↓
train_loss 계산
   ↓
Validation
   ↓
val_loss 계산
   ↓
ReduceLROnPlateau에 전달
   ↓
Learning Rate 조정
```

입니다.

특히 다음 코드의 개념을 이해하는 것이 중요합니다.

```python
scheduler.step(avg_val_loss)
```

즉,

> **Validation Loss를 보고 Scheduler가 학습률을 조정한다.**

---

# 24. 왜 모델을 초기 상태로 되돌리는가?

TODO 4 시작 부분에서 모델을 학습 전 상태로 복원합니다.

이것은 매우 중요합니다.

첫 번째 실험에서 이미 모델이 학습되었습니다.

그 상태에서 Adam을 적용하면

```text
실험 1의 학습 결과
       ↓
실험 2
```

가 됩니다.

그러면 Optimizer의 차이를 정확하게 비교하기 어렵습니다.

따라서

```text
동일한 초기 모델
       ↓
SGD 실험

동일한 초기 모델
       ↓
Adam 실험
```

으로 만들어야 합니다.

이렇게 해야 **실험 조건을 공정하게 통제**할 수 있습니다.

---

# 25. Loss Curve 비교

마지막에는

```python
plt.plot(naive_losses)
plt.plot(new_losses)
```

를 이용하여 두 실험의 학습 곡선을 비교합니다.

관찰해야 할 것은 크게 세 가지입니다.

### ① 수렴 속도

초기 1~3 epoch에서

> 어느 방법이 Loss를 더 빠르게 감소시키는가?

### ② 최종 성능

10 epoch 후

> 어느 방법의 Loss가 더 낮은가?

그리고

> Test Accuracy도 더 높은가?

를 확인합니다.

### ③ 학습 안정성

Loss가

```text
부드럽게 감소
```

하는지 또는

```text
상승 ↕ 하락 ↕ 상승
```

하는지 관찰합니다.

---

# 26. 코드에서 반드시 이해해야 할 주요 라이브러리

| 라이브러리         | 주요 역할              |
| ------------- | ------------------ |
| `torch`       | PyTorch 핵심 기능      |
| `torch.nn`    | 신경망 Layer와 Loss    |
| `torch.optim` | Optimizer          |
| `torchvision` | 이미지 데이터셋/컴퓨터 비전 모델 |
| `transforms`  | 이미지 전처리            |
| `DataLoader`  | Batch 단위 데이터 제공    |
| `matplotlib`  | Loss Curve 시각화     |
| `numpy`       | 수치 계산              |
| `tqdm`        | 학습 진행률 표시          |
| `copy`        | 모델 상태 복사           |

---

# 27. 주요 PyTorch 코드 사용법

### Dataset

```python
datasets.Flowers102(...)
```

→ Flowers102 데이터셋을 불러옵니다.

### Transform

```python
transforms.Compose([...])
```

→ 여러 전처리를 순서대로 연결합니다.

### DataLoader

```python
DataLoader(dataset, batch_size=64)
```

→ 데이터를 Batch 단위로 제공합니다.

### Model

```python
model(x)
```

→ Forward Pass를 수행합니다.

### Loss

```python
loss = criterion(outputs, y)
```

→ 예측과 정답의 차이를 계산합니다.

### Backward

```python
loss.backward()
```

→ Gradient를 계산합니다.

### Parameter Update

```python
optimizer.step()
```

→ 계산된 Gradient를 이용해 가중치를 업데이트합니다.

### 평가

```python
model.eval()

with torch.no_grad():
    ...
```

→ 모델을 평가 모드로 변경하고 Gradient 계산을 하지 않습니다.

---

# 28. 학습자가 최종적으로 이해해야 하는 핵심

이 실습을 단순히

> "TODO를 채워서 ResNet을 학습했다."

라고 끝내면 안 됩니다.

다음 질문에 답할 수 있어야 합니다.

### Q1. 왜 ResNet-18을 처음부터 학습하지 않는가?

→ ImageNet에서 학습된 특징을 재사용하기 위해서입니다.

### Q2. 왜 FC를 변경하는가?

→ ImageNet은 1000개 클래스지만 Flowers102는 102개 클래스이기 때문입니다.

### Q3. 왜 layer1~3을 Freeze하는가?

→ 이미 학습된 일반적인 특징을 보존하고 불필요한 파라미터 학습을 줄이기 위해서입니다.

### Q4. 왜 layer4를 학습하는가?

→ 고수준 특징을 새로운 꽃 데이터셋에 맞게 조정하기 위해서입니다.

### Q5. 왜 Baseline을 먼저 학습하는가?

→ 이후 실험의 성능을 비교할 기준이 필요하기 때문입니다.

### Q6. 왜 Adam으로 변경하는가?

→ Optimizer의 차이가 학습 속도와 성능에 미치는 영향을 비교하기 위해서입니다.

### Q7. 왜 ReduceLROnPlateau를 사용하는가?

→ Validation Loss가 개선되지 않을 때 학습률을 자동으로 낮추기 위해서입니다.

---

# 29. 마지막으로 전체 실습을 한 번에 정리

이 실습의 핵심 흐름은 다음 **6단계**로 기억하면 좋습니다.

```text
① 데이터 준비
   Flowers102
       ↓
   Resize / Normalize
       ↓
   DataLoader

② 사전학습 모델 준비
   ImageNet
       ↓
   Pretrained ResNet-18

③ 모델 수정
   FC: 1000 → 102
       ↓
   Flowers102에 맞춤

④ 부분 Fine-tuning
   layer1~3 → Freeze
   layer4   → Train
   fc       → Train

⑤ 두 가지 학습 전략 비교
   ┌────────────────────┐
   │ SGD + Momentum     │
   │       +            │
   │ StepLR             │
   └────────────────────┘

             VS

   ┌────────────────────┐
   │ Adam               │
   │       +            │
   │ ReduceLROnPlateau  │
   └────────────────────┘

⑥ 결과 분석
   Loss Curve
      +
   Test Accuracy
      ↓
   수렴 속도
   최종 성능
   학습 안정성
```

**한 문장으로 요약하면:**

> **"ImageNet에서 학습된 ResNet-18의 지식을 Flowers102에 전이하고, Layer4와 FC만 Fine-tuning한 뒤 SGD/StepLR과 Adam/ReduceLROnPlateau의 차이를 실험하고 분석하는 실습"**입니다.
