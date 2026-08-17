업로드하신 **「3-2_이미지 생성 및 평가와 모델 학습.ipynb」**의 전체 코드를 기준으로 분석하면, 이 실습은 단순히 여러 모델을 사용하는 실습이 아니라 다음과 같은 **하나의 AI 파이프라인**을 경험하도록 구성되어 있습니다.

> **텍스트 → 이미지 생성 → 이미지 평가 → CNN과 비교 → 생성 데이터를 이용한 모델 학습**

특히 핵심은 **생성 AI(Generative AI)와 전통적인 이미지 분류 AI를 연결**해 보는 것입니다.

---

# 1. 실습 전체 흐름

실습은 크게 4단계입니다.

```text
[Step 1]
텍스트 프롬프트
      ↓
   SANA
      ↓
생성 이미지
      ↓
[Step 2]
     CLIP
      ↓
이미지 ↔ 텍스트 유사도 평가
      ↓
[Step 3]
   ResNet-50
      ↓
ImageNet 클래스 분류
      ↓
CLIP과 결과 비교
      ↓
[Step 4]
생성 이미지들을 데이터셋으로 구성
      ↓
   ResNet-18
      ↓
전이학습(Linear Probing)
      ↓
새로운 Fox/Dog 분류 모델
```

즉, 이 실습에서 학생이 경험해야 하는 핵심 흐름은 다음과 같습니다.

**① 생성한다 → ② 평가한다 → ③ 기존 모델과 비교한다 → ④ 생성 데이터를 이용해 새로운 모델을 학습한다**

이 흐름을 이해하는 것이 개별 코드보다 중요합니다.

---

# 2. Step 1 — SANA를 이용한 이미지 생성

## 2-1. 알아야 할 이론: Diffusion Model

디퓨전 모델은 기본적으로 다음과 같은 아이디어입니다.

```text
랜덤 노이즈
   ↓
노이즈 제거
   ↓
노이즈 제거
   ↓
노이즈 제거
   ↓
...
   ↓
최종 이미지
```

즉, 처음부터 이미지를 그리는 것이 아니라 **노이즈에서 시작하여 점진적으로 이미지를 만들어 갑니다.**

이 실습에서는 SANA가 이 역할을 합니다.

```python
pipe = SanaPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16
)
```

여기서 중요한 것은 `SanaPipeline` 자체를 직접 구현하는 것이 아니라 **이미 학습된 생성 모델을 불러와 추론(inference)하는 것**입니다.

---

## 2-2. Hugging Face `from_pretrained()`

```python
model_id = "Efficient-Large-Model/Sana_1600M_1024px_diffusers"

pipe = SanaPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16
)
```

이 코드의 의미는:

> "Hugging Face Hub에 저장되어 있는 SANA의 사전학습된 모델을 가져와서 사용할 준비를 해라."

입니다.

여기서 반드시 이해해야 하는 개념은 **사전학습 모델(Pretrained Model)**입니다.

이미 대규모 데이터로 학습이 끝난 모델을 가져와 **추론에 사용하는 것**입니다.

---

# 3. 프롬프트와 이미지 생성

핵심 코드입니다.

```python
positive_prompt = (
    "A watercolor painting of a red fox sitting on a forest floor, "
    "vibrant autumn colors"
)
```

그리고

```python
result = pipe(
    prompt=positive_prompt,
    guidance_scale=4.5,
    num_inference_steps=20,
    height=1024,
    width=1024,
    generator=generator,
)
```

여기에서 각각의 역할을 이해해야 합니다.

| 코드                    | 의미                   |
| --------------------- | -------------------- |
| `prompt`              | 생성하고 싶은 이미지의 조건      |
| `guidance_scale`      | 텍스트 조건을 얼마나 강하게 반영할지 |
| `num_inference_steps` | 노이즈 제거 단계 수          |
| `height`, `width`     | 생성 이미지 크기            |
| `generator`           | 난수 및 시드 제어           |

