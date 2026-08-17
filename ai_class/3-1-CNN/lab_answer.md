프로젝트에 있는 두 노트북(문제/정답)을 대조해서 TODO 1~6을 전부 확인했습니다. 아래에 **개념 → 코드 채우는 법 → 데이터 크기 변화 → 주의할 점** 순서로 정리했습니다.

---

## TODO 1: `train_transform` / `test_transform` 구성

**무엇을 채워야 하나?**

```python
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean, std)
])

test_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean, std)
])
```

**알아야 할 개념**

- `transforms.Compose`: 여러 전처리 단계를 순서대로 묶어주는 파이프라인. 순서가 중요합니다 — `Resize → ToTensor → Normalize` 순서를 지켜야 합니다. (`Normalize`는 텐서에만 적용되므로 `ToTensor` 뒤에 와야 함)
- **왜 224×224로 리사이즈?** CIFAR-10 이미지는 32×32인데, ResNet-18은 ImageNet(224×224)으로 사전 학습됐습니다. 사전 학습된 가중치의 합성곱 필터가 학습한 "특징의 스케일"이 224 입력을 기준으로 최적화돼 있어서, 입력 크기를 맞춰줘야 전이 학습 효과를 제대로 살릴 수 있습니다.
- **왜 정규화(Normalize)?** 픽셀 값(0~255)을 그대로 넣으면 값의 범위가 커서 학습이 불안정합니다. 평균 0, 분산 1 근처로 맞춰주면 gradient가 안정적으로 흐릅니다. 코드에서 이미 `mean`, `std`를 CIFAR-10 학습 데이터 전체로 계산해뒀으니 그대로 사용하면 됩니다.

**데이터 크기 변화**

| 단계                  | shape                                                           |
| --------------------- | --------------------------------------------------------------- |
| 원본 (PIL Image)      | 32×32×3                                                       |
| `Resize((224,224))` | 224×224×3 (PIL)                                               |
| `ToTensor()`        | `[3, 224, 224]` (C,H,W 순서로 바뀌고, 0~255 → 0~1 스케일링) |
| `Normalize`         | `[3, 224, 224]` (값 범위만 바뀜, shape은 동일)                |

**> [ToTensor 내부 동작에 대해 알아보기](./to_tensor_dim.md)**

**주의할 점**

- `test_transform`에는 증강(augmentation)을 넣지 않습니다. 평가는 항상 같은 조건으로 재현 가능해야 하기 때문입니다.
- `mean`, `std`는 **학습 데이터**로만 계산해야 합니다(테스트 데이터 정보가 학습 과정에 섞이면 안 됨 — data leakage 방지).

---

## TODO 2: Linear Probing 설정 (분류층 교체 + 동결)

**무엇을 채워야 하나?**

```python
model.fc = nn.Linear(model.fc.in_features, 10)

for name, param in model.named_parameters():
    if "fc" not in name:
        param.requires_grad = False
```

**알아야 할 개념**

- `model.fc`: ResNet-18의 마지막 Fully Connected 층 이름입니다(`model` 출력에서 확인 가능). 원래 `nn.Linear(512, 1000)`(ImageNet 1000개 클래스)인데, `model.fc.in_features`로 입력 차원(512)을 그대로 가져오고 출력만 10으로 바꿔줍니다. 입력 차원을 하드코딩하지 않고 `in_features`로 가져오는 이유는 백본 구조가 바뀌어도 코드가 깨지지 않게 하기 위함입니다.
- `requires_grad = False`: PyTorch에서 파라미터가 gradient를 계산/저장하지 않게 만드는 스위치입니다. 이게 곧 "동결(freeze)"입니다. `"fc" not in name` 조건으로 `fc`가 아닌 모든 층만 False로 만들어 백본은 얼려두고, 새로 만든 `fc`는 기본값(`True`)을 그대로 유지해 학습 가능하게 둡니다.

**데이터(파라미터) 크기 변화**

