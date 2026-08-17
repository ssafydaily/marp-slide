---
marp: true
theme: gaia
paginate: true
header: 'Matplotlib 핵심 개념과 주요 기능'
footer: '데이터 수집·전처리·분석 교육과정 — Part 3 / 3'
style: |
  section { font-size: 26px; }
  section.lead { text-align: center; }
  code { font-size: 0.9em; }
  pre { font-size: 0.78em; line-height: 1.35; }
  table { font-size: 0.85em; }
---

<!-- _class: lead -->

# Matplotlib
## 데이터와 모델 결과의 시각화 (Visualization)

**데이터 수집·전처리·분석 교육과정 Part 3**
소요 시간: 약 1.5~2시간 | 대상: Python 중급

---

## 학습 목표 (Learning Objectives)

- Figure / Axes 구조와 객체지향(OO) API를 이해한다
- 선(line)·산점도(scatter)·막대(bar)·히스토그램(histogram) 등
  기본 차트를 그린다
- 제목·축·범례·주석으로 그래프를 완성도 있게 꾸민다
- 서브플롯(subplot)으로 다중 그래프를 배치한다
- **ML 연계**: EDA 분포 확인, 학습 곡선(learning curve),
  혼동 행렬(confusion matrix) 등 모델링 전 과정의 눈이 된다

---

## 목차 (Agenda)

1. Matplotlib의 구조: Figure와 Axes
2. 기본 차트 5종
3. 스타일링: 색·마커·선
4. 라벨·범례·주석
5. 한글 폰트 설정
6. 서브플롯 (Subplots)
7. pandas와의 연동
8. 이미지와 히트맵
9. ML 시각화 실전 3종
10. 저장과 마무리

---

<!-- _class: lead -->

# 1. Matplotlib의 구조

---

## Figure와 Axes — 도화지와 좌표평면

```
Figure (전체 캔버스)
 └── Axes (그래프 1개 영역)
      ├── title, xlabel, ylabel
      ├── xaxis / yaxis (눈금, tick)
      └── plot 요소들 (선, 점, 막대...)
```

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 5))    # Figure + Axes 동시 생성
ax.plot([1, 2, 3], [2, 4, 3])
plt.show()
```

- **Figure** = 창(도화지), **Axes** = 실제 그래프가 그려지는 좌표 영역
- Axes ≠ Axis(축) — 이름 주의!

---

## 두 가지 API: pyplot vs 객체지향(OO)

```python
# pyplot 스타일 — 빠른 확인용
plt.plot(x, y)
plt.title('Result')
plt.show()

# 객체지향(OO) 스타일 — 권장 ★
fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_title('Result')
plt.show()
```

한 화면에 여러 그래프를 다루기 시작하면 OO 스타일이 필수 —
**이 교육과정은 OO 스타일로 통일한다.**

---

<!-- _class: lead -->

# 2. 기본 차트 5종

---

## 선 그래프 (Line Plot) — 추세와 변화

```python
import numpy as np
x = np.linspace(0, 10, 100)

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x, np.sin(x), label='sin')
ax.plot(x, np.cos(x), label='cos', linestyle='--')
ax.legend()
ax.set_title('Trigonometric Functions')
plt.show()
```

**용도**: 시간에 따른 변화, 시계열, **학습 곡선(epoch별 loss)**

**ML 연계**: 훈련 중 loss/accuracy 추적 그래프가 대표적 선 그래프.

---

## 산점도 (Scatter Plot) — 두 변수의 관계

```python
rng = np.random.default_rng(0)
x = rng.normal(170, 8, 200)               # 키
y = x * 0.9 - 90 + rng.normal(0, 5, 200)  # 몸무게

fig, ax = plt.subplots()
ax.scatter(x, y, alpha=0.5, s=30)
ax.set_xlabel('Height (cm)')
ax.set_ylabel('Weight (kg)')
```

`alpha`(투명도)로 겹침 표현, `s`로 점 크기, `c`로 색 매핑.

**ML 연계**: 특성 간 상관관계 확인, 군집(cluster) 시각화,
`c=y`로 클래스별 색을 입히면 **분류 문제의 분리 가능성**이 보인다.

---

## 막대 그래프 (Bar Chart) — 범주 비교

```python
cities = ['Seoul', 'Busan', 'Daegu', 'Incheon']
values = [9.7, 3.3, 2.4, 3.0]