---

# 4. Seed가 중요한 이유

실습에서 다음과 같이 작성했습니다.

```python
seeds = [42, 777]

for seed in seeds:
    generator = torch.Generator(device=device).manual_seed(seed)
```

왜 서로 다른 seed를 사용할까요?

디퓨전 모델은 랜덤 노이즈에서 시작합니다.

```text
Seed = 42
   ↓
Random Noise A
   ↓
Image A

Seed = 777
   ↓
Random Noise B
   ↓
Image B
```

따라서 같은 프롬프트라도 seed가 다르면 서로 다른 결과를 만들 수 있습니다.

반대로

```python
manual_seed(42)
```

를 계속 사용하면 동일한 조건에서 거의 같은 결과를 얻을 수 있습니다.

### 교육할 때 강조할 부분

**Seed = 재현성(Reproducibility)**

라고 설명하면 이해하기 쉽습니다.

> "AI 생성 결과를 다시 똑같이 만들어보고 싶다면 랜덤성을 통제해야 한다."

---

# 5. `guidance_scale`과 `num_inference_steps`

학생들이 자주 혼동할 부분입니다.

### `guidance_scale`

```python
guidance_scale=4.5
```

대략적으로

> **"내가 입력한 프롬프트를 얼마나 강하게 따라갈 것인가?"**

와 관련됩니다.

너무 낮으면 프롬프트 반영이 약해질 수 있고, 너무 높다고 항상 좋은 결과가 나오는 것은 아닙니다.

---

### `num_inference_steps`

```python
num_inference_steps=20
```

노이즈를 제거하는 과정의 횟수입니다.

개념적으로:

```text
Step 1 → Step 2 → Step 3 → ... → Step 20
```

일반적으로 단계가 많아지면 품질이나 안정성이 좋아질 가능성이 있지만 **실행 시간이 증가**합니다.

따라서 둘은 완전히 다른 개념입니다.

> `guidance_scale` → **프롬프트 조건을 얼마나 강하게 반영?**

> `num_inference_steps` → **노이즈 제거를 몇 단계 수행?**

---

# 6. 반드시 확인할 부분 — GPU 메모리

SANA는 상당히 큰 모델입니다.

실습 코드에는

```python
pipe.to(device)
```

가 있습니다.

GPU를 사용하는 경우 모델 전체를 GPU로 이동시킵니다.

GPU 메모리가 부족하다면 실습 파일에서 설명한 것처럼

```python
pipe.enable_model_cpu_offload()
```

를 사용할 수 있습니다.

단,

```python
pipe.to(device)
pipe.enable_model_cpu_offload()
```

를 **동시에 사용하는 것은 주의**해야 합니다.

---

# 7. Step 2 — CLIP으로 생성 이미지 평가

여기서 실습의 중요한 전환이 일어납니다.

Step 1에서는

> **AI가 이미지를 생성**

했습니다.

Step 2에서는

> **AI가 생성된 이미지를 평가**

합니다.

---

# 8. CLIP의 핵심 개념

CLIP은 이미지와 텍스트를 각각 벡터로 변환합니다.

```text
이미지
 ↓
Image Encoder
 ↓
이미지 벡터
       ↘
        유사도 계산
       ↗
텍스트 벡터
 ↑
Text Encoder
 ↑
텍스트
```

즉,

```text
"수채화 여우"
"수채화 강아지"
"유화 여우"
"사진 속 여우"
```

와 이미지 사이의 의미적 유사도를 비교할 수 있습니다.

---

# 9. CLIP 코드에서 가장 중요한 부분

```python
inputs = processor(
    text=labels,
    images=image,
    return_tensors="pt",
    padding=True
).to(device)
```

여기서 `processor`가 중요한 역할을 합니다.

이미지와 텍스트를 CLIP이 처리할 수 있는 형태로 변환합니다.

즉,

