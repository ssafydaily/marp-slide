Scaled dot-product attention에서 $\sqrt{d_k}$로 나누는 이유는 **내적(dot product) 값의 분산이 차원 수에 비례해서 커지는 문제를 막기 위해서**입니다.

## 문제의 원인: 차원이 커지면 내적 값도 커진다

Q와 K의 각 원소가 평균 0, 분산 1인 독립적인 확률변수라고 가정해봅시다.

$$q \cdot k = \sum_{i=1}^{d_k} q_i k_i$$

이때 $d_k$개의 항을 더하는 것이므로:

- 평균: $E[q \cdot k] = 0$
- 분산: $\text{Var}(q \cdot k) = d_k$ (각 항의 분산이 1이고 서로 독립이므로 분산들이 더해짐)

즉, **차원 $d_k$가 커질수록 내적 값의 분산도 그만큼 커집니다.** 예를 들어 $d_k = 64$라면 내적 값이 $d_k=8$일 때보다 훨씬 더 큰 값들(양수든 음수든)로 퍼지게 됩니다.

## 왜 이게 문제인가: Softmax의 saturation

Softmax 함수는:

$$\text{softmax}(z_i) = \frac{e^{z_i}}{\sum_j e^{z_j}}$$

입력 값들의 스케일이 크면 (예: [-30, 50, 2] 처럼) 가장 큰 값에 지수함수가 극도로 쏠리면서 **softmax 출력이 거의 one-hot에 가까운 극단적인 분포**가 됩니다.

이렇게 되면:
1. **다른 토큰들에 대한 attention이 거의 0에 가까운 값이 되어**, 사실상 모델이 한두 개의 토큰만 참고하게 됩니다 (attention의 의미가 퇴색)
2. 더 심각한 문제는 **gradient 소실(vanishing gradient)**입니다. Softmax가 saturation 영역(0 또는 1 근처)에 있으면, 그 지점에서의 기울기가 거의 0이 되어 역전파 시 gradient가 제대로 흐르지 않습니다.

## 해결책: $\sqrt{d_k}$로 나누기

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$

내적 값을 $\sqrt{d_k}$로 나누면:

$$\text{Var}\left(\frac{q \cdot k}{\sqrt{d_k}}\right) = \frac{d_k}{d_k} = 1$$

분산이 다시 **1로 정규화**되어, $d_k$ 값에 상관없이 내적 값의 스케일이 일정하게 유지됩니다. 그 결과:

- Softmax 입력이 적당한 범위에 머물러 **saturation을 방지**
- Gradient가 건강하게 흐를 수 있음
- 다양한 head 차원(64, 128 등)을 사용해도 안정적인 학습 가능

## 요약

| 나누지 않을 때 | $\sqrt{d_k}$로 나눌 때 |
|---|---|
| 내적 분산이 $d_k$에 비례해 커짐 | 분산이 항상 1로 유지됨 |
| Softmax가 극단적으로 편향됨 (one-hot에 가까움) | Softmax가 부드러운 분포 유지 |
| Gradient vanishing 발생 가능 | 안정적인 gradient 흐름 |

이 내용은 원래 "Attention Is All You Need" (Vaswani et al., 2017) 논문에서 제안된 것으로, 논문에서도 $d_k$가 커질수록 additive attention이 dot-product attention보다 성능이 좋아지는 이유를 이 스케일링 문제로 설명하고 있습니다.