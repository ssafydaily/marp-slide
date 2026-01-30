# 머신러닝을 위한 Pandas 핵심 가이드

## 1. 기본 데이터 구조

### Series (1차원)
```python
import pandas as pd
import numpy as np

# Series 생성
s = pd.Series([1, 2, 3, 4, 5])
print(s)

# 인덱스 지정
s = pd.Series([100, 200, 300], index=['a', 'b', 'c'])
print("\n인덱스 지정:\n", s)

# 딕셔너리에서 생성
data = {'apple': 5, 'banana': 3, 'orange': 7}
s = pd.Series(data)
print("\n딕셔너리에서:\n", s)

# 기본 속성
print("\n값:", s.values)  # NumPy 배열
print("인덱스:", s.index)
print("크기:", s.shape)
```

### DataFrame (2차원) - 가장 중요!
```python
# 딕셔너리에서 생성
data = {
    'age': [25, 30, 35, 40],
    'salary': [50000, 60000, 70000, 80000],
    'city': ['Seoul', 'Busan', 'Seoul', 'Incheon']
}
df = pd.DataFrame(data)
print(df)

# NumPy 배열에서 생성
arr = np.random.randn(5, 3)
df = pd.DataFrame(arr, columns=['A', 'B', 'C'])
print("\nNumPy에서:\n", df)

# 기본 정보
print("\n형태:", df.shape)        # (행, 열)
print("열 이름:", df.columns.tolist())
print("인덱스:", df.index.tolist())
print("데이터 타입:\n", df.dtypes)
print("기본 정보:")
df.info()
```

## 2. 데이터 읽기/쓰기

### CSV 파일 - 가장 많이 사용
```python
# CSV 읽기
df = pd.read_csv('data.csv')

# 옵션들
df = pd.read_csv('data.csv',
                 sep=',',              # 구분자
                 header=0,             # 헤더 행 (0부터 시작)
                 names=['A', 'B'],     # 열 이름 직접 지정
                 index_col=0,          # 인덱스로 사용할 열
                 usecols=['A', 'B'],   # 특정 열만 읽기
                 nrows=1000,           # 처음 N행만 읽기
                 skiprows=[1, 2],      # 특정 행 건너뛰기
                 na_values=['NA', '?']) # 결측치로 처리할 값

# CSV 쓰기
df.to_csv('output.csv', index=False)  # 인덱스 제외

# 예제 데이터 생성 (연습용)
df = pd.DataFrame({
    'feature1': np.random.randn(100),
    'feature2': np.random.randn(100),
    'target': np.random.randint(0, 2, 100)
})
```

### Excel, JSON 등
```python
# Excel
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')
df.to_excel('output.xlsx', index=False)

# JSON
df = pd.read_json('data.json')
df.to_json('output.json', orient='records')

# SQL (필요시)
# import sqlite3
# conn = sqlite3.connect('database.db')
# df = pd.read_sql_query("SELECT * FROM table", conn)
```

## 3. 데이터 탐색 (EDA 필수!)

### 기본 탐색
```python
# 샘플 데이터 생성
df = pd.DataFrame({
    'age': [25, 30, 35, np.nan, 45, 50],
    'salary': [50000, 60000, 70000, 80000, 90000, 100000],
    'city': ['Seoul', 'Busan', 'Seoul', 'Incheon', 'Seoul', 'Busan'],
    'score': [85, 90, 78, 92, 88, 95]
})

# 처음/마지막 N행
print(df.head(3))    # 처음 3행 (기본 5)
print(df.tail(2))    # 마지막 2행

# 기술 통계
print(df.describe())  # 수치형 컬럼의 통계
print(df.describe(include='all'))  # 모든 컬럼

# 정보
print(df.info())     # 데이터 타입, 결측치 등

# 고유값 개수
print(df['city'].nunique())
print(df['city'].value_counts())  # 빈도수
```

