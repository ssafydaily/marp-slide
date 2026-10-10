# Lab 04. DML 기본

슬라이드: `04_DML_기본.md`

모든 실습은 `student` 계정으로 `study` 데이터베이스에서 실행한다. 데이터는 `lab00` 의 표를 참고한다.

## 1. 따라 하기

### 1-1. 조건과 정렬

```sql
SELECT 이름, 학년 FROM 학생 WHERE 학년 >= 3 ORDER BY 학년 DESC, 이름;
```

| 이름 | 학년 |
| --- | --- |
| 김철수 | 4 |
| 정우성 | 4 |
| 박민수 | 3 |
| 오세훈 | 3 |

### 1-2. IN, BETWEEN, LIKE

```sql
SELECT 이름, 직급, 급여 FROM 사원 WHERE 급여 BETWEEN 4200 AND 5500 ORDER BY 사번;
```

| 이름 | 직급 | 급여 |
| --- | --- | --- |
| 정코딩 | 과장 | 5500 |
| 한서버 | 대리 | 4200 |
| 윤판매 | 과장 | 5500 |
| 조인사 | 과장 | 5200 |
| 문기획 | 대리 | 4200 |

경계값 4200과 5500이 모두 포함된다.

```sql
SELECT 이름 FROM 학생 WHERE 이름 LIKE '김%';    -- 김철수, 김철수
SELECT 이름 FROM 학생 WHERE 이름 LIKE '_영%';   -- 이영희
SELECT 이름 FROM 사원 WHERE 이름 LIKE '%기획';  -- 이기획, 문기획
```

### 1-3. NULL

```sql
SELECT COUNT(*) FROM 학생 WHERE 주소 = NULL;                      -- 0
SELECT COUNT(*) FROM 학생 WHERE 주소 IS NULL;                     -- 1
SELECT COUNT(*) FROM 학생 WHERE 주소 = '서울';                    -- 4
SELECT COUNT(*) FROM 학생 WHERE 주소 <> '서울';                   -- 5
SELECT COUNT(*) FROM 학생 WHERE 주소 <> '서울' OR 주소 IS NULL;   -- 6
```

### 1-4. 정렬에서 NULL 위치

```sql
SELECT 이름, 보너스 FROM 사원 WHERE 부서번호 IN (20, 30) ORDER BY 보너스, 이름;
```

| 이름 | 보너스 |
| --- | --- |
| 오신입 | NULL |
| 최영업 | NULL |
| 한서버 | NULL |
| 강매출 | 0 |
| 정코딩 | 300 |
| 윤판매 | 400 |
| 박개발 | 600 |

MySQL은 NULL을 가장 작은 값으로 취급한다. `ORDER BY 보너스 DESC` 로 바꾸면 NULL이 맨 뒤로 간다.

### 1-5. 데이터 변경과 ROLLBACK

`START TRANSACTION` 으로 시작하면 `ROLLBACK` 으로 되돌릴 수 있다.

```sql
START TRANSACTION;

INSERT INTO 학생 (학번, 이름, 학과코드) VALUES (1011, '홍길동', 'D01');
SELECT * FROM 학생 WHERE 학번 = 1011;
```

| 학번 | 이름 | 학년 | 학과코드 | 주소 |
| --- | --- | --- | --- | --- |
| 1011 | 홍길동 | 1 | D01 | NULL |

학년에는 DEFAULT 값 1이, 주소에는 NULL이 들어갔다.

```sql
UPDATE 사원 SET 급여 = 급여 * 1.1 WHERE 직급 = '사원';
SELECT 이름, 급여 FROM 사원 WHERE 직급 = '사원';
```

| 이름 | 급여 |
| --- | --- |
| 오신입 | 3300 |
| 강매출 | 3520 |
| 신수습 | 3080 |

```sql
DELETE FROM 수강 WHERE 점수 IS NULL;
SELECT COUNT(*) FROM 수강;   -- 12

ROLLBACK;
SELECT COUNT(*) FROM 수강;   -- 14
```

## 2. 결과 예측

실행하기 전에 결과를 먼저 적어 본다.

**Q1.** 다음 쿼리의 결과 행 수는?

```sql
SELECT * FROM 학생 WHERE 학년 BETWEEN 2 AND 3;
```

**Q2.** 다음 쿼리의 결과 행 수는?

```sql
SELECT * FROM 학생 WHERE 학과코드 NOT IN ('D01', 'D02');
```

