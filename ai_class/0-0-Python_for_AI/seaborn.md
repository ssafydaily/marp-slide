# 머신러닝을 위한 Seaborn 핵심 가이드

## 1. 기본 설정

### Import 및 초기 설정

```python
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Seaborn 스타일 설정
sns.set_theme()  # 기본 테마 적용

# 또는 특정 스타일
sns.set_style("whitegrid")  # "darkgrid", "white", "dark", "ticks"

# 컨텍스트 설정 (크기)
sns.set_context("notebook")  # "paper", "talk", "poster"

# 색상 팔레트
sns.set_palette("husl")  # "deep", "muted", "pastel", "bright", "dark", "colorblind"

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
```

### 샘플 데이터셋

```python
# Seaborn 내장 데이터셋
tips = sns.load_dataset('tips')
iris = sns.load_dataset('iris')
titanic = sns.load_dataset('titanic')

print(tips.head())
print(tips.info())

# 커스텀 데이터 생성
np.random.seed(42)
df = pd.DataFrame({
    'feature1': np.random.randn(200),
    'feature2': np.random.randn(200),
    'feature3': np.random.randn(200),
    'category': np.random.choice(['A', 'B', 'C'], 200),
    'target': np.random.randint(0, 2, 200)
})
```

## 2. 분포 시각화 (Distribution Plots)

### histplot - 히스토그램 (가장 기본)

```python
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 기본 히스토그램
sns.histplot(data=tips, x='total_bill', ax=axes[0])
axes[0].set_title('Basic Histogram')

# KDE (커널 밀도 추정) 추가
sns.histplot(data=tips, x='total_bill', kde=True, ax=axes[1])
axes[1].set_title('Histogram with KDE')

# 카테고리별 분포
sns.histplot(data=tips, x='total_bill', hue='sex', multiple='stack', ax=axes[2])
axes[2].set_title('Stacked by Category')

plt.tight_layout()
plt.show()
```

### kdeplot - 커널 밀도 추정

```python
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 기본 KDE
sns.kdeplot(data=tips, x='total_bill', ax=axes[0], fill=True)
axes[0].set_title('KDE Plot')

# 카테고리별
sns.kdeplot(data=tips, x='total_bill', hue='time', fill=True, ax=axes[1])
axes[1].set_title('KDE by Category')

# 2D KDE (밀도 등고선)
sns.kdeplot(data=tips, x='total_bill', y='tip', ax=axes[2], fill=True, cmap='Blues')
axes[2].set_title('2D KDE Plot')

plt.tight_layout()
plt.show()
```

### displot - 종합 분포 플롯 (Figure-level)

```python
# 히스토그램 + KDE
sns.displot(data=tips, x='total_bill', kde=True, height=5, aspect=1.5)
plt.show()

# 카테고리별 비교 (facet)
sns.displot(data=tips, x='total_bill', hue='sex', col='time', kde=True, height=4)
plt.show()

# 종류 변경: histogram, kde, ecdf
sns.displot(data=tips, x='total_bill', kind='kde', hue='day', fill=True, height=5, aspect=1.5)
plt.show()
```

### rugplot - 데이터 포인트 위치 표시

```python
fig, ax = plt.subplots(figsize=(10, 6))

# KDE + rug plot
sns.kdeplot(data=tips, x='total_bill', fill=True, ax=ax)
sns.rugplot(data=tips, x='total_bill', ax=ax, height=0.05, color='red')
ax.set_title('KDE with Rug Plot')

plt.show()
```

## 3. 관계형 플롯 (Relational Plots)

### scatterplot - 산점도

```python
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 기본 산점도
sns.scatterplot(data=tips, x='total_bill', y='tip', ax=axes[0])
axes[0].set_title('Basic Scatter Plot')

# 색상과 크기로 정보 추가
sns.scatterplot(data=tips, x='total_bill', y='tip', 
                hue='time', size='size', ax=axes[1])
axes[1].set_title('With Hue and Size')

# 스타일 추가
sns.scatterplot(data=tips, x='total_bill', y='tip', 
                hue='day', style='time', s=100, ax=axes[2])
axes[2].set_title('With Style')

plt.tight_layout()
plt.show()
```

### lineplot - 선 그래프