### 통계량
```python
# 개별 통계
print("평균:", df['age'].mean())
print("중앙값:", df['salary'].median())
print("표준편차:", df['score'].std())
print("분산:", df['score'].var())
print("최솟값:", df['age'].min())
print("최댓값:", df['age'].max())

# 상관관계 - 매우 중요!
correlation = df[['age', 'salary', 'score']].corr()
print("\n상관관계:\n", correlation)

# 공분산
covariance = df[['age', 'salary']].cov()
```

## 4. 데이터 선택 및 인덱싱

### 열 선택
```python
df = pd.DataFrame({
    'A': [1, 2, 3, 4],
    'B': [5, 6, 7, 8],
    'C': [9, 10, 11, 12]
})

# 단일 열 (Series)
print(df['A'])
print(df.A)  # 속성 방식 (공백 없을 때만)

# 여러 열 (DataFrame)
print(df[['A', 'C']])

# 특성과 타겟 분리 (머신러닝 필수!)
features = df[['A', 'B']]
target = df['C']
```

### 행 선택 - loc, iloc
```python
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'David'],
    'age': [25, 30, 35, 40],
    'score': [85, 90, 78, 92]
}, index=['a', 'b', 'c', 'd'])

# iloc: 정수 인덱스 (위치 기반)
print(df.iloc[0])        # 첫 번째 행
print(df.iloc[0:2])      # 첫 2행
print(df.iloc[0, 1])     # 첫 행, 두 번째 열
print(df.iloc[:, 0:2])   # 모든 행, 첫 2열

# loc: 레이블 인덱스 (이름 기반)
print(df.loc['a'])       # 'a' 행
print(df.loc['a':'c'])   # 'a'부터 'c'까지 (끝 포함!)
print(df.loc['a', 'age']) # 'a' 행, 'age' 열
print(df.loc[:, 'age':'score'])  # 모든 행, age부터 score까지

# 조건부 선택 (필터링) - 매우 중요!
print(df[df['age'] > 30])           # 나이 30 초과
print(df[df['score'] >= 85])        # 점수 85 이상
print(df[(df['age'] > 25) & (df['score'] > 80)])  # 복합 조건
```

### Boolean 인덱싱
```python
# 조건 마스크 생성
mask = df['age'] > 30
print(mask)  # Boolean Series

# 마스크 적용
filtered = df[mask]
print(filtered)

# 여러 조건
mask = (df['age'] > 25) & (df['score'] >= 85)
filtered = df[mask]

# isin: 특정 값들 포함 여부
cities = df[df['city'].isin(['Seoul', 'Busan'])]

# query 메서드 (문자열 쿼리)
result = df.query('age > 30 and score >= 85')
```

## 5. 데이터 전처리

### 결측치 처리 - 필수!
```python
df = pd.DataFrame({
    'A': [1, 2, np.nan, 4, 5],
    'B': [np.nan, 2, 3, 4, 5],
    'C': [1, 2, 3, 4, 5]
})

# 결측치 확인
print(df.isnull())        # Boolean DataFrame
print(df.isnull().sum())  # 열별 결측치 개수
print(df.isna().sum())    # isnull과 동일

# 결측치 비율
print(df.isnull().sum() / len(df))

# 결측치 제거
df_dropped = df.dropna()           # 결측치 있는 행 제거
df_dropped = df.dropna(axis=1)     # 결측치 있는 열 제거
df_dropped = df.dropna(thresh=2)   # 최소 2개 유효값 필요

# 결측치 채우기 (Imputation)
df_filled = df.fillna(0)                    # 0으로 채우기
df_filled = df.fillna(df.mean())            # 평균으로 채우기
df_filled = df.fillna(df.median())          # 중앙값으로 채우기
df_filled = df.fillna(method='ffill')       # 앞 값으로 채우기
df_filled = df.fillna(method='bfill')       # 뒤 값으로 채우기

# 열별로 다르게 채우기
df_filled = df.fillna({'A': 0, 'B': df['B'].mean()})

# interpolate (보간)
df_interpolated = df.interpolate(method='linear')
```

