---
marp: true
theme: dark-plus-code
paginate: true
---

# 6단계. JOIN 과 집합 연산

INNER · OUTER · CROSS · SELF JOIN / UNION · INTERSECT · EXCEPT

- 조인 종류별 결과 행 수를 예측한다
- 짝이 없는 행이 어디로 가는지 안다
- 집합 연산자의 중복 처리 규칙을 안다

> 실습지: `labs/lab06_JOIN.md`

---

# 조인의 종류

| 조인 | 결과 |
| --- | --- |
| INNER JOIN | 조건이 맞는 행만 |
| LEFT OUTER JOIN | INNER + 왼쪽 테이블의 짝 없는 행 |
| RIGHT OUTER JOIN | INNER + 오른쪽 테이블의 짝 없는 행 |
| FULL OUTER JOIN | INNER + 양쪽의 짝 없는 행 |
| CROSS JOIN | 모든 조합 (카티션 곱) |
| SELF JOIN | 같은 테이블끼리 |
| NATURAL JOIN | 이름이 같은 컬럼으로 자동 동등 조인 |

- 조건이 `=` 이면 동등 조인(EQUI JOIN), 그 밖의 비교면 비동등 조인(NON-EQUI JOIN)

---

# 학생과 학과의 관계

| | 학생 | 학과 |
| --- | --- | --- |
| 전체 행 수 | 10 | 4 |
| 짝이 있는 행 | 9 | 3 (D01, D02, D03) |
| 짝이 없는 행 | 1 (윤아름, 학과 NULL) | 1 (수학과, 학생 없음) |

| 조인 | 행 수 | 계산 |
| --- | --- | --- |
| INNER | 9 | 짝이 맞는 학생 |
| LEFT (학생 기준) | 10 | 9 + 윤아름 |
| RIGHT (학과 기준) | 10 | 9 + 수학과 |
| FULL | 11 | 9 + 윤아름 + 수학과 |
| CROSS | 40 | 10 × 4 |

---

# INNER JOIN

```sql
SELECT s.학번, s.이름, d.학과명
FROM 학생 s INNER JOIN 학과 d ON s.학과코드 = d.학과코드
WHERE s.학년 = 2;
```

| 학번 | 이름 | 학과명 |
| --- | --- | --- |
| 1002 | 이영희 | 컴퓨터공학과 |
| 1004 | 최지은 | 전자공학과 |

- 2학년은 3명이지만 학과코드가 NULL인 윤아름은 조인 조건을 만족하지 못해 빠진다
- 같은 뜻의 다른 표기

```sql
SELECT s.학번, s.이름, d.학과명 FROM 학생 s, 학과 d
WHERE s.학과코드 = d.학과코드 AND s.학년 = 2;
```

---

# LEFT · RIGHT OUTER JOIN

```sql
SELECT s.이름, d.학과명
FROM 학생 s LEFT JOIN 학과 d ON s.학과코드 = d.학과코드
WHERE s.학년 = 2;
```

| 이름 | 학과명 |
| --- | --- |
| 이영희 | 컴퓨터공학과 |
| 최지은 | 전자공학과 |
| 윤아름 | **NULL** |

- 기준 테이블(LEFT 면 왼쪽)의 행은 모두 나오고, 짝이 없으면 상대 컬럼이 NULL
- `OUTER` 는 생략할 수 있다. `LEFT JOIN` = `LEFT OUTER JOIN`
- `A LEFT JOIN B` 와 `B RIGHT JOIN A` 는 같은 결과

---

# FULL OUTER JOIN — MySQL 에는 없다

```sql
SELECT s.이름, d.학과명
FROM 학생 s FULL OUTER JOIN 학과 d ON s.학과코드 = d.학과코드;
-- MySQL: ERROR 1064 (42000) ... near 'FULL OUTER JOIN ...'
```

MySQL에서는 LEFT 와 RIGHT 를 `UNION` 으로 합친다.