```python
# 시계열 데이터 생성
dates = pd.date_range('2024-01-01', periods=100)
data = pd.DataFrame({
    'date': np.tile(dates, 2),
    'value': np.concatenate([
        np.cumsum(np.random.randn(100)),
        np.cumsum(np.random.randn(100))
    ]),
    'category': ['A'] * 100 + ['B'] * 100
})

fig, axes = plt.subplots(1, 2, figsize=(16, 5))

# 기본 선 그래프 (자동으로 평균과 신뢰구간)
sns.lineplot(data=data, x='date', y='value', ax=axes[0])
axes[0].set_title('Line Plot with Confidence Interval')

# 카테고리별
sns.lineplot(data=data, x='date', y='value', hue='category', ax=axes[1])
axes[1].set_title('Line Plot by Category')

plt.tight_layout()
plt.show()
```

### relplot - 관계형 플롯 (Figure-level)

```python
# scatter 타입
sns.relplot(data=tips, x='total_bill', y='tip', 
            hue='day', size='size', col='time',
            height=4, aspect=1.2)
plt.show()

# line 타입
sns.relplot(data=data, x='date', y='value', 
            kind='line', hue='category',
            height=5, aspect=2)
plt.show()
```

## 4. 범주형 플롯 (Categorical Plots)

### boxplot - 박스플롯

```python
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 기본 박스플롯
sns.boxplot(data=tips, x='day', y='total_bill', ax=axes[0])
axes[0].set_title('Box Plot')

# 카테고리 추가
sns.boxplot(data=tips, x='day', y='total_bill', hue='sex', ax=axes[1])
axes[1].set_title('Box Plot with Hue')

plt.tight_layout()
plt.show()
```

### violinplot - 바이올린 플롯

```python
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 기본 바이올린
sns.violinplot(data=tips, x='day', y='total_bill', ax=axes[0])
axes[0].set_title('Violin Plot')

# split으로 비교
sns.violinplot(data=tips, x='day', y='total_bill', hue='sex', 
               split=True, ax=axes[1])
axes[1].set_title('Split Violin Plot')

plt.tight_layout()
plt.show()
```

### boxenplot - 향상된 박스플롯

```python
fig, ax = plt.subplots(figsize=(10, 6))

# 이상치를 더 잘 보여줌
sns.boxenplot(data=tips, x='day', y='total_bill', hue='time', ax=ax)
ax.set_title('Boxen Plot (Letter-Value Plot)')

plt.show()
```

### barplot - 막대 그래프 (평균값)

```python
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 카테고리별 평균
sns.barplot(data=tips, x='day', y='total_bill', ax=axes[0])
axes[0].set_title('Bar Plot (Mean with CI)')

# 오차 막대 제거
sns.barplot(data=tips, x='day', y='total_bill', hue='sex', 
            errorbar=None, ax=axes[1])
axes[1].set_title('Bar Plot without Error Bars')

plt.tight_layout()
plt.show()
```

### countplot - 빈도수 막대 그래프

```python
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 기본 카운트
sns.countplot(data=tips, x='day', ax=axes[0])
axes[0].set_title('Count Plot')

# 카테고리별
sns.countplot(data=tips, x='day', hue='sex', ax=axes[1])
axes[1].set_title('Count Plot with Hue')

plt.tight_layout()
plt.show()
```

### pointplot - 포인트 플롯

```python
fig, ax = plt.subplots(figsize=(10, 6))

# 평균을 점과 선으로 표시
sns.pointplot(data=tips, x='day', y='total_bill', hue='sex', ax=ax)
ax.set_title('Point Plot')

plt.show()
```

### stripplot & swarmplot - 개별 데이터 포인트

```python
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Strip plot (지터 적용)
sns.stripplot(data=tips, x='day', y='total_bill', hue='sex', 
              dodge=True, alpha=0.6, ax=axes[0])
axes[0].set_title('Strip Plot')

# Swarm plot (겹치지 않게)
sns.swarmplot(data=tips, x='day', y='total_bill', hue='sex', 
              dodge=True, ax=axes[1])
axes[1].set_title('Swarm Plot')

plt.tight_layout()
plt.show()
```

### catplot - 범주형 플롯 (Figure-level)

```python
# 다양한 kind 옵션
kinds = ['box', 'violin', 'bar', 'point']

for kind in kinds:
    sns.catplot(data=tips, x='day', y='total_bill', 
                hue='sex', kind=kind, height=5, aspect=1.5)
    plt.show()

# facet으로 비교
sns.catplot(data=tips, x='day', y='total_bill', 
            hue='sex', col='time', kind='box', height=4)
plt.show()
```

## 5. 행렬 플롯 (Matrix Plots)

### heatmap - 히트맵 (가장 중요!)

