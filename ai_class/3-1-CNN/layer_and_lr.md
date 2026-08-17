아니요, 반대입니다. **하위 층(lower layer)은 입력(input)에 가까운 층**이고, **상위 층(upper layer)은 출력(output)에 가까운 층**입니다.

## 용어 정리

```
[입력 이미지] → [하위 층] → ... → [상위 층] → [출력]
                (input에 가까움)   (output에 가까움)
```

ResNet-18 구조로 보면:
- **하위 층(lower layers)** = 앞쪽 conv 블록들 (`conv1`, `layer1`, `layer2` 등) — 입력과 가까움
- **상위 층(upper/higher layers)** = 뒤쪽 conv 블록들 (`layer4`)과 `fc` — 출력과 가까움

## 왜 이렇게 부르나 (직관)

이 "하위/상위"는 물리적 위치(입력이 아래, 출력이 위)라기보다 **네트워크 다이어그램을 아래→위로 쌓아 그리는 관례**에서 온 표현입니다. 층을 쌓아 올리는(stack) 그림을 떠올리면, 입력이 맨 아래 바닥에 있고 그 위로 층을 하나씩 쌓아 올라가 맨 꼭대기에 출력이 나오는 구조입니다. 그래서:

- 바닥(입력)에 가까운 층 → "하위(lower)"
- 꼭대기(출력)에 가까운 층 → "상위(upper/higher)"

## 왜 학습률을 다르게 주는가 (실습 내용과 연결)

이 실습의 Concept Check에 나온 "저수준 특징 vs 고수준 특징" 설명과 정확히 맞물립니다.

| | 하위 층 (input 쪽) | 상위 층 (output 쪽) |
|---|---|---|
| 학습하는 특징 | 엣지, 색상, 질감 등 **저수준·범용적** 특징 | 물체 형태, 클래스 구분 등 **고수준·태스크 특화** 특징 |
| ImageNet에서 배운 지식의 재사용성 | 매우 높음 (CIFAR-10에도 그대로 유용) | 상대적으로 낮음 (ImageNet 1000개 클래스에 특화) |
| Fine-tuning 시 권장 학습률 | **작게** (이미 좋은 특징이니 크게 흔들지 않음) | **크게** (새 태스크에 맞게 많이 바뀌어야 함) |

그래서 "하위 층은 작은 학습률, 상위 층은 큰 학습률"이라는 Layer-wise Learning Rate 전략이 나온 겁니다. 엣지/색상 검출 같은 범용 특징은 굳이 크게 건드릴 필요가 없고, 클래스 판단을 담당하는 뒤쪽 층은 CIFAR-10 10개 클래스에 맞게 더 적극적으로 바뀌어야 하기 때문입니다.

## 참고: 이 실습 코드와의 관계

이번 노트북의 TODO 5는 Layer-wise가 아니라 **단일 학습률(0.0005)로 전체를 fine-tuning**하는 단순한 버전입니다. 표에 있는 "Layer-wise Learning Rate"는 개념 설명(Concept Check)에서 소개만 되고 실습 TODO로는 구현하지 않는 심화 내용입니다. 만약 직접 구현해보고 싶다면 PyTorch에서는 이렇게 파라미터 그룹을 나눠서 옵티마이저에 전달하면 됩니다.

```python
optimizer = optim.SGD([
    {'params': model.layer1.parameters(), 'lr': 0.0001},  # 하위 층: 작게
    {'params': model.layer2.parameters(), 'lr': 0.0001},
    {'params': model.layer3.parameters(), 'lr': 0.0003},
    {'params': model.layer4.parameters(), 'lr': 0.0005},  # 상위 층: 크게
    {'params': model.fc.parameters(),     'lr': 0.001},   # 최상위: 가장 크게
])
```