```text
사람이 이해하는 이미지/문장
        ↓
     Processor
        ↓
CLIP이 처리할 수 있는 Tensor
```

입니다.

---

## 9-1. `logits_per_image`

```python
outputs = clip_model(**inputs)

logits_per_image = outputs.logits_per_image
```

여기서 이미지와 각 텍스트 사이의 유사도 점수를 얻습니다.

예를 들어 개념적으로:

```text
이미지
 ↓
 ├─ "watercolor fox"  → 8.2
 ├─ "watercolor dog"  → 2.1
 ├─ "oil painting fox" → 6.4
 └─ "photo fox"       → 3.8
```

이런 식으로 비교할 수 있습니다.

---

# 10. Softmax의 역할

```python
probs = logits_per_image.softmax(dim=1)
```

`logits`는 그냥 점수입니다.

Softmax를 통과시키면 이를 확률처럼 해석할 수 있는 값으로 변환합니다.

개념적으로:

```text
Logits
[8.2, 2.1, 6.4, 3.8]

       ↓ Softmax

확률
[0.80, 0.001, 0.15, 0.04]
```

그리고

```python
best_idx = logits_per_image.argmax(dim=1).item()
```

을 이용해 가장 높은 점수를 가진 레이블을 찾습니다.

---

# 11. 여기서 반드시 주의할 점

CLIP의 결과를 **절대적인 정답이라고 생각하면 안 됩니다.**

CLIP은

> "이 이미지가 이 텍스트와 얼마나 잘 어울리는가?"

를 평가하는 모델입니다.

즉,

**CLIP score = 절대적인 이미지 품질 점수**

가 아닙니다.

이 실습에서는 **여러 후보 문장 중 어느 것이 이미지와 가장 의미적으로 가까운지**를 비교하는 용도로 사용하는 것입니다.

---

# 12. Step 3 — ResNet-50과 비교

이 단계가 이 실습에서 **AI 모델의 목적 차이를 이해하는 핵심 부분**입니다.

동일한 이미지를

```text
                ┌── CLIP
이미지 ─────────┤
                └── ResNet-50
```

에 각각 넣습니다.

하지만 두 모델의 질문이 다릅니다.

### CLIP

> "이 이미지가 어떤 텍스트 설명과 가장 잘 어울리는가?"

### ResNet-50

> "이 이미지가 내가 학습한 ImageNet 1000개 클래스 중 어디에 해당하는가?"

---

# 13. ResNet-50 전처리

코드:

```python
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])
```

이 부분은 매우 중요합니다.

사전학습된 ResNet-50은 **ImageNet 학습 당시의 입력 전처리 방식과 유사한 형태**로 데이터를 넣어줘야 합니다.

특히:

```python
Normalize(
    mean=[0.485, 0.456, 0.406],
    std=[0.229, 0.224, 0.225]
)
```

를 빼먹으면 사전학습 모델이 기대하는 입력 분포와 달라질 수 있습니다.

---

# 14. `unsqueeze(0)`도 중요

```python
img_tensor = preprocess(image).unsqueeze(0)
```

이미지 하나를 전처리하면 일반적으로

```text
[C, H, W]
```

형태입니다.

하지만 CNN은 일반적으로 배치 차원을 포함한

```text
[B, C, H, W]
```

형태를 기대합니다.

따라서

```python
unsqueeze(0)
```

을 사용하면

```text
[C, H, W]
      ↓
[1, C, H, W]
```

가 됩니다.

여기서 `1`은 **배치 크기 1**입니다.

---

# 15. ResNet과 CLIP의 차이를 반드시 이해

| 항목      | CLIP          | ResNet-50             |
| ------- | ------------- | --------------------- |
| 입력      | 이미지 + 텍스트     | 이미지                   |
| 핵심 목적   | 이미지-텍스트 의미 비교 | 이미지 분류                |
| 학습      | 이미지-텍스트 대조학습  | ImageNet 분류           |
| 클래스     | 텍스트로 자유롭게 지정  | 학습된 ImageNet 클래스      |
| 스타일 비교  | 가능            | 직접적인 스타일 클래스가 없으면 어려움 |
| 대표적인 활용 | Zero-shot 평가  | 이미지 분류                |