```python
# 상관관계 행렬
corr = tips[['total_bill', 'tip', 'size']].corr()

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 기본 히트맵
sns.heatmap(corr, ax=axes[0])
axes[0].set_title('Basic Heatmap')

# 값 표시
sns.heatmap(corr, annot=True, fmt='.2f', ax=axes[1])
axes[1].set_title('With Annotations')

# 컬러맵과 중심값 설정
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', 
            center=0, square=True, linewidths=1, ax=axes[2])
axes[2].set_title('Customized Heatmap')

plt.tight_layout()
plt.show()
```

### 혼동 행렬 시각화

```python
from sklearn.metrics import confusion_matrix

# 가짜 예측 데이터
y_true = np.random.randint(0, 3, 100)
y_pred = y_true.copy()
y_pred[np.random.choice(100, 20, replace=False)] = np.random.randint(0, 3, 20)

cm = confusion_matrix(y_true, y_pred)

fig, ax = plt.subplots(figsize=(8, 6))

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Class 0', 'Class 1', 'Class 2'],
            yticklabels=['Class 0', 'Class 1', 'Class 2'],
            ax=ax)
ax.set_xlabel('Predicted')
ax.set_ylabel('True')
ax.set_title('Confusion Matrix')

plt.show()
```

### clustermap - 계층적 클러스터링 히트맵

```python
# 데이터 준비
data = pd.DataFrame(np.random.randn(10, 12), 
                   columns=[f'Feature {i+1}' for i in range(12)])

# 클러스터맵 (행과 열을 클러스터링)
sns.clustermap(data, cmap='viridis', figsize=(10, 8),
               standard_scale=1,  # 열 단위로 정규화
               dendrogram_ratio=0.2)
plt.show()

# 상관관계 클러스터맵
corr_matrix = data.corr()
sns.clustermap(corr_matrix, annot=True, fmt='.2f', 
               cmap='coolwarm', center=0, figsize=(10, 8))
plt.show()
```

## 6. 회귀 플롯 (Regression Plots)

### regplot - 회귀선 추가

```python
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 기본 회귀 플롯
sns.regplot(data=tips, x='total_bill', y='tip', ax=axes[0])
axes[0].set_title('Basic Regression Plot')

# 신뢰구간 제거
sns.regplot(data=tips, x='total_bill', y='tip', ci=None, ax=axes[1])
axes[1].set_title('Without Confidence Interval')

# 다항 회귀
sns.regplot(data=tips, x='total_bill', y='tip', order=2, ax=axes[2])
axes[2].set_title('Polynomial Regression (order=2)')

plt.tight_layout()
plt.show()
```

### residplot - 잔차 플롯

```python
fig, ax = plt.subplots(figsize=(10, 6))

# 잔차 시각화 (모델 적합도 확인)
sns.residplot(data=tips, x='total_bill', y='tip', ax=ax)
ax.axhline(y=0, color='red', linestyle='--', linewidth=2)
ax.set_title('Residual Plot')

plt.show()
```

### lmplot - 회귀 플롯 (Figure-level)

```python
# 기본 회귀
sns.lmplot(data=tips, x='total_bill', y='tip', height=5, aspect=1.5)
plt.show()

# 카테고리별로 다른 회귀선
sns.lmplot(data=tips, x='total_bill', y='tip', hue='sex', height=5, aspect=1.5)
plt.show()

# facet으로 분할
sns.lmplot(data=tips, x='total_bill', y='tip', col='time', row='sex', height=4)
plt.show()
```

## 7. Pair Plot - 다변량 분석

### pairplot - 모든 변수 쌍 시각화

```python
# 기본 pairplot
sns.pairplot(iris)
plt.show()

# 타겟 변수로 색상 구분
sns.pairplot(iris, hue='species', height=2.5)
plt.show()

# 대각선 종류 변경
sns.pairplot(iris, hue='species', diag_kind='kde', height=2.5)
plt.show()

# 특정 변수만 선택
sns.pairplot(iris, vars=['sepal_length', 'sepal_width', 'petal_length'],
             hue='species', height=3)
plt.show()
```

### PairGrid - 커스터마이징 가능

```python
# 각 위치에 다른 플롯 타입
g = sns.PairGrid(iris, hue='species', height=2.5)
g.map_upper(sns.scatterplot)  # 상단: 산점도
g.map_lower(sns.kdeplot)       # 하단: KDE
g.map_diag(sns.histplot)       # 대각: 히스토그램
g.add_legend()
plt.show()
```

