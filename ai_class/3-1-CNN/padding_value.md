`transforms.RandomCrop`의 `padding` 관련 파라미터에는 `fill`과 `padding_mode`가 따로 있는데, 이 실습 코드처럼 `padding=4`만 쓰고 나머지를 지정하지 않으면 **기본값**이 적용됩니다.공식 시그니처를 보면 명확합니다.

```python
class torchvision.transforms.RandomCrop(
    size, padding=None, pad_if_needed=False,
    fill=0, padding_mode='constant'
)
```

실습 코드는 `transforms.RandomCrop(32, padding=4)`처럼 `fill`, `padding_mode`를 지정하지 않았으니 **기본값**이 그대로 적용됩니다.

## 기본값 = `fill=0`, `padding_mode='constant'`

- `padding_mode='constant'`: constant 모드는 지정된 상수 값으로 패딩을 채웁니다.
- `fill=0`: 채우는 픽셀 값은 기본적으로 0입니다.

즉 **패딩 부분은 픽셀 값 0으로 채워집니다.**

## 이게 실제로 뭘 의미하는가

`RandomCrop`은 `Resize`, `ToTensor`보다 **먼저** 적용되므로(코드 순서 기억하시죠 — `RandomCrop → Flip → Resize → ToTensor → Normalize`), 이 시점의 이미지는 아직 PIL 이미지이고 픽셀 값은 0~255 범위입니다.

- `fill=0` → RGB 각 채널이 (0, 0, 0) → **검은색**으로 채워집니다.
- 32×32 이미지 주변에 검은 테두리 4픽셀이 둘러진 40×40 이미지가 만들어지고, 그중 무작위 32×32 영역이 잘려나오는 것입니다.

## 다른 옵션도 있다는 것 (참고)

`padding_mode`에는 다른 선택지도 있습니다.

| padding_mode | 동작 |
|---|---|
| `constant` (기본) | 지정한 단일 값(`fill`)으로 채움 — 이 실습은 검은색(0) |
| `edge` | 이미지 가장자리의 마지막 픽셀 값을 그대로 늘려서 채움 |
| `reflect` | 가장자리를 기준으로 이미지를 거울처럼 반사시켜 채움 |
| `symmetric` | reflect와 비슷하지만 가장자리 픽셀 자체도 포함해서 반사 |

## 주의할 점 / 실무 팁

- CIFAR-10은 배경이 다양해서 검은 테두리(`fill=0`)가 큰 문제가 되지 않지만, 만약 이미지 배경이 밝은 색 위주인 데이터셋이라면 검은 테두리가 부자연스러운 인공적 패턴으로 학습될 수 있습니다. 이럴 땐 `padding_mode='reflect'`가 더 자연스러운 증강이 됩니다.
- `Normalize`는 `RandomCrop` 이후, `ToTensor` 다음에 적용되므로, 텐서 기준으로는 검은 패딩(0)이 정규화되어 `(0 - mean) / std` 값(보통 음수)으로 바뀝니다 — 순수한 0이 그대로 모델에 들어가는 건 아니라는 점도 알아두면 좋습니다.