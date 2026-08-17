업로드해 주신 실습 자료를 기준으로 보면, **마지막 섹션의 Vision Transformer(ViT) 실습은 “ViT를 직접 학습시키는 실습”이라기보다, Hugging Face에서 CIFAR-10에 맞게 사전 학습된 ViT를 가져와 전처리 → 추론 → 결과 시각화까지 경험하는 실습**으로 구성되어 있습니다. 

특히 이 부분은 **ResNet 전이학습과 ViT 전이학습의 차이를 보여주는 실습**으로 설명하면 입문자에게 좋습니다.

---

# 1. 실습 전체 흐름

현재 자료의 ViT 실습은 다음 순서입니다.

```text
CIFAR-10 테스트 데이터
        ↓
Hugging Face datasets
        ↓
PIL Image
        ↓
ViTImageProcessor
        ↓
pixel_values Tensor
        ↓
ViTForImageClassification
        ↓
logits
        ↓
argmax
        ↓
CIFAR-10 클래스
```

실습에서는 다음 모델을 사용합니다.

```python
model_name = "nateraw/vit-base-patch16-224-cifar10"
```

즉, **일반적인 ImageNet ViT를 가져와서 CIFAR-10에 새로 학습하는 것이 아니라, 이미 CIFAR-10에 맞게 Fine-tuning된 ViT 모델을 가져와 추론**합니다. 자료에서도 이 모델이 ImageNet-21k 사전학습 후 CIFAR-10에 Fine-tuning된 모델이라고 설명하고 있습니다. 

---

# 2. Vision Transformer란?

ViT의 핵심은 이미지를 CNN처럼 직접 convolution하는 것이 아니라 **이미지를 작은 Patch로 잘라 Transformer의 입력인 Token처럼 처리한다는 것**입니다.

예를 들어 실습의 ViT는:

```text
224 × 224 이미지
       ↓
16 × 16 Patch로 분할
       ↓
14 × 14 = 196개 Patch
       ↓
Patch Embedding
       ↓
Position Embedding
       ↓
[CLS] + 196개 Patch Token
       ↓
Transformer Encoder
       ↓
[CLS] Token
       ↓
Classification Head
       ↓
10개 클래스
```

자료에서도 224×224 이미지를 16×16 패치로 나누면 **196개의 패치**가 만들어진다고 설명합니다. 

---

# 3. CNN과 ViT의 가장 중요한 차이

실습에서는 ResNet과 ViT를 비교해서 이해하면 좋습니다.

|         | ResNet                   | ViT                 |
| ------- | ------------------------ | ------------------- |
| 핵심      | Convolution              | Self-Attention      |
| 입력 처리   | 이미지 전체를 Feature Map으로 처리 | 이미지를 Patch로 분할      |
| 기본 단위   | Pixel/Feature Map        | Patch Token         |
| 특징 관계   | 주로 지역적인 특징부터 학습          | Patch 간 전역 관계 학습    |
| 구조      | CNN                      | Transformer Encoder |
| 대표적인 장점 | 상대적으로 적은 데이터에서도 강함       | 대규모 데이터에서 강력        |
| 대표적인 단점 | 전역적인 관계 학습에 한계           | 많은 데이터와 계산량 필요      |

자료에서도 CNN은 **지역적 패턴**, ViT는 **Self-Attention을 통한 전역적 관계**를 학습하는 구조로 비교하고 있습니다. 

---

# 4. 실습에서 사용하는 핵심 라이브러리

이번 ViT 부분에서 중요한 라이브러리는 크게 3개입니다.

```python
from datasets import load_dataset

from transformers import (
    ViTImageProcessor,
    ViTForImageClassification
)
```

각각의 역할을 구분해서 설명하는 것이 좋습니다.

---

## 4-1. `datasets`

Hugging Face의 **Datasets 라이브러리**입니다.

실습에서는:

```python
from datasets import load_dataset

dataset = load_dataset(
    'cifar10',
    split='test'
)
```

를 사용합니다. 

### `load_dataset()`

Hugging Face Hub에 등록된 데이터셋을 다운로드하고 `Dataset` 객체로 만들어 줍니다.

```python
dataset = load_dataset(
    "cifar10",
    split="test"
)
```

여기서:

* `"cifar10"` → 데이터셋 이름
* `split="test"` → 테스트 데이터만 사용

결과적으로:

```text
Dataset
 ├── img
 └── label
```

형태가 됩니다.

자료에서는 10,000개의 테스트 이미지와 `img`, `label` 두 개의 feature가 존재하는 것으로 나타납니다. 

---

# 5. `dataset.features`

이번 실습에서 상당히 중요한 부분입니다.

```python
labels = dataset.features['label'].names
```

자료에서도 이 방법으로 CIFAR-10의 클래스 이름을 가져옵니다. 

결과:

```python
[
    'airplane',
    'automobile',
    'bird',
    'cat',
    'deer',
    'dog',
    'frog',
    'horse',
    'ship',
    'truck'
]
```

예를 들어:

```python
dataset[0]["label"]
```

결과가:

```text
3
```

이라면

```python
labels[3]
```

을 통해

```text
cat
```

으로 변환할 수 있습니다.

즉,

```text
정수 Label
   ↓
labels 리스트
   ↓
사람이 이해할 수 있는 클래스 이름
```

입니다.

---

# 6. `ViTImageProcessor`

ViT 실습에서 **가장 중요한 클래스 중 하나**입니다.

```python
from transformers import ViTImageProcessor
```

그리고:

```python
image_processor = ViTImageProcessor.from_pretrained(model_name)
```

을 사용합니다. 

### 역할

쉽게 말하면:

> **"이 이미지를 이 ViT 모델이 먹을 수 있는 형태로 변환해주는 전처리기"**

입니다.

예를 들어 원본 CIFAR-10 이미지는:

```text
32 × 32 × 3
```

입니다.

하지만 ViT 모델은:

```text
224 × 224 × 3
```

형태의 입력을 기대합니다.

따라서 `ViTImageProcessor`가 모델이 요구하는 방식에 맞춰 이미지 전처리를 수행합니다.

---

# 7. `from_pretrained()`

Hugging Face에서 매우 중요한 공통 메소드입니다.

```python
ViTImageProcessor.from_pretrained(model_name)
```

또는

```python
ViTForImageClassification.from_pretrained(model_name)
```

형태로 사용합니다.

의미는:

> **이미 학습되어 있는 모델 또는 해당 모델에 필요한 설정을 Hugging Face Hub에서 가져온다.**

입니다.

자료에서도 Hugging Face의 주요 기능으로 `from_pretrained()`를 소개하고 있습니다. 

---

# 8. `ViTForImageClassification`

두 번째 핵심 클래스입니다.

```python
from transformers import ViTForImageClassification
```

그리고:

```python
vit_model = ViTForImageClassification.from_pretrained(
    model_name
)
```

합니다. 

이 클래스는 단순한 ViT Encoder만 제공하는 것이 아니라:

```text
ViT Encoder
      ↓
Classification Head
      ↓
Class logits
```

구조를 가지고 있습니다.

실습에서 출력된 구조를 보면:

```text
ViTForImageClassification
 ├── vit
 │    ├── embeddings
 │    ├── encoder
 │    │    └── 12 × ViTLayer
 │    └── layernorm
 │
 └── classifier
      └── Linear(768 → 10)
```

입니다. 

즉 이 모델은 최종적으로 **10개의 CIFAR-10 클래스를 분류**하도록 되어 있습니다.

---

# 9. ViT의 구조를 코드와 연결해서 보기

실습 모델을 보면:

```text
patch_embeddings
    ↓
Transformer Encoder
    ↓
LayerNorm
    ↓
classifier
```

입니다.

특히 다음 부분이 중요합니다.

```text
Conv2d(
    3,
    768,
    kernel_size=(16,16),
    stride=(16,16)
)
```



여기서 convolution이 **일반적인 CNN의 특징 추출용 convolution과는 목적이 다릅니다.**

ViT에서는 이를 이용해서:

```text
224 × 224 이미지
       ↓
16 × 16 Patch
       ↓
Patch Embedding
       ↓
768차원 Vector
```

로 변환합니다.

즉:

> **Patch 하나를 하나의 Token처럼 만드는 과정**

이라고 이해하면 됩니다.

---

# 10. 실제 추론 과정

실습의 핵심 코드는 다음 부분입니다.

```python
inputs = image_processor(
    images=sample_images,
    return_tensors="pt"
)
```



