---
marp: true
theme: gaia
paginate: true
header: 'NumPy 핵심 개념과 주요 기능'
footer: '데이터 수집·전처리·분석 교육과정 — Part 1 / 3'
style: |
  section { font-size: 26px; }
  section.lead { text-align: center; }
  code { font-size: 0.9em; }
  pre { font-size: 0.78em; line-height: 1.35; }
  table { font-size: 0.85em; }
---

<!-- _class: lead -->

# NumPy
## 수치 계산(Numerical Computing)의 기초

**데이터 수집·전처리·분석 교육과정 Part 1**
소요 시간: 약 2시간 | 대상: Python 중급

---

## 학습 목표 (Learning Objectives)

- `ndarray`의 구조와 동작 원리를 이해한다
- 배열 생성, 인덱싱(indexing), 슬라이싱(slicing)을 자유롭게 다룬다
- 브로드캐스팅(broadcasting)과 벡터화(vectorization)를 활용한다
- 집계(aggregation), 선형대수(linear algebra), 난수(random) 기능을 사용한다
- **ML 연계**: 텐서(tensor) 연산의 기반인 NumPy를 이해하면
  scikit-learn, PyTorch, TensorFlow의 데이터 구조가 그대로 보인다

---

## 목차 (Agenda)

1. NumPy를 쓰는 이유
2. ndarray 생성과 속성
3. 인덱싱과 슬라이싱
4. 형태 변경 (Reshape)
5. 벡터화 연산과 유니버설 함수 (ufunc)
6. 브로드캐스팅 (Broadcasting)
7. 집계 함수와 axis
8. 정렬·검색·조건 연산
9. 배열 결합과 분리
10. 난수와 선형대수
11. 실습: ML 전처리 미니 시나리오

---

<!-- _class: lead -->

# 1. NumPy를 쓰는 이유

---

## 순수 Python 리스트의 한계

```python
# 100만 개 원소를 모두 2배로
data = list(range(1_000_000))

result = [x * 2 for x in data]      # 반복문 기반: 느림
```

- Python 리스트: 각 원소가 **개별 객체** → 메모리 낭비, 캐시 비효율
- 반복문은 인터프리터가 한 스텝씩 실행 → C 대비 수십~수백 배 느림

```python
import numpy as np
arr = np.arange(1_000_000)
result = arr * 2                    # C로 구현된 벡터 연산: 10~100배 빠름
```

---

## ndarray의 핵심: 연속 메모리 + 단일 타입

| | Python list | NumPy ndarray |
|---|---|---|
| 원소 타입 | 자유 (혼합 가능) | **단일 dtype** |
| 메모리 배치 | 포인터 배열 | **연속(contiguous) 블록** |
| 연산 방식 | 반복문 | **벡터화 (C 루프)** |
| ML 사용 | ✗ | scikit-learn/DL 입력 표준 |

**ML 연계**: 학습 데이터 `X`는 항상 `(샘플 수, 특성 수)` 형태의
2차원 ndarray — 이 구조가 모든 ML 라이브러리의 공용어다.

---

<!-- _class: lead -->

# 2. ndarray 생성과 속성

---

## 배열 생성하기 — `np.array`

```python
import numpy as np

a = np.array([1, 2, 3])                # 1차원 (vector)
b = np.array([[1, 2, 3],
              [4, 5, 6]])              # 2차원 (matrix)

print(a.ndim, a.shape, a.dtype)        # 1 (3,) int64
print(b.ndim, b.shape, b.dtype)        # 2 (2, 3) int64
```

핵심 속성 3가지:
- `ndim` — 차원 수 (number of dimensions)
- `shape` — 각 차원의 크기 튜플
- `dtype` — 원소의 자료형 (data type)

---

## 자동 생성 함수들

```python
np.zeros((2, 3))          # 0으로 채운 2×3
np.ones((3, 3))           # 1로 채운 3×3
np.full((2, 2), 7)        # 7로 채운 2×2
np.eye(3)                 # 3×3 단위 행렬 (identity)

np.arange(0, 10, 2)       # [0 2 4 6 8]  — range와 유사
np.linspace(0, 1, 5)      # [0. 0.25 0.5 0.75 1.]  — 구간 균등 분할
```

**ML 연계**: 가중치 초기화(`zeros`, 난수), 학습률 스케줄(`linspace`),
에폭 인덱스(`arange`) 등 도처에서 사용된다.

