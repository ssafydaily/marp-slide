---
marp: true
theme: default
paginate: true
style: |
  section {
    padding: 1.5rem; /* 원하는 여백 값으로 조절 */
    font-size: 24px
  }
  h1 {
    font-size: 2rem;
    position: absolute;
    left: 50px;
    top: 50px;
  }
  h2 {
    font-size: 1.5rem;
  }
  h3 {
    font-size: 1.2rem;
  }
---

<style>
.cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-top: 1rem;
}
.box {
  background: #f0f4ff;
  border-left: 4px solid #4a6cf7;
  border-radius: 8px;
  padding: 1rem 1.2rem;
}
</style>



# 문서 유사도

### 다수의 문서들(또는 문장)중에서 얼마나 비슷한 내용을 포함하는지를 `수치`로 표현한 것


-----------

# 주요 서비스 분야

<div class="cols">
<div>

#### 검색 및 징의 응답
- RAG 기반 챗봇
- 시맨틱 검색
#### 콘텐츠 추천 시스템
- 뉴스 및 블로그 추천
- 학술 논문 및 전문 자료 추천

</div>
<div>

#### 표절 검사 및 저작권 보호
- 코드 유사도 검사
- 학업 및 연구 문서 검사
#### 지식 그래프 및 문서 군집화
- 토픽 모델링 및 뉴스 모아 보기

</div>
</div>

--------------

## 문서 유사도 계산법

- 자카드 유사도
  - 두 집합의 교집합 크기를 합집합 크기로 나눈 값
  - 텍스트 유사도 측정 시 단어 존재 여부만 고려
- 유클리드 거리
  - 공간적 거리 측정 방식
  - 거리가 0에 가까울수록 유사도 높음
- 코사인 유사도
  - 두 벡터가 이루는 각도에 대한 *cosine* 값을 이용
  - -1 에서 1 사이의 값으로 1에 가까울수록 유사도가 높음

--------------

# 벡터

- 방향과 크기를 나타내는 수학적 표현


-------------

# 벡터 (Vector)

**크기와 방향**을 동시에 가지는 수학적 객체

<div class="cols">
<div>

## 정의
- $n$개의 숫자를 순서대로 나열한 것
- $\mathbf{a} = (a_1, a_2, \dots, a_n)$
- 2D 예시: $\mathbf{a} = (3, 4)$

## 기하학적 의미
- 원점에서 점 $(a_1, a_2)$까지의 **화살표**
- **크기(norm):** $\|\mathbf{a}\| = \sqrt{a_1^2 + a_2^2}$

</div>
<div>

## 텍스트의 벡터 표현

단어나 문장을 숫자 벡터로 변환

<div class="box">

"고양이" → $(0.2,\ 0.8,\ 0.1)$

"강아지" → $(0.3,\ 0.7,\ 0.2)$

"자동차" → $(0.9,\ 0.1,\ 0.8)$

</div>

→ 의미가 비슷한 단어는  
　**비슷한 방향**의 벡터를 가짐

</div>
</div>

-------------------

# 내적 (Dot Product)

두 벡터가 **얼마나 같은 방향**을 향하는지 측정하는 연산

<div class="cols">
<div>

## 계산 방법

$$\mathbf{a} \cdot \mathbf{b} = \sum_{i=1}^{n} a_i b_i$$

**예시:**

$$\mathbf{a} = (1, 2, 3)$$
$$\mathbf{b} = (4, 5, 6)$$
$$\mathbf{a} \cdot \mathbf{b} = 1{\times}4 + 2{\times}5 + 3{\times}6 = 32$$

</div>
<div>

## 기하학적 의미

$$\mathbf{a} \cdot \mathbf{b} = \|\mathbf{a}\| \|\mathbf{b}\| \cos\theta$$

| 상황 | 내적 값 |
|------|--------|
| 같은 방향 ($\theta=0°$) | **최대 양수** |
| 수직 ($\theta=90°$) | **0** |
| 반대 방향 ($\theta=180°$) | **최대 음수** |

> ⚠️ 내적은 벡터의 **크기**에도 영향을 받음

</div>
</div>

--------------------
# 코사인 유사도 (Cosine Similarity)

<div class="cols">
<div>
- 크기 영향 없이 **방향만으로** 두 벡터의 유사도를 측정

### 공식

$$\cos(\theta) = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \|\mathbf{b}\|}$$

내적을 두 벡터의 크기로 **정규화**

### 값의 범위

| 값 | 의미 |
|----|------|
| $1.0$ | 완전히 같은 방향 (매우 유사) |
| $0.0$ | 수직 (관련 없음) |
| $-1.0$ | 완전히 반대 방향 |

</div>
<div>

### 내적과의 차이점

<div class="box">

**내적:** 크기 × 방향 → 크기가 크면 값도 커짐

**코사인 유사도:** 방향만 비교 → 크기 무관

</div>

### 활용 사례
- 🔍 **문서 검색** — 질문과 문서의 의미적 유사도
- 🤖 **추천 시스템** — 사용자 선호도 벡터 비교
- 🌐 **번역 모델** — 언어 간 의미 정렬

</div>
</div>

-------------------