fig, ax = plt.subplots()
ax.bar(cities, values, color='steelblue')
ax.set_ylabel('Population (M)')

ax.barh(cities, values)      # 가로 막대 — 라벨 길 때 유용
```

**ML 연계**: 특성 중요도(feature importance) 시각화의 표준.
가로 막대 + 중요도 내림차순 정렬이 관용 패턴.

---

## 히스토그램 (Histogram) — 분포 확인

```python
data = rng.normal(70, 12, 1000)     # 시험 점수 분포

fig, ax = plt.subplots()
ax.hist(data, bins=30, edgecolor='white')
ax.axvline(data.mean(), color='red', linestyle='--', label='mean')
ax.legend()
```

`bins` 개수에 따라 인상이 달라진다 — 여러 값을 시도해 볼 것.

**ML 연계**: 전처리 전 필수 확인 —
분포가 심하게 치우쳤으면(skewed) 로그 변환, 이상치가 보이면 클리핑.

---

## 박스 플롯 (Box Plot) — 분포 요약과 이상치

```python
groups = [rng.normal(70, 8, 100),
          rng.normal(75, 15, 100),
          rng.normal(65, 5, 100)]

fig, ax = plt.subplots()
ax.boxplot(groups, labels=['A', 'B', 'C'])
```

상자 = 사분위수(IQR), 수염 밖 점 = **이상치(outlier) 후보**

**ML 연계**: 그룹 간 분포 비교(예: 클래스별 특성 분포)와
이상치 탐지를 한 그림으로 — EDA 단골 차트.

---

## 따라하기 ①

```python
rng = np.random.default_rng(42)
scores = rng.normal(72, 15, 500).clip(0, 100)

# 1. 히스토그램을 bins=20으로 그리세요
fig, ax = plt.subplots()
ax.hist(scores, bins=20, edgecolor='white')

# 2. 평균선(빨강 점선)과 중앙값선(파랑 점선)을 추가하세요
ax.axvline(scores.mean(), color='red', linestyle='--', label='mean')
ax.axvline(np.median(scores), color='blue', linestyle='--', label='median')

# 3. 제목과 범례를 붙이세요
ax.set_title('Score Distribution')
ax.legend()
plt.show()
```

---

<!-- _class: lead -->

# 3. 스타일링

---

## 색·마커·선 스타일

```python
ax.plot(x, y,
        color='tomato',          # 색 이름, '#FF6347', 'C0'~'C9'
        linestyle='--',          # '-' '--' ':' '-.'
        linewidth=2,
        marker='o',              # 'o' 's' '^' 'x' '.'
        markersize=6,
        alpha=0.8)

ax.plot(x, y, 'ro--')            # 축약형: 빨강+원+점선
```

```python
plt.style.use('ggplot')          # 전역 스타일 프리셋
# 'seaborn-v0_8', 'bmh', 'fivethirtyeight', 'dark_background' ...
```

색은 3~4가지 이내로 절제 — 많을수록 읽기 어렵다.

---

<!-- _class: lead -->

# 4. 라벨·범례·주석

---

## 그래프를 "읽을 수 있게" 만드는 요소들

```python
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(epochs, loss, label='train loss')
ax.plot(epochs, val_loss, label='val loss')

ax.set_title('Training Curve', fontsize=14)
ax.set_xlabel('Epoch')
ax.set_ylabel('Loss')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 50)
ax.set_ylim(0, None)
```

**체크리스트**: 제목 / 축 라벨(단위 포함) / 범례 / 격자
— 넷 중 하나라도 없으면 남에게 보여줄 그래프가 아니다.

---

## 주석 (Annotation)

```python
best = np.argmin(val_loss)
ax.annotate(f'best epoch = {best}',
            xy=(best, val_loss[best]),          # 가리킬 지점
            xytext=(best + 5, val_loss[best] + 0.1),  # 텍스트 위치
            arrowprops=dict(arrowstyle='->'))

