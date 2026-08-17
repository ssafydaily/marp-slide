---
marp: true
theme: gaia
paginate: true
header: 'pandas 핵심 개념과 주요 기능'
footer: '데이터 수집·전처리·분석 교육과정 — Part 2 / 3'
style: |
  section { font-size: 26px; }
  section.lead { text-align: center; }
  code { font-size: 0.9em; }
  pre { font-size: 0.78em; line-height: 1.35; }
  table { font-size: 0.85em; }
---

<!-- _class: lead -->

# pandas
## 표 형태(Tabular) 데이터의 수집과 전처리

**데이터 수집·전처리·분석 교육과정 Part 2**
소요 시간: 약 2.5시간 | 대상: Python 중급

---

## 학습 목표 (Learning Objectives)

- `Series`와 `DataFrame`의 구조를 이해한다
- 파일 입출력(I/O)으로 데이터를 수집·저장한다
- `loc`/`iloc`, 조건 필터링으로 원하는 데이터를 추출한다
- 결측치(missing value)·중복·타입 문제를 정제한다
- `groupby`, `merge`, `pivot`으로 데이터를 집계·결합·재구조화한다
- **ML 연계**: 원시 데이터 → 특성 행렬 `X`, 라벨 `y`를 만드는
  전 과정이 pandas의 영역이다

---

## 목차 (Agenda)

1. Series와 DataFrame
2. 데이터 수집: 파일 읽기/쓰기
3. 데이터 탐색: info, describe
4. 선택과 필터링: loc, iloc, 조건식
5. 열 추가·수정·삭제
6. 결측치 처리 (Missing Data)
7. 타입 변환과 중복 제거
8. 문자열·날짜 다루기
9. 정렬과 순위
10. GroupBy 집계
11. 병합과 연결 (Merge & Concat)
12. 피벗과 재구조화
13. 종합 실습: Titanic 전처리

---

<!-- _class: lead -->

# 1. Series와 DataFrame

---

## Series — 인덱스가 붙은 1차원 배열

```python
import pandas as pd

s = pd.Series([25, 30, 35], index=['kim', 'lee', 'park'])
# kim     25
# lee     30
# park    35

s['lee']        # 30       — 라벨(label) 접근
s.iloc[1]       # 30       — 위치(position) 접근
s + 1           # 벡터 연산 (NumPy 기반)
s.values        # NumPy 배열로 변환
```

**Series = NumPy 배열 + 인덱스(index)** — DataFrame의 한 열이 곧 Series.

---

## DataFrame — 2차원 표 (여러 Series의 묶음)

```python
df = pd.DataFrame({
    'name':  ['kim', 'lee', 'park', 'choi'],
    'age':   [25, 30, 35, 28],
    'city':  ['Seoul', 'Busan', 'Seoul', 'Daegu'],
    'score': [88.5, 92.0, 79.5, 85.0],
})
```

| | name | age | city | score |
|---|---|---|---|---|
| 0 | kim | 25 | Seoul | 88.5 |
| 1 | lee | 30 | Busan | 92.0 |
| 2 | park | 35 | Seoul | 79.5 |
| 3 | choi | 28 | Daegu | 85.0 |

**ML 연계**: 각 행 = 샘플(sample), 각 열 = 특성(feature). `X = df[특성들]`, `y = df['라벨']`.

---

<!-- _class: lead -->

# 2. 데이터 수집
## 파일 읽기와 쓰기 (I/O)

---

## read_csv — 가장 많이 쓰는 함수

```python
df = pd.read_csv('data.csv')

# 자주 쓰는 옵션들
df = pd.read_csv(
    'data.csv',
    encoding='utf-8',          # 한글 깨지면 'cp949' 시도
    sep=',',                   # 구분자 (탭이면 '\t')
    header=0,                  # 헤더 행 위치
    na_values=['?', 'N/A'],    # 결측으로 처리할 문자열
    usecols=['age', 'score'],  # 필요한 열만
    nrows=1000,                # 앞부분만 (대용량 미리보기)
    parse_dates=['date'],      # 날짜 자동 파싱
)
```

---

## 다양한 소스에서 수집하기

