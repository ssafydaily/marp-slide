# 선형 회귀와 로지스틱 회귀 — 실습자료 정리노트

> 원본 자료: `0-2 선형회귀와 로지스틱회귀 (Easy)` — 머신러닝 입문자를 위한 실습 노트북
> 이 문서는 원본 노트북의 흐름을 따라가며 핵심 개념 · 손실함수 · 경사하강법 미분 과정 · 선형회귀/로지스틱회귀 비교 · 검증/평가 방법을 정리한 것입니다.

---

## 1. 실습 자료의 전체 구성

이 노트북은 "AI를 위한 Math"라기보다 **머신러닝 기초**를 다루는 자료로, 다음 순서로 구성되어 있습니다.

| 단계 | 주제 |
|---|---|
| 1 | 머신러닝 개념 (모델·학습·추론) |
| 2 | 선형 회귀 모델 이해 (직선의 방정식) |
| 3 | MAE (Mean Absolute Error) |
| 4 | MSE (Mean Squared Error) |
| 5 | 정규방정식 (Normal Equation) |
| 6 | 정규방정식의 단점 |
| 7 | 경사하강법 (Gradient Descent) |
| 8 | 더 똑똑한 경사하강법 — Adam Optimizer |
| 9 | 선형 회귀 정리 |
| 10 | 로지스틱 회귀 이해 (분류 문제, 시그모이드) |
| 11 | 로지스틱 회귀에 Grid Search 적용 |
| 12 | 크로스 엔트로피(Cross Entropy) 적용 |
| 13 | 로지스틱 회귀의 경사하강법 학습 |
| 14 | 마무리 |

실습 데이터는 Seaborn의 기본 제공 데이터셋인 **`tips`**(미국 레스토랑 팁 데이터)를 사용하며, `total_bill`(음식 값)로 `tip`(팁)을 예측하는 문제를 선형회귀 예제로 사용합니다. 로지스틱 회귀 파트에서는 "공부 시간 → 합격/불합격" 이진 분류 예시를 사용합니다.

---

## 2. 주요 개념

### 2.1 머신러닝의 정의
1. 데이터를 기반으로 최적의 **모델**을 계산하여 완성한다.
2. 이를 활용해 새로운 데이터를 **예측**하거나 **분류**할 수 있게 하는 방법이다.

### 2.2 모델(Model)이란?
- 모델은 **수식**이다. 입력 데이터 $x$와 출력 데이터 $y$의 관계를 함수 $f$로 표현한 것이다.

$$\hat{y} = f(x)$$

- $x$: 입력값(feature, 피쳐)
- $f$: 모델
- $\hat{y}$(y-hat): 모델의 예측 결과값

### 2.3 학습(Training)과 추론(Inference)
- **학습**: 데이터를 보고 최적의 모델(추세선 등)을 만들어내는 과정
- **추론**: 만들어진 모델을 이용해 새로운 입력에 대한 값을 예측하는 과정

### 2.4 피쳐(Feature)
- 대상을 값으로 표현하여 모델에 입력하는 변수. 예) 사람이 대상이면 키·몸무게·나이 등.
- 피쳐가 1개면 선형회귀 모델은 **직선**, 2개면 **평면**이 된다.

---

## 3. 손실함수 (Loss Function)

손실함수는 **모델의 예측값과 실제값이 얼마나 차이나는지**를 하나의 숫자로 표현하는 함수입니다. 학습의 목표는 이 손실함수 값을 최소로 만드는 파라미터(a, b 등)를 찾는 것입니다.

### 3.1 오차의 합 (Sum of Errors) — 첫 시도
$$E = \sum_{i=1}^{n} |y_i - \hat{y}_i|$$
- 문제점: 데이터 개수가 많아지면 값이 커져서, 절대적인 크기 자체는 의미가 없어짐(예: 179.9라는 숫자 자체는 해석하기 어려움).

### 3.2 MAE (Mean Absolute Error, 평균 절대 오차)
$$\text{MAE} = \frac{1}{n}\sum_{i=1}^{n} \left| y_i - \hat{y}_i \right|$$
- 오차의 **평균**을 사용하므로 데이터 개수와 무관하게 "모델이 평균적으로 얼마나 틀리는지"를 해석할 수 있음.

