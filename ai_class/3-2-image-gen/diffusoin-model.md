좋습니다. 아래처럼 **수업용 슬라이드 형태**로 구성하면 좋습니다. 단순히 Diffusion Model의 개념만 설명하는 것이 아니라, **"이미지 하나가 모델 내부에서 어떻게 노이즈가 되고, 다시 이미지로 복원되는가"**를 단계적으로 이해하도록 구성했습니다.

## 슬라이드 1. Diffusion Model이란?

### 핵심 질문

> **"완전히 랜덤한 노이즈에서 어떻게 그럴듯한 이미지를 만들어낼 수 있을까?"**

Diffusion Model은 **데이터에 점진적으로 노이즈를 추가하는 과정의 반대 방향을 학습하여, 노이즈로부터 새로운 데이터를 생성하는 생성 모델**입니다.

```text
학습할 때

원본 이미지
   │
   ▼
노이즈 조금 추가
   │
   ▼
노이즈 더 추가
   │
   ▼
      ...
   │
   ▼
완전한 노이즈
```

그리고 생성할 때는 반대로 진행합니다.

```text
생성할 때

완전한 노이즈
   │
   ▼
노이즈 제거
   │
   ▼
노이즈 제거
   │
   ▼
      ...
   │
   ▼
깨끗한 이미지
```

### 핵심

**Forward Process + Reverse Process**

---

# 슬라이드 2. Diffusion Model의 전체 구조

```text
                 ┌─────────────────────┐
                 │     학습 과정        │
                 │   Forward Process   │
                 └──────────┬──────────┘
                            │
                            ▼
원본 이미지 x₀ ──────► 노이즈 추가 ──────► xₜ
                            │
                            ▼
                       Noise ε 학습


                 ┌─────────────────────┐
                 │     생성 과정        │
                 │   Reverse Process   │
                 └──────────┬──────────┘
                            │
                            ▼
                       랜덤 노이즈 xₜ
                            │
                            ▼
                      노이즈 제거
                            │
                            ▼
                         xₜ₋₁
                            │
                            ▼
                          xₜ₋₂
                            │
                           ...
                            │
                            ▼
                       생성 이미지 x₀
```

### 가장 중요한 개념

Diffusion Model은 **"이미지를 직접 생성하는 방법"을 배우는 것이 아니라 "노이즈를 제거하는 방법"을 학습한다**고 이해하면 쉽습니다.

---

# 슬라이드 3. 왜 노이즈를 추가하는가?

원본 이미지가 있다고 생각해 봅시다.

```text
🐕
강아지 이미지
```

여기에 조금씩 Gaussian Noise를 추가합니다.

```text
t = 0

🐕
원본
```

↓

```text
t = 1

🐕 + 약간의 노이즈
```

↓

```text
t = 100

▓🐕▓
많은 노이즈
```

↓

```text
t = 500

▒▓▒▓▒
이미지 형태가 거의 보이지 않음
```

↓

```text
t = T

░▒▓░▒▓░▒
완전한 랜덤 노이즈
```

결국

> **어떤 이미지든 충분히 많은 노이즈를 추가하면 거의 랜덤한 Gaussian Noise가 됩니다.**

이 성질이 Diffusion Model의 핵심 출발점입니다.

---

# 슬라이드 4. Forward Process

### Forward Process

원본 이미지 `x₀`에 조금씩 Gaussian Noise를 추가합니다.

```text
x₀ → x₁ → x₂ → x₃ → ... → xₜ → ... → xT
```

각 단계에서:

```text
현재 이미지
    +
작은 Gaussian Noise
    ↓
다음 단계 이미지
```

즉,

> **Forward Process = 데이터를 망가뜨리는 과정**

입니다.

### 중요한 특징

이 과정은 **학습해야 하는 과정이 아닙니다.**

노이즈를 얼마나 추가할지는 미리 정한 **Noise Schedule**에 의해 결정됩니다.

---

# 슬라이드 5. Noise Schedule

노이즈를 무작정 추가하는 것이 아닙니다.

각 timestep `t`마다 노이즈의 양을 정합니다.

```text
t       Noise
────────────────
0         0%
1         조금
2         조금 더
3         ...
...
T         거의 100%
```