ax.text(0.5, 0.9, 'overfitting starts here',
        transform=ax.transAxes)     # 축 비율 좌표 (0~1)
```

**ML 연계**: 최적 에폭, 과적합(overfitting) 시작점 등
"이 그래프에서 봐야 할 지점"을 명시하는 도구.

---

## 한글 폰트 설정

```python
import matplotlib.pyplot as plt

# Windows
plt.rcParams['font.family'] = 'Malgun Gothic'
# macOS
plt.rcParams['font.family'] = 'AppleGothic'
# Colab / Linux (나눔폰트 설치 후)
# !apt-get install -y fonts-nanum
plt.rcParams['font.family'] = 'NanumGothic'

plt.rcParams['axes.unicode_minus'] = False   # 음수 부호 깨짐 방지
```

한글이 `□□□`로 보이면 100% 폰트 문제 — 위 설정을 스크립트 최상단에.

---

<!-- _class: lead -->

# 5. 서브플롯
## 여러 그래프를 한 화면에

---

## plt.subplots(nrows, ncols)

```python
fig, axes = plt.subplots(2, 2, figsize=(10, 8))

axes[0, 0].plot(x, y1);        axes[0, 0].set_title('Line')
axes[0, 1].scatter(x, y2);     axes[0, 1].set_title('Scatter')
axes[1, 0].hist(data);         axes[1, 0].set_title('Hist')
axes[1, 1].bar(cats, vals);    axes[1, 1].set_title('Bar')

fig.suptitle('EDA Overview', fontsize=16)
fig.tight_layout()             # 겹침 자동 정리 ★
```

```python
# 특성이 많을 때: 반복문으로 전 특성 분포 확인
fig, axes = plt.subplots(1, 4, figsize=(16, 3))
for ax, col in zip(axes, df.columns):
    ax.hist(df[col], bins=20)
    ax.set_title(col)
```

---

<!-- _class: lead -->

# 6. pandas와의 연동

---

## DataFrame.plot — 가장 빠른 시각화 경로

```python
df['age'].hist(bins=20)                        # Series → 히스토그램
df.plot(x='age', y='fare', kind='scatter')     # 산점도
df['city'].value_counts().plot(kind='bar')     # 빈도 막대

df.groupby('pclass')['survived'].mean().plot(
    kind='bar', color='steelblue',
    title='Survival Rate by Class')
```

내부적으로 Matplotlib을 호출 — `ax`를 받아 이어서 꾸밀 수 있다:

```python
ax = df['age'].hist(bins=20)
ax.set_xlabel('Age')
```

**ML 연계**: `groupby` 결과 → `.plot()` 한 줄이 EDA의 80%를 해결한다.

---

<!-- _class: lead -->

# 7. 이미지와 히트맵

---

## imshow — 행렬을 그림으로

```python
# 이미지 표시 (예: MNIST 손글씨)
fig, ax = plt.subplots()
ax.imshow(digit_28x28, cmap='gray')
ax.axis('off')

# 상관관계 히트맵 (heatmap)
corr = df.corr(numeric_only=True)
fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
ax.set_xticks(range(len(corr)), corr.columns, rotation=45)
ax.set_yticks(range(len(corr)), corr.columns)
fig.colorbar(im)
```

**ML 연계**: 상관 히트맵으로 중복 특성(다중공선성)을 찾아 제거하고,
`imshow`로 이미지 데이터·필터·혼동 행렬을 확인한다.

---

<!-- _class: lead -->

# 8. ML 시각화 실전 3종

---

## ① 학습 곡선 (Learning Curve)

```python
epochs = np.arange(1, 51)
train_loss = 2.0 * np.exp(-epochs / 10) + 0.1
val_loss = 2.0 * np.exp(-epochs / 12) + 0.15 + \
           np.maximum(0, (epochs - 30) * 0.01)   # 30 이후 과적합

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(epochs, train_loss, label='train')
ax.plot(epochs, val_loss, label='validation')
ax.axvline(30, color='gray', linestyle=':', label='overfit point')
ax.set_xlabel('Epoch'); ax.set_ylabel('Loss')
ax.legend(); ax.grid(alpha=0.3)
```

train은 계속 내려가는데 val이 다시 오른다 → **과적합의 신호**.
딥러닝 훈련 모니터링의 가장 기본이 되는 그래프.

---

## ② 혼동 행렬 (Confusion Matrix)

```python
cm = np.array([[50,  5],
               [ 8, 37]])       # 실제×예측 집계표