### 3.3 MSE (Mean Squared Error, 평균 제곱 오차)
$$\text{MSE} = \frac{1}{n}\sum_{i=1}^{n} \left( y_i - \hat{y}_i \right)^2$$
- 오차를 제곱하여, **큰 오차일수록 더 크게 반영**(패널티를 크게 부여)되도록 만든 손실함수.
- 머신러닝에서 회귀 문제에 가장 흔하게 사용되는 손실함수.
- 선형회귀 모델 $\hat{y} = ax+b$ 에서는 MSE가 $a, b$에 대해 **아래로 볼록한 2차식**이므로, 미분해서 최솟값을 구하는 것이 가능(→ 정규방정식, 경사하강법의 근거).

### 3.4 크로스 엔트로피 (Cross Entropy, 분류 문제용 손실함수)
분류(로지스틱 회귀)에서는 MSE 대신 **크로스 엔트로피**를 사용합니다.

$$\text{Loss} = -\frac{1}{n}\sum_{i=1}^{n} \Big[ y_i \log(\hat{y}_i) + (1-y_i)\log(1-\hat{y}_i) \Big]$$

- MSE를 분류에 쓰면 생기는 문제: 확률값(0~1 사이)은 제곱하면 오히려 더 **작아지는** 역설이 발생(예: $0.5^2 = 0.25$). 즉 오차를 "확대"하려는 MSE의 의도가 확률 구간에서는 반대로 작동함.
- 크로스 엔트로피는 예측이 정답에서 멀어질수록(예: 정답이 1인데 예측이 0에 가까울수록) **로그 함수의 특성상 손실이 급격히 커지도록** 설계되어, 작은 오차는 작게, 큰 오차는 아주 크게 벌점을 준다.
- 그래서 분류 문제에서는 크로스 엔트로피가 표준적으로 사용된다.

---

## 4. 경사하강법(Gradient Descent) — 손실함수 미분 과정

### 4.1 선형회귀의 경사하강법 미분

**모델**: $\hat{y}_i = a x_i + b$

**손실함수(MSE)**:
$$L(a, b) = \frac{1}{n}\sum_{i=1}^{n} \left( y_i - \hat{y}_i \right)^2 = \frac{1}{n}\sum_{i=1}^{n} \left( y_i - (a x_i + b) \right)^2$$

경사하강법을 적용하려면 $L$을 파라미터 $a$, $b$ 각각에 대해 **편미분**해야 합니다.

**Step 1) $a$에 대한 편미분**

체인룰(chain rule)을 적용합니다. $u_i = y_i - (ax_i+b)$ 라 하면 $L = \frac{1}{n}\sum u_i^2$ 이고,

$$\frac{\partial L}{\partial a} = \frac{1}{n}\sum_{i=1}^{n} 2\,u_i \cdot \frac{\partial u_i}{\partial a}$$

여기서 $\dfrac{\partial u_i}{\partial a} = \dfrac{\partial}{\partial a}\big(y_i - ax_i - b\big) = -x_i$ 이므로,

$$\frac{\partial L}{\partial a} = \frac{1}{n}\sum_{i=1}^{n} 2\big(y_i-(ax_i+b)\big)\cdot(-x_i) = -\frac{2}{n}\sum_{i=1}^{n} \big(y_i-\hat{y}_i\big)x_i$$

예측 오차를 $e_i = \hat{y}_i - y_i$ (코드에서 `error = y_hat - y`)로 정의하면 부호가 뒤집혀 다음과 같이 정리됩니다.

$$\boxed{\frac{\partial L}{\partial a} = \frac{2}{n}\sum_{i=1}^{n} e_i \, x_i = 2\,\text{mean}(e \cdot x)}$$

**Step 2) $b$에 대한 편미분**

같은 방식으로 $\dfrac{\partial u_i}{\partial b} = \dfrac{\partial}{\partial b}\big(y_i-ax_i-b\big) = -1$ 이므로,

$$\frac{\partial L}{\partial b} = \frac{1}{n}\sum_{i=1}^{n} 2\big(y_i-\hat{y}_i\big)\cdot(-1) = -\frac{2}{n}\sum_{i=1}^{n}\big(y_i-\hat{y}_i\big)$$