이를 **Noise Schedule**이라고 합니다.

대표적으로 `β(t)` 또는 `βₜ`를 사용하여 각 단계에서 추가할 노이즈의 크기를 결정합니다.

```text
β₁ → β₂ → β₃ → ... → βT
```

### 핵심

> **t가 증가할수록 원본 이미지의 정보는 감소하고 노이즈의 비율은 증가합니다.**

---

# 슬라이드 6. 한 번에 노이즈를 많이 넣지 않는 이유

질문:

> "그냥 이미지에 한 번에 노이즈를 왕창 넣으면 안 되나요?"

가능하지만 Diffusion Model에서는 **작은 변화가 반복되는 구조**를 사용합니다.

```text
한 번에

이미지 ─────────────► 노이즈
```

보다

```text
이미지
 ↓
조금 노이즈
 ↓
조금 더 노이즈
 ↓
조금 더 노이즈
 ↓
...
 ↓
노이즈
```

라는 과정을 사용합니다.

이렇게 하면 모델이 **각 단계에서 어떻게 노이즈를 제거해야 하는지** 학습하기 쉬워집니다.

---

# 슬라이드 7. 핵심 수식

Forward Process는 다음과 같이 표현할 수 있습니다.

[
q(x_t|x_{t-1})
==============

\mathcal{N}
\left(
x_t;
\sqrt{1-\beta_t}x_{t-1},
\beta_t I
\right)
]

처음 보면 어려워 보이지만 의미는 간단합니다.

```text
xₜ
=
원본 정보
+
Gaussian Noise
```

즉,

> **이전 이미지 xₜ₋₁에 일정한 비율의 노이즈를 추가해서 xₜ를 만든다.**

라고 이해하면 됩니다.

---

# 슬라이드 8. 더 중요한 표현 — 한 번에 xₜ 만들기

실제 Diffusion Model에서는 매 단계마다 노이즈를 넣지 않고 **원본 x₀에서 원하는 timestep의 xₜ를 바로 만들 수 있는 수식**을 사용합니다.

[
x_t =
\sqrt{\bar{\alpha}_t}x_0
+
\sqrt{1-\bar{\alpha}_t}\epsilon
]

여기서

* `x₀` : 원본 이미지
* `xₜ` : t 단계의 noisy image
* `ε` : Gaussian Noise
* `ᾱₜ` : 원본 이미지가 얼마나 남아 있는지를 결정
* `1-ᾱₜ` : 노이즈가 얼마나 들어갔는지를 결정

입니다.

개념적으로 보면:

```text
                원본 이미지
                    │
                    ▼
              √ᾱₜ × x₀
                    │
                    ├──────┐
                    │      │
                    │      ▼
                    │    +
                    │      ▲
                    │      │
                    │  √(1-ᾱₜ) × ε
                    │      ▲
                    │      │
                    │   Random Noise
                    │
                    ▼
                   xₜ
```

---

# 슬라이드 9. 이제 핵심 질문

## "그렇다면 이미지를 다시 복원하려면?"

우리가 원하는 것은:

```text
xₜ
 ↓
xₜ₋₁
 ↓
xₜ₋₂
 ↓
...
 ↓
x₀
```

입니다.

그런데 문제가 있습니다.

### 모델은 무엇을 알아야 할까요?

현재 이미지 `xₜ`만 보고는

> **"이 이미지에 어떤 노이즈가 들어갔는가?"**

를 알아야 합니다.

따라서 Diffusion Model은 **현재 이미지에 포함된 Noise를 예측하도록 학습**합니다.

---

# 슬라이드 10. 핵심 모델 — Noise Predictor

Diffusion Model의 핵심 신경망을 간단하게 표현하면:

```text
               xₜ
                │
                │
                ▼
        ┌───────────────┐
        │ Neural Network│
        │    U-Net      │
        └───────┬───────┘
                │
                ▼
          예측 Noise εθ
```

모델의 목표는:

> **"현재 이미지 xₜ에 어떤 노이즈가 들어있는지 예측하라."**

입니다.

학습이 잘 되면:

```text
실제 Noise ε
       ↓
     비교
       ↑
예측 Noise εθ
```

두 값이 점점 비슷해집니다.

---

