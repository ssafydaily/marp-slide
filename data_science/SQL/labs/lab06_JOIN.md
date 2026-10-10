# Lab 06. JOIN 과 집합 연산

슬라이드: `06_JOIN_집합연산.md`

## 1. 따라 하기

### 1-1. 조인별 행 수 비교

```sql
SELECT COUNT(*) FROM 학생 s JOIN 학과 d       ON s.학과코드 = d.학과코드;   -- 9
SELECT COUNT(*) FROM 학생 s LEFT JOIN 학과 d  ON s.학과코드 = d.학과코드;   -- 10
SELECT COUNT(*) FROM 학생 s RIGHT JOIN 학과 d ON s.학과코드 = d.학과코드;   -- 10
SELECT COUNT(*) FROM 학생 s CROSS JOIN 학과 d;                              -- 40
```

### 1-2. RIGHT JOIN 에서 짝 없는 행

```sql
SELECT d.학과명, s.이름
FROM 학생 s RIGHT JOIN 학과 d ON s.학과코드 = d.학과코드
WHERE d.학과코드 IN ('D03', 'D04')
ORDER BY d.학과코드, s.학번;
```

| 학과명 | 이름 |
| --- | --- |
| 경영학과 | 정우성 |
| 경영학과 | 한소희 |
| 경영학과 | 강하늘 |
| 수학과 | NULL |

### 1-3. FULL OUTER JOIN 대체

```sql
SELECT s.학번, s.이름, d.학과명 FROM 학생 s LEFT JOIN 학과 d ON s.학과코드 = d.학과코드
UNION
SELECT s.학번, s.이름, d.학과명 FROM 학생 s RIGHT JOIN 학과 d ON s.학과코드 = d.학과코드;
```

11행이 나온다. `UNION` 이 양쪽에 공통으로 나온 9행의 중복을 제거한다.

### 1-4. ON 조건과 WHERE 조건

```sql
SELECT s.이름, d.학과명
FROM 학생 s LEFT JOIN 학과 d ON s.학과코드 = d.학과코드 AND d.학과명 = '경영학과'
WHERE s.학년 = 1
ORDER BY s.학번;
```

| 이름 | 학과명 |
| --- | --- |
| 김철수 | NULL |
| 한소희 | 경영학과 |
| 강하늘 | 경영학과 |

```sql
SELECT s.이름, d.학과명
FROM 학생 s LEFT JOIN 학과 d ON s.학과코드 = d.학과코드
WHERE s.학년 = 1 AND d.학과명 = '경영학과'
ORDER BY s.학번;
```

| 이름 | 학과명 |
| --- | --- |
| 한소희 | 경영학과 |
| 강하늘 | 경영학과 |

### 1-5. OUTER JOIN 과 집계

```sql
SELECT d.부서명, COUNT(e.사번) AS 인원, COUNT(*) AS 행수
FROM 부서 d LEFT JOIN 사원 e ON d.부서번호 = e.부서번호
GROUP BY d.부서번호, d.부서명
ORDER BY d.부서번호;
```

| 부서명 | 인원 | 행수 |
| --- | --- | --- |
| 기획부 | 3 | 3 |
| 개발부 | 4 | 4 |
| 영업부 | 3 | 3 |
| 인사부 | 1 | 1 |
| 연구소 | 0 | 1 |

### 1-6. 집합 연산

```sql
SELECT 주소 FROM 학생 UNION     SELECT 지역 FROM 부서;   -- 7행
SELECT 주소 FROM 학생 UNION ALL SELECT 지역 FROM 부서;   -- 15행
SELECT 주소 FROM 학생 INTERSECT SELECT 지역 FROM 부서;   -- 서울, 부산, 대전
SELECT 주소 FROM 학생 EXCEPT    SELECT 지역 FROM 부서;   -- NULL, 광주, 인천
SELECT 지역 FROM 부서 EXCEPT    SELECT 주소 FROM 학생;   -- 판교
```

`MINUS` 는 MySQL에서 문법 오류다.

## 2. 결과 예측

**Q1.** 다음 쿼리의 결과 행 수는?

```sql
SELECT * FROM 사원 e JOIN 부서 d ON e.부서번호 = d.부서번호;
```

**Q2.** 다음 쿼리의 결과 행 수는?