따라서 **CLIP이 무조건 ResNet보다 좋은 모델이라는 의미가 아닙니다.**

**문제의 목적이 다릅니다.**

이 부분을 학생들에게 강조하는 것이 좋습니다.

---

# 16. Step 4 — 생성 데이터를 이용한 전이학습

이제 실습의 가장 중요한 부분으로 넘어갑니다.

앞에서는 SANA가 이미지를 생성했습니다.

이번에는 그 이미지를 **학습 데이터로 사용합니다.**

```text
SANA
 ↓
Fox 이미지 생성
Dog 이미지 생성
 ↓
data/train
 ├── fox
 │    ├── fox_0.png
 │    └── fox_1.png
 └── dog
      ├── dog_0.png
      └── dog_1.png
```

즉, **생성 AI가 머신러닝 학습 데이터를 만들어주는 구조**입니다.

---

# 17. `ImageFolder`의 핵심 원리

```python
train_dataset = ImageFolder(
    "data/train",
    transform=train_transforms
)
```

폴더 이름 자체가 클래스가 됩니다.

```text
data/train/
    fox/
    dog/
```

그러면 `ImageFolder`가 자동으로

```text
fox → 0
dog → 1
```

같은 클래스 인덱스를 만들어줍니다.

따라서 이미지 분류에서 **폴더 구조가 매우 중요**합니다.

---

# 18. Train/Test 데이터 분리가 중요한 이유

실습에서는:

```text
data/train/
data/test/
```

를 별도로 생성합니다.

그리고 seed도 다릅니다.

```python
train_seeds = [42, 777]
test_seeds = [2024, 3000]
```

이것은 중요한 개념입니다.

```text
Train
↓
모델이 학습

Test
↓
학습에 사용하지 않음
↓
모델의 일반화 성능 평가
```

입니다.

---

# 19. 데이터 증강

학습 데이터에는:

```python
train_transforms = transforms.Compose([
    transforms.RandomResizedCrop((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(...)
])
```

가 사용됩니다.

반면 테스트 데이터는:

```python
test_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(...)
])
```

입니다.

### 왜 다를까요?

훈련에서는

> **다양한 형태의 데이터를 만들어 모델의 일반화 능력을 높이기 위해**

Random Augmentation을 사용합니다.

테스트에서는

> **동일한 기준으로 공정하게 평가하기 위해**

랜덤 변형을 사용하지 않습니다.

이 차이는 반드시 이해해야 합니다.

---

# 20. ResNet-18 전이학습

핵심 코드는 다음입니다.

```python
model = models.resnet18(
    weights=models.ResNet18_Weights.IMAGENET1K_V1
)
```

이미 ImageNet으로 학습된 ResNet-18을 가져옵니다.

그 다음:

```python
for param in model.parameters():
    param.requires_grad = False
```

모든 기존 가중치를 고정합니다.

그리고:

```python
num_features = model.fc.in_features

model.fc = nn.Linear(
    num_features,
    len(train_dataset.classes)
)
```

마지막 출력층만 새로운 문제에 맞게 교체합니다.

---

# 21. 이것이 Linear Probing

전체 구조를 보면:

```text
Image
 ↓
ResNet-18
 ↓
[기존 Feature Extractor]
 ↓
고정된 가중치
 ↓
새로운 FC Layer
 ↓
Fox / Dog
```

입니다.

즉,

> **이미 학습된 ResNet의 특징 추출 능력은 그대로 사용하고, 마지막 분류기만 새로운 데이터에 맞춰 학습**

하는 것입니다.

이것이 **Linear Probing**입니다.

---

# 22. `requires_grad=False`의 의미