---

## dtype — 자료형 이해하기

```python
a = np.array([1, 2, 3], dtype=np.float32)
print(a.dtype)                  # float32

b = np.array([1.7, 2.9])
c = b.astype(np.int64)          # [1 2]  — 소수점 버림 (truncation)
```

| dtype | 용도 |
|---|---|
| `int32`, `int64` | 정수 라벨, 인덱스 |
| `float32` | **딥러닝 표준** (GPU 메모리 절약) |
| `float64` | NumPy 기본 실수형 |
| `bool` | 마스크(mask), 조건 필터 |

**ML 연계**: DL 프레임워크는 `float32`가 기본 — `astype` 변환이 잦다.

---

## 따라하기 ①

```python
import numpy as np

# 1. 0~19 정수로 이루어진 (4, 5) 행렬을 만드세요
m = np.arange(20).reshape(4, 5)

# 2. 형태·차원·타입을 확인하세요
print(m.shape, m.ndim, m.dtype)     # (4, 5) 2 int64

# 3. float32로 변환하세요
m32 = m.astype(np.float32)
print(m32.dtype)                    # float32
```

---

<!-- _class: lead -->

# 3. 인덱싱과 슬라이싱
## Indexing & Slicing

---

## 기본 인덱싱

```python
m = np.arange(20).reshape(4, 5)
# [[ 0  1  2  3  4]
#  [ 5  6  7  8  9]
#  [10 11 12 13 14]
#  [15 16 17 18 19]]

m[1, 2]        # 7      — 행 1, 열 2 (쉼표 하나로!)
m[1][2]        # 7      — 동작하지만 비효율
m[-1, -1]      # 19     — 음수 인덱스
```

`m[행, 열]` 표기가 NumPy 스타일 — pandas의 `iloc`도 동일한 문법.

---

## 슬라이싱 — 부분 배열 추출

```python
m[0:2, 1:3]    # 행 0~1, 열 1~2
# [[1 2]
#  [6 7]]

m[:, 0]        # 첫 번째 열 전체 → [ 0  5 10 15]
m[2, :]        # 세 번째 행 전체 → [10 11 12 13 14]
m[::2]         # 짝수 행만
```

⚠️ **슬라이스는 뷰(view)** — 복사가 아니라 원본을 가리킨다!

```python
sub = m[0:2, 0:2]
sub[0, 0] = 999          # 원본 m도 함께 바뀜
safe = m[0:2, 0:2].copy()  # 독립 복사본이 필요하면 .copy()
```

---

## 불리언 마스킹 (Boolean Masking)

```python
scores = np.array([72, 95, 61, 88, 45, 90])

mask = scores >= 80          # [False True False True False True]
scores[mask]                 # [95 88 90]

scores[scores < 60] = 60     # 조건에 맞는 원소만 수정 (하한 클리핑)
```

**ML 연계**: 이상치(outlier) 제거, 특정 클래스 샘플만 추출,
결측 구간 필터링 — 전처리의 절반은 불리언 마스킹이다.

```python
X_positive = X[y == 1]       # 라벨이 1인 샘플만 선택
```

---

## 팬시 인덱싱 (Fancy Indexing)

```python
a = np.array([10, 20, 30, 40, 50])

idx = [0, 2, 4]
a[idx]                    # [10 30 50] — 인덱스 배열로 선택

m = np.arange(12).reshape(3, 4)
m[[0, 2], :]              # 행 0과 2만
m[[0, 1, 2], [1, 2, 3]]   # (0,1), (1,2), (2,3) 원소들
```

**ML 연계**: 데이터 셔플링(shuffling)의 핵심 패턴

```python
perm = np.random.permutation(len(X))
X_shuffled, y_shuffled = X[perm], y[perm]   # 같은 순서로 섞기
```

---

## 따라하기 ②

```python
np.random.seed(0)
scores = np.random.randint(0, 101, size=20)   # 학생 20명 점수

# 1. 80점 이상 학생 수는?
print((scores >= 80).sum())

# 2. 60점 미만 점수를 모두 60으로 올리세요
scores[scores < 60] = 60

# 3. 상위 5명의 점수를 출력하세요 (힌트: np.sort / argsort)
top5 = np.sort(scores)[-5:][::-1]
print(top5)
```

---

<!-- _class: lead -->

# 4. 형태 변경
## Reshape & Transpose

---

