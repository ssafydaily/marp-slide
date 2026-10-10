# Lab 07. 서브쿼리

슬라이드: `07_서브쿼리.md`

## 1. 따라 하기

### 1-1. 단일 행 서브쿼리

```sql
SELECT AVG(급여) FROM 사원;   -- 5300.0000

SELECT 이름, 급여 FROM 사원
WHERE 급여 > (SELECT AVG(급여) FROM 사원)
ORDER BY 급여 DESC;
```

| 이름 | 급여 |
| --- | --- |
| 김대표 | 9000 |
| 박개발 | 7200 |
| 이기획 | 7000 |
| 최영업 | 6800 |
| 정코딩 | 5500 |
| 윤판매 | 5500 |

### 1-2. NOT IN 과 NULL

```sql
SELECT COUNT(*) FROM 사원 WHERE 사번 NOT IN (SELECT 상사사번 FROM 사원);   -- 0

SELECT 이름 FROM 사원
WHERE 사번 NOT IN (SELECT 상사사번 FROM 사원 WHERE 상사사번 IS NOT NULL)
ORDER BY 사번;
```

| 이름 |
| --- |
| 한서버 |
| 오신입 |
| 강매출 |
| 조인사 |
| 문기획 |
| 신수습 |

`NOT EXISTS` 로도 같은 결과를 얻는다.

```sql
SELECT 이름 FROM 사원 e
WHERE NOT EXISTS (SELECT 1 FROM 사원 x WHERE x.상사사번 = e.사번)
ORDER BY 사번;
```

### 1-3. ANY 와 ALL

```sql
SELECT 이름, 급여 FROM 사원
WHERE 급여 > ALL (SELECT 급여 FROM 사원 WHERE 부서번호 = 30)
ORDER BY 급여;
```

| 이름 | 급여 |
| --- | --- |
| 이기획 | 7000 |
| 박개발 | 7200 |
| 김대표 | 9000 |

```sql
SELECT 이름, 급여 FROM 사원
WHERE 급여 > ANY (SELECT 급여 FROM 사원 WHERE 부서번호 = 30)
  AND 부서번호 = 20
ORDER BY 급여;
```

| 이름 | 급여 |
| --- | --- |
| 한서버 | 4200 |
| 정코딩 | 5500 |
| 박개발 | 7200 |

30번 부서의 최솟값 3200보다 크면 된다. 오신입(3000)만 빠진다.

### 1-4. 상관 서브쿼리

```sql
SELECT 이름, 부서번호, 급여 FROM 사원 e
WHERE 급여 > (SELECT AVG(급여) FROM 사원 WHERE 부서번호 = e.부서번호)
ORDER BY 부서번호, 사번;
```

| 이름 | 부서번호 | 급여 |
| --- | --- | --- |
| 김대표 | 10 | 9000 |
| 이기획 | 10 | 7000 |
| 박개발 | 20 | 7200 |
| 정코딩 | 20 | 5500 |
| 최영업 | 30 | 6800 |
| 윤판매 | 30 | 5500 |

### 1-5. 과목별 최고 점수자

```sql
SELECT c.과목명, s.이름, e.점수
FROM 수강 e
JOIN 학생 s ON e.학번 = s.학번
JOIN 과목 c ON c.과목코드 = e.과목코드
WHERE e.점수 = (SELECT MAX(점수) FROM 수강 WHERE 과목코드 = e.과목코드)
ORDER BY c.과목코드;
```

| 과목명 | 이름 | 점수 |
| --- | --- | --- |
| 데이터베이스 | 이영희 | 92 |
| 자료구조 | 김철수 | 90 |
| 회로이론 | 최지은 | 95 |
| 회계원리 | 한소희 | 85 |
| 운영체제 | 이영희 | 78 |

### 1-6. WITH 절 (CTE)

인라인 뷰에 이름을 붙여 여러 번 쓸 수 있다.

```sql
WITH 부서평균 AS (
    SELECT 부서번호, AVG(급여) AS 평균 FROM 사원 GROUP BY 부서번호
)
SELECT 부서번호, 평균 FROM 부서평균
WHERE 평균 = (SELECT MAX(평균) FROM 부서평균);
```

| 부서번호 | 평균 |
| --- | --- |
| 10 | 6733.3333 |

## 2. 결과 예측

**Q1.** 다음 쿼리의 결과 행 수는?

```sql
SELECT 이름 FROM 학생
WHERE 학번 IN (SELECT 학번 FROM 수강 WHERE 과목코드 = 'C101');
```

**Q2.** 다음 쿼리의 결과 행 수는?

```sql
SELECT 이름 FROM 사원 WHERE 사번 NOT IN (SELECT 상사사번 FROM 사원);
```