```sql
SELECT s.학번, s.이름, d.학과명 FROM 학생 s LEFT JOIN 학과 d ON s.학과코드 = d.학과코드
UNION
SELECT s.학번, s.이름, d.학과명 FROM 학생 s RIGHT JOIN 학과 d ON s.학과코드 = d.학과코드;
-- 11행
```

- 시험 답안은 표준 문법인 `FULL OUTER JOIN` 으로 쓴다

---

# 함정 — OUTER JOIN 의 ON 과 WHERE

```sql
-- (가) 조건을 ON 에
SELECT s.이름, d.학과명 FROM 학생 s
LEFT JOIN 학과 d ON s.학과코드 = d.학과코드 AND d.학과명 = '경영학과'
WHERE s.학년 = 1;                  -- 3행: 김철수(NULL), 한소희, 강하늘

-- (나) 조건을 WHERE 에
SELECT s.이름, d.학과명 FROM 학생 s
LEFT JOIN 학과 d ON s.학과코드 = d.학과코드
WHERE s.학년 = 1 AND d.학과명 = '경영학과';   -- 2행: 한소희, 강하늘
```

- ON 은 "어떻게 짝지을지", WHERE 는 "짝지은 뒤 무엇을 남길지"
- 상대 테이블 컬럼에 대한 조건을 WHERE 에 쓰면 NULL 행이 걸러져 **INNER JOIN 과 같아진다**

---

# 짝이 없는 행 찾기

```sql
-- 수강 내역이 없는 학생
SELECT s.학번, s.이름
FROM 학생 s LEFT JOIN 수강 e ON s.학번 = e.학번
WHERE e.학번 IS NULL;              -- 1010 강하늘
```

OUTER JOIN 후 집계할 때는 `COUNT(*)` 와 `COUNT(컬럼)` 이 다르다.

```sql
SELECT d.부서명, COUNT(e.사번) AS 인원, COUNT(*) AS 행수
FROM 부서 d LEFT JOIN 사원 e ON d.부서번호 = e.부서번호
GROUP BY d.부서번호, d.부서명;
```

| 부서명 | 인원 | 행수 |
| --- | --- | --- |
| 연구소 | **0** | **1** |

- 사원이 없는 부서도 NULL로 채워진 행이 1개 있으므로 `COUNT(*)` 는 1이다

---

# SELF JOIN

같은 테이블에 별칭을 두 개 붙여 서로 다른 테이블처럼 조인한다.

```sql
SELECT e.이름 AS 사원, m.이름 AS 상사
FROM 사원 e LEFT JOIN 사원 m ON e.상사사번 = m.사번
WHERE e.부서번호 = 10 OR e.부서번호 IS NULL;
```

| 사원 | 상사 |
| --- | --- |
| 김대표 | NULL |
| 이기획 | 김대표 |
| 문기획 | 이기획 |
| 신수습 | 이기획 |

- INNER JOIN 으로 바꾸면 상사가 없는 김대표가 빠진다
- 별칭이 없으면 컬럼이 어느 쪽 것인지 구분할 수 없어 오류가 난다

---

# CROSS · NATURAL JOIN · USING

```sql
SELECT COUNT(*) FROM 학생 CROSS JOIN 학과;   -- 40
SELECT COUNT(*) FROM 학생, 과목;             -- 60 (조건이 없으면 카티션 곱)
```

```sql
SELECT 학번, 이름, 학과명 FROM 학생 NATURAL JOIN 학과;
SELECT 학번, 이름, 학과명 FROM 학생 JOIN 학과 USING (학과코드);
```

| | NATURAL JOIN | USING |
| --- | --- | --- |
| 조인 컬럼 | 이름이 같은 **모든** 컬럼 | 지정한 컬럼 |
| 조인 컬럼 표시 | 한 번만 | 한 번만 |
| 테이블 별칭 붙이기 | 조인 컬럼에는 불가 | 조인 컬럼에는 불가 |

- 조인 조건을 빠뜨린 쿼리의 행 수는 두 테이블 행 수의 곱이다

---

