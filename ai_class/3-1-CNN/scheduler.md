PyTorch의 학습률 스케줄러들을 확인하고 정리해드리겠습니다.내용을 확인했습니다. `StepLR`을 먼저 자세히 설명하고, 이어서 자주 쓰이는 다른 스케줄러들을 소개하겠습니다.

## StepLR

**무엇인가**: 정해진 epoch 간격마다 학습률을 일정 비율(`gamma`)로 뚝뚝 떨어뜨리는(계단식) 스케줄러입니다.

**어떻게 동작하는가**
```python
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)
```
- `step_size=5`: 5 epoch마다 한 번씩 학습률을 조정
- `gamma=0.1`: 조정할 때 현재 학습률에 0.1을 곱함(=10분의 1로 감소)

이 실습(`lr=0.0005`, `step_size=5`, `gamma=0.1`)에 대입하면:

| Epoch | 학습률 |
|---|---|
| 1~5 | 0.0005 |
| 6~10 | 0.00005 |
| 11~15 | 0.000005 |

**왜 필요한가**: 학습 초반에는 큰 학습률로 빠르게 좋은 영역을 찾고, 후반에는 작은 학습률로 세밀하게 다듬는 게 일반적으로 더 좋은 결과를 냅니다. 학습률이 계속 크면 최적점 근처에서 진동만 하고 수렴하지 못할 수 있습니다.

**사용법 (실습 코드)**
```python
for epoch in range(num_epochs):
    # ... 한 epoch 학습 ...
    scheduler.step()  # epoch이 끝날 때마다 호출 → 내부 카운터 +1, 조건 맞으면 lr 감소
```
`scheduler.step()`은 배치마다가 아니라 **epoch이 끝날 때 한 번** 호출하는 게 일반적입니다(스케줄러 종류에 따라 다를 수 있음).

**주의할 점**
- 이전에 설명드렸듯 `scheduler`는 `optimizer` 객체를 감싸는 wrapper라서, optimizer를 새로 만들면 scheduler도 반드시 다시 만들어야 합니다.
- 계단식이라 감소 시점(예: epoch 5→6)에서 학습률이 급격히 바뀝니다. 총 epoch 수에 비해 `step_size`를 너무 작게 잡으면 학습률이 너무 빨리 0에 가까워져 후반부 학습이 거의 멈출 수 있습니다.

---

## 그 외 자주 쓰이는 스케줄러

### 1. MultiStepLR
`StepLR`의 확장판. 고정 간격이 아니라 **원하는 epoch 지점을 직접 지정**해서 감소시킵니다.
```python
scheduler = optim.lr_scheduler.MultiStepLR(optimizer, milestones=[8, 24, 28], gamma=0.5)
```
지정한 epoch 인덱스 목록(milestones)마다 학습률에 gamma를 곱해 감소시킵니다. "8, 24, 28 epoch에서만 줄이고 싶다" 같은 불규칙한 스케줄이 필요할 때 씁니다.

### 2. CosineAnnealingLR
학습률을 계단식이 아니라 **코사인 곡선을 따라 부드럽게** 감소시킵니다.
```python
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=10, eta_min=0)
```
T_max는 최대 반복(iteration) 횟수, eta_min은 최소 학습률(기본값 0)을 의미합니다. 시작 학습률에서 `eta_min`까지 코사인 곡선 모양으로 완만하게 떨어집니다. 계단식 급감이 없어 학습이 더 안정적이라는 평가가 많아 최근 실무/논문에서 널리 쓰입니다.

### 3. ExponentialLR
매 epoch마다 **일정 비율로 지수적으로** 감소시킵니다.
```python
scheduler = optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.95)
```
매 epoch 학습률에 0.95를 곱하는 식 — StepLR처럼 계단이 아니라 매번 조금씩 부드럽게 줄어드는 버전입니다.

### 4. ReduceLROnPlateau
지금까지와 달리 **미리 정한 스케줄이 없고, 검증 지표(validation loss 등)를 보고 즉석에서 판단**합니다.
```python
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=10)
```
지정한 지표가 patience만큼의 epoch 동안 개선되지 않으면 학습률을 감소시키는 방식입니다(`mode='min'`이면 손실이 줄지 않을 때 발동). 다른 스케줄러는 `scheduler.step()`만 호출하면 되지만, 이 스케줄러는 **`scheduler.step(val_loss)`처럼 지표 값을 넣어줘야** 합니다 — "학습이 정체됐는지"를 스스로 판단해야 하기 때문입니다.

### 5. OneCycleLR
학습률을 **한 번 크게 올렸다가(warmup) 다시 크게 내리는** 사이클을 학습 전체에 걸쳐 딱 한 번 적용하는 방식입니다. 최근 빠른 수렴을 위해 많이 쓰이며, `fastai` 라이브러리가 대중화시킨 기법입니다.

---

## 비교 요약

| 스케줄러 | 감소 패턴 | 특징 | 언제 적합한가 |
|---|---|---|---|
| **StepLR** | 계단식, 고정 간격 | 단순, 이해하기 쉬움 | 실습·빠른 프로토타이핑, 이번 노트북처럼 명확한 스케줄이 필요할 때 |
| **MultiStepLR** | 계단식, 지정 지점 | 불규칙한 스케줄 가능 | 특정 epoch에서만 감소가 필요할 때 |
| **CosineAnnealingLR** | 부드러운 곡선 | 급격한 변화 없음, 최근 인기 | 이미지 분류 등 안정적 수렴이 중요할 때 |
| **ExponentialLR** | 부드러운 지수 감소 | 단순, 매 epoch 일정 비율 | 지속적인 미세 감소가 필요할 때 |
| **ReduceLROnPlateau** | 지표 기반, 비고정 | 데이터/학습 특성에 자동 적응 | 언제 감소시켜야 할지 미리 알기 어려울 때 |
| **OneCycleLR** | 상승 후 하강 (1회 사이클) | 빠른 수렴, warmup 포함 | 학습 시간을 단축하고 싶을 때 |

**이번 실습 관점에서**: `StepLR`은 개념(학습률 스케줄링)을 배우기에 가장 직관적이라 선택된 것으로 보입니다. 실무에서는 `CosineAnnealingLR`이나 `ReduceLROnPlateau`가 더 흔히 쓰이는 편이니, 이번 실습을 마친 뒤 스케줄러만 바꿔서 성능 차이를 비교해보는 것도 좋은 추가 학습이 될 수 있습니다.