**Q3.** 다음 두 쿼리의 결과 행 수는 각각 몇인가?

```sql
SELECT 이름 FROM 학생 WHERE 학과코드 = 'D01' OR 학과코드 = 'D02' AND 학년 >= 3;
SELECT 이름 FROM 학생 WHERE (학과코드 = 'D01' OR 학과코드 = 'D02') AND 학년 >= 3;
```

**Q4.** 다음 쿼리의 결과를 쓰시오.

```sql
SELECT COUNT(주소), COUNT(DISTINCT 주소) FROM 학생;
```

**Q5.** 다음 쿼리의 결과에서 `합계` 가 NULL인 행은 몇 개인가?

```sql
SELECT 이름, 급여 + 보너스 AS 합계 FROM 사원;
```

**Q6.** 다음 쿼리의 결과를 순서대로 쓰시오.

```sql
SELECT 이름 FROM 사원 ORDER BY 급여 DESC LIMIT 3;
```

<details>
<summary>정답과 해설</summary>

- **Q1.** 5행. 2학년 3명(이영희, 최지은, 윤아름)과 3학년 2명(박민수, 오세훈). 경계값을 포함한다.
- **Q2.** 3행. D03 학생 3명. 학과코드가 NULL인 윤아름은 `NOT IN` 의 결과가 UNKNOWN 이므로 제외된다.
- **Q3.** 5행, 3행. 첫 번째는 D01 학생 3명 + D02 중 3학년 이상 2명(박민수, 김철수). 두 번째는 D01·D02 중 3학년 이상인 오세훈, 박민수, 김철수.
- **Q4.** 9, 5. 주소가 NULL인 1명을 뺀 9건, 서로 다른 주소는 서울·부산·대전·광주·인천 5개. `COUNT(컬럼)` 은 NULL을 세지 않는다.
- **Q5.** 6개. 보너스가 NULL인 사원이 6명이다. 보너스가 0인 강매출은 3200으로 계산된다.
- **Q6.** 김대표, 박개발, 이기획 (9000, 7200, 7000).

</details>

## 3. 쿼리 작성

**Q7.** 학생 테이블에서 주소가 '서울' 이 아니거나 입력되지 않은 학생의 이름을 조회하시오.

**Q8.** 사원 테이블에서 2020년 1월 1일 이후에 입사한 사원의 이름과 입사일을 입사일 오름차순으로 조회하시오.

**Q9.** 사원 테이블에서 직급이 '과장' 이고 보너스가 NULL인 사원의 보너스를 100으로 수정하시오.

**Q10.** 수강 테이블에서 점수가 60 미만인 행을 삭제하시오.

**Q11.** 학생 테이블에 학번 1020, 이름 '임꺽정', 학년 3, 학과코드 'D02' 인 학생을 삽입하시오. 주소는 입력하지 않는다.

**Q12.** 사원 테이블에서 이름의 두 번째 글자가 '기' 인 사원의 이름과 직급을 조회하시오.

<details>
<summary>정답과 해설</summary>

```sql
-- Q7 (6행)
SELECT 이름 FROM 학생 WHERE 주소 <> '서울' OR 주소 IS NULL;

-- Q8 (문기획, 강매출, 오신입, 신수습)
SELECT 이름, 입사일 FROM 사원 WHERE 입사일 >= '2020-01-01' ORDER BY 입사일;

-- Q9 (조인사 1행)
UPDATE 사원 SET 보너스 = 100 WHERE 직급 = '과장' AND 보너스 IS NULL;

-- Q10 (1009 C103 1행)
DELETE FROM 수강 WHERE 점수 < 60;

-- Q11
INSERT INTO 학생 (학번, 이름, 학년, 학과코드) VALUES (1020, '임꺽정', 3, 'D02');

-- Q12 (이기획, 문기획)
SELECT 이름, 직급 FROM 사원 WHERE 이름 LIKE '_기%';
```

- Q9에서 `보너스 = NULL` 로 쓰면 0행이 수정된다.
- Q10에서 점수가 NULL인 2행은 `점수 < 60` 이 UNKNOWN 이므로 삭제되지 않는다.
- Q9~Q11을 실행했다면 `lab00` 의 초기화 명령으로 데이터를 되돌린다. `START TRANSACTION` 후 실행하고 `ROLLBACK` 해도 된다.

</details>