# 세 테이블 조인

```sql
SELECT s.이름, c.과목명, e.점수
FROM 학생 s
JOIN 수강 e ON s.학번 = e.학번
JOIN 과목 c ON e.과목코드 = c.과목코드
WHERE s.학과코드 = 'D01';
```

| 이름 | 과목명 | 점수 |
| --- | --- | --- |
| 김철수 | 데이터베이스 | 85 |
| 김철수 | 자료구조 | 90 |
| 이영희 | 데이터베이스 | 92 |
| 이영희 | 운영체제 | 78 |
| 오세훈 | 데이터베이스 | 85 |
| 오세훈 | 운영체제 | NULL |

- 테이블 N개를 조인하려면 조인 조건이 최소 N − 1개 필요하다

---

# 집합 연산자

| 연산자 | 의미 | 중복 |
| --- | --- | --- |
| `UNION` | 합집합 | 제거 |
| `UNION ALL` | 합집합 | **유지** |
| `INTERSECT` | 교집합 | 제거 |
| `EXCEPT` (Oracle `MINUS`) | 차집합 | 제거 |

- 두 SELECT 의 **컬럼 수가 같고** 대응하는 컬럼의 타입이 호환되어야 한다
- 결과의 컬럼 이름은 첫 번째 SELECT 를 따른다
- ORDER BY 는 맨 마지막에 한 번만 쓴다
- 집합 연산에서는 NULL끼리 같은 값으로 취급한다

---

# 집합 연산 예

학생.주소: 서울×4, 부산×2, 대전, 광주, 인천, NULL / 부서.지역: 서울×2, 부산, 대전, 판교

```sql
SELECT 주소 FROM 학생  [연산자]  SELECT 지역 FROM 부서;
```

| 연산자 | 결과 | 행 수 |
| --- | --- | --- |
| `UNION` | 서울, 부산, 대전, NULL, 광주, 인천, 판교 | 7 |
| `UNION ALL` | 중복 포함 전부 | 15 |
| `INTERSECT` | 서울, 부산, 대전 | 3 |
| `EXCEPT` | NULL, 광주, 인천 | 3 |

- 순서를 바꾼 `부서 EXCEPT 학생` 의 결과는 판교 1행이다. 차집합은 순서가 중요하다

---

# 표준 SQL 과 MySQL 차이

| 항목 | 표준·시험 | MySQL |
| --- | --- | --- |
| FULL OUTER JOIN | 지원 | 미지원. LEFT `UNION` RIGHT 로 대체 |
| 차집합 | `EXCEPT` (Oracle 은 `MINUS`) | `EXCEPT` (8.0.31 이상). `MINUS` 는 오류 |
| 교집합 | `INTERSECT` | 8.0.31 이상 |
| Oracle 외부 조인 `(+)` | Oracle 전용 | 미지원 |

```sql
-- Oracle 표기: (+) 가 붙은 쪽이 NULL로 채워지는 쪽
SELECT s.이름, d.학과명 FROM 학생 s, 학과 d WHERE s.학과코드 = d.학과코드(+);
-- = 학생 LEFT OUTER JOIN 학과
```

---

# 정리 — 자주 틀리는 것

1. INNER JOIN 은 NULL 키와 짝 없는 행을 모두 버린다
2. LEFT 는 왼쪽, RIGHT 는 오른쪽 테이블의 모든 행을 남긴다
3. OUTER JOIN 뒤 WHERE 에 상대 테이블 조건을 쓰면 INNER 와 같아진다
4. OUTER JOIN 후 인원을 셀 때는 `COUNT(*)` 가 아니라 `COUNT(상대 테이블 컬럼)`
5. 조인 조건이 없으면 행 수는 곱
6. `UNION` 은 중복 제거, `UNION ALL` 은 유지
7. 차집합은 순서를 바꾸면 결과가 달라진다
8. 답안은 `FULL OUTER JOIN`, `EXCEPT`/`MINUS` 등 문제가 제시한 DBMS 표기를 따른다