fig, ax = plt.subplots(figsize=(4, 4))
im = ax.imshow(cm, cmap='Blues')
for i in range(2):
    for j in range(2):
        ax.text(j, i, cm[i, j], ha='center', va='center', fontsize=16)
ax.set_xticks([0, 1], ['Pred 0', 'Pred 1'])
ax.set_yticks([0, 1], ['True 0', 'True 1'])
ax.set_title('Confusion Matrix')
```

분류 모델 평가의 표준 — 어떤 클래스를 어떻게 틀리는지 한눈에.
(`sklearn.metrics.ConfusionMatrixDisplay`가 같은 그림을 자동 생성)

---

## ③ 특성 중요도 (Feature Importance)

```python
features = ['fare', 'age', 'sex', 'pclass', 'family_size']
importance = np.array([0.31, 0.26, 0.22, 0.14, 0.07])

order = importance.argsort()             # NumPy 복습!
fig, ax = plt.subplots(figsize=(7, 4))
ax.barh(np.array(features)[order], importance[order],
        color='steelblue')
ax.set_xlabel('Importance')
ax.set_title('Feature Importance')
```

가로 막대 + 오름차순 정렬(위가 최대) — 이 조합이 관용 패턴.
모델이 **무엇을 근거로 판단하는지** 설명할 때 필수.

---

## 따라하기 ② — 종합

```python
# Titanic으로 2×2 EDA 대시보드를 만드세요
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

df['age'].hist(bins=25, ax=axes[0, 0], edgecolor='white')
axes[0, 0].set_title('Age Distribution')

df.groupby('pclass')['survived'].mean().plot(
    kind='bar', ax=axes[0, 1], title='Survival by Class')

axes[1, 0].scatter(df['age'], df['fare'],
                   c=df['survived'], cmap='coolwarm', alpha=0.5)
axes[1, 0].set_title('Age vs Fare (color = survived)')

axes[1, 1].boxplot([df[df.survived == 0]['fare'].dropna(),
                    df[df.survived == 1]['fare'].dropna()],
                   labels=['died', 'survived'])
axes[1, 1].set_title('Fare by Survival')
fig.tight_layout()
```

---

<!-- _class: lead -->

# 9. 저장과 마무리

---

## 그림 저장하기

```python
fig.savefig('result.png', dpi=150, bbox_inches='tight')
fig.savefig('result.svg')                  # 벡터 — 보고서/논문용
fig.savefig('result.png', transparent=True)
```

- `dpi` — 해상도 (기본 100, 문서용 150~300)
- `bbox_inches='tight'` — 여백 잘림 방지 (거의 항상 사용)

**ML 연계**: 실험마다 학습 곡선·평가 그림을 파일로 남기는 습관 =
실험 추적(experiment tracking)의 출발점.

---

## 전체 과정 정리 (Course Summary)

| 라이브러리 | 역할 | ML 워크플로우에서 |
|---|---|---|
| **NumPy** | 수치 배열 연산 | 텐서 연산·수학의 기반 |
| **pandas** | 표 데이터 수집·전처리 | 원시 데이터 → `X`, `y` |
| **Matplotlib** | 시각화 | EDA·학습 모니터링·평가 |

**데이터 흐름**:
`read_csv`(pandas) → 정제·특성 공학(pandas) → `.values`(NumPy)
→ 모델 학습 → 결과 시각화(Matplotlib)

**다음 단계**: scikit-learn으로 첫 ML 모델 만들기 →
PyTorch/TensorFlow로 딥러닝 입문

---

<!-- _class: lead -->

# Q&A

**참고 자료**
Matplotlib 공식 튜토리얼: matplotlib.org/stable/tutorials
Cheatsheets: matplotlib.org/cheatsheets