$e_i = \hat{y}_i-y_i$ 로 정리하면,

$$\boxed{\frac{\partial L}{\partial b} = \frac{2}{n}\sum_{i=1}^{n} e_i = 2\,\text{mean}(e)}$$

**Step 3) 파라미터 업데이트 (경사하강법 규칙)**

학습률(learning rate) $\eta$(코드에서 `lr`)만큼, 기울기의 반대 방향으로 이동합니다.

$$a \leftarrow a - \eta \cdot \frac{\partial L}{\partial a}, \qquad b \leftarrow b - \eta \cdot \frac{\partial L}{\partial b}$$

상수 2는 학습률에 흡수시켜 실제 구현에서는 다음처럼 단순화해서 사용합니다(노트북 코드와 동일):

```python
y_hat = a * X + b
error = y_hat - y                  # e_i = y_hat_i - y_i

grad_a = np.mean(error * X)        # ∂L/∂a  (상수 2 생략, lr에 흡수)
grad_b = np.mean(error)            # ∂L/∂b  (상수 2 생략, lr에 흡수)

a -= lr * grad_a
b -= lr * grad_b
```

> 참고 — **정규방정식(Normal Equation)**: 위 두 편미분을 0으로 놓고 연립방정식을 풀면(=미분해서 최솟값을 한 번에 계산) 아래처럼 행렬식으로 $a, b$를 바로 구할 수 있습니다.
> $$\begin{bmatrix} b \\ a \end{bmatrix} = (X_b^{\top}X_b)^{-1}X_b^{\top}Y, \quad X_b = \begin{bmatrix}1 & x_1\\ 1& x_2\\ \vdots&\vdots\\ 1&x_n\end{bmatrix}$$
> 단점: 역행렬 계산 비용이 커서 피쳐(feature) 수가 많아지면 계산이 비효율적 → 경사하강법을 사용하는 이유.

### 4.2 로지스틱 회귀의 경사하강법 미분

**모델**: 시그모이드 함수를 사용해 확률을 예측합니다.

$$\hat{y}_i = \sigma(z_i), \quad z_i = ax_i+b, \quad \sigma(z) = \frac{1}{1+e^{-z}}$$

**손실함수(크로스 엔트로피)**:
$$L(a,b) = -\frac{1}{n}\sum_{i=1}^n \Big[y_i\log\hat{y}_i + (1-y_i)\log(1-\hat{y}_i)\Big]$$

이를 $a, b$에 대해 직접 미분하면 복잡해 보이지만, 시그모이드 함수의 도함수 성질 $\sigma'(z)=\sigma(z)(1-\sigma(z))$ 덕분에 **크로스 엔트로피 + 시그모이드** 조합은 놀랍도록 단순한 형태로 정리됩니다.

**Step 1) 크로스 엔트로피를 $\hat{y}$에 대해 미분**
$$\frac{\partial L}{\partial \hat{y}_i} = -\frac{1}{n}\left(\frac{y_i}{\hat{y}_i} - \frac{1-y_i}{1-\hat{y}_i}\right)$$

**Step 2) 시그모이드를 $z$에 대해 미분**
$$\frac{\partial \hat{y}_i}{\partial z_i} = \sigma(z_i)\big(1-\sigma(z_i)\big) = \hat{y}_i(1-\hat{y}_i)$$

**Step 3) 체인룰로 결합**
$$\frac{\partial L}{\partial z_i} = \frac{\partial L}{\partial \hat{y}_i}\cdot\frac{\partial \hat{y}_i}{\partial z_i} = -\frac{1}{n}\left(\frac{y_i}{\hat{y}_i}-\frac{1-y_i}{1-\hat{y}_i}\right)\hat{y}_i(1-\hat{y}_i)$$

괄호를 전개하면 $\hat{y}_i, (1-\hat{y}_i)$가 약분되어

$$\frac{\partial L}{\partial z_i} = \frac{1}{n}\big(\hat{y}_i-y_i\big)$$