## reshape — 데이터는 그대로, 모양만 변경

```python
a = np.arange(12)          # shape (12,)

a.reshape(3, 4)            # (3, 4)
a.reshape(4, -1)           # (4, 3)  — -1은 "자동 계산"
a.reshape(2, 2, 3)         # 3차원도 가능
```

```python
a.flatten()                # 1차원으로 펴기 (복사본)
a.ravel()                  # 1차원으로 펴기 (가능하면 뷰)
```

**ML 연계**: 이미지 `(28, 28)` → `(784,)` 펼치기(flatten)는
신경망 입력층의 고전적 전처리다.

---

## 전치(Transpose)와 축 추가

```python
m = np.arange(6).reshape(2, 3)
m.T                        # (3, 2) — 행↔열 교환

v = np.array([1, 2, 3])            # shape (3,)
v[np.newaxis, :]                   # (1, 3) — 행 벡터
v[:, np.newaxis]                   # (3, 1) — 열 벡터
v.reshape(-1, 1)                   # (3, 1) — 같은 결과
```

**ML 연계**: scikit-learn은 특성 1개짜리 입력도 반드시 2차원을 요구

```python
model.fit(x.reshape(-1, 1), y)     # (n,) → (n, 1) 필수 관용구
```

---

<!-- _class: lead -->

# 5. 벡터화 연산과 ufunc

---

## 반복문 대신 벡터화 (Vectorization)

```python
a = np.array([1, 2, 3, 4])
b = np.array([10, 20, 30, 40])

a + b        # [11 22 33 44]   원소별(element-wise) 연산
a * b        # [10 40 90 160]
a ** 2       # [ 1  4  9 16]
a > 2        # [False False True True]
```

같은 위치의 원소끼리 계산 — **반복문이 코드에서 사라진다.**

```python
# 섭씨 → 화씨: 반복문 없이 한 줄
fahrenheit = celsius * 9 / 5 + 32
```

---

## 유니버설 함수 (Universal Functions, ufunc)

```python
x = np.array([1., 4., 9.])

np.sqrt(x)         # [1. 2. 3.]
np.exp(x)          # 지수
np.log(x)          # 자연로그
np.abs(x)          # 절댓값
np.round(x, 2)     # 반올림
np.clip(x, 2, 8)   # [2. 4. 8.] — 범위 제한
```

**ML 연계**: 활성화 함수를 직접 만들어 보면 ufunc의 가치가 보인다

```python
def sigmoid(z):
    return 1 / (1 + np.exp(-z))     # 어떤 shape가 와도 동작
```

---

<!-- _class: lead -->

# 6. 브로드캐스팅
## Broadcasting

---

## 서로 다른 shape끼리의 연산 규칙

```python
m = np.arange(6).reshape(2, 3)   # (2, 3)
m + 10                            # 스칼라 → 전체에 적용

v = np.array([100, 200, 300])     # (3,)
m + v                             # (2,3) + (3,) → 각 행에 v를 더함
# [[100 201 302]
#  [103 204 305]]
```

**규칙**: 뒤쪽 차원부터 비교하여
① 크기가 같거나 ② 한쪽이 1이면 → 자동 확장(stretch)

---

## 브로드캐스팅 실전: 표준화 (Standardization)

```python
# X: (샘플 100개, 특성 4개)
X = np.random.randn(100, 4) * [10, 2, 5, 1] + [50, 0, 30, 5]

mean = X.mean(axis=0)      # (4,)  특성별 평균
std  = X.std(axis=0)       # (4,)  특성별 표준편차

X_scaled = (X - mean) / std        # (100,4)-(4,) 브로드캐스팅!
```

**ML 연계**: 이 세 줄이 곧 `sklearn.preprocessing.StandardScaler`의
내부 동작이다. 스케일링은 거의 모든 ML 모델의 첫 전처리 단계.

---

## 따라하기 ③

```python
np.random.seed(42)
X = np.random.randint(0, 100, size=(5, 3)).astype(float)

# 1. 각 열(특성)의 평균과 표준편차를 구하세요
mu, sigma = X.mean(axis=0), X.std(axis=0)

# 2. 표준화하세요 (평균 0, 표준편차 1)
Xs = (X - mu) / sigma

# 3. 검증: 표준화 결과의 평균≈0, 표준편차≈1 인지 확인
print(Xs.mean(axis=0).round(6))    # [0. 0. 0.]
print(Xs.std(axis=0).round(6))     # [1. 1. 1.]
```