### 데이터 타입 변환
```python
df = pd.DataFrame({
    'A': ['1', '2', '3'],
    'B': [1.5, 2.5, 3.5],
    'C': ['2020-01-01', '2020-02-01', '2020-03-01']
})

# 타입 확인
print(df.dtypes)

# 타입 변환
df['A'] = df['A'].astype(int)
df['B'] = df['B'].astype(int)
df['C'] = pd.to_datetime(df['C'])

print("\n변환 후:\n", df.dtypes)

# 카테고리형 변환 (메모리 절약)
df['category'] = pd.Categorical(['A', 'B', 'A', 'C'])
df['category'] = df['category'].astype('category')
```

### 중복 데이터 처리
```python
df = pd.DataFrame({
    'A': [1, 1, 2, 2, 3],
    'B': [10, 10, 20, 20, 30]
})

# 중복 확인
print(df.duplicated())        # Boolean Series
print(df.duplicated().sum())  # 중복 개수

# 중복 제거
df_unique = df.drop_duplicates()
df_unique = df.drop_duplicates(subset=['A'])  # 특정 열 기준
df_unique = df.drop_duplicates(keep='last')   # 마지막 것 유지
```

## 6. 데이터 변환

### 새 열 추가/수정
```python
df = pd.DataFrame({
    'height': [170, 180, 165],
    'weight': [70, 80, 60]
})

# 새 열 추가
df['BMI'] = df['weight'] / (df['height'] / 100) ** 2

# 조건부 열 생성
df['category'] = df['BMI'].apply(lambda x: 'Overweight' if x > 25 else 'Normal')

# numpy 함수 적용
df['height_log'] = np.log(df['height'])

# 여러 열 사용
df['ratio'] = df['weight'] / df['height']
```

### apply, map, applymap
```python
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6]
})

# apply: 함수를 행/열에 적용
df['A_squared'] = df['A'].apply(lambda x: x ** 2)
df['sum'] = df.apply(lambda row: row['A'] + row['B'], axis=1)

# 사용자 정의 함수
def categorize(value):
    if value < 2:
        return 'Low'
    elif value < 4:
        return 'Medium'
    else:
        return 'High'

df['category'] = df['A'].apply(categorize)

# map: Series의 값을 매핑
mapping = {1: 'one', 2: 'two', 3: 'three'}
df['A_text'] = df['A'].map(mapping)

# applymap: DataFrame 전체에 함수 적용
df_squared = df[['A', 'B']].applymap(lambda x: x ** 2)
# 또는 (pandas 2.1+)
df_squared = df[['A', 'B']].map(lambda x: x ** 2)
```

### 문자열 처리
```python
df = pd.DataFrame({
    'name': ['  Alice  ', 'bob', 'CHARLIE'],
    'email': ['alice@email.com', 'bob@email.com', 'charlie@email.com']
})

# 문자열 메서드 (str 접근자)
df['name_clean'] = df['name'].str.strip()        # 공백 제거
df['name_upper'] = df['name'].str.upper()        # 대문자
df['name_lower'] = df['name'].str.lower()        # 소문자
df['name_title'] = df['name'].str.title()        # 첫 글자 대문자

# 포함 여부 확인
mask = df['email'].str.contains('alice')

# 분할
df['domain'] = df['email'].str.split('@').str[1]

# 길이
df['name_length'] = df['name'].str.len()

# 정규표현식
df['has_number'] = df['email'].str.contains(r'\d')
```

## 7. 그룹화 및 집계 - 매우 중요!

### groupby 기본
```python
df = pd.DataFrame({
    'city': ['Seoul', 'Seoul', 'Busan', 'Busan', 'Seoul'],
    'product': ['A', 'B', 'A', 'B', 'A'],
    'sales': [100, 150, 200, 120, 130],
    'quantity': [10, 15, 20, 12, 13]
})

# 단일 열로 그룹화
grouped = df.groupby('city')
print(grouped['sales'].sum())
print(grouped['sales'].mean())
print(grouped.mean(numeric_only=True))  # 수치형 열만

# 여러 열로 그룹화
grouped = df.groupby(['city', 'product'])
print(grouped['sales'].sum())

# 여러 집계 함수
print(grouped['sales'].agg(['sum', 'mean', 'count']))

# 열별로 다른 집계
print(grouped.agg({
    'sales': ['sum', 'mean'],
    'quantity': ['sum', 'max']
}))
```