즉, **예측 오차 $e_i=\hat{y}_i-y_i$ 그 자체**가 $z$에 대한 기울기가 됩니다 (MSE의 선형회귀 미분 결과와 형태가 완전히 동일!).

**Step 4) $z_i=ax_i+b$ 이므로 체인룰을 한 번 더 적용**
$$\frac{\partial z_i}{\partial a}=x_i, \qquad \frac{\partial z_i}{\partial b}=1$$

$$\boxed{\frac{\partial L}{\partial a} = \frac{1}{n}\sum_{i=1}^{n} e_i\, x_i = \text{mean}(e\cdot x)}$$
$$\boxed{\frac{\partial L}{\partial b} = \frac{1}{n}\sum_{i=1}^{n} e_i = \text{mean}(e)}$$

**Step 5) 업데이트**
$$a \leftarrow a-\eta\,\frac{\partial L}{\partial a}, \qquad b\leftarrow b-\eta\,\frac{\partial L}{\partial b}$$

노트북 코드 그대로:
```python
y_hat = sigmoid(a * X + b)
error = y_hat - y                 # e_i = y_hat_i - y_i

grad_a = np.mean(error * X)
grad_b = np.mean(error)

a -= lr * grad_a
b -= lr * grad_b
```

> **핵심 통찰**: 선형회귀(MSE)와 로지스틱회귀(크로스 엔트로피)는 손실함수도, 모델도 다르지만, 미분 후 얻어지는 기울기(gradient) 공식이 `mean(error * X)`, `mean(error)`로 **완전히 동일한 형태**가 됩니다. 이는 손실함수와 출력 활성화 함수(항등함수/시그모이드)를 짝지어 설계했기 때문이며, 신경망의 역전파(backpropagation) 원리를 이해하는 데 중요한 발판이 됩니다.

### 4.3 경사하강법의 한계와 개선 — Adam Optimizer
- 기본 경사하강법은 학습률만큼 매번 동일하게 "점프"하기 때문에, **지역 최소점(Local Minimum)**에 갇히거나 진동할 수 있음.
- **Adam**은 다음 아이디어로 더 똑똑하게 점프한다.
  - 이전 이동 방향과 같은 방향이면 관성을 적용해 조금 더 크게 이동
  - 방향이 자주 바뀌면(왔다갔다 하면) 점프 거리(학습률)를 줄임
- 신경망(딥러닝)에서는 기본 GD보다 Adam이 훨씬 널리 사용됨(이 자료에서는 수식·구현은 생략).

---

## 5. 선형 회귀 vs 로지스틱 회귀(분류) 비교

| 구분 | 선형 회귀 (Linear Regression) | 로지스틱 회귀 (Logistic Regression) |
|---|---|---|
| **목적** | 연속적인 **수치**를 예측 | 두 범주 중 하나에 속할 **확률**을 예측(이진 분류) |
| **출력 범위** | $(-\infty, \infty)$ 전체 실수 | $[0, 1]$ 사이의 확률값 |
| **모델식** | $\hat{y} = ax + b$ (직선/추세선) | $\hat{y} = \sigma(ax+b) = \dfrac{1}{1+e^{-(ax+b)}}$ (S자 곡선) |
| **활성화 함수** | 없음 (항등함수) | 시그모이드(sigmoid) 함수 |
| **손실함수** | MSE (평균 제곱 오차) | 크로스 엔트로피(Cross Entropy) |
| **최적해를 구하는 방법** | 정규방정식으로 **닫힌 형태(closed-form)** 해를 한 번에 계산 가능 | 크로스 엔트로피는 닫힌 형태 해가 없어 **경사하강법** 등 반복적 최적화가 필수 |
| **예시** | 음식값(total_bill) → 팁(tip) 금액 예측 | 공부 시간 → 합격/불합격 확률 예측 |
| **활용 분류 문제 예시** | (해당 없음) | 스팸 메일 여부, 암 진단 여부 등 이진 분류 |

**공통점**
- 둘 다 "$a, b$(파라미터)를 데이터로부터 찾아내는" 문제라는 점에서 본질적으로 동일한 구조.
- 둘 다 경사하강법으로 학습 가능하며, 미분 후 얻는 기울기 공식의 형태가 동일(`mean(error * X)`, `mean(error)`).
- 이름에 둘 다 "회귀(Regression)"가 들어가지만, 로지스틱 회귀는 실제로는 **분류(Classification)** 기법이라는 점에 주의.