```python
pd.read_excel('data.xlsx', sheet_name='Sheet1')   # 엑셀
pd.read_json('data.json')                         # JSON
pd.read_html('https://example.com/table.html')    # 웹 페이지의 <table>
pd.read_sql('SELECT * FROM users', conn)          # 데이터베이스
pd.read_parquet('data.parquet')                   # 대용량 컬럼 저장 포맷
```

저장:

```python
df.to_csv('out.csv', index=False)      # index=False 습관화!
df.to_excel('out.xlsx', index=False)
df.to_parquet('out.parquet')           # 빠르고 작음 — ML 파이프라인 권장
```

---

<!-- _class: lead -->

# 3. 데이터 탐색
## 첫 만남에서 반드시 하는 5가지

---

## 탐색 필수 루틴

```python
df.head()            # 앞 5행 미리보기
df.tail(3)           # 뒤 3행
df.shape             # (행 수, 열 수)
df.info()            # 열별 타입 + 결측 아닌 개수 + 메모리
df.describe()        # 수치형 열의 기초 통계량
```

```python
df['city'].value_counts()          # 범주별 빈도
df['city'].unique()                # 고유값 목록
df['city'].nunique()               # 고유값 개수
df.isna().sum()                    # 열별 결측 개수 ★ 매번 확인
```

**ML 연계**: 모델링 전 EDA(탐색적 데이터 분석)의 출발점.
결측 비율·타입·분포를 모르면 전처리 계획을 세울 수 없다.

---

## 따라하기 ① — Titanic 데이터 탐색

```python
url = 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv'
df = pd.read_csv(url)

# 1. 크기와 열 구성을 확인하세요
print(df.shape)              # (891, 15)
df.info()

# 2. 결측치가 있는 열을 찾으세요
print(df.isna().sum())       # age 177, deck 688, ...

# 3. 생존률(survived 평균)을 구하세요
print(df['survived'].mean()) # 0.3838...
```

---

<!-- _class: lead -->

# 4. 선택과 필터링

---

## 열 선택

```python
df['age']                 # Series 하나 (1개 열)
df[['name', 'age']]       # DataFrame (여러 열 — 리스트로!)

df.age                    # 점 표기 — 가능하지만 비권장
                          # (공백/예약어 열 이름에서 깨짐)
```

**ML 연계**: 특성/라벨 분리의 표준 패턴

```python
X = df[['age', 'fare', 'pclass']]     # 특성 행렬
y = df['survived']                     # 타깃 벡터
```

---

## loc과 iloc — 행 선택의 두 축

```python
df.loc[2]                  # 라벨(index)이 2인 행
df.loc[0:2, 'name':'city'] # 라벨 슬라이스 — 끝 포함!
df.loc[df['age'] > 28, ['name', 'age']]   # 조건 + 열 지정

df.iloc[0]                 # 첫 번째 행 (위치 기반)
df.iloc[0:2, 1:3]          # 위치 슬라이스 — 끝 미포함 (NumPy식)
```

| | `loc` | `iloc` |
|---|---|---|
| 기준 | 라벨 (label) | 정수 위치 (position) |
| 슬라이스 끝 | **포함** | 미포함 |

---

## 조건 필터링 (Boolean Filtering)

```python
df[df['age'] >= 30]                        # 단일 조건

df[(df['city'] == 'Seoul') & (df['age'] < 30)]   # AND는 &
df[(df['age'] < 26) | (df['score'] > 90)]        # OR는 |
```

⚠️ `and`/`or`가 아니라 `&`/`|`, 각 조건은 **괄호 필수**

```python
df[df['city'].isin(['Seoul', 'Busan'])]    # 목록 포함 여부
df[df['name'].str.startswith('k')]         # 문자열 조건
df.query('age >= 30 and city == "Seoul"')  # SQL 느낌의 대안
```

---

<!-- _class: lead -->

# 5. 열 추가·수정·삭제

---

## 파생 변수 만들기 (Feature Engineering의 시작)

```python
df['age_group'] = df['age'] // 10 * 10       # 25 → 20 (연령대)
df['pass'] = df['score'] >= 80               # 불리언 열
df['score_pct'] = df['score'] / df['score'].max()

# 조건부 열: np.where / pd.cut
import numpy as np
df['grade'] = np.where(df['score'] >= 90, 'A',
              np.where(df['score'] >= 80, 'B', 'C'))

df['age_bin'] = pd.cut(df['age'], bins=[0, 20, 40, 100],
                       labels=['young', 'middle', 'senior'])
```