```sql
SELECT * FROM 사원 e RIGHT JOIN 부서 d ON e.부서번호 = d.부서번호;
```

**Q3.** 다음 쿼리의 결과 행 수는?

```sql
SELECT * FROM 부서, 학과;
```

**Q4.** 다음 쿼리의 결과 행 수는?

```sql
SELECT e.이름, m.이름 FROM 사원 e JOIN 사원 m ON e.상사사번 = m.사번;
```

**Q5.** 다음 쿼리의 결과 행 수는?

```sql
SELECT 학과코드 FROM 학생
UNION
SELECT 학과코드 FROM 과목;
```

**Q6.** 다음 쿼리의 결과 값은?

```sql
SELECT COUNT(*) FROM 학생 s, 수강 e WHERE s.학번 = e.학번 AND e.점수 >= 85;
```

<details>
<summary>정답과 해설</summary>

- **Q1.** 11행. 부서번호가 NULL인 신수습이 빠진다.
- **Q2.** 12행. INNER 11행 + 사원이 없는 연구소 1행. 신수습은 포함되지 않는다.
- **Q3.** 20행. 조인 조건이 없으므로 5 × 4.
- **Q4.** 11행. 상사사번이 NULL인 김대표가 빠진다.
- **Q5.** 5행. D01, D02, D03, D04, NULL. 학생 쪽에는 D04가 없고 NULL이 있으며, 과목 쪽에는 D04가 있다. UNION 은 중복을 제거한다.
- **Q6.** 7. 점수가 85 이상인 수강 행은 85, 90, 92, 88, 95, 85, 85 로 7건이다. NULL 점수는 제외된다.

</details>

## 3. 쿼리 작성

**Q7.** 사원의 이름과 소속 부서명을 조회하시오. 부서가 없는 사원도 포함한다.

**Q8.** 학과명과 그 학과 학생들의 평균 점수를 평균이 높은 순으로 조회하시오. (학과, 학생, 수강 조인)

**Q9.** 수강생이 한 명도 없는 과목의 과목명을 OUTER JOIN 으로 조회하시오.

**Q10.** 부하 직원이 2명 이상인 사원의 이름과 부하 직원 수를 조회하시오.

**Q11.** 자신의 상사 급여의 80% 이상을 받는 사원의 이름과 급여, 상사 이름을 조회하시오.

**Q12.** 근무 지역별 사원 수를 조회하시오.

<details>
<summary>정답과 해설</summary>

```sql
-- Q7 (12행, 신수습의 부서명은 NULL)
SELECT e.이름, d.부서명
FROM 사원 e LEFT JOIN 부서 d ON e.부서번호 = d.부서번호;

-- Q8: 컴퓨터공학과 86.0, 경영학과 77.5, 전자공학과 74.5
SELECT d.학과명, AVG(e.점수) AS 평균
FROM 학과 d
JOIN 학생 s ON d.학과코드 = s.학과코드
JOIN 수강 e ON s.학번 = e.학번
GROUP BY d.학과코드, d.학과명
ORDER BY 평균 DESC;

-- Q9: 선형대수
SELECT c.과목명
FROM 과목 c LEFT JOIN 수강 e ON c.과목코드 = e.과목코드
WHERE e.과목코드 IS NULL;

-- Q10: 김대표 4, 이기획 2, 정코딩 2
SELECT m.이름, COUNT(*) AS 부하수
FROM 사원 e JOIN 사원 m ON e.상사사번 = m.사번
GROUP BY m.사번, m.이름
HAVING COUNT(*) >= 2;

-- Q11: 박개발(7200, 김대표), 윤판매(5500, 최영업)
SELECT e.이름, e.급여, m.이름 AS 상사
FROM 사원 e JOIN 사원 m ON e.상사사번 = m.사번
WHERE e.급여 >= m.급여 * 0.8;

-- Q12: 대전 1, 부산 3, 서울 7
SELECT d.지역, COUNT(*) AS 인원
FROM 사원 e JOIN 부서 d ON e.부서번호 = d.부서번호
GROUP BY d.지역;
```

- Q8에서 수학과는 학생이 없고, 학과가 NULL인 윤아름은 조인에서 빠진다.
- Q10에서 `GROUP BY m.이름` 만 쓰면 동명이인이 한 그룹으로 합쳐진다. 기본키를 함께 묶는다.

</details>
