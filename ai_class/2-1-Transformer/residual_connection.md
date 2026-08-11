# Residual Connection (잔차 연결)의 역할과 필요성

## 기본 구조

```python
x = x + self_attention(LN1(x))   # residual 1
x = x + mlp(LN2(x))              # residual 2
```

핵심은 `F(x)`를 계산해서 그대로 쓰는 게 아니라, **`x + F(x)`처럼 원본 입력을 항상 더해준다**는 것입니다.

## 1. Gradient Vanishing 문제 해결 (가장 핵심적인 이유)

Transformer는 보통 수십~수백 개의 layer를 쌓습니다 (GPT-2만 해도 12~48개 블록). Residual이 없다면 역전파 시 gradient가 이렇게 흘러갑니다:

$$
\frac{\partial L}{\partial x} = \frac{\partial L}{\partial y} \cdot \frac{\partial F_n}{\partial x} \cdot \frac{\partial F_{n-1}}{\partial x} \cdots \frac{\partial F_1}{\partial x}
$$

각 layer의 gradient가 1보다 작은 값들이 계속 곱해지면, layer가 깊어질수록 gradient가 **지수적으로 0에 가까워지는** vanishing gradient 문제가 발생합니다. 즉, 앞쪽 layer(입력에 가까운 layer)에는 학습 신호가 거의 도달하지 못합니다.

Residual을 쓰면:

$$
y = x + F(x) \quad \Rightarrow \quad \frac{\partial y}{\partial x} = 1 + \frac{\partial F(x)}{\partial x}
$$

미분값에 **항상 "+1"이라는 항등(identity) 경로가 존재**합니다. 이는 gradient가 각 layer를 거칠 때마다 최소한 1배는 그대로 뒤로 전달될 수 있는 "지름길(shortcut)"을 만들어줍니다. 그 결과 아무리 layer가 깊어져도 gradient가 소실되지 않고 앞쪽 layer까지 안정적으로 전달됩니다.

## 2. 항등 함수(identity mapping) 학습을 쉽게 만듦

만약 특정 layer(예: attention이나 MLP)가 "이번엔 딱히 유용한 변환을 안 해도 된다"고 판단하면:

- Residual이 없을 때: layer가 입력을 그대로 출력하는 항등 함수를 **처음부터 새로 학습**해야 함 (의외로 어려운 일)
- Residual이 있을 때: `F(x) ≈ 0`으로만 만들면 자동으로 `y = x + F(x) ≈ x` (항등 함수)가 됨

즉, **"아무것도 안 하기"가 기본값(default)이 되고, layer는 필요한 만큼만 조금씩 정보를 추가(residual = 잔차, 남은 차이)하면 되는 구조**가 됩니다. 이게 "residual(잔차)"이라는 이름의 유래입니다 — 전체를 새로 만드는 게 아니라 "차이만" 학습한다는 의미입니다.

## 3. 정보 손실 방지 — "정보의 고속도로"

질문에서 언급하신 것처럼, attention과 MLP는 각각 LayerNorm을 거친 뒤 계산되므로 입력이 변형된 스케일로 처리됩니다. 이 과정에서 원본 정보가 왜곡되거나 손실될 수 있습니다.

Residual connection은 **원본 입력 정보를 다음 layer로 그대로 전달하는 "우회로(bypass path)"** 역할을 합니다.

```
x ──────────────────────────┐
│                            │ (원본 정보 그대로 보존)
└─→ LN1 → Attention ─────→ (+) → x'
```

Attention이나 MLP가 잘못된 변환을 하더라도, 원본 `x`의 정보는 덧셈을 통해 다음 단계로 살아남습니다. 즉 각 sub-layer(Attention, MLP)는 "완전히 새로운 표현을 만드는 것"이 아니라 "기존 표현에 유용한 정보를 조금씩 더해가는 것"으로 역할이 바뀝니다.

## 4. 매우 깊은 네트워크 학습을 가능하게 함

이 아이디어는 원래 ResNet(2015, He et al.)에서 이미지 분류를 위해 제안되었는데, 그 논문에서 실험적으로 보여준 것이 인상적입니다:

- Residual 없이 layer를 20층 → 56층으로 늘리면 오히려 **학습 오차(training error)조차 더 나빠짐** (degradation problem, overfitting이 아니라 최적화 자체가 안 되는 문제)
- Residual을 추가하면 layer를 100층, 1000층까지 늘려도 안정적으로 학습됨

Transformer도 동일한 원리를 차용해서, GPT-2/3처럼 수십~수백 layer를 쌓아도 학습이 가능해진 것입니다. Residual이 없었다면 이렇게 깊은 Transformer는 애초에 학습 자체가 불가능했을 것입니다.

## 요약

| 문제 | Residual 없을 때 | Residual 있을 때 |
|---|---|---|
| Gradient 흐름 | 깊어질수록 gradient vanishing | `+1` 경로로 gradient가 안정적으로 전달 |
| 항등 함수 학습 | 직접 학습해야 함 (어려움) | `F(x)≈0`이면 자동 달성 (쉬움) |
| 정보 보존 | LN, Attention 등을 거치며 정보 손실 가능 | 원본 정보가 우회로로 보존됨 |
| 네트워크 깊이 | 깊게 쌓으면 오히려 성능 저하 (degradation) | 수백 layer도 안정적으로 학습 가능 |

결론적으로, residual connection은 Transformer block에서 **"각 layer가 전체를 새로 만드는 대신, 이전 표현에 필요한 만큼의 변화(잔차)만 더해가는" 구조를 만들어**, 깊은 네트워크에서도 gradient가 원활히 흐르고 정보가 안정적으로 보존되도록 하는 핵심 장치입니다.