# 머신러닝을 위한 Matplotlib 핵심 가이드

## 1. 기본 설정 및 구조

### 기본 import 및 설정
```python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 한글 폰트 설정 (Windows)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# 스타일 설정
plt.style.use('seaborn-v0_8-darkgrid')  # 또는 'default', 'ggplot', 'fivethirtyeight'

# 그림 크기 기본값 설정
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 100

# 폰트 크기
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12
```

### Figure와 Axes 이해하기 - 가장 중요!
```python
# 방법 1: pyplot 인터페이스 (간단한 플롯)
plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
plt.show()

# 방법 2: 객체 지향 인터페이스 (권장!)
fig, ax = plt.subplots()
ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
plt.show()

# 방법 3: 여러 서브플롯
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes[0, 0].plot([1, 2, 3], [1, 2, 3])
axes[0, 1].scatter([1, 2, 3], [1, 4, 2])
axes[1, 0].bar([1, 2, 3], [1, 4, 2])
axes[1, 1].hist([1, 2, 2, 3, 3, 3])
plt.tight_layout()  # 겹침 방지
plt.show()
```

## 2. 기본 플롯 유형

### 선 그래프 (Line Plot) - 학습 곡선
```python
# 학습 곡선 예제
epochs = np.arange(1, 51)
train_loss = np.exp(-epochs/10) + np.random.rand(50) * 0.1
val_loss = np.exp(-epochs/10) + np.random.rand(50) * 0.15

fig, ax = plt.subplots(figsize=(10, 6))

# 여러 선 그리기
ax.plot(epochs, train_loss, label='Train Loss', linewidth=2, color='blue', marker='o', markersize=4)
ax.plot(epochs, val_loss, label='Validation Loss', linewidth=2, color='red', linestyle='--', marker='s', markersize=4)

# 꾸미기
ax.set_xlabel('Epoch')
ax.set_ylabel('Loss')
ax.set_title('Training and Validation Loss')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)

plt.show()
```

### 산점도 (Scatter Plot) - 데이터 분포
```python
# 2개 특성의 관계 시각화
np.random.seed(42)
x = np.random.randn(100)
y = 2 * x + np.random.randn(100) * 0.5

fig, ax = plt.subplots(figsize=(8, 6))

# 산점도
scatter = ax.scatter(x, y, c=y, cmap='viridis', s=50, alpha=0.6, edgecolors='black')

# 컬러바 추가
plt.colorbar(scatter, ax=ax, label='Y value')

ax.set_xlabel('Feature X')
ax.set_ylabel('Feature Y')
ax.set_title('Feature Relationship')
ax.grid(True, alpha=0.3)

plt.show()
```

### 히스토그램 (Histogram) - 분포 확인
```python
# 특성 분포 확인
data = np.random.randn(1000)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 기본 히스토그램
axes[0].hist(data, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
axes[0].set_xlabel('Value')
axes[0].set_ylabel('Frequency')
axes[0].set_title('Histogram')
axes[0].grid(True, alpha=0.3)

# 누적 히스토그램
axes[1].hist(data, bins=30, cumulative=True, color='coral', edgecolor='black', alpha=0.7)
axes[1].set_xlabel('Value')
axes[1].set_ylabel('Cumulative Frequency')
axes[1].set_title('Cumulative Histogram')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

### 박스플롯 (Box Plot) - 이상치 탐지
```python
# 여러 특성 비교
data = [np.random.randn(100) * i + i for i in range(1, 5)]

fig, ax = plt.subplots(figsize=(10, 6))

bp = ax.boxplot(data, labels=['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4'],
                patch_artist=True, notch=True, showmeans=True)

# 색상 설정
colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)

ax.set_ylabel('Value')
ax.set_title('Feature Distribution Comparison')
ax.grid(True, alpha=0.3, axis='y')

plt.show()
```

### 막대 그래프 (Bar Plot) - 범주형 데이터
```python
# 클래스별 샘플 수
categories = ['Class A', 'Class B', 'Class C', 'Class D']
counts = [120, 85, 95, 110]

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 수직 막대
axes[0].bar(categories, counts, color=['red', 'blue', 'green', 'orange'], 
            edgecolor='black', alpha=0.7)