```python
for param in model.parameters():
    param.requires_grad = False
```

이것은

> "이 파라미터를 역전파로 업데이트하지 않겠다."

라는 의미입니다.

따라서 실제 학습되는 것은 새로 만든:

```python
model.fc
```

뿐입니다.

그리고 이것을 옵티마이저에서도 명확하게 합니다.

```python
optimizer = optim.SGD(
    model.fc.parameters(),
    lr=0.001,
    momentum=0.9
)
```

즉,

```text
ResNet 기존 층 → 학습 X
FC 층         → 학습 O
```

입니다.

---

# 23. Loss와 Optimizer

```python
criterion = nn.CrossEntropyLoss()
```

2개 이상의 클래스를 분류하는 문제이므로 `CrossEntropyLoss`를 사용합니다.

모델은:

```python
outputs = model(inputs)
```

를 통해 클래스별 **logit**을 출력합니다.

예:

```text
Fox : 2.8
Dog : 0.7
```

그리고 Cross Entropy Loss가 실제 정답과 비교하여 손실을 계산합니다.

```python
loss = criterion(outputs, labels)
```

---

# 24. 학습 루프의 핵심 구조

실습 코드의 다음 5줄은 PyTorch 학습의 핵심입니다.

```python
optimizer.zero_grad()

outputs = model(inputs)

loss = criterion(outputs, labels)

loss.backward()

optimizer.step()
```

순서대로 보면:

```text
① 기존 gradient 제거
       ↓
② Forward
       ↓
③ Loss 계산
       ↓
④ Backpropagation
       ↓
⑤ Weight 업데이트
```

이 순서는 반드시 익혀두는 것이 좋습니다.

---

# 25. 마지막 — Test Accuracy

```python
model.eval()
```

평가 모드로 전환합니다.

그리고:

```python
with torch.no_grad():
```

를 사용합니다.

이는 테스트 과정에서 gradient 계산이 필요 없기 때문입니다.

마지막으로:

```python
predicted = outputs.argmax(dim=1)
```

가 가장 높은 logit을 가진 클래스를 예측값으로 선택합니다.

그리고:

```python
correct += (predicted == labels).sum().item()
```

으로 맞춘 개수를 계산합니다.

최종적으로:

```python
100 * correct / total
```

을 통해 정확도를 계산합니다.

---

# 26. 이 실습에서 반드시 기억해야 할 핵심 개념

학생들에게 다음 정도를 핵심 학습 목표로 제시하면 좋습니다.

### ① Diffusion Model

> **노이즈에서 시작하여 점진적으로 노이즈를 제거하면서 이미지를 생성한다.**

### ② Prompt Engineering

> **생성 모델에게 원하는 결과를 얻기 위해 입력 프롬프트를 설계한다.**

### ③ Seed

> **랜덤성을 제어하여 생성 결과의 재현성을 확보한다.**

### ④ CLIP

> **이미지와 텍스트를 동일한 임베딩 공간에서 비교한다.**

### ⑤ ResNet

> **학습된 클래스 집합을 기준으로 이미지를 분류한다.**

### ⑥ Transfer Learning

> **사전학습 모델의 지식을 새로운 문제에 활용한다.**

### ⑦ Linear Probing

> **기존 모델을 고정하고 마지막 분류층만 학습한다.**

### ⑧ Synthetic Data

> **생성 모델이 만든 인공 데이터를 실제 모델 학습에 활용한다.**

---

# 27. 실습에서 특히 주의해야 할 사항

## ⚠️ 1. GPU 메모리

SANA 1600M 모델을 사용하므로 GPU 메모리 부족이 발생할 수 있습니다.

필요하면:

```python
pipe.enable_model_cpu_offload()
```

을 고려합니다.

---

## ⚠️ 2. `float16`

```python
torch_dtype=torch.float16
```