**ML 연계**: 좋은 파생 변수 하나가 모델 성능을 좌우한다 (feature engineering).

---

## 삭제와 이름 변경

```python
df = df.drop(columns=['score_pct'])          # 열 삭제
df = df.drop(index=[0, 1])                   # 행 삭제

df = df.rename(columns={'name': 'student_name'})
df.columns = df.columns.str.lower()          # 열 이름 일괄 소문자화
```

pandas 기본 스타일: **원본을 바꾸지 않고 새 객체를 반환**
→ `df = df.drop(...)` 처럼 재할당하는 습관을 들이자
(`inplace=True`는 최신 pandas에서 비권장)

---

<!-- _class: lead -->

# 6. 결측치 처리
## Missing Data — 전처리의 핵심

---

## 결측 확인과 제거

```python
df.isna().sum()                    # 열별 결측 개수
df.isna().mean() * 100             # 열별 결측 비율(%)

df.dropna()                        # 결측 있는 행 전부 제거
df.dropna(subset=['age'])          # age가 결측인 행만 제거
df.dropna(axis=1, thresh=len(df)*0.5)   # 결측 50% 초과 열 제거
```

**판단 기준 (실무 감각)**
- 결측 비율이 아주 높은 열(예: 70%+) → 열 자체 제거 고려
- 소수의 결측 행 → 제거 또는 대치
- 결측 자체가 정보일 수도 → `is_missing` 플래그 열 추가

---

## 결측 대치 (Imputation)

```python
df['age'] = df['age'].fillna(df['age'].median())     # 중앙값 대치
df['city'] = df['city'].fillna(df['city'].mode()[0]) # 최빈값 대치
df['sales'] = df['sales'].ffill()                    # 직전 값으로 (시계열)
df['sales'] = df['sales'].interpolate()              # 선형 보간
```

**ML 연계 — 주의사항**:
대치 통계량(중앙값 등)은 **train 데이터에서만 계산**하고
test에는 그 값을 그대로 적용해야 한다 (데이터 누수, data leakage 방지).

```python
med = train['age'].median()
train['age'] = train['age'].fillna(med)
test['age']  = test['age'].fillna(med)     # train의 중앙값 사용!
```

---

## 따라하기 ② — Titanic 결측 처리

```python
df = pd.read_csv(url)   # titanic

# 1. 결측 비율을 % 로 출력하세요
print((df.isna().mean() * 100).round(1))

# 2. deck 열은 결측 77% → 제거하세요
df = df.drop(columns=['deck'])

# 3. age는 중앙값, embarked는 최빈값으로 대치하세요
df['age'] = df['age'].fillna(df['age'].median())
df['embarked'] = df['embarked'].fillna(df['embarked'].mode()[0])

print(df.isna().sum().sum())    # 남은 결측 확인
```

---

<!-- _class: lead -->

# 7. 타입 변환과 중복 제거

---

## astype과 to_numeric

```python
df['age'] = df['age'].astype(int)
df['pclass'] = df['pclass'].astype('category')   # 범주형 — 메모리 절약

# '1,234' 같은 지저분한 숫자 문자열
df['price'] = df['price'].str.replace(',', '')
df['price'] = pd.to_numeric(df['price'], errors='coerce')
#              errors='coerce': 변환 불가 → NaN
```

```python
df.duplicated().sum()               # 중복 행 개수
df = df.drop_duplicates()           # 중복 제거
df = df.drop_duplicates(subset=['name'], keep='last')
```

**ML 연계**: 잘못된 dtype(숫자가 문자열로 읽힘)은 가장 흔한 수집 단계 버그.

---

## 범주형 인코딩 (Categorical Encoding)

```python
# 원-핫 인코딩 (One-Hot Encoding)
pd.get_dummies(df, columns=['city'], dtype=int)
#  city_Busan  city_Daegu  city_Seoul
#           0           0           1  ...

# 라벨 매핑 (순서가 있는 범주)
df['grade_num'] = df['grade'].map({'C': 0, 'B': 1, 'A': 2})
```

**ML 연계**: 모델은 숫자만 이해한다.
- 순서 없는 범주(도시, 색상) → **원-핫**
- 순서 있는 범주(등급, 크기) → **정수 매핑**