## 8. Joint Plot - 2변수 상세 분석

### jointplot - 결합 플롯

```python
# 산점도 + 히스토그램
sns.jointplot(data=tips, x='total_bill', y='tip', height=6)
plt.show()

# KDE
sns.jointplot(data=tips, x='total_bill', y='tip', kind='kde', height=6)
plt.show()

# 회귀
sns.jointplot(data=tips, x='total_bill', y='tip', kind='reg', height=6)
plt.show()

# hex binning (대용량 데이터)
sns.jointplot(data=tips, x='total_bill', y='tip', kind='hex', height=6)
plt.show()
```

### JointGrid - 커스터마이징

```python
g = sns.JointGrid(data=tips, x='total_bill', y='tip', height=6)
g.plot_joint(sns.scatterplot, alpha=0.5)
g.plot_marginals(sns.histplot, kde=True)
plt.show()
```

## 9. FacetGrid - 다차원 시각화

### FacetGrid - 소그룹별 플롯

```python
# 기본 FacetGrid
g = sns.FacetGrid(tips, col='time', row='sex', height=4)
g.map(sns.histplot, 'total_bill')
plt.show()

# 색상 추가
g = sns.FacetGrid(tips, col='day', hue='sex', height=4, aspect=1.2)
g.map(sns.scatterplot, 'total_bill', 'tip', alpha=0.7)
g.add_legend()
plt.show()

# 다양한 플롯 타입
g = sns.FacetGrid(tips, col='time', col_wrap=2, height=4)
g.map(sns.boxplot, 'day', 'total_bill')
plt.show()
```

## 10. 색상 팔레트 (Color Palettes)

### 색상 팔레트 설정

```python
# 사용 가능한 팔레트 확인
palettes = ['deep', 'muted', 'pastel', 'bright', 'dark', 'colorblind']

fig, axes = plt.subplots(len(palettes), 1, figsize=(12, 10))

for idx, palette in enumerate(palettes):
    sns.set_palette(palette)
    sns.barplot(data=tips, x='day', y='total_bill', ax=axes[idx])
    axes[idx].set_title(f'Palette: {palette}')

plt.tight_layout()
plt.show()
```

### 커스텀 색상 팔레트

```python
# 연속형 색상
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 단일 색상 그라디언트
sns.heatmap(np.random.rand(10, 10), cmap='Blues', ax=axes[0])
axes[0].set_title('Blues')

# 발산형 (중심값 기준)
sns.heatmap(np.random.randn(10, 10), cmap='RdBu_r', center=0, ax=axes[1])
axes[1].set_title('RdBu (Diverging)')

# 커스텀
custom_palette = sns.color_palette(['#FF0000', '#00FF00', '#0000FF'])
sns.heatmap(np.random.rand(10, 10), cmap=sns.color_palette(custom_palette, as_cmap=True), ax=axes[2])
axes[2].set_title('Custom Palette')

plt.tight_layout()
plt.show()
```

### 범주형 색상

```python
# 카테고리 개수에 따라
colors = sns.color_palette('husl', n_colors=5)
sns.barplot(data=tips.groupby('day')['total_bill'].sum().reset_index(), 
            x='day', y='total_bill', palette=colors)
plt.title('Custom Category Colors')
plt.show()
```

## 11. 실전 EDA 워크플로우

### 단변량 분석

```python
# 데이터 준비
df = pd.DataFrame({
    'age': np.random.randint(20, 70, 500),
    'income': np.random.lognormal(10, 1, 500),
    'education': np.random.choice(['HS', 'BS', 'MS', 'PhD'], 500),
    'experience': np.random.randint(0, 30, 500),
    'target': np.random.randint(0, 2, 500)
})

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 수치형 변수 분포
sns.histplot(data=df, x='age', kde=True, ax=axes[0, 0])
axes[0, 0].set_title('Age Distribution')

sns.histplot(data=df, x='income', kde=True, ax=axes[0, 1])
axes[0, 1].set_title('Income Distribution')

# 범주형 변수 빈도
sns.countplot(data=df, x='education', ax=axes[1, 0])
axes[1, 0].set_title('Education Levels')

# 타겟 변수
sns.countplot(data=df, x='target', ax=axes[1, 1])
axes[1, 1].set_title('Target Distribution')

plt.tight_layout()
plt.show()
```

### 이변량 분석

