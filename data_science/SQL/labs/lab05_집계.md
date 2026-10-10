# Lab 05. 집계와 그룹

슬라이드: `05_집계_그룹.md`

## 1. 따라 하기

### 1-1. 집계 함수와 NULL

```sql
SELECT COUNT(*), COUNT(점수), SUM(점수), AVG(점수), MAX(점수), MIN(점수) FROM 수강;
```

| COUNT(*) | COUNT(점수) | SUM(점수) | AVG(점수) | MAX(점수) | MIN(점수) |
| --- | --- | --- | --- | --- | --- |
| 14 | 12 | 960 | 80.0000 | 95 | 55 |

```sql
SELECT COUNT(*), COUNT(보너스), SUM(보너스), AVG(보너스), AVG(IFNULL(보너스, 0)) FROM 사원;
```

| COUNT(*) | COUNT(보너스) | SUM(보너스) | AVG(보너스) | AVG(IFNULL(보너스,0)) |
| --- | --- | --- | --- | --- |
| 12 | 6 | 2000 | 333.3333 | 166.6667 |

### 1-2. GROUP BY 와 HAVING

```sql
SELECT 부서번호, COUNT(*) AS 인원, SUM(급여) AS 합계, AVG(급여) AS 평균
FROM 사원
GROUP BY 부서번호
ORDER BY 부서번호;
```

| 부서번호 | 인원 | 합계 | 평균 |
| --- | --- | --- | --- |
| NULL | 1 | 2800 | 2800.0000 |
| 10 | 3 | 20200 | 6733.3333 |
| 20 | 4 | 19900 | 4975.0000 |
| 30 | 3 | 15500 | 5166.6667 |
| 40 | 1 | 5200 | 5200.0000 |

```sql
SELECT 주소, COUNT(*) AS 인원 FROM 학생 GROUP BY 주소 HAVING COUNT(*) >= 2;
```

| 주소 | 인원 |
| --- | --- |
| 서울 | 4 |
| 부산 | 2 |

### 1-3. ROLLUP

```sql
SELECT 부서번호, 직급, SUM(급여) AS 합계
FROM 사원
WHERE 부서번호 IN (10, 20)
GROUP BY 부서번호, 직급 WITH ROLLUP;
```

| 부서번호 | 직급 | 합계 |
| --- | --- | --- |
| 10 | 대리 | 4200 |
| 10 | 부장 | 7000 |
| 10 | 사장 | 9000 |
| 10 | NULL | 20200 |
| 20 | 과장 | 5500 |
| 20 | 대리 | 4200 |
| 20 | 부장 | 7200 |
| 20 | 사원 | 3000 |
| 20 | NULL | 19900 |
| NULL | NULL | 40100 |

MySQL 8.4에서는 `GROUP BY ROLLUP(부서번호, 직급)` 형태도 실행된다. `CUBE` 는 지원하지 않는다.

소계 행의 NULL과 데이터의 NULL을 구분하려면 `GROUPING()` 을 쓴다. 소계·총계 행에서 1을 반환한다.

```sql
SELECT 부서번호, GROUPING(부서번호) AS g, COUNT(*)
FROM 사원 WHERE 부서번호 IN (10, 20)
GROUP BY 부서번호 WITH ROLLUP;
```

| 부서번호 | g | COUNT(*) |
| --- | --- | --- |
| 10 | 0 | 3 |
| 20 | 0 | 4 |
| NULL | 1 | 7 |

### 1-4. 윈도우 함수

```sql
SELECT 부서번호, 이름, 급여,
       RANK() OVER (PARTITION BY 부서번호 ORDER BY 급여 DESC) AS 부서내순위,
       SUM(급여) OVER (PARTITION BY 부서번호) AS 부서합계
FROM 사원
WHERE 부서번호 IN (10, 30);
```

| 부서번호 | 이름 | 급여 | 부서내순위 | 부서합계 |
| --- | --- | --- | --- | --- |
| 10 | 김대표 | 9000 | 1 | 20200 |
| 10 | 이기획 | 7000 | 2 | 20200 |
| 10 | 문기획 | 4200 | 3 | 20200 |
| 30 | 최영업 | 6800 | 1 | 15500 |
| 30 | 윤판매 | 5500 | 2 | 15500 |
| 30 | 강매출 | 3200 | 3 | 15500 |

```sql
SELECT 이름, 급여, SUM(급여) OVER (ORDER BY 사번) AS 누적 FROM 사원 WHERE 부서번호 = 20;
```

| 이름 | 급여 | 누적 |
| --- | --- | --- |
| 박개발 | 7200 | 7200 |
| 정코딩 | 5500 | 12700 |
| 한서버 | 4200 | 16900 |
| 오신입 | 3000 | 19900 |

```sql
SELECT 이름, 급여,
       LAG(급여)  OVER (ORDER BY 급여 DESC) AS 앞,
       LEAD(급여) OVER (ORDER BY 급여 DESC) AS 뒤,
       NTILE(2)   OVER (ORDER BY 급여 DESC) AS 조
FROM 사원 WHERE 부서번호 = 20;
```