- 기존 `fc`: `[1000, 512]` 가중치 → 새 `fc`: `[10, 512]` 가중치로 교체 (파라미터 개수 약 51만 → 5,130개)
- 학습 대상 파라미터 비율: 전체 약 1,100만 개 중 **fc층 약 5천 개(0.05% 미만)**만 학습됩니다 → 이래서 "Linear Probing"이 빠릅니다.

**주의할 점**

- 반드시 `model.fc = nn.Linear(...)`로 **새 층을 먼저 교체한 후** 동결 루프를 돌려야 합니다. 순서가 바뀌면 새 fc까지 얼어버릴 수 있습니다(코드는 이름 문자열로 걸러서 순서 상관없지만, 개념적으로는 "새 층 추가 → 나머지 동결" 흐름을 이해하는 게 중요).
- `.to(device)`는 파라미터 교체·동결 이후에 호출해야 새 레이어까지 GPU로 함께 옮겨집니다.

---

## TODO 3: 손실함수 / 옵티마이저 / 학습 루프

**무엇을 채워야 하나?**

```python
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.fc.parameters(), lr=0.001)

for xb, yb in trainloader:
    xb, yb = xb.to(device), yb.to(device)

    optimizer.zero_grad()          # 3.1
    outputs = model(xb)            # 3.2
    loss = criterion(outputs, yb)  # 3.3
    loss.backward()                # 3.4
    optimizer.step()               # 3.5
```

**알아야 할 개념 (왜 이 순서인가?)**

1. `optimizer.zero_grad()` — PyTorch는 gradient를 **누적**시킵니다. 초기화 안 하면 이전 배치의 gradient가 계속 더해져 학습이 망가집니다.
2. `outputs = model(xb)` — forward pass. 모델에 이미지를 넣어 클래스별 점수(logits)를 얻습니다. shape: `[256, 10]` (배치 256, 클래스 10개)
3. `loss = criterion(outputs, yb)` — `CrossEntropyLoss`는 내부적으로 softmax + NLL을 합친 것으로, 다중 클래스 분류의 표준 손실 함수입니다.
4. `loss.backward()` — 역전파로 각 파라미터에 대한 gradient를 계산합니다.
5. `optimizer.step()` — 계산된 gradient로 파라미터를 업데이트합니다. **이때 `requires_grad=False`인 파라미터는 gradient가 애초에 계산되지 않으므로 업데이트되지 않습니다.**

**핵심 포인트**: `optim.SGD(model.fc.parameters(), lr=0.001)`처럼 **옵티마이저에 전달하는 파라미터 자체를 `model.fc.parameters()`로 한정**하는 것도 동결의 또 다른 안전장치입니다. TODO 2의 `requires_grad=False`와 이중으로 "fc층만 학습"을 보장하는 셈입니다.

**데이터 크기 변화 (배치 흐름)**

- 입력 `xb`: `[256, 3, 224, 224]` → ResNet-18 통과 → `outputs`: `[256, 10]`
- `yb`(정답 레이블): `[256]` (정수 인덱스, one-hot 아님 — `CrossEntropyLoss`가 알아서 처리)

**주의할 점**

- `loss.backward()`를 두 번 연속 호출하면 gradient가 누적되어 에러 없이 잘못된 값이 나올 수 있음 → 매 배치마다 `zero_grad()` 필수.
- `model.train()`을 학습 루프 시작 전에 호출해야 BatchNorm/Dropout이 학습 모드로 동작합니다(평가 시엔 `model.eval()`).

---

## TODO 4: 데이터 증강 추가

**무엇을 채워야 하나?**

```python
train_transform_aug = transforms.Compose([
    transforms.RandomCrop(32, padding=4),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=mean, std=std)
])
```

**알아야 할 개념**