axes[0].set_ylabel('Count')
axes[0].set_title('Class Distribution')
axes[0].grid(True, alpha=0.3, axis='y')

# 수평 막대
axes[1].barh(categories, counts, color=['red', 'blue', 'green', 'orange'],
             edgecolor='black', alpha=0.7)
axes[1].set_xlabel('Count')
axes[1].set_title('Class Distribution (Horizontal)')
axes[1].grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.show()
```

## 3. 데이터 탐색 시각화

### 상관관계 히트맵
```python
# 특성 간 상관관계
np.random.seed(42)
data = np.random.randn(100, 5)
df = pd.DataFrame(data, columns=['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4', 'Feature 5'])
corr_matrix = df.corr()

fig, ax = plt.subplots(figsize=(10, 8))

# 히트맵
im = ax.imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)

# 눈금 설정
ax.set_xticks(np.arange(len(corr_matrix.columns)))
ax.set_yticks(np.arange(len(corr_matrix.columns)))
ax.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')
ax.set_yticklabels(corr_matrix.columns)

# 값 표시
for i in range(len(corr_matrix)):
    for j in range(len(corr_matrix)):
        text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                      ha='center', va='center', color='black', fontsize=10)

# 컬러바
plt.colorbar(im, ax=ax, label='Correlation')
ax.set_title('Feature Correlation Matrix')

plt.tight_layout()
plt.show()
```

### 쌍 그림 (Pair Plot) 수동 구현
```python
# 여러 특성 쌍 비교
features = np.random.randn(200, 3)
labels = np.random.randint(0, 2, 200)

fig, axes = plt.subplots(3, 3, figsize=(12, 12))

feature_names = ['Feature 1', 'Feature 2', 'Feature 3']

for i in range(3):
    for j in range(3):
        ax = axes[i, j]
        
        if i == j:
            # 대각선: 히스토그램
            ax.hist(features[:, i], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax.set_ylabel('Frequency' if j == 0 else '')
        else:
            # 비대각선: 산점도
            ax.scatter(features[:, j], features[:, i], c=labels, cmap='viridis', 
                      s=20, alpha=0.6, edgecolors='black', linewidth=0.5)
            ax.set_ylabel(feature_names[i] if j == 0 else '')
        
        if i == 2:
            ax.set_xlabel(feature_names[j])
        else:
            ax.set_xlabel('')

plt.tight_layout()
plt.show()
```

### 클래스별 분포 비교
```python
# 2개 클래스의 특성 분포
class_0 = np.random.randn(100) * 1.5 + 2
class_1 = np.random.randn(100) * 1.2 + 4

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 겹친 히스토그램
axes[0].hist(class_0, bins=20, alpha=0.6, label='Class 0', color='blue', edgecolor='black')
axes[0].hist(class_1, bins=20, alpha=0.6, label='Class 1', color='red', edgecolor='black')
axes[0].set_xlabel('Feature Value')
axes[0].set_ylabel('Frequency')
axes[0].set_title('Feature Distribution by Class')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 바이올린 플롯 스타일
axes[1].violinplot([class_0, class_1], positions=[1, 2], showmeans=True, showmedians=True)
axes[1].set_xticks([1, 2])
axes[1].set_xticklabels(['Class 0', 'Class 1'])
axes[1].set_ylabel('Feature Value')
axes[1].set_title('Feature Distribution (Violin Plot)')
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.show()
```

## 4. 머신러닝 학습 과정 시각화

### 학습 곡선 (Learning Curve)
```python
# 에포크별 손실 및 정확도
epochs = np.arange(1, 101)
train_loss = 2 * np.exp(-epochs/20) + 0.1 + np.random.rand(100) * 0.05
val_loss = 2 * np.exp(-epochs/20) + 0.15 + np.random.rand(100) * 0.08
train_acc = 1 - np.exp(-epochs/15) * 0.5 + np.random.rand(100) * 0.02
val_acc = 1 - np.exp(-epochs/15) * 0.5 + np.random.rand(100) * 0.04

fig, axes = plt.subplots(1, 2, figsize=(16, 5))

# 손실 그래프
axes[0].plot(epochs, train_loss, label='Train Loss', linewidth=2, color='#1f77b4')
axes[0].plot(epochs, val_loss, label='Validation Loss', linewidth=2, color='#ff7f0e')
axes[0].fill_between(epochs, train_loss, alpha=0.2, color='#1f77b4')
axes[0].fill_between(epochs, val_loss, alpha=0.2, color='#ff7f0e')
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('Loss')
axes[0].set_title('Training and Validation Loss')
axes[0].legend(loc='upper right')
axes[0].grid(True, alpha=0.3)

# 정확도 그래프
axes[1].plot(epochs, train_acc, label='Train Accuracy', linewidth=2, color='#2ca02c')
axes[1].plot(epochs, val_acc, label='Validation Accuracy', linewidth=2, color='#d62728')
axes[1].fill_between(epochs, train_acc, alpha=0.2, color='#2ca02c')
axes[1].fill_between(epochs, val_acc, alpha=0.2, color='#d62728')
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Accuracy')
axes[1].set_title('Training and Validation Accuracy')
axes[1].legend(loc='lower right')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

### 과적합 탐지 시각화
```python
# 학습 데이터 크기에 따른 성능
train_sizes = [10, 50, 100, 200, 500, 1000, 2000]
train_scores = [0.6, 0.75, 0.82, 0.88, 0.92, 0.94, 0.95]
val_scores = [0.55, 0.68, 0.73, 0.75, 0.76, 0.76, 0.75]

fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(train_sizes, train_scores, 'o-', linewidth=2, label='Training Score', 
        color='blue', markersize=8)
ax.plot(train_sizes, val_scores, 'o-', linewidth=2, label='Validation Score', 
        color='red', markersize=8)

# 차이 영역 강조
ax.fill_between(train_sizes, train_scores, val_scores, alpha=0.2, color='gray')

ax.set_xlabel('Training Set Size')
ax.set_ylabel('Score')
ax.set_title('Learning Curve - Overfitting Detection')
ax.legend(loc='lower right')
ax.grid(True, alpha=0.3)
ax.set_xscale('log')  # 로그 스케일

plt.show()
```

### 하이퍼파라미터 튜닝 결과
```python
# 하이퍼파라미터별 성능
learning_rates = [0.0001, 0.001, 0.01, 0.1, 1.0]
accuracies = [0.65, 0.78, 0.85, 0.82, 0.70]

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.bar(range(len(learning_rates)), accuracies, 
              color=['red' if acc < 0.8 else 'green' for acc in accuracies],
              alpha=0.7, edgecolor='black')

# 최고 성능 표시
best_idx = np.argmax(accuracies)
bars[best_idx].set_color('gold')
bars[best_idx].set_edgecolor('black')
bars[best_idx].set_linewidth(3)

# 값 표시
for i, (lr, acc) in enumerate(zip(learning_rates, accuracies)):
    ax.text(i, acc + 0.01, f'{acc:.2f}', ha='center', va='bottom', fontweight='bold')

ax.set_xticks(range(len(learning_rates)))
ax.set_xticklabels([f'{lr}' for lr in learning_rates])
ax.set_xlabel('Learning Rate')
ax.set_ylabel('Validation Accuracy')
ax.set_title('Hyperparameter Tuning Results')
ax.set_ylim(0, 1)
ax.grid(True, alpha=0.3, axis='y')

plt.show()
```

## 5. 모델 평가 시각화

### 혼동 행렬 (Confusion Matrix)
```python
from sklearn.metrics import confusion_matrix

# 실제와 예측값
y_true = np.random.randint(0, 3, 100)
y_pred = y_true.copy()
y_pred[np.random.choice(100, 20, replace=False)] = np.random.randint(0, 3, 20)

cm = confusion_matrix(y_true, y_pred)

fig, ax = plt.subplots(figsize=(8, 6))

# 히트맵
im = ax.imshow(cm, cmap='Blues', aspect='auto')

# 눈금
classes = ['Class 0', 'Class 1', 'Class 2']
ax.set_xticks(np.arange(len(classes)))
ax.set_yticks(np.arange(len(classes)))
ax.set_xticklabels(classes)
ax.set_yticklabels(classes)

# 값 표시
for i in range(len(classes)):
    for j in range(len(classes)):
        text = ax.text(j, i, cm[i, j], ha='center', va='center', 
                      color='white' if cm[i, j] > cm.max()/2 else 'black',
                      fontsize=16, fontweight='bold')

ax.set_xlabel('Predicted Label')
ax.set_ylabel('True Label')
ax.set_title('Confusion Matrix')

plt.colorbar(im, ax=ax)
plt.tight_layout()
plt.show()
```

### ROC 곡선
```python
from sklearn.metrics import roc_curve, auc

# 가짜 데이터 생성
y_true = np.random.randint(0, 2, 200)
y_scores = np.random.rand(200)
y_scores[y_true == 1] += 0.3  # 클래스 1의 점수를 약간 높임

fpr, tpr, thresholds = roc_curve(y_true, y_scores)
roc_auc = auc(fpr, tpr)

fig, ax = plt.subplots(figsize=(8, 8))

# ROC 곡선
ax.plot(fpr, tpr, color='darkorange', linewidth=2, 
        label=f'ROC curve (AUC = {roc_auc:.2f})')

# 랜덤 분류기 (대각선)
ax.plot([0, 1], [0, 1], color='navy', linewidth=2, linestyle='--', 
        label='Random Classifier')

# 영역 채우기
ax.fill_between(fpr, tpr, alpha=0.2, color='darkorange')

ax.set_xlabel('False Positive Rate')
ax.set_ylabel('True Positive Rate')
ax.set_title('Receiver Operating Characteristic (ROC) Curve')
ax.legend(loc='lower right')
ax.grid(True, alpha=0.3)
ax.set_xlim([0, 1])
ax.set_ylim([0, 1])

plt.show()
```

### Precision-Recall 곡선
```python
from sklearn.metrics import precision_recall_curve

precision, recall, thresholds = precision_recall_curve(y_true, y_scores)

fig, ax = plt.subplots(figsize=(8, 6))

ax.plot(recall, precision, color='blue', linewidth=2, label='PR curve')
ax.fill_between(recall, precision, alpha=0.2, color='blue')

ax.set_xlabel('Recall')
ax.set_ylabel('Precision')
ax.set_title('Precision-Recall Curve')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_xlim([0, 1])
ax.set_ylim([0, 1])

plt.show()
```

### 특성 중요도
```python
# 특성 중요도 (Random Forest 등)
features = ['Age', 'Income', 'Education', 'Experience', 'Credit Score']
importances = np.array([0.25, 0.35, 0.15, 0.18, 0.07])

# 정렬
indices = np.argsort(importances)

fig, ax = plt.subplots(figsize=(10, 6))

# 수평 막대 그래프
bars = ax.barh(range(len(importances)), importances[indices], 
               color='steelblue', edgecolor='black', alpha=0.8)

# 색상 그라디언트
colors = plt.cm.viridis(importances[indices] / importances.max())
for bar, color in zip(bars, colors):
    bar.set_color(color)

ax.set_yticks(range(len(importances)))
ax.set_yticklabels([features[i] for i in indices])
ax.set_xlabel('Importance')
ax.set_title('Feature Importance')
ax.grid(True, alpha=0.3, axis='x')

# 값 표시
for i, v in enumerate(importances[indices]):
    ax.text(v + 0.01, i, f'{v:.2f}', va='center')

plt.tight_layout()
plt.show()
```

## 6. 결정 경계 시각화

### 2D 결정 경계
```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression

# 2개 특성 데이터 생성
X, y = make_classification(n_samples=200, n_features=2, n_redundant=0, 
                           n_informative=2, n_clusters_per_class=1, 
                           random_state=42)

# 모델 학습
model = LogisticRegression()
model.fit(X, y)

# 메쉬 그리드 생성
h = 0.02
x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                     np.arange(y_min, y_max, h))

# 예측
Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

fig, ax = plt.subplots(figsize=(10, 8))

# 결정 경계
contour = ax.contourf(xx, yy, Z, alpha=0.3, cmap='RdYlBu')

# 데이터 포인트
scatter = ax.scatter(X[:, 0], X[:, 1], c=y, cmap='RdYlBu', 
                     edgecolors='black', s=50, linewidth=1.5)

ax.set_xlabel('Feature 1')
ax.set_ylabel('Feature 2')
ax.set_title('Decision Boundary')
plt.colorbar(scatter, ax=ax, label='Class')

plt.show()
```

### 다중 클래스 결정 경계
```python
from sklearn.datasets import make_blobs

# 3개 클래스 데이터
X, y = make_blobs(n_samples=300, centers=3, n_features=2, random_state=42)

# 모델 학습
model = LogisticRegression(multi_class='multinomial')
model.fit(X, y)

# 메쉬 그리드
h = 0.02
x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                     np.arange(y_min, y_max, h))

Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

fig, ax = plt.subplots(figsize=(10, 8))

# 결정 경계
ax.contourf(xx, yy, Z, alpha=0.4, cmap='viridis')

# 데이터 포인트
scatter = ax.scatter(X[:, 0], X[:, 1], c=y, cmap='viridis', 
                     edgecolors='black', s=60, linewidth=1.5)

ax.set_xlabel('Feature 1')
ax.set_ylabel('Feature 2')
ax.set_title('Multi-class Decision Boundary')
plt.colorbar(scatter, ax=ax, label='Class')

plt.show()
```

## 7. 회귀 모델 시각화

### 선형 회귀 결과
```python
from sklearn.linear_model import LinearRegression

# 데이터 생성
X = np.random.rand(100, 1) * 10
y = 2 * X.squeeze() + 1 + np.random.randn(100) * 2

# 모델 학습
model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 실제 vs 예측
axes[0].scatter(X, y, alpha=0.6, edgecolors='black', s=50, label='Actual')
axes[0].plot(X, y_pred, color='red', linewidth=2, label='Prediction')
axes[0].set_xlabel('X')
axes[0].set_ylabel('y')
axes[0].set_title('Linear Regression Fit')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 잔차 플롯
residuals = y - y_pred
axes[1].scatter(y_pred, residuals, alpha=0.6, edgecolors='black', s=50)
axes[1].axhline(y=0, color='red', linestyle='--', linewidth=2)
axes[1].set_xlabel('Predicted Values')
axes[1].set_ylabel('Residuals')
axes[1].set_title('Residual Plot')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

### 실제 vs 예측 플롯
```python
# 실제 값 vs 예측 값
y_true = np.random.rand(100) * 100
y_pred = y_true + np.random.randn(100) * 10

fig, ax = plt.subplots(figsize=(8, 8))

# 산점도
ax.scatter(y_true, y_pred, alpha=0.6, s=50, edgecolors='black')

# 완벽한 예측선 (y=x)
min_val = min(y_true.min(), y_pred.min())
max_val = max(y_true.max(), y_pred.max())
ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')

ax.set_xlabel('True Values')
ax.set_ylabel('Predicted Values')
ax.set_title('True vs Predicted Values')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_aspect('equal')

# R² 표시
from sklearn.metrics import r2_score
r2 = r2_score(y_true, y_pred)
ax.text(0.05, 0.95, f'R² = {r2:.3f}', transform=ax.transAxes, 
        fontsize=14, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.show()
```

## 8. 고급 시각화 기법

### 서브플롯 레이아웃 고급
```python
# GridSpec으로 복잡한 레이아웃
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(12, 8))
gs = GridSpec(3, 3, figure=fig)

# 큰 플롯
ax1 = fig.add_subplot(gs[0:2, :])
ax1.plot(np.random.randn(100).cumsum())
ax1.set_title('Main Plot')

# 작은 플롯들
ax2 = fig.add_subplot(gs[2, 0])
ax2.hist(np.random.randn(100), bins=20)
ax2.set_title('Histogram')

ax3 = fig.add_subplot(gs[2, 1])
ax3.scatter(np.random.rand(50), np.random.rand(50))
ax3.set_title('Scatter')

ax4 = fig.add_subplot(gs[2, 2])
ax4.bar([1, 2, 3], [