| 이름 | 급여 | 앞 | 뒤 | 조 |
| --- | --- | --- | --- | --- |
| 박개발 | 7200 | NULL | 5500 | 1 |
| 정코딩 | 5500 | 7200 | 4200 | 1 |
| 한서버 | 4200 | 5500 | 3000 | 2 |
| 오신입 | 3000 | 4200 | NULL | 2 |

## 2. 결과 예측

**Q1.** 다음 쿼리의 결과를 쓰시오.

```sql
SELECT COUNT(*), COUNT(점수) FROM 수강 WHERE 과목코드 = 'C101';
```

**Q2.** 다음 쿼리의 결과 행 수는?

```sql
SELECT 학과코드, COUNT(*) FROM 학생 GROUP BY 학과코드;
```

**Q3.** 다음 쿼리의 결과를 쓰시오.

```sql
SELECT 직급, COUNT(*) FROM 사원
WHERE 급여 >= 4000
GROUP BY 직급
HAVING COUNT(*) >= 2
ORDER BY 직급;
```

**Q4.** 다음 쿼리의 결과에서 `조인사` 의 `a`, `b` 값은?

```sql
SELECT 이름,
       RANK()       OVER (ORDER BY 급여 DESC) AS a,
       DENSE_RANK() OVER (ORDER BY 급여 DESC) AS b
FROM 사원 WHERE 급여 <= 5500;
```

**Q5.** 다음 쿼리의 결과 행 수는?

```sql
SELECT 학년, 학과코드, COUNT(*) FROM 학생
WHERE 학과코드 IN ('D01', 'D02')
GROUP BY 학년, 학과코드 WITH ROLLUP;
```

**Q6.** 다음 쿼리의 결과를 쓰시오.

```sql
SELECT 직급, MAX(급여) - MIN(급여) AS 차이 FROM 사원 GROUP BY 직급 HAVING COUNT(*) >= 3;
```

<details>
<summary>정답과 해설</summary>

- **Q1.** 4, 3. C101 수강 4건 중 1003의 점수가 NULL이다.
- **Q2.** 4행. D01, D02, D03 그리고 NULL 그룹. 학생이 없는 D04는 학생 테이블에 행이 없으므로 나오지 않는다.
- **Q3.** 과장 3, 대리 2, 부장 3. 급여 4000 미만인 사원 3명이 WHERE 에서 빠져 '사원' 직급 그룹 자체가 없고, 사장은 1명이라 HAVING 에서 빠진다.
- **Q4.** a = 3, b = 2. 5500이 2명이므로 RANK 는 2위를 건너뛰고 3, DENSE_RANK 는 2.
- **Q5.** 11행. 상세 6행(1-D01, 2-D01, 2-D02, 3-D01, 3-D02, 4-D02) + 학년별 소계 4행 + 총계 1행.
- **Q6.** 부장 400 (7200 − 6800), 과장 300 (5500 − 5200), 사원 400 (3200 − 2800).

</details>

## 3. 쿼리 작성

**Q7.** 수강 테이블에서 과목코드별 평균 점수를 구하되, 평균이 79점 이상인 과목만 평균이 높은 순으로 조회하시오.

**Q8.** 사원 테이블에서 직급별 평균 급여를 평균 급여가 높은 순으로 조회하시오.

**Q9.** 학생 테이블에서 학년별 학생 수를 학년 오름차순으로 조회하시오.

**Q10.** 사원 테이블에서 급여가 두 번째로 높은 사원의 이름과 급여를 조회하시오. 동점자는 같은 순위로 보고 순위를 건너뛰지 않는다.

**Q11.** 사원 테이블에서 입사 연도별 입사자 수를 조회하시오. (MySQL의 `YEAR()` 함수 사용)

<details>
<summary>정답과 해설</summary>

```sql
-- Q7: C101 87.3333, C103 79.3333
SELECT 과목코드, AVG(점수) AS 평균
FROM 수강
GROUP BY 과목코드
HAVING AVG(점수) >= 79
ORDER BY 평균 DESC;

-- Q8: 사장 9000, 부장 7000, 과장 5400, 대리 4200, 사원 3000
SELECT 직급, AVG(급여) AS 평균급여
FROM 사원
GROUP BY 직급
ORDER BY 평균급여 DESC;

-- Q9: 1학년 3, 2학년 3, 3학년 2, 4학년 2
SELECT 학년, COUNT(*) AS 학생수 FROM 학생 GROUP BY 학년 ORDER BY 학년;

-- Q10: 박개발 7200
SELECT 이름, 급여
FROM (SELECT 이름, 급여, DENSE_RANK() OVER (ORDER BY 급여 DESC) AS r FROM 사원) t
WHERE r = 2;

-- Q11
SELECT YEAR(입사일) AS 연도, COUNT(*) AS 인원 FROM 사원 GROUP BY YEAR(입사일) ORDER BY 연도;
```

- Q7에서 `WHERE AVG(점수) >= 79` 로 쓰면 오류다.
- Q10에서 윈도우 함수는 WHERE 절에 직접 쓸 수 없어서 인라인 뷰로 감싼다 (7단계).

</details>