---

<!-- _class: lead -->

# 7. 집계 함수와 axis

---

## 집계 (Aggregation)

```python
m = np.arange(1, 7).reshape(2, 3)
# [[1 2 3]
#  [4 5 6]]

m.sum()          # 21     — 전체
m.sum(axis=0)    # [5 7 9]  — 열 방향으로 합침 (행들을 접음)
m.sum(axis=1)    # [6 15]   — 행 방향으로 합침 (열들을 접음)
```

`axis=0` → **행 축을 따라** 계산 = 각 **열**의 결과
`axis=1` → **열 축을 따라** 계산 = 각 **행**의 결과

암기 팁: **"axis는 사라지는 축"** — `(2,3)`에서 `axis=0`이면 2가 사라져 `(3,)`

---

## 주요 집계 함수 모음

```python
m.mean(), m.std(), m.var()       # 평균, 표준편차, 분산
m.min(),  m.max()                # 최소, 최대
m.argmin(), m.argmax()           # 최소/최대의 "위치(index)"
np.median(m)                     # 중앙값
np.percentile(m, 75)             # 백분위수
m.cumsum()                       # 누적합
```

**ML 연계**: `argmax`는 분류 모델의 최종 예측 그 자체

```python
probs = np.array([[0.1, 0.7, 0.2],
                  [0.6, 0.3, 0.1]])
pred = probs.argmax(axis=1)      # [1 0] — 샘플별 예측 클래스
```

---

<!-- _class: lead -->

# 8. 정렬·검색·조건 연산

---

## 정렬과 argsort

```python
a = np.array([30, 10, 50, 20])

np.sort(a)          # [10 20 30 50]  — 복사본 정렬
a.sort()            # 원본을 직접 정렬 (in-place)
a.argsort()         # 정렬했을 때의 원본 인덱스
```

```python
# 성적 내림차순으로 이름 정렬하기
names  = np.array(['kim', 'lee', 'park'])
scores = np.array([88, 95, 72])
names[scores.argsort()[::-1]]    # ['lee' 'kim' 'park']
```

**ML 연계**: 특성 중요도(feature importance) 상위 k개 추출에 필수.

---

## np.where — 조건 삼항 연산

```python
scores = np.array([72, 95, 61, 88, 45])

np.where(scores >= 70, '합격', '불합격')
# ['합격' '합격' '불합격' '합격' '불합격']

np.where(scores >= 70)           # 조건 만족 인덱스: (array([0,1,3]),)
```

```python
# ML: 확률 → 이진 예측 (threshold)
proba = np.array([0.2, 0.85, 0.55, 0.4])
pred = np.where(proba >= 0.5, 1, 0)     # [0 1 1 0]
```

관련 함수: `np.any()`, `np.all()`, `np.isnan()`, `np.unique()`

---

## 결측값(NaN) 다루기

```python
a = np.array([1.0, np.nan, 3.0, np.nan, 5.0])

np.isnan(a)              # [False True False True False]
np.isnan(a).sum()        # 2 — 결측 개수

a.mean()                 # nan!  — NaN이 하나라도 있으면 오염
np.nanmean(a)            # 3.0   — NaN 무시 버전
a[~np.isnan(a)]          # NaN 제거
```

**ML 연계**: 결측값이 남아 있으면 대부분의 모델이 에러를 낸다.
`np.isnan` 점검은 전처리 마지막 관문 — pandas에서 더 깊게 다룬다.

---

<!-- _class: lead -->

# 9. 배열 결합과 분리

---

## concatenate / stack / split

```python
a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])

np.concatenate([a, b], axis=0)   # 위아래로 붙임 (4, 2)
np.concatenate([a, b], axis=1)   # 좌우로 붙임   (2, 4)
np.vstack([a, b])                # axis=0 단축형
np.hstack([a, b])                # axis=1 단축형
```

```python
x = np.arange(10)
np.split(x, [6, 8])    # [0:6], [6:8], [8:] 세 조각으로 분리
```

**ML 연계**: 특성 행렬에 새 특성 열 추가(`hstack`),
train/test 분할(`split`)의 기본 도구.

---

<!-- _class: lead -->

# 10. 난수와 선형대수

---

## 난수 생성 (Random)