**Q3.** 다음 쿼리의 결과 행 수는?

```sql
SELECT 이름 FROM 사원
WHERE 급여 > ALL (SELECT 급여 FROM 사원 WHERE 부서번호 = 50);
```

**Q4.** 다음 쿼리의 결과를 쓰시오.

```sql
SELECT 부서명 FROM 부서 d
WHERE NOT EXISTS (SELECT * FROM 사원 e WHERE e.부서번호 = d.부서번호);
```

**Q5.** 다음 쿼리의 결과 행 수는?

```sql
SELECT 이름 FROM 학생
WHERE 학번 IN (SELECT 학번 FROM 수강 GROUP BY 학번 HAVING AVG(점수) >= 85);
```

**Q6.** 다음 쿼리의 결과 행 수는?

```sql
SELECT 이름, 급여 FROM 사원
WHERE (부서번호, 급여) IN (SELECT 부서번호, MAX(급여) FROM 사원 GROUP BY 부서번호);
```

<details>
<summary>정답과 해설</summary>

- **Q1.** 4행. 1001, 1002, 1003, 1007. 점수가 NULL이어도 수강 행은 존재한다.
- **Q2.** 0행. 서브쿼리 결과에 NULL(김대표의 상사사번)이 있다.
- **Q3.** 12행. 50번 부서에는 사원이 없어 서브쿼리가 빈 결과다. 빈 집합에 대한 `ALL` 은 항상 TRUE.
- **Q4.** 연구소.
- **Q5.** 5행. 김철수(1001, 87.5), 이영희(85), 박민수(88, NULL 제외), 한소희(85), 오세훈(85, NULL 제외). `AVG` 는 NULL을 빼고 계산한다.
- **Q6.** 4행. 김대표, 박개발, 최영업, 조인사. 부서번호가 NULL인 신수습은 NULL 비교가 섞여 일치하지 않는다.

</details>

## 3. 쿼리 작성

**Q7.** 수강생이 한 명도 없는 과목의 과목명을 서브쿼리로 조회하시오.

**Q8.** '서울' 지역 부서에 근무하면서 전체 평균 급여보다 적게 받는 사원의 이름을 조회하시오.

**Q9.** 데이터베이스(C101)는 수강하지만 자료구조(C102)는 수강하지 않는 학생의 이름을 조회하시오.

**Q10.** 각 학생의 학번, 이름, 최고 점수를 조회하시오. 수강 내역이 없는 학생도 포함한다. (스칼라 서브쿼리 사용)

**Q11.** 영업부(부서명) 사원 중 누구보다도 급여가 많은 사원의 이름을 `ALL` 을 사용해 조회하시오.

**Q12.** 평균 급여가 가장 높은 부서의 부서명을 조회하시오.

<details>
<summary>정답과 해설</summary>

```sql
-- Q7: 선형대수
SELECT 과목명 FROM 과목
WHERE 과목코드 NOT IN (SELECT 과목코드 FROM 수강);

-- Q8: 한서버, 오신입, 문기획
SELECT 이름 FROM 사원
WHERE 부서번호 IN (SELECT 부서번호 FROM 부서 WHERE 지역 = '서울')
  AND 급여 < (SELECT AVG(급여) FROM 사원);

-- Q9: 이영희, 박민수, 오세훈
SELECT 이름 FROM 학생
WHERE 학번 IN     (SELECT 학번 FROM 수강 WHERE 과목코드 = 'C101')
  AND 학번 NOT IN (SELECT 학번 FROM 수강 WHERE 과목코드 = 'C102');

-- Q10 (10행, 강하늘의 최고 점수는 NULL)
SELECT 학번, 이름,
       (SELECT MAX(점수) FROM 수강 e WHERE e.학번 = s.학번) AS 최고점수
FROM 학생 s;

-- Q11: 이기획, 박개발, 김대표
SELECT 이름 FROM 사원
WHERE 급여 > ALL (SELECT e.급여 FROM 사원 e JOIN 부서 d ON e.부서번호 = d.부서번호
                  WHERE d.부서명 = '영업부');

-- Q12: 기획부
SELECT 부서명 FROM 부서
WHERE 부서번호 = (SELECT 부서번호 FROM 사원
                  GROUP BY 부서번호
                  ORDER BY AVG(급여) DESC LIMIT 1);
```

- Q7의 `NOT IN` 은 `수강.과목코드` 가 NOT NULL 이라 안전하다.
- Q12는 `LIMIT` 을 쓰지 않고 `HAVING AVG(급여) >= ALL (SELECT AVG(급여) FROM 사원 GROUP BY 부서번호)` 로도 풀 수 있다. 이 방식이 표준 SQL에 가깝다.

</details>