---

<!-- _class: lead -->

# 8. 문자열·날짜 다루기

---

## .str 접근자 — 문자열 벡터 연산

```python
s = df['name']

s.str.upper()               # 대문자
s.str.len()                 # 길이
s.str.contains('kim')       # 포함 여부 (불리언)
s.str.replace('-', '')      # 치환
s.str.split('@').str[0]     # 분리 후 첫 조각
s.str.strip()               # 공백 제거
s.str.extract(r'(\d+)')     # 정규식 추출
```

```python
# 실전: "Braund, Mr. Owen" → 호칭(title) 추출
df['title'] = df['name'].str.extract(r',\s*([^\.]+)\.')
```

**ML 연계**: 텍스트 열에서 파생 특성을 뽑는 표준 도구.

---

## 날짜/시간 (Datetime)

```python
df['date'] = pd.to_datetime(df['date'])       # 문자열 → datetime

df['year']    = df['date'].dt.year
df['month']   = df['date'].dt.month
df['weekday'] = df['date'].dt.dayofweek       # 월=0 ... 일=6
df['is_weekend'] = df['date'].dt.dayofweek >= 5
```

```python
df = df.set_index('date')
df['2024-03']                    # 2024년 3월만 슬라이스
df.resample('W')['sales'].sum()  # 주 단위 리샘플링(resampling)
df['sales'].rolling(7).mean()    # 7일 이동평균 (rolling)
```

**ML 연계**: 시계열 예측의 특성(요일·월·이동평균)은 전부 여기서 나온다.

---

<!-- _class: lead -->

# 9. 정렬과 순위

---

## sort_values와 rank

```python
df.sort_values('age')                          # 오름차순
df.sort_values('score', ascending=False)      # 내림차순
df.sort_values(['city', 'age'],               # 다중 기준
               ascending=[True, False])

df.nlargest(3, 'score')                       # 상위 3개 — 정렬보다 빠름
df.nsmallest(3, 'age')

df['rank'] = df['score'].rank(ascending=False, method='min')
```

```python
df = df.sort_index()          # 인덱스 기준 정렬
df = df.reset_index(drop=True)  # 인덱스 0부터 재부여 — 필터링 후 습관!
```

---

<!-- _class: lead -->

# 10. GroupBy 집계
## Split → Apply → Combine

---

## groupby 기본

```python
df.groupby('city')['score'].mean()
# city
# Busan    92.0
# Daegu    85.0
# Seoul    84.0
```

동작 원리 — **분할(split) → 적용(apply) → 결합(combine)**
① `city`별로 그룹을 나누고 ② 각 그룹의 `score` 평균을 구해 ③ 합친다

```python
df.groupby('city').size()             # 그룹별 행 수
df.groupby(['city', 'pass']).mean(numeric_only=True)   # 다중 키
```

---

## agg — 여러 통계량 한 번에

```python
df.groupby('city').agg(
    avg_score=('score', 'mean'),
    max_age=('age', 'max'),
    count=('name', 'count'),
)
#        avg_score  max_age  count
# Busan       92.0       30      1
# Daegu       85.0       28      1
# Seoul       84.0       35      2
```

```python
# transform: 그룹 통계를 원본 행 수 그대로 되돌려줌
df['city_avg'] = df.groupby('city')['score'].transform('mean')
df['diff_from_city'] = df['score'] - df['city_avg']
```

**ML 연계**: `transform`으로 만든 "그룹 대비 편차"는 강력한 파생 특성.

---

## 따라하기 ③ — Titanic 그룹 분석

```python
# 1. 성별 생존률
df.groupby('sex')['survived'].mean()
# female 0.742 / male 0.189

# 2. 객실 등급(pclass)별 생존률과 인원
df.groupby('pclass').agg(
    survival_rate=('survived', 'mean'),
    n=('survived', 'size'),
)

# 3. 성별×등급 교차 생존률
df.groupby(['sex', 'pclass'])['survived'].mean().round(2)
```

→ "여성·1등석일수록 생존률이 높다" — 모델이 학습할 패턴을 미리 확인!

---

<!-- _class: lead -->

# 11. 병합과 연결

---

## merge — SQL JOIN과 동일