```python
rng = np.random.default_rng(seed=42)    # 권장: Generator 방식

rng.random((2, 3))            # 0~1 균등분포 (uniform)
rng.normal(0, 1, size=100)    # 정규분포 (평균 0, 표준편차 1)
rng.integers(0, 10, size=5)   # 정수 난수
rng.choice([1, 2, 3], size=5) # 샘플링
rng.permutation(10)           # 0~9 무작위 순열
```

**시드(seed) 고정 = 재현성(reproducibility)**
**ML 연계**: 실험 재현을 위해 모든 ML 코드는 시드 고정으로 시작한다.
가중치 초기화·데이터 분할·증강 모두 난수 기반.

---

## 선형대수 (Linear Algebra)

```python
A = np.array([[1, 2], [3, 4]])
v = np.array([1, 0])

A @ v                    # 행렬-벡터 곱 → [1 3]
A @ A                    # 행렬 곱 (matrix multiplication)
np.dot(A, v)             # @와 동일

np.linalg.inv(A)         # 역행렬 (inverse)
np.linalg.det(A)         # 행렬식 (determinant)
np.linalg.norm(v)        # 노름 (거리)
```

⚠️ `A * B`는 원소별 곱, `A @ B`가 행렬 곱 — 혼동 주의!

---

## 선형대수 실전: 선형 회귀를 손으로

```python
rng = np.random.default_rng(0)
X = rng.random((100, 1)) * 10
y = 3 * X[:, 0] + 5 + rng.normal(0, 1, 100)   # y = 3x + 5 + 잡음

Xb = np.hstack([X, np.ones((100, 1))])         # 절편항 추가

# 정규방정식 (Normal Equation): w = (XᵀX)⁻¹ Xᵀy
w = np.linalg.inv(Xb.T @ Xb) @ Xb.T @ y
print(w)        # ≈ [3.0, 5.0] — 기울기와 절편 복원!
```

**ML 연계**: `sklearn.linear_model.LinearRegression`의 수학적 본질.
NumPy만으로 ML 알고리즘의 뼈대를 구현할 수 있다.

---

<!-- _class: lead -->

# 11. 종합 실습
## ML 전처리 미니 시나리오

---

## 시나리오: 학습 데이터 준비 파이프라인

가상의 센서 데이터 → 정제 → 표준화 → 분할까지 NumPy만으로.

```python
rng = np.random.default_rng(7)

# 1) 데이터 수집 (가상): 샘플 200개, 특성 3개 + 라벨
X = rng.normal([20, 50, 0.5], [5, 15, 0.1], size=(200, 3))
y = (X[:, 0] + X[:, 2] * 40 > 40).astype(int)

# 2) 결측 주입 후 처리
X[rng.integers(0, 200, 10), 0] = np.nan
col_mean = np.nanmean(X[:, 0])
X[np.isnan(X[:, 0]), 0] = col_mean          # 평균 대치 (imputation)
```

---

## 시나리오 (계속): 표준화와 분할

```python
# 3) 이상치 클리핑: 1~99 백분위수 범위로 제한
lo, hi = np.percentile(X, [1, 99], axis=0)
X = np.clip(X, lo, hi)

# 4) 표준화 (Standardization)
X = (X - X.mean(axis=0)) / X.std(axis=0)

# 5) 셔플 후 train/test 8:2 분할
perm = rng.permutation(len(X))
X, y = X[perm], y[perm]
split = int(len(X) * 0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

print(X_train.shape, X_test.shape)    # (160, 3) (40, 3)
```

---

## 정리 (Summary)

| 개념 | 핵심 API | ML에서의 역할 |
|---|---|---|
| 배열 생성 | `array` `arange` `zeros` | 데이터/가중치 컨테이너 |
| 인덱싱 | 마스킹, 팬시 인덱싱 | 필터링, 셔플링 |
| 형태 변경 | `reshape` `T` | 모델 입력 규격 맞추기 |
| 브로드캐스팅 | shape 규칙 | 스케일링 한 줄 구현 |
| 집계 | `mean` `argmax` + `axis` | 통계량, 예측 클래스 |
| 선형대수 | `@` `linalg` | 모델의 수학적 기반 |

**다음 파트**: pandas — 표 형태(tabular) 데이터의 수집과 전처리

---

<!-- _class: lead -->

# Q&A

**참고 자료**
NumPy 공식 문서: numpy.org/doc
NumPy for Absolute Beginners: numpy.org/doc/stable/user/absolute_beginners.html
