---
marp: true
theme: default
paginate: true
style: |
  section {
    padding: 1.5rem; /* 원하는 여백 값으로 조절 */
  }
  h1 {
    position: absolute;
    left: 50px;
    top: 50px;
  }
---


# 데이터 분석

## 왜 필요한가?
## 가지고 있는 자원을 통해 최적의 선택
## **합리적인 의사 결정을 위해**

---

# 데이터 분석은 어떻게?

## 1. 가설을 설정하고 데이터 만들기(인터뷰, 리서치, 데이터 설계 후 수집)
## 2. 쌓인 데이터에서 필요 데이터 선별 및 조회(쿼리 조회, 데이터 가공, 인프라 구축)
## 3. 데이터 기반 가설 검증(통계 분석, 수학적 모델링)
## 4. 결과 공유(데이터 시각화, PT 작성)

---

# 데이터 분석 절차

## 1. 문제 정의
## 2. 데이터 기획
## 3. 데이터 수집
## 4. 데이터 전처리
## 5. 데이터 시각화
## 6. 분석 및 인사이트 도출

---


# 파이썬 머신 러닝 기술

## ML  ![h:100](images/scikit-learn.png)

## 배열/선형대수/통계   ![w:70](images/NumPy.png)  ![w:70]()
## 데이터 핸들링 ![w:100](images/Pandas.png)
## 시각화 ![w:100](images/Matplotlib.svg) ![w:100](images/Seaborn.svg)
## 대화형 파이썬 도구 ![w:100](images/jupyter.svg)

---


# Pandas

## 관계형(realtional) 혹은 레이블(labeling)된 데이터를 효율적으로 처리하기 위한 Python 기반의 데이터 분석 라이브러리

### **빠르고 유연하며 표현력이 풍부한 데이터 구조**
### **오픈 소스 라이브러리**
### **numpy 기반으로 과학 계산 및 머신러닝 라이브러리들과의 호환성과 통합성 제공**


---

# Pandas 자료형

## SQL table, Excel spreadsheet와 같은 표 형식의 데이터(Tabular)
## 순서가 있거나 없는 데이터
## 시계열(TIme series) 데이터
## 행 및 열이 있는 임의의 행렬 데이터(행렬의 각 구성요소의 다른 유형 처리 가능)
## 다른 유형의 관찰 / 통계 데이터셋(명시적인 레이블이 없어도 유연하게 처리)

---

# Pandas 자료 구조
## Series : 1차원, 한줄 데이터의 자료형 동일
## DataFrame: 2차원, 각열의 데이터 타입이 다를 수 있으며, 크기를 자유롭게 조절

![h:300](https://pandas.pydata.org/docs/_images/01_table_dataframe.svg) ![h:300](https://pandas.pydata.org/docs/_images/01_table_series.svg)

---

# Pandas 장점
- 결측치 처리: `NaN`, `dropan`, `fillna`
- 행/열 추가 삭제 용이: `append`, `drop`
- 정렬 기능: `sort_values`, `sort_index`
- GroupBy 제공: SQL의 그룹단위 집계 가능
- 다양한 형태 변환: 리스트, 딕션너리, NumPy 등에서 DataFrame 생성
- Merge/Join 지원: `merge`, `join`, `concat` 지원
- 파일 입출력 지원: CSV, Excel, DB, JSON 등 다양한 포맷 지원