여기서 매우 중요한 것은:

```python
sample_images
```

가 PIL Image라는 점입니다.

즉:

```text
PIL Image
   ↓
ViTImageProcessor
   ↓
Tensor
```

가 됩니다.

---

# 11. `return_tensors="pt"`

이것도 자주 나오는 Hugging Face 문법입니다.

```python
return_tensors="pt"
```

의 의미는:

> 결과를 **PyTorch Tensor** 형태로 반환하라.

입니다.

다른 예로:

```python
return_tensors="tf"
```

라면 TensorFlow Tensor가 됩니다.

따라서 이번 실습에서는:

```python
return_tensors="pt"
```

가 필요합니다.

---

# 12. `inputs`의 정체

다음 코드:

```python
inputs = image_processor(
    images=sample_images,
    return_tensors="pt"
)
```

결과는 일반적인 하나의 Tensor라기보다는 **딕셔너리 형태**입니다.

개념적으로:

```python
{
    "pixel_values": ...
}
```

형태입니다.

그래서:

```python
inputs = {
    k: v.to(device)
    for k, v in inputs.items()
}
```

를 통해 Tensor들을 GPU로 이동시킵니다. 

---

# 13. `vit_model(**inputs)`

이 부분은 처음 보는 학습자들이 많이 헷갈립니다.

```python
outputs = vit_model(**inputs)
```

여기서 `**inputs`는 Python의 **Dictionary Unpacking**입니다.

예를 들어:

```python
inputs = {
    "pixel_values": tensor
}
```

라면:

```python
vit_model(**inputs)
```

는 사실상:

```python
vit_model(
    pixel_values=tensor
)
```

와 같은 의미입니다.

---

# 14. `outputs.logits`

ViT 모델의 출력에서 가장 중요한 값입니다.

```python
outputs.logits
```

입니다.

예를 들어 5장의 이미지를 넣으면:

```text
outputs.logits

shape = (5, 10)
```

개념적으로:

```text
이미지 1 → [10개 클래스 점수]
이미지 2 → [10개 클래스 점수]
이미지 3 → [10개 클래스 점수]
...
```

입니다.

즉:

> **각 이미지가 10개 클래스에 속할 가능성을 판단하기 위한 점수**

라고 설명하면 됩니다.

---

# 15. `argmax(dim=1)`

실습에서는:

```python
predicted_class_idxs = (
    outputs.logits.argmax(dim=1)
    .cpu()
    .numpy()
)
```

를 사용합니다. 

예를 들어:

```text
logits

image 1 → [1.2, 0.4, -1.2, 8.5, ...]
```

라면 가장 큰 값:

```text
8.5
```

의 위치가 `3`이라고 할 때:

```python
argmax(dim=1)
```

결과는:

```text
3
```

입니다.

그리고:

```python
labels[3]
```

을 통해:

```text
cat
```

이 됩니다.

---

# 16. ViT 데이터 전처리에서 가장 중요한 주의점

여기가 **실습 자료에 추가하면 상당히 좋은 내용**입니다.

## ① CIFAR-10은 32×32인데 ViT는 224×224

원본:

```text
CIFAR-10
32 × 32
```

ViT:

```text
224 × 224
```

따라서 단순히 모델에 넣을 수 없습니다.

이번 실습에서는 `ViTImageProcessor`가 이 문제를 해결합니다.

```text
32×32
 ↓
Resize
 ↓
224×224
 ↓
Normalize
 ↓
Tensor
```

---

# 17. 그런데 단순 Resize에는 문제가 있다

여기서 교육적으로 꼭 짚어줄 부분이 있습니다.

```text
32×32
   ↓ Resize
224×224
```

라고 해서 **새로운 정보가 생기는 것은 아닙니다.**

원래 CIFAR-10 자체가 매우 작은 이미지이기 때문에:

```text
32×32
```

의 정보를 크게 확대해서:

```text
224×224
```

로 만드는 것입니다.

따라서:

> **입력 크기는 ViT에 맞출 수 있지만, 이미지의 정보량 자체가 증가하는 것은 아니다.**

이 점이 중요합니다.

실습 자료에서도 CIFAR-10이 32×32의 저해상도 데이터이므로 실제 적용에서는 더 높은 해상도의 데이터를 사용하는 것이 좋다고 명시하고 있습니다. 