# 슬라이드 11. U-Net 구조

전통적인 DDPM에서는 **U-Net** 구조가 핵심 네트워크로 사용됩니다.

전체적인 형태는:

```text
                 입력 xₜ
                    │
                    ▼
              ┌─────────┐
              │ Encoder │
              └────┬────┘
                   │
              Feature 추출
                   │
                   ▼
              ┌─────────┐
              │ Bottleneck
              └────┬────┘
                   │
                   ▼
              ┌─────────┐
              │ Decoder │
              └────┬────┘
                   │
                   ▼
              예측 Noise
```

U-Net의 특징은 **Skip Connection**입니다.

```text
Encoder ───────────────► Decoder
   │                        ▲
   └──── Skip Connection ──┘
```

이를 통해 이미지의 세부적인 공간 정보를 유지하면서 복원할 수 있습니다.

---

# 슬라이드 12. U-Net 내부에서는 무엇을 입력받는가?

실제로 U-Net은 이미지 하나만 받는 것이 아닙니다.

대표적으로:

```text
              ┌─────────────┐
xₜ ──────────►│             │
              │    U-Net    │────► 예측 Noise
t ───────────►│             │
              └─────────────┘
```

즉,

### ① 현재 noisy image

`xₜ`

### ② 현재 timestep

`t`

을 함께 사용합니다.

왜 `t`가 필요할까요?

```text
t = 10
→ 노이즈가 조금 들어 있음

t = 900
→ 노이즈가 매우 많이 들어 있음
```

같은 이미지라도 timestep이 다르면 **제거해야 할 노이즈의 양과 성격이 다르기 때문**입니다.

---

# 슬라이드 13. Text-to-Image에서는 무엇이 추가되는가?

여기서 우리가 실습한 **SANA와 같은 Text-to-Image 모델**로 확장됩니다.

사용자가:

```text
"A red fox sitting in a forest"
```

라고 입력하면 텍스트를 그대로 U-Net에 넣는 것이 아니라 **텍스트를 벡터로 변환**합니다.

```text
"A red fox sitting in a forest"
              │
              ▼
       Text Encoder
              │
              ▼
        Text Embedding
              │
              │
              ▼
       ┌─────────────┐
xₜ ───►│             │
t ────►│    U-Net    │
text ─►│             │
       └──────┬──────┘
              │
              ▼
        예측 Noise
```

이렇게 하면 모델이 단순히 노이즈를 제거하는 것이 아니라

> **"텍스트가 설명하는 이미지가 되도록 노이즈를 제거"**

할 수 있습니다.

---

# 슬라이드 14. Cross-Attention

Text-to-Image 모델에서 중요한 기술이 **Cross-Attention**입니다.

예를 들어:

```text
"A red fox sitting in a forest"
```

라는 문장이 있다면 모델은 이미지의 어느 부분이

```text
red
fox
forest
```

와 관련되는지를 연결할 수 있습니다.

개념적으로:

```text
이미지 Feature
     │
     │      Text Embedding
     │            │
     └──────┬─────┘
            ▼
      Cross-Attention
            │
            ▼
"어떤 이미지 영역을
 어떤 텍스트 정보와
 연결할 것인가?"
```

이 메커니즘이 **텍스트 조건을 이미지 생성 과정에 반영하는 중요한 역할**을 합니다.

---

# 슬라이드 15. Reverse Process

이제 진짜 이미지 생성 과정입니다.

처음에는:

```text
xT

░▒▓▒░▓▒▓░▒▓
완전한 랜덤 노이즈
```

입니다.

U-Net이 노이즈를 예측합니다.

```text
xT
 │
 ▼
U-Net
 │
 ▼
예측 Noise
 │
 ▼
Noise 제거
 │
 ▼
xT-1
```

다시 반복합니다.

```text
xT
 ↓
xT-1
 ↓
xT-2
 ↓
xT-3
 ↓
...
 ↓
x2
 ↓
x1
 ↓
x0
```

즉,

> **하나의 신경망을 timestep을 바꿔가며 반복적으로 사용합니다.**

---

# 슬라이드 16. 이미지 생성 과정 내부를 자세히 보면

한 번의 denoising step을 확대해 보면:

```text
현재 이미지 xₜ
      │
      ├──────────────┐
      │              │
      ▼              ▼
   Timestep       Text Embedding
      │              │
      └──────┬───────┘
             ▼
           U-Net
             │
             ▼
        예측 Noise εθ
             │
             ▼
      Sampling / Update
             │
             ▼
          xₜ₋₁
```

여기서 중요한 것은:

**U-Net이 최종 이미지를 직접 출력하는 것이 아닙니다.**

> **현재 이미지에 포함된 노이즈를 예측합니다.**

그리고 그 예측 결과를 이용하여 다음 상태 `xₜ₋₁`을 계산합니다.

---

# 슬라이드 17. 생성 과정을 사람의 관점으로 이해하기

예를 들어 모델에게:

> **"숲속의 빨간 여우"**

를 생성하라고 했다고 생각해 봅시다.

처음:

```text
░▒▓▒░▒▓░▒▓▒
```

모델:

> "현재 노이즈 상태에서 빨간 여우와 숲이 있는 이미지가 되려면 이 방향의 노이즈를 제거해야 한다."

↓

```text
▒░▒▓▒
   ↓
희미한 형태
```

다시 모델:

> "여우의 형태가 나타나야 한다."

↓

```text
🐕?
희미한 동물 형태
```

다시:

> "여우의 얼굴과 몸을 좀 더 명확하게..."

↓

```text
🦊
```

반복하면서 최종적으로:

```text
🦊 + 🌲 + 🍂
```

에 가까운 이미지가 만들어집니다.

물론 실제 모델 내부에서 이런 문장으로 판단하는 것은 아니며, **신경망이 벡터 공간에서 이러한 관계를 계산한다는 점**을 함께 강조해야 합니다.

---

# 슬라이드 18. 전체 과정을 한 장으로 정리

```text
                 Text Prompt
                     │
                     ▼
               Text Encoder
                     │
                     ▼
              Text Embedding
                     │
                     │
                     ▼
Random Noise ──► ┌─────────┐
      xT         │  U-Net  │
                 └────┬────┘
                      │
                Noise Prediction
                      │
                      ▼
                Denoising Step
                      │
                      ▼
                     xT-1
                      │
                    반복
                      │
                      ▼
                     xT-2
                      │
                    반복
                      │
                     ...
                      │
                      ▼
                     x1
                      │
                      ▼
              최종 이미지 x0
```

### 핵심 구조

**Text Encoder + U-Net + Sampling/Denoising**

---

# 슬라이드 19. 학습 과정은 어떻게 이루어지는가?

지금까지 설명한 것은 **이미지를 생성하는 과정**이었습니다.

그렇다면 모델은 어떻게 이런 능력을 배웠을까요?

학습 데이터:

```text
이미지
+
텍스트 설명
```

예:

```text
🦊
"A red fox in a forest"
```

학습 과정:

```text
원본 이미지 x₀
      │
      ▼
Random Noise ε 생성
      │
      ▼
x₀에 Noise 추가
      │
      ▼
xₜ 생성
      │
      ▼
U-Net
      │
      ▼
예측 Noise εθ
      │
      ▼
실제 Noise ε와 비교
      │
      ▼
Loss
      │
      ▼
Backpropagation
      │
      ▼
U-Net 가중치 업데이트
```

---

# 슬라이드 20. Diffusion Model의 학습 핵심

모델에게 문제를 이렇게 냅니다.

> **"내가 원본 이미지에 어떤 노이즈를 넣었는지 맞혀봐."**

예를 들어:

```text
원본 이미지
     🦊
      │
      │ + Noise ε
      ▼
░▒▓▒🦊▓▒░
      │
      ▼
     U-Net
      │
      ▼
"내가 보기에는
이런 Noise입니다."
```

그리고 실제 Noise와 비교합니다.

```text
실제 Noise ε
     │
     ├──── Loss ────┐
     │              │
예측 Noise εθ      │
     │              │
     └──────────────┘
```

---

# 슬라이드 21. Loss는 무엇을 비교하는가?

가장 기본적인 Diffusion Model에서는 **MSE(Mean Squared Error)** 형태의 Loss를 사용할 수 있습니다.

개념적으로:

[
L = ||\epsilon-\epsilon_\theta(x_t,t)||^2
]

의 의미는:

> **실제 Noise와 모델이 예측한 Noise의 차이를 최소화한다.**

입니다.

```text
실제 Noise
    │
    │      차이 ↓
    │
    ▼
예측 Noise
```

학습이 반복되면서:

```text
예측 Noise ≈ 실제 Noise
```

가 되도록 모델이 학습됩니다.

---

# 슬라이드 22. 그런데 왜 Noise를 예측하는가?

여기가 학생들이 가장 많이 질문하는 부분입니다.

> "이미지를 생성하려는데 왜 이미지를 직접 예측하지 않고 Noise를 예측하나요?"

핵심은 **학습 문제를 단순화할 수 있기 때문**입니다.

이미지를 직접 생성하는 것은 매우 복잡합니다.

하지만

```text
현재 이미지가 있고
↓
여기에 섞여 있는 Noise를 추정
```

하는 문제로 바꾸면 반복적인 denoising 과정을 학습할 수 있습니다.

즉,

> **복잡한 이미지 생성 문제를 "노이즈 예측 문제"로 바꾸어 학습하는 아이디어**

라고 이해하면 좋습니다.

---

# 슬라이드 23. 실제 Text-to-Image 모델에서는 더 복잡하다

여기서 중요한 주의사항입니다.

앞에서 설명한 구조는 **Diffusion의 기본 원리를 이해하기 위한 단순화된 구조**입니다.

실제 최신 Text-to-Image 모델은 다음과 같이 훨씬 복잡합니다.

```text
                    Text
                     │
                     ▼
               Text Encoder
                     │
                     ▼
               Text Embedding
                     │
                     ▼
Random Noise ─► Diffusion Network
                     │
             ┌───────┴───────┐
             │               │
       Attention        Time Embedding
             │               │
             └───────┬───────┘
                     ▼
              Noise Prediction
                     │
                     ▼
                 Scheduler
                     │
                     ▼
               Denoising
                     │
                   반복
                     │
                     ▼
               Latent/Image
```

SANA와 같은 최신 모델에서는 **Latent Space, VAE, Transformer 계열 구조 등**이 추가될 수 있습니다.

따라서:

> **"Diffusion Model = 무조건 U-Net"**

이라고 가르치면 안 됩니다.

**U-Net은 대표적인 Diffusion architecture 중 하나**라고 설명하는 것이 정확합니다.

---

# 슬라이드 24. Latent Diffusion은 왜 사용하는가?

고해상도 이미지를 픽셀 공간에서 직접 처리하면 계산량이 매우 커집니다.

예를 들어:

```text
1024 × 1024 × 3
```

픽셀 공간에서 직접 diffusion을 수행하면 상당히 많은 계산이 필요합니다.

그래서 일부 모델은:

```text
이미지
  │
  ▼
VAE Encoder
  │
  ▼
Latent
  │
  ▼
Diffusion
  │
  ▼
Latent
  │
  ▼
VAE Decoder
  │
  ▼
이미지
```

처럼 **압축된 Latent Space에서 Diffusion을 수행**합니다.

---

# 슬라이드 25. SANA 실습과 연결하기

이번 실습의 SANA를 생각해 봅시다.

학생들에게 다음 질문을 던질 수 있습니다.

### 입력

```text
"A watercolor painting of a red fox..."
```

### 내부

```text
Prompt
 ↓
Text Encoding
 ↓
Conditioning
 ↓
Noise
 ↓
Denoising Network
 ↓
Scheduler
 ↓
반복적인 Denoising
```

### 출력

```text
🦊
Watercolor Fox Image
```

즉, 우리가 실습에서 단순히:

```python
result = pipe(prompt=positive_prompt)
```

라고 작성한 한 줄의 코드 내부에서 **수많은 denoising 과정이 반복적으로 수행됩니다.**

---

# 슬라이드 26. `num_inference_steps`의 의미

실습 코드의:

```python
num_inference_steps=20
```

을 다시 생각해 봅시다.

개념적으로:

```text
Random Noise
     │
    Step 1
     ↓
    Step 2
     ↓
    Step 3
     ↓
    ...
     ↓
   Step 20
     ↓
Final Image
```

즉,