```python
fig, axes = plt.subplots(2, 3, figsize=(18, 10))

# 수치형 vs 수치형
sns.scatterplot(data=df, x='age', y='income', hue='target', ax=axes[0, 0])
axes[0, 0].set_title('Age vs Income')

sns.regplot(data=df, x='experience', y='income', ax=axes[0, 1])
axes[0, 1].set_title('Experience vs Income (Regression)')

# 범주형 vs 수치형
sns.boxplot(data=df, x='education', y='income', ax=axes[0, 2])
axes[0, 2].set_title('Income by Education')

sns.violinplot(data=df, x='target', y='age', ax=axes[1, 0])
axes[1, 0].set_title('Age by Target')

# 범주형 vs 범주형
pd.crosstab(df['education'], df['target']).plot(kind='bar', ax=axes[1, 1])
axes[1, 1].set_title('Education vs Target')

# 상관관계
corr = df[['age', 'income', 'experience']].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, ax=axes[1, 2])
axes[1, 2].set_title('Correlation Matrix')

plt.tight_layout()
plt.show()
```

### 다변량 분석 - 종합 대시보드

```python
# PairPlot으로 전체 관계 파악
g = sns.pairplot(df[['age', 'income', 'experience', 'target']], 
                 hue='target', diag_kind='kde', height=2.5)
g.fig.suptitle('Comprehensive Pairplot Analysis', y=1.02)
plt.show()
```

## 12. 머신러닝 결과 시각화

### 특성 중요도 시각화

```python
# 특성 중요도 데이터
feature_importance = pd.DataFrame({
    'feature': ['age', 'income', 'education_BS', 'education_MS', 'experience'],
    'importance': [0.25, 0.35, 0.15, 0.12, 0.13]
}).sort_values('importance', ascending=False)

fig, ax = plt.subplots(figsize=(10, 6))

sns.barplot(data=feature_importance, x='importance', y='feature', 
            palette='viridis', ax=ax)
ax.set_title('Feature Importance', fontsize=16)
ax.set_xlabel('Importance Score')

plt.tight_layout()
plt.show()
```

### 학습 곡선 시각화

```python
# 학습 히스토리 데이터
history = pd.DataFrame({
    'epoch': list(range(1, 51)) * 2,
    'loss': np.concatenate([
        2 * np.exp(-np.arange(1, 51)/10) + 0.1,
        2 * np.exp(-np.arange(1, 51)/10) + 0.15
    ]),
    'type': ['train'] * 50 + ['validation'] * 50
})

fig, ax = plt.subplots(figsize=(10, 6))

sns.lineplot(data=history, x='epoch', y='loss', hue='type', 
             style='type', markers=True, dashes=False, ax=ax)
ax.set_title('Training History', fontsize=16)
ax.set_xlabel('Epoch')
ax.set_ylabel('Loss')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

### 예측 오차 분석

```python
# 실제 vs 예측
predictions_df = pd.DataFrame({
    'actual': np.random.rand(200) * 100,
    'predicted': np.random.rand(200) * 100
})
predictions_df['residual'] = predictions_df['actual'] - predictions_df['predicted']

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 실제 vs 예측 산점도
sns.scatterplot(data=predictions_df, x='actual', y='predicted', ax=axes[0])
axes[0].plot([0, 100], [0, 100], 'r--', linewidth=2, label='Perfect Prediction')
axes[0].set_title('Actual vs Predicted')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 잔차 분포
sns.histplot(data=predictions_df, x='residual', kde=True, ax=axes[1])
axes[1].axvline(x=0, color='red', linestyle='--', linewidth=2)
axes[1].set_title('Residuals Distribution')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

## 13. 고급 시각화 팁

### 스타일 커스터마이징

```python
# 커스텀 스타일 적용
custom_params = {
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.labelsize": 14,
    "axes.titlesize": 16,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 12
}

sns.set_theme(style="whitegrid", rc=custom_params)

# 테스트
sns.boxplot(data=tips, x='day', y='total_bill')
plt.title('Custom Styled Plot')
plt.show()
```

### 애니메이션 프레임 생성

```python
# 시간에 따른 변화를 여러 프레임으로
time_points = [10, 25, 50, 75, 100]

fig, axes = plt.subplots(1, len(time_points), figsize=(20, 4))

for idx, t in enumerate(time_points):
    data_subset = pd.DataFrame({
        'x': np.random.randn(t),
        'y': np.random.randn(t)
    })
  
    sns.scatterplot(data=data_subset, x='x', y='y', ax=axes[idx])
    axes[idx].set_title(f'Time: {t}')
    axes[idx].set_xlim(-3, 3)
    axes[idx].set_ylim(-
```