---

# 18. 더 중요한 문제: Patch 크기

이번 모델은:

```text
patch_size = 16
image_size = 224
```

입니다.

따라서:

```text
224 / 16 = 14
```

이고,

```text
14 × 14 = 196
```

개의 Patch가 만들어집니다.

그런데 원본 CIFAR-10:

```text
32 × 32
```

에서 16×16 Patch를 사용한다면:

```text
32 / 16 = 2
```

밖에 안 됩니다.

즉 원본 이미지를 그대로 넣을 수 없고, 모델이 기대하는 224×224 입력으로 맞춰야 합니다.

---

# 19. ViT에서는 데이터 전처리가 CNN보다 더 중요하다

특히 **Pretrained ViT**를 사용할 때 다음 4가지를 반드시 확인해야 합니다.

### ① Image Size

```text
224 × 224인가?
```

### ② Normalization

```text
어떤 mean/std를 사용했는가?
```

### ③ Color Channel

```text
RGB인가?
```

### ④ 데이터 형식

```text
PIL Image인가?
Tensor인가?
```

Pretrained 모델을 사용할 때는 **모델이 학습될 당시 사용했던 전처리와 가능한 한 동일하게 맞추는 것**이 중요합니다.

이번 실습에서는 이 역할을 `ViTImageProcessor`가 담당합니다.

---

# 20. `ViTImageProcessor`를 사용하는 것이 좋은 이유

직접:

```python
transforms.Resize(...)
transforms.ToTensor(...)
transforms.Normalize(...)
```

를 작성할 수도 있지만 pretrained 모델에서는 실수할 가능성이 있습니다.

예를 들어:

```python
mean = ...
std = ...
```

를 잘못 사용하면 모델의 입력 분포가 달라집니다.

그래서:

```python
image_processor = ViTImageProcessor.from_pretrained(model_name)
```

처럼 **해당 모델에 연결된 Processor를 사용하는 것이 안전합니다.**

즉:

> **모델만 가져오는 것이 아니라 모델에 맞는 전처리 설정도 함께 가져온다.**

라고 설명하면 좋습니다.

---

# 21. ResNet 실습과 ViT 실습의 중요한 차이

이번 자료에서는 앞부분의 ResNet 실습과 마지막 ViT 실습을 이렇게 비교하면 좋습니다.

|       | ResNet                        | ViT                       |
| ----- | ----------------------------- | ------------------------- |
| 라이브러리 | torchvision                   | Hugging Face Transformers |
| 모델    | ResNet18                      | ViT                       |
| 학습    | 직접 Linear Probing/Fine-tuning | 이미 Fine-tuning된 모델 사용     |
| 데이터   | torchvision CIFAR10           | HF datasets CIFAR10       |
| 전처리   | torchvision.transforms        | ViTImageProcessor         |
| 입력    | Tensor                        | Processor가 Tensor로 변환     |
| 출력    | Tensor                        | ModelOutput의 `logits`     |
| 목적    | 전이학습 과정 학습                    | pretrained ViT 추론 경험      |

실습 자료 자체도 Step 1·2에서는 ResNet-18을 학습하고, Step 3에서는 Hugging Face ViT를 **Inference**하는 구성입니다. 

---

# 22. 실습에서 특히 주의할 데이터 문제

교육할 때 다음을 강조하면 좋습니다.

### ① Train/Test 전처리 구분

학습 데이터:

```text
Resize
+ Augmentation
+ Normalize
```

테스트 데이터:

```text
Resize
+ Normalize
```

테스트 데이터에는 RandomCrop, RandomFlip 같은 랜덤 증강을 적용하면 안 됩니다.

자료에서도 테스트 데이터에는 증강을 적용하지 않는다고 명시하고 있습니다. 

---

### ② Label mapping 확인

모델의 출력:

```text
0 ~ 9
```

와 사람이 보는:

```text
airplane
automobile
...
```

의 매핑이 정확해야 합니다.

이번 실습에서는:

```python
labels = dataset.features['label'].names
```

을 사용합니다. 

---

### ③ Model과 Input의 Device 일치

모델:

```python
vit_model.to(device)
```

입력:

```python
inputs = {
    k: v.to(device)
    for k, v in inputs.items()
}
```