은 GPU 메모리를 줄이는 데 도움이 되지만, 실습 코드에서도 언급했듯 특정 프롬프트와 seed 조합에서 수치 문제가 발생하여 **검은 이미지가 생성될 가능성**이 있습니다.

검은 이미지가 나오면 seed를 변경해 보는 것이 좋습니다.

---

## ⚠️ 3. 모델마다 전처리가 다르다

특히 ResNet의:

```python
Resize
ToTensor
Normalize
```

를 임의로 변경하면 사전학습 모델의 성능에 영향을 줄 수 있습니다.

---

## ⚠️ 4. Train/Test 전처리를 구분

```text
Train → Random augmentation 사용
Test  → Random augmentation 사용하지 않음
```

을 기억해야 합니다.

---

## ⚠️ 5. `model.train()`과 `model.eval()`

학습:

```python
model.train()
```

평가:

```python
model.eval()
```

를 구분해야 합니다.

특히 BatchNorm, Dropout 등이 있는 모델에서는 중요한 차이입니다.

---

## ⚠️ 6. `torch.no_grad()`

추론/평가에서는:

```python
with torch.no_grad():
```

를 사용하면 불필요한 gradient 계산을 방지할 수 있습니다.

---

## ⚠️ 7. 합성 데이터가 항상 좋은 데이터는 아니다

이 실습에서 상당히 중요한 확장 개념입니다.

```text
SANA
 ↓
합성 이미지
 ↓
ResNet 학습
```

이라고 해서 무조건 좋은 모델이 만들어지는 것은 아닙니다.

생성 이미지 자체에 문제가 있다면:

```text
잘못된 생성 데이터
      ↓
잘못된 학습
      ↓
모델 성능 저하
```

가 발생할 수 있습니다.

즉,

> **Synthetic Data의 품질이 모델의 품질에 영향을 준다.**

는 점을 학생들이 생각해볼 필요가 있습니다.

---

# 28. 이 실습의 가장 중요한 교육적 포인트

이 실습을 단순히

> "SANA 사용법 → CLIP 사용법 → ResNet 사용법"

으로 가르치기보다는 다음과 같이 연결해서 설명하는 것이 좋습니다.

```text
                    생성 AI
                      │
                 ┌────▼────┐
                 │   SANA  │
                 └────┬────┘
                      │
                이미지 생성
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
       CLIP 평가              학습 데이터
          │                       │
 이미지-텍스트 평가          Synthetic Dataset
          │                       │
          ▼                       ▼
      ResNet-50              ResNet-18
       비교 분석              Transfer Learning
                                  │
                                  ▼
                            Fox / Dog 분류
```

즉, **하나의 생성 모델이 단순히 이미지를 만들어내는 데서 끝나는 것이 아니라, 생성한 데이터를 다시 다른 AI 모델의 학습에 사용할 수 있다**는 것이 이 실습의 핵심입니다.

---

## 한 문장으로 정리하면

> **이 실습은 SANA로 이미지를 생성하고, CLIP으로 생성 결과를 의미적으로 평가한 뒤, ResNet-50과 비교하고, 마지막으로 생성된 이미지를 합성 데이터로 활용하여 ResNet-18을 전이학습하는 생성 AI → 평가 AI → 분류 AI의 전체 파이프라인 실습입니다.**

그리고 학생들이 실습을 마친 뒤 최소한 다음 질문에 답할 수 있으면 실습의 핵심을 이해한 것입니다.

1. **Diffusion 모델은 어떻게 이미지를 생성하는가?**
2. **Seed를 왜 사용하는가?**
3. **CLIP은 이미지를 어떻게 평가하는가?**
4. **CLIP과 ResNet의 근본적인 차이는 무엇인가?**
5. **왜 ResNet-18의 기존 가중치를 freeze하는가?**
6. **Linear Probing이란 무엇인가?**
7. **생성된 이미지를 왜 학습 데이터로 사용할 수 있는가?**
8. **Synthetic Data를 사용할 때 어떤 문제가 발생할 수 있는가?**