### 고급 그룹화
```python
# transform: 그룹별 연산 후 원래 형태 유지
df['sales_mean_by_city'] = df.groupby('city')['sales'].transform('mean')
df['sales_normalized'] = df['sales'] / df.groupby('city')['sales'].transform('sum')

print(df)

# filter: 그룹 필터링
high_sales = df.groupby('city').filter(lambda x: x['sales'].mean() > 130)

# 사용자 정의 집계
def range_func(x):
    return x.max() - x.min()

print(df.groupby('city')['sales'].agg(range_func))
```

## 8. 데이터 병합 및 결합

### merge (SQL JOIN과 유사)
```python
# 샘플 데이터
df1 = pd.DataFrame({
    'user_id': [1, 2, 3, 4],
    'name': ['Alice', 'Bob', 'Charlie', 'David']
})

df2 = pd.DataFrame({
    'user_id': [1, 2, 3, 5],
    'age': [25, 30, 35, 40]
})

# Inner join (기본)
merged = pd.merge(df1, df2, on='user_id')
print("Inner join:\n", merged)

# Left join
merged = pd.merge(df1, df2, on='user_id', how='left')
print("\nLeft join:\n", merged)

# Right join
merged = pd.merge(df1, df2, on='user_id', how='right')

# Outer join
merged = pd.merge(df1, df2, on='user_id', how='outer')
print("\nOuter join:\n", merged)

# 열 이름이 다를 때
merged = pd.merge(df1, df2, left_on='user_id', right_on='id')

# 여러 열 기준
merged = pd.merge(df1, df2, on=['col1', 'col2'])
```

### concat (연결)
```python
df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})

# 수직 연결 (행 추가)
result = pd.concat([df1, df2], ignore_index=True)
print("수직 연결:\n", result)

# 수평 연결 (열 추가)
result = pd.concat([df1, df2], axis=1)
print("\n수평 연결:\n", result)

# 여러 DataFrame
dfs = [df1, df2, df1]
result = pd.concat(dfs, ignore_index=True)
```

### append (추가)
```python
# 행 추가 (concat 권장)
df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
new_row = pd.DataFrame({'A': [5], 'B': [6]})
df = pd.concat([df, new_row], ignore_index=True)
```

## 9. 피벗 및 재구조화

### pivot_table - 매우 유용!
```python
df = pd.DataFrame({
    'date': ['2024-01', '2024-01', '2024-02', '2024-02'],
    'city': ['Seoul', 'Busan', 'Seoul', 'Busan'],
    'sales': [100, 150, 120, 180]
})

# 피벗 테이블
pivot = df.pivot_table(
    values='sales',
    index='date',
    columns='city',
    aggfunc='sum'
)
print(pivot)

# 여러 집계 함수
pivot = df.pivot_table(
    values='sales',
    index='date',
    columns='city',
    aggfunc=['sum', 'mean']
)
```

### melt (wide -> long)
```python
df = pd.DataFrame({
    'name': ['Alice', 'Bob'],
    'math': [90, 85],
    'english': [95, 80]
})

# Long format으로 변환
melted = df.melt(
    id_vars=['name'],
    value_vars=['math', 'english'],
    var_name='subject',
    value_name='score'
)
print(melted)
```

## 10. 정렬

### sort_values
```python
df = pd.DataFrame({
    'name': ['Charlie', 'Alice', 'Bob'],
    'age': [35, 25, 30],
    'score': [78, 92, 85]
})

# 단일 열 정렬
df_sorted = df.sort_values('age')
print(df_sorted)

# 내림차순
df_sorted = df.sort_values('age', ascending=False)

# 여러 열 정렬
df_sorted = df.sort_values(['age', 'score'], ascending=[True, False])

# 인덱스 재설정
df_sorted = df.sort_values('age').reset_index(drop=True)
```

### sort_index
```python
# 인덱스로 정렬
df_sorted = df.sort_index()
```

## 11. 시계열 데이터