둘 다 GPU라면:

```text
Model → GPU
Input → GPU
```

여야 합니다.

CPU/GPU가 서로 다르면 오류가 발생합니다.

---

### ④ `eval()`과 `no_grad()`

추론에서는:

```python
vit_model.eval()

with torch.no_grad():
    outputs = vit_model(**inputs)
```

형태가 좋습니다.

`no_grad()`는 추론에 필요 없는 gradient 계산을 하지 않게 해서 메모리와 계산량을 줄입니다.

현재 실습 코드에는 `no_grad()`가 적용되어 있습니다. 

---

# 23. 이번 실습에서 한 가지 특히 주의할 점

현재 실습의 제목은 **"Vision Transformer Inference"**입니다.

따라서 학습자에게:

> "ViT를 학습했다."

라고 설명하면 정확하지 않습니다.

정확하게는:

> **"CIFAR-10에 Fine-tuning된 pretrained ViT를 가져와 CIFAR-10 테스트 이미지에 대해 추론했다."**

입니다.

실제로 코드에서도:

```python
ViTForImageClassification.from_pretrained(model_name)
```

으로 이미 학습된 모델을 가져오고 별도의 `loss.backward()`나 `optimizer.step()`이 없습니다. 

---

# 24. 실습 자료에 추가하면 좋은 "ViT 데이터 전처리 체크리스트"

교육용으로는 다음 정도를 별도 박스로 넣으면 좋겠습니다.

| 확인 항목      | 확인 내용                       |
| ---------- | --------------------------- |
| 이미지 크기     | 모델이 요구하는 Image Size 확인      |
| Patch Size | 모델의 Patch Size 확인           |
| Channel    | RGB 3채널인지 확인                |
| Resize     | Processor 또는 모델 요구사항에 맞게 변환 |
| Normalize  | pretrained 모델의 mean/std 사용  |
| Image Type | PIL Image / Tensor 확인       |
| Batch      | 여러 이미지를 Batch로 구성           |
| Label      | label index ↔ class name 확인 |
| Device     | model과 input의 device 일치     |
| Evaluation | `eval()` + `no_grad()` 사용   |

---

# 25. 입문자에게는 이렇게 설명하면 가장 이해하기 쉽습니다

ViT 전체를 한 문장으로 표현하면:

> **"ViT는 이미지를 작은 조각(Patch)으로 잘라서 각각을 하나의 단어(Token)처럼 생각하고, Transformer의 Self-Attention으로 이미지 전체의 관계를 학습하는 모델이다."**

그리고 이번 실습은:

> **"이미 CIFAR-10을 학습한 ViT를 가져와서, CIFAR-10 이미지를 모델이 이해할 수 있는 형태로 전처리하고, 예측 결과를 확인하는 실습이다."**

라고 정리하면 됩니다.

### 핵심 코드만 뽑으면

```python
# 1. 데이터셋
dataset = load_dataset("cifar10", split="test")

# 2. 클래스 이름
labels = dataset.features["label"].names

# 3. pretrained ViT
model_name = "nateraw/vit-base-patch16-224-cifar10"

image_processor = ViTImageProcessor.from_pretrained(model_name)

vit_model = ViTForImageClassification.from_pretrained(
    model_name
)

# 4. 이미지 전처리
inputs = image_processor(
    images=sample_images,
    return_tensors="pt"
)

# 5. 추론
with torch.no_grad():
    outputs = vit_model(**inputs)

# 6. 가장 높은 점수의 클래스 선택
predicted = outputs.logits.argmax(dim=1)
```

이 코드에서 학습자가 반드시 이해해야 하는 핵심은 **`load_dataset → ViTImageProcessor → ViTForImageClassification → logits → argmax`**의 흐름입니다.

참고로 현재 실습 자료에서는 `transformers==4.57.1`을 고정하고 있는데, 이는 자료 작성 당시 `ViTImageProcessor` 사용을 기준으로 한 버전 조건입니다. 

또 하나 중요한 점은, **ViT에서는 "모델 구조" 못지않게 "pretrained 모델이 기대하는 전처리"를 맞추는 것이 중요**하다는 것입니다. 이 부분을 ResNet 실습의 `transforms`와 비교해서 설명하면 교육 효과가 상당히 좋습니다.