- `RandomCrop(32, padding=4)`: 원본 32×32 이미지에 상하좌우 4픽셀씩 패딩을 붙여 40×40으로 만든 뒤, 그중 무작위 32×32 영역을 잘라냅니다. 이렇게 하면 물체 위치가 살짝씩 달라진 이미지를 매 에포크 새로 생성 — 위치 변화에 강인한 모델을 만듭니다.
- `RandomHorizontalFlip(p=0.5)`: 50% 확률로 좌우 반전. 자동차, 동물 등은 좌우가 바뀌어도 같은 클래스이므로 자연스러운 증강입니다.
- **왜 32×32 상태에서 증강을 먼저 하고 그 다음 Resize(224,224)를 하나?** 원본 해상도(32×32)에서 Crop/Flip을 하는 게 계산이 가볍고, 원래 CIFAR-10 이미지의 패딩 비율(4/32)이 의미 있게 설계된 값이기 때문입니다. 224로 먼저 키운 뒤 크롭하면 패딩 비율의 의미가 달라지고 연산량도 커집니다.

**데이터 크기 변화**

```
32×32×3 → (padding 4) → 40×40×3 → (random crop) → 32×32×3 
→ (flip, shape 불변) → 32×32×3 → (resize) → 224×224×3 → (ToTensor) → [3,224,224]
```

→ **최종 shape은 증강 전과 동일**하지만, 매 epoch마다 실제 픽셀 값이 달라집니다(무작위성 때문에). 그래서 같은 이미지라도 매번 조금씩 다른 "버전"을 모델이 보게 됩니다.

**주의할 점**

- 증강은 **`train_transform_aug`에만** 적용, `test_transform`에는 적용하지 않습니다. 테스트 시 증강을 넣으면 평가 결과가 실행마다 달라져 성능 비교가 불가능해집니다.
- 증강을 적용하면 초반 훈련 손실(training loss)이 오히려 더 높게 나올 수 있습니다 — 매번 다른/더 어려운 이미지를 보기 때문. 이건 버그가 아니라 정상입니다. 대신 테스트 정확도(일반화 성능)는 개선됩니다.

---

## TODO 5: Fine-tuning 설정 (동결 해제 + 새 옵티마이저)

**무엇을 채워야 하나?**

```python
for param in model.parameters():
    param.requires_grad = True

optimizer = optim.SGD(model.parameters(), lr=0.0005)
```

**알아야 할 개념**

- TODO 2에서 얼렸던 백본을 이제 전부 풀어줍니다. `model.parameters()`는 fc층뿐 아니라 **conv, batchnorm 등 전체 파라미터**를 순회합니다.
- **왜 학습률을 0.001 → 0.0005로 낮추나?** 백본은 이미 ImageNet에서 유용한 특징을 학습해 "좋은 상태"에 있습니다. 학습률이 크면 이 좋은 가중치가 크게 흔들려서 오히려 성능이 나빠질 수 있습니다(=catastrophic forgetting). 작은 학습률로 "미세 조정"만 하는 게 Fine-tuning의 핵심 아이디어입니다.
- 옵티마이저는 **반드시 새로 선언**해야 합니다. 기존 옵티마이저는 `model.fc.parameters()`만 추적하고 있어서, 그대로 두면 여전히 fc층만 업데이트됩니다.

**데이터/파라미터 크기 변화**

- 학습 대상 파라미터: 5천 개(0.05%) → **약 1,100만 개(100%)**로 급증
- 이 때문에 GPU 메모리 사용량과 epoch당 학습 시간도 함께 증가합니다(gradient를 모든 층에서 계산·저장해야 하므로).

**주의할 점**

- 데이터가 적은데 전체를 fine-tuning하면 과적합 위험이 커집니다(그래서 TODO 4의 데이터 증강이 TODO 5보다 먼저 나온 것 — 증강으로 일반화 성능을 미리 보강).
- `scheduler = optim.lr_scheduler.StepLR(optimizer, ...)`는 **새 optimizer를 만든 뒤**에 선언해야 합니다(코드 순서상 이미 그렇게 되어 있음). 스케줄러는 옵티마이저 내부의 학습률을 조작하는 객체라서, 옵티마이저가 바뀌면 스케줄러도 다시 만들어야 합니다.

---

## TODO 6: HuggingFace ViT 모델 로드

**무엇을 채워야 하나?**

```python
image_processor = ViTImageProcessor.from_pretrained(model_name)
vit_model = ViTForImageClassification.from_pretrained(model_name)
```