### 날짜/시간 처리
```python
# 날짜 범위 생성
dates = pd.date_range('2024-01-01', periods=10, freq='D')
df = pd.DataFrame({
    'date': dates,
    'value': np.random.randn(10)
})

# 문자열을 datetime으로 변환
df['date'] = pd.to_datetime(df['date'])

# datetime 속성 추출
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day
df['dayofweek'] = df['date'].dt.dayofweek
df['quarter'] = df['date'].dt.quarter

print(df)

# 날짜를 인덱스로 설정
df_time = df.set_index('date')

# 리샘플링
df_monthly = df_time.resample('M').mean()  # 월별 평균
df_weekly = df_time.resample('W').sum()    # 주별 합계
```

## 12. 범주형 데이터 인코딩

### 원-핫 인코딩 - 필수!
```python
df = pd.DataFrame({
    'color': ['red', 'blue', 'green', 'red'],
    'size': ['S', 'M', 'L', 'M']
})

# get_dummies (원-핫 인코딩)
encoded = pd.get_dummies(df, columns=['color', 'size'])
print(encoded)

# prefix 지정
encoded = pd.get_dummies(df, columns=['color'], prefix='color')

# drop_first (다중공선성 방지)
encoded = pd.get_dummies(df, columns=['color'], drop_first=True)
```

### Label Encoding
```python
# map 사용
df['color_encoded'] = df['color'].map({'red': 0, 'blue': 1, 'green': 2})

# 또는 Categorical
df['color_cat'] = pd.Categorical(df['color'])
df['color_codes'] = df['color_cat'].codes
```

## 13. 실전 머신러닝 워크플로우

### 전체 파이프라인 예제
```python
# 1. 데이터 로드
df = pd.read_csv('data.csv')

# 2. 기본 탐색
print(df.head())
print(df.info())
print(df.describe())
print(df.isnull().sum())

# 3. 결측치 처리
df = df.dropna(subset=['target'])  # 타겟 결측치 제거
df['feature1'] = df['feature1'].fillna(df['feature1'].median())
df['feature2'] = df['feature2'].fillna(df['feature2'].mean())

# 4. 이상치 처리
Q1 = df['feature1'].quantile(0.25)
Q3 = df['feature1'].quantile(0.75)
IQR = Q3 - Q1
df = df[(df['feature1'] >= Q1 - 1.5*IQR) & (df['feature1'] <= Q3 + 1.5*IQR)]

# 5. 범주형 인코딩
df = pd.get_dummies(df, columns=['category'], drop_first=True)

# 6. 특성/타겟 분리
X = df.drop('target', axis=1)
y = df['target']

# 7. NumPy 배열로 변환 (scikit-learn용)
X_array = X.values  # 또는 X.to_numpy()
y_array = y.values

print("최종 특성 shape:", X_array.shape)
print("최종 타겟 shape:", y_array.shape)
```

### 특성 공학 예제
```python
df = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=100),
    'price': np.random.uniform(100, 200, 100),
    'quantity': np.random.randint(1, 50, 100)
})

# 날짜 특성 추출
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['dayofweek'] = df['date'].dt.dayofweek
df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)

# 수치 변환
df['total_sales'] = df['price'] * df['quantity']
df['price_log'] = np.log(df['price'])

# 구간화 (Binning)
df['price_category'] = pd.cut(
    df['price'],
    bins=[0, 120, 150, 200],
    labels=['Low', 'Medium', 'High']
)

# 또는 동일 크기 구간
df['price_quartile'] = pd.qcut(df['price'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])

# 이동 평균 (시계열)
df['price_ma7'] = df['price'].rolling(window=7).mean()

# Lag 특성
df['price_lag1'] = df['price'].shift(1)
df['price_diff'] = df['price'].diff()

print(df.head(10))
```

## 14. 유용한 팁과 트릭

### 체이닝 (Method Chaining)
```python
# 여러 작업을 연결
result = (df
    .dropna()
    .drop_duplicates()
    .query('age > 25')
    .sort_values('score', ascending=False)
    .reset_index(drop=True)
)
```