> **20번의 추론 단계에 걸쳐 노이즈를 점진적으로 제거한다**

는 의미입니다.

단, 실제 최신 diffusion pipeline의 내부 동작은 사용하는 scheduler와 모델 구조에 따라 세부 구현이 달라질 수 있습니다.

---

# 슬라이드 27. `guidance_scale`과 연결

실습의:

```python
guidance_scale=4.5
```

도 이 생성 과정과 연결됩니다.

Text-to-Image 모델은 단순히:

```text
Noise → Image
```

를 만드는 것이 아니라

```text
Noise
 +
Text Condition
      ↓
Text에 맞는 Image
```

를 만들려고 합니다.

**Classifier-Free Guidance(CFG)**를 사용하는 계열에서는 guidance scale을 높이면 일반적으로 텍스트 조건을 더 강하게 반영하도록 유도할 수 있습니다.

하지만:

> **높을수록 무조건 좋은 것은 아닙니다.**

너무 높으면 부자연스러운 결과나 품질 저하가 발생할 수도 있습니다.

---

# 슬라이드 28. Diffusion Model을 한 문장으로 설명한다면?

### 가장 쉬운 설명

> **"Diffusion Model은 이미지에 노이즈를 넣었다가 다시 제거하는 방법을 학습한 모델이다."**

### 조금 더 정확한 설명

> **"Diffusion Model은 데이터에 노이즈를 점진적으로 추가하는 Forward Process를 정의하고, 그 역과정에서 노이즈를 예측·제거하는 Reverse Process를 학습하여 새로운 데이터를 생성한다."**

### Text-to-Image까지 포함하면

> **"텍스트 조건을 참고하면서 랜덤 노이즈를 반복적으로 변환하여 텍스트에 대응하는 이미지를 만들어낸다."**

---

# 슬라이드 29. 학생들이 반드시 기억해야 할 5가지

| 개념                        | 핵심 내용                              |
| ------------------------- | ---------------------------------- |
| Forward Process           | 이미지에 점진적으로 Noise를 추가               |
| Reverse Process           | Noise를 점진적으로 제거                    |
| U-Net / Diffusion Network | 현재 Noise를 예측                       |
| Text Encoder              | Prompt를 벡터로 변환                     |
| Scheduler                 | 각 Denoising Step에서 다음 상태를 계산하도록 제어 |

### 가장 중요한 흐름

```text
학습
이미지
 ↓
Noise 추가
 ↓
Noisy Image
 ↓
Noise 예측
 ↓
실제 Noise와 비교
 ↓
학습


생성
Random Noise
 ↓
Noise 예측
 ↓
Noise 제거
 ↓
Noise 예측
 ↓
Noise 제거
 ↓
...
 ↓
Image
```

---

# 슬라이드 30. 최종 정리 — Diffusion Model의 핵심

```text
                [학습]

              원본 이미지
                   │
                   ▼
              Noise 추가
                   │
                   ▼
                  xₜ
                   │
                   ▼
                 U-Net
                   │
                   ▼
              Noise 예측
                   │
                   ▼
          실제 Noise와 비교
                   │
                   ▼
                  Loss
                   │
                   ▼
             가중치 업데이트


                [생성]

             Random Noise
                   │
                   ▼
                 U-Net
          + Text Condition
                   │
                   ▼
              Noise 예측
                   │
                   ▼
               Scheduler
                   │
                   ▼
               xₜ₋₁ 생성
                   │
                   ▼
                 반복
                   │
                  ...
                   │
                   ▼
              최종 이미지
```

### 🎯 핵심 메시지

**Diffusion Model은 "이미지를 만드는 모델"이라기보다**

> **"노이즈를 제거하는 방법을 학습하여, 랜덤 노이즈를 점차 의미 있는 데이터로 변환하는 모델"**

이라고 이해하면 가장 좋습니다.

특히 이번 실습의 **SANA를 설명할 때는 `Prompt → Text Encoder → Noise → Denoising Network → Scheduler → 반복 → Image`라는 흐름을 중심으로 설명**하면 학생들이 `pipe(prompt=...)`라는 한 줄의 코드 뒤에서 실제로 어떤 일이 일어나는지 이해하기 쉽습니다.