**알아야 할 개념**

- `from_pretrained(model_name)`: HuggingFace Hub에서 모델 이름(`"nateraw/vit-base-patch16-224-cifar10"`)만으로 가중치·설정 파일을 자동 다운로드해 객체를 만들어주는 함수입니다. torchvision의 `pretrained=True`와 비슷한 역할이지만, HuggingFace는 Hub에 있는 수십만 개 모델 어떤 것이든 같은 인터페이스로 불러올 수 있다는 게 차이입니다.
- `ViTImageProcessor`: 모델 전용 전처리기. ViT가 학습될 때 사용한 것과 **동일한** 리사이즈(224×224)/정규화 값을 내장하고 있어서, TODO 1처럼 직접 mean/std를 계산할 필요 없이 `image_processor(images=...)` 한 줄로 처리됩니다.
- `ViTForImageClassification`: ViT 백본 뒤에 분류 헤드가 이미 CIFAR-10 10개 클래스로 fine-tuning되어 붙어있는 모델입니다. 이 실습은 **추론(inference) 전용**이라 별도 학습 루프가 없습니다 — Step 1/2와 달리 이미 남이 학습을 끝낸 모델을 "그대로 가져다 쓰는" 전이학습의 극단적 예시입니다.

**데이터 크기 변화**

- `image_processor(images=sample_images, return_tensors="pt")` → `pixel_values`: `[5, 3, 224, 224]` (5장의 PIL 이미지가 한 번에 배치 텐서로 변환됨)
- `vit_model(**inputs)` → `outputs.logits`: `[5, 10]`
- `argmax(dim=1)` → `[5]` (각 이미지의 예측 클래스 인덱스)

**주의할 점**

- `vit_model.to(device)`처럼 모델은 GPU로 옮기지만, `image_processor`는 텐서를 만드는 전처리 도구일 뿐 신경망이 아니므로 `.to(device)`가 필요 없습니다. 대신 만들어진 `inputs` 딕셔너리를 `{k: v.to(device) for k, v in inputs.items()}`로 옮겨야 합니다(코드에 이미 되어 있음).
- `transformers==4.57.1`로 버전이 고정된 이유가 노트북에 명시돼 있습니다 — `ViTImageProcessor`의 인터페이스가 버전마다 조금씩 달라질 수 있어서입니다. 이 노트북을 실습할 때도 반드시 지정된 버전을 설치하세요.

---

## 전체 파이프라인에서 본 데이터 크기 요약

| 단계              | Shape                       | 비고                      |
| ----------------- | --------------------------- | ------------------------- |
| 원본 CIFAR-10     | `(N, 32, 32, 3)` numpy    | `trainset.data`         |
| Resize + ToTensor | `[3, 224, 224]` per image | ResNet 입력 규격          |
| 배치 묶음         | `[256, 3, 224, 224]`      | DataLoader batch_size=256 |
| ResNet-18 통과    | `[256, 10]`               | 마지막 fc 출력            |
| ViT 전처리 (5장)  | `[5, 3, 224, 224]`        | image_processor           |
| ViT 출력          | `[5, 10]`                 | logits                    |

---

## 학습 개념으로 다시 정리하면

이 6개 TODO는 결국 **"전이학습을 얼마나 많이/적게 활용하느냐"의 스펙트럼**을 실습하는 구조입니다.

- TODO 1~3 (Linear Probing): 백본은 100% 재사용, 분류층 0.05%만 새로 학습 → 빠르지만 성능 상한 있음
- TODO 4~5 (Fine-tuning): 백본까지 100% 재학습, 대신 학습률을 낮춰 사전 지식을 보존 → 느리지만 성능 최고
- TODO 6 (ViT 추론): 이미 학습이 끝난 모델을 통째로 재사용, 추가 학습 0% → 가장 빠르지만 우리 데이터에 맞춰 조정할 수는 없음

이 스펙트럼을 이해하면 "왜 이 순서로 실습이 구성됐는지"도 자연스럽게 설명할 수 있습니다.