---

## 6. 검증 및 평가 방법

노트북 자체는 입문 단계라 별도의 train/test 분리를 다루지는 않지만, 실전에서 선형회귀·로지스틱회귀 모델을 제대로 평가하려면 아래 절차와 지표들이 사용됩니다.

### 6.1 데이터 분할을 통한 검증
- **Train / Validation / Test 분할**: 학습에 사용한 데이터로만 평가하면 "외운" 성능(과적합, overfitting)인지 "일반화"된 성능인지 알 수 없음. 보통 전체 데이터를 학습용/검증용/테스트용으로 나누어 사용.
- **K-Fold 교차검증(Cross Validation)**: 데이터를 K개 그룹으로 나누어 매번 다른 그룹을 검증용으로 사용, K번 반복 평가하여 평균 성능을 봄. 데이터가 적을 때 특히 유용.
- 노트북에서 언급된 문구: *"모델은 반드시 주어지는 데이터에서 MSE가 최소가 되는 값일 필요가 없습니다. 처음 보는 데이터에도 잘 동작되기 위해서는 적절히 MSE가 적은 값이 필요"* — 이것이 바로 **일반화 성능**을 검증해야 하는 이유.

### 6.2 회귀(선형회귀) 평가지표
- **MAE**: 평균 절대 오차. 해석이 직관적(단위가 원본 데이터와 동일).
- **MSE / RMSE**: 평균 제곱 오차 / 그 제곱근. 큰 오차에 민감하게 반응.
- **$R^2$ (결정계수)**: 모델이 데이터의 분산을 얼마나 설명하는지(0~1에 가까울수록 좋음).

### 6.3 분류(로지스틱회귀) 평가지표
- **정확도(Accuracy)**: 전체 중 맞춘 비율. 클래스가 불균형할 경우 왜곡될 수 있음.
- **정밀도(Precision) / 재현율(Recall) / F1-score**: 클래스 불균형이 있는 경우(예: 암 진단) 정확도만으로는 부족하므로 함께 확인.
- **혼동행렬(Confusion Matrix)**: 실제/예측 클래스 조합별 개수를 표로 정리해 오류 유형을 파악.
- **ROC Curve / AUC**: 분류 임계값(threshold)을 바꿔가며 성능을 종합적으로 평가.
- **로그 손실(Cross Entropy / Log Loss)**: 확률 예측의 정밀도를 그대로 평가 지표로도 활용 가능.

### 6.4 학습 곡선을 통한 점검
- 노트북의 `epoch % 100 == 0` 마다 손실(loss/MSE)을 출력하는 코드처럼, **학습이 진행됨에 따라 손실이 잘 줄어드는지**를 관찰하는 것도 실전에서 중요한 검증 방법입니다.
- 학습 손실은 계속 줄어드는데 검증 손실이 다시 증가하기 시작하면 **과적합(overfitting)**의 신호로 간주하고 학습을 조기 종료(early stopping)하는 경우가 많습니다.

---

## 7. 마무리 요약

- 머신러닝은 데이터를 기반으로 모델(수식)의 파라미터를 최적화하는 과정이다.
- **선형회귀**: 연속값 예측, MSE 손실, 정규방정식 또는 경사하강법으로 학습.
- **로지스틱회귀**: 이진 분류(확률 예측), 시그모이드 + 크로스 엔트로피 손실, 경사하강법으로 학습(닫힌 해 없음).
- **경사하강법**은 손실함수를 파라미터에 대해 미분(기울기 계산) → 기울기의 반대 방향으로 파라미터를 조금씩 이동(학습률만큼) → 반복하여 손실을 최소화하는 방법이며, Adam 같은 개선된 옵티마이저가 실전에서 널리 쓰인다.
- 실전에서는 학습 데이터에서의 손실 최소화뿐 아니라, **검증/테스트 데이터에서의 일반화 성능**을 함께 확인해야 한다.

이 내용은 이후 신경망(딥러닝)을 배울 때의 기반 지식이 됩니다.
