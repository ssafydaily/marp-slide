이건 에러가 아니라 **경고(warning)**입니다. 코드는 정상적으로 실행되고 학습도 문제없이 진행됩니다. 다만 왜 뜨는지, 어떻게 해결하는지 정리해드릴게요.

## 무슨 상황인가

노트북에서 쓴 코드:

```python
model = torchvision.models.resnet18(pretrained=True)
```

torchvision 0.13 버전부터 사전 학습 모델을 불러오는 API가 바뀌었습니다.

- **옛날 방식(지금은 deprecated)**: `pretrained=True/False`라는 boolean으로 "사전학습 가중치 쓸지 말지"만 지정
- **새로운 방식**: `weights=...`라는 파라미터에 **어떤 가중치 세트**를 쓸지 명시적으로 지정

경고 메시지 두 번째 줄이 알려주는 정보가 핵심입니다:

> 현재 `pretrained=True`는 내부적으로 `weights=ResNet18_Weights.IMAGENET1K_V1`을 쓴 것과 똑같이 동작한다고 안내하고 있습니다.

즉 **결과는 지금까지와 동일**합니다 — ImageNet-1K로 학습된 V1 가중치를 그대로 불러옵니다.

## 왜 API가 바뀌었나 (배경)

`pretrained=True` 방식은 "어떤 가중치인지"를 표현할 방법이 없었습니다. 예를 들어 같은 ResNet-18이라도 나중에 더 좋은 학습 레시피로 만든 `IMAGENET1K_V2` 같은 가중치가 추가되면, boolean으로는 이를 선택할 수 없습니다. `weights` enum 방식은 어떤 가중치 버전인지 명시적으로 고를 수 있고, 그 가중치에 맞는 전처리(리사이즈/정규화 값)까지 함께 제공합니다.

## 고치는 방법 (선택 사항)

경고를 없애고 최신 방식을 쓰려면 이렇게 바꾸면 됩니다.

```python
from torchvision.models import ResNet18_Weights

# 방법 1: 지금까지와 동일한 가중치를 명시적으로
model = torchvision.models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)

# 방법 2: 그냥 "가장 최신/권장 가중치"를 쓰고 싶다면
model = torchvision.models.resnet18(weights=ResNet18_Weights.DEFAULT)
```

**참고**: `weights=ResNet18_Weights.DEFAULT`를 쓰면 torchvision이 관리하는 "가장 성능 좋은 최신 가중치"로 자동 연결되므로, 나중에 더 나은 가중치가 추가되면 코드 수정 없이 자동으로 최신 버전을 쓰게 됩니다. 다만 이번 실습처럼 "정확히 이 가중치로 재현 가능해야 한다"는 목적이면 `IMAGENET1K_V1`처럼 버전을 못 박는 게 더 안전합니다.

## 정리

| 항목                  | 내용                                                                                                              |
| --------------------- | ----------------------------------------------------------------------------------------------------------------- |
| 경고 심각도           | 낮음 — 코드 동작에는 영향 없음                                                                                   |
| 지금 당장 고쳐야 하나 | 아니요, 실습 진행에는 지장 없습니다                                                                               |
| 왜 뜨나               | `pretrained=True/False` API가 deprecated되고 `weights=` API로 대체됨(0.13~)                                   |
| 실제 불러오는 가중치  | 이전과 동일하게`IMAGENET1K_V1`                                                                                  |
| 미래 대비             | `weights=` 방식으로 바꿔두면 향후 torchvision 버전에서 `pretrained` 인자가 완전히 제거돼도 코드가 깨지지 않음 |

지금 실습 목적(전이학습 개념 이해)에는 전혀 문제가 되지 않으니, 무시하고 진행하셔도 됩니다. 다만 나중에 실무 코드를 작성할 때는 `weights=` 방식을 쓰는 습관을 들이시는 게 좋습니다.