### 조건부 값 할당
```python
# np.where 사용
df['category'] = np.where(df['age'] > 30, 'Senior', 'Junior')

# 다중 조건
conditions = [
    df['age'] < 25,
    (df['age'] >= 25) & (df['age'] < 40),
    df['age'] >= 40
]
choices = ['Young', 'Middle', 'Senior']
df['age_group'] = np.select(conditions, choices, default='Unknown')

# loc으로 조건부 할당
df.loc[df['age'] > 30, 'category'] = 'Senior'
df.loc[df['age'] <= 30, 'category'] = 'Junior'
```

### 메모리 최적화
```python
# 데이터 타입 최적화
def reduce_mem_usage(df):
    for col in df.columns:
        col_type = df[col].dtype
        
        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()
            
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float32)
    
    return df

# 사용
df = reduce_mem_usage(df)
```

### 대용량 데이터 처리
```python
# 청크로 읽기
chunk_size = 10000
chunks = []

for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    # 각 청크 처리
    chunk = chunk[chunk['age'] > 25]
    chunks.append(chunk)

df = pd.concat(chunks, ignore_index=True)

# 특정 열만 읽기
df = pd.read_csv('data.csv', usecols=['feature1', 'feature2', 'target'])
```

## 15. Pandas와 머신러닝 라이브러리 연동

### Scikit-learn과 함께 사용
```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# 1. 데이터 준비
df = pd.read_csv('data.csv')

# 2. 특성/타겟 분리
X = df.drop('target', axis=1)
y = df['target']

# 3. Train/Test 분할
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4. 전처리
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# DataFrame으로 다시 변환 (열 이름 유지)
X_train_scaled = pd.DataFrame(
    X_train_scaled,
    columns=X_train.columns,
    index=X_train.index
)

# 5. 모델 학습
model = RandomForestClassifier()
model.fit(X_train_scaled, y_train)

# 6. 예측
predictions = model.predict(X_test_scaled)

# 7. 특성 중요도를 DataFrame으로
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print(feature_importance)
```

### PyTorch와 함께 사용
```python
import torch
from torch.utils.data import Dataset, DataLoader

# Pandas DataFrame을 PyTorch Dataset으로
class PandasDataset(Dataset):
    def __init__(self, dataframe, target_col):
        self.features = dataframe.drop(target_col, axis=1).values
        self.targets = dataframe[target_col].values
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        x = torch.FloatTensor(self.features[idx])
        y = torch.LongTensor([self.targets[idx]])
        return x, y

# 사용
df = pd.read_csv('data.csv')
dataset = PandasDataset(df, target_col='target')
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
```

## 핵심 요약

### 필수 작업 순서
```python
# 1. 데이터 로드
df = pd.read_csv('data.csv')

# 2. 탐색
df.head()
df.info()
df.describe()
df.isnull().sum()
df['column'].value_counts()

# 3. 결측치 처리
df.dropna()
df.fillna()

# 4. 중복 제거
df.drop_duplicates()

# 5. 데이터 선택
df[['col1', 'col2']]
df[df['age'] > 30]

# 6. 변환
df['new'] = df['old'].apply(func)
pd.get_dummies(df)

# 7. 그룹화 및 집계
df.groupby('col').agg(['mean', 'sum'])

# 8. 병합
pd.merge(df1, df2, on='key')

# 9. NumPy 변환
X = df.values
```

### 자주 사용하는 패턴

```python
# 특성/타겟 분리
X = df.drop('target', axis=1)
y = df['target']

# 수치형/범주형 분리
numeric_cols = df.select_dtypes(include=[np.number]).columns
categorical_cols = df.select_dtypes(include=['object']).columns

# 결측치 비율
missing_ratio = df.isnull().sum() / len(df)

# 고유값이 적은 열 찾기 (범주형 후보)
for col in df.columns:
    if df[col].nunique() < 10:
        print(f"{col}: {df[col].nunique()} unique values")

# 상관관계가 높은 특성 찾기
corr_matrix = df.corr().abs()
upper = corr_matrix.where(
    np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
)
high_corr = [column for column in upper.columns if any(upper[column] > 0.95)]
```

이 가이드로 머신러닝에 필요한 Pandas 작업의 95%를 수행할 수 있습니다!