```python
users = pd.DataFrame({'user_id': [1, 2, 3],
                      'name': ['kim', 'lee', 'park']})
orders = pd.DataFrame({'user_id': [1, 1, 2, 4],
                       'amount': [100, 200, 150, 300]})

pd.merge(users, orders, on='user_id', how='inner')  # 교집합
pd.merge(users, orders, on='user_id', how='left')   # users 기준
pd.merge(users, orders, on='user_id', how='outer')  # 합집합
```

| how | 의미 |
|---|---|
| `inner` | 양쪽에 다 있는 키만 |
| `left` | 왼쪽 전부 유지 (없으면 NaN) |
| `outer` | 양쪽 전부 |

---

## concat — 단순 이어붙이기

```python
pd.concat([df_jan, df_feb, df_mar])                  # 위아래 (행 추가)
pd.concat([df_a, df_b], axis=1)                      # 좌우 (열 추가)
pd.concat([df_jan, df_feb], ignore_index=True)       # 인덱스 재부여
```

**ML 연계 — 전형적 수집 패턴**:
월별/파일별로 흩어진 CSV를 모아 하나의 학습 데이터로

```python
import glob
files = glob.glob('data/sales_*.csv')
df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
```

---

<!-- _class: lead -->

# 12. 피벗과 재구조화

---

## pivot_table과 crosstab

```python
df.pivot_table(values='survived', index='sex',
               columns='pclass', aggfunc='mean').round(2)
# pclass     1     2     3
# female  0.97  0.92  0.50
# male    0.37  0.16  0.14

pd.crosstab(df['sex'], df['survived'])       # 빈도 교차표
```

```python
# melt: 넓은(wide) 형태 → 긴(long) 형태
pd.melt(df, id_vars=['name'], value_vars=['math', 'eng'],
        var_name='subject', value_name='score')
```

**ML 연계**: 시각화 라이브러리·통계 모델은 long 형태를 선호 —
`melt`/`pivot`은 두 형태를 오가는 변환기다.

---

<!-- _class: lead -->

# 13. 종합 실습
## Titanic → 학습용 X, y 완성하기

---

## 전처리 파이프라인 전체 코드 (1/2)

```python
import pandas as pd, numpy as np

df = pd.read_csv(url)   # titanic

# 1) 사용할 열 선택
cols = ['survived', 'pclass', 'sex', 'age',
        'sibsp', 'parch', 'fare', 'embarked']
df = df[cols]

# 2) 결측 처리
df['age'] = df['age'].fillna(df['age'].median())
df['embarked'] = df['embarked'].fillna(df['embarked'].mode()[0])

# 3) 파생 변수
df['family_size'] = df['sibsp'] + df['parch'] + 1
df['is_alone'] = (df['family_size'] == 1).astype(int)
```

---

## 전처리 파이프라인 전체 코드 (2/2)

```python
# 4) 범주형 인코딩
df['sex'] = df['sex'].map({'male': 0, 'female': 1})
df = pd.get_dummies(df, columns=['embarked'], dtype=int)

# 5) X, y 분리 → NumPy로
X = df.drop(columns=['survived']).values     # (891, 10) float
y = df['survived'].values                    # (891,)

print(X.shape, y.shape, X.dtype)
# 이제 그대로 모델에 투입 가능:
# from sklearn.ensemble import RandomForestClassifier
# RandomForestClassifier().fit(X, y)
```

수집(read_csv) → 정제(fillna) → 특성 공학 → 인코딩 → **X, y**
이 흐름이 모든 ML 프로젝트의 표준 전처리 골격이다.

---

## 정리 (Summary)

| 단계 | 핵심 API |
|---|---|
| 수집 | `read_csv` `read_excel` `concat` |
| 탐색 | `info` `describe` `value_counts` `isna` |
| 선택 | `loc` `iloc` 조건식 `query` |
| 정제 | `fillna` `dropna` `astype` `drop_duplicates` |
| 특성 공학 | `.str` `.dt` `cut` `get_dummies` `transform` |
| 집계·결합 | `groupby` `agg` `merge` `pivot_table` |

**다음 파트**: Matplotlib — 데이터와 모델 결과의 시각화

---

<!-- _class: lead -->

# Q&A

**참고 자료**
pandas 공식 문서: pandas.pydata.org/docs
10 minutes to pandas: pandas.pydata.org/docs/user_guide/10min.html
