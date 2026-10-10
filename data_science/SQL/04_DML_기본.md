---
marp: true
theme: dark-plus-code
paginate: true
---

# 4단계. DML 기본

SELECT · INSERT · UPDATE · DELETE

- 구문 순서와 실행 순서를 구분한다
- NULL이 조건과 연산에 미치는 영향을 정확히 안다
- 결과 행 수를 손으로 예측할 수 있다

> 실습지: `labs/lab04_DML.md`

---

# SQL 명령어 분류

| 분류 | 명령어 | 대상 |
| --- | --- | --- |
| DDL (정의어) | CREATE, ALTER, DROP, TRUNCATE | 구조 |
| DML (조작어) | SELECT, INSERT, UPDATE, DELETE | 데이터 |
| DCL (제어어) | GRANT, REVOKE | 권한 |
| TCL (트랜잭션 제어어) | COMMIT, ROLLBACK, SAVEPOINT | 트랜잭션 |

- 분류와 명령어를 짝짓는 문제는 용어 서술형으로 자주 나온다
- TCL을 DCL에 포함시켜 분류하기도 한다

---

# SELECT 구문 순서와 실행 순서

```sql
SELECT   [DISTINCT] 컬럼, ...     -- 5
FROM     테이블                   -- 1
WHERE    행 조건                  -- 2
GROUP BY 그룹 기준                -- 3
HAVING   그룹 조건                -- 4
ORDER BY 정렬 기준 [ASC | DESC]   -- 6
```

- 작성 순서: SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY
- 실행 순서: **FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY**
- 그래서 SELECT에서 붙인 별칭은 WHERE에서 쓸 수 없고 ORDER BY에서는 쓸 수 있다

```sql
SELECT 이름, 급여 * 12 AS 연봉 FROM 사원 WHERE 연봉 > 80000;
-- ERROR 1054: Unknown column '연봉' in 'where clause'
```

---

# WHERE — 비교와 논리 연산자

```sql
SELECT 이름, 학년 FROM 학생
WHERE 학년 >= 3
ORDER BY 학년 DESC, 이름;
```

| 이름 | 학년 |
| --- | --- |
| 김철수 | 4 |
| 정우성 | 4 |
| 박민수 | 3 |
| 오세훈 | 3 |

- 비교: `=`, `<>` (`!=`), `<`, `<=`, `>`, `>=`
- 논리: `NOT` → `AND` → `OR` 순으로 우선순위가 높다
- ORDER BY 기본값은 `ASC` (오름차순)

---

# 함정 — AND 가 OR 보다 먼저

```sql
SELECT 학년, 이름 FROM 학생
WHERE 학과코드 = 'D01' OR 학과코드 = 'D02' AND 학년 >= 3;   -- 5행
```

`D01 전체` + `D02 이면서 3학년 이상` 으로 해석된다.

```sql
SELECT 학년, 이름 FROM 학생
WHERE (학과코드 = 'D01' OR 학과코드 = 'D02') AND 학년 >= 3;  -- 3행
```

- 괄호가 없으면 AND 부터 묶는다
- 결과 예측 문제에서 괄호 유무를 먼저 확인한다

---

# IN · BETWEEN · LIKE

```sql
WHERE 직급 IN ('사장', '부장')          -- 목록 중 하나와 일치
WHERE 급여 BETWEEN 4200 AND 5500        -- 4200 이상 5500 이하 (양 끝 포함)
WHERE 이름 LIKE '김%'                   -- 김으로 시작
WHERE 이름 LIKE '_영%'                  -- 두 번째 글자가 영
```

| 와일드카드 | 의미 |
| --- | --- |
| `%` | 0개 이상의 임의 문자 |
| `_` | 정확히 1개의 임의 문자 |

- `BETWEEN a AND b` 는 `>= a AND <= b` 와 같다. **경계값을 포함**한다
- 부정형: `NOT IN`, `NOT BETWEEN`, `NOT LIKE`

---

# NULL — 비교하면 참도 거짓도 아니다

```sql
SELECT COUNT(*) FROM 학생 WHERE 주소 = NULL;    -- 0
SELECT 이름     FROM 학생 WHERE 주소 IS NULL;   -- 한소희
```

- NULL은 "값이 없음" 이다. 0이나 빈 문자열과 다르다
- NULL과의 비교 결과는 **UNKNOWN** 이고, WHERE는 TRUE인 행만 통과시킨다
- NULL 검사는 반드시 `IS NULL`, `IS NOT NULL`

| 조건 | 행 수 |
| --- | --- |
| `주소 = '서울'` | 4 |
| `주소 <> '서울'` | 5 |
| 전체 | 10 |

4 + 5 = 9. 주소가 NULL인 1명은 **어느 쪽에도 포함되지 않는다**.

---

# NULL — 연산하면 NULL

```sql
SELECT 이름, 급여, 보너스,
       급여 + 보너스            AS 합계1,
       급여 + IFNULL(보너스, 0) AS 합계2
FROM 사원 WHERE 부서번호 = 30;
```

| 이름 | 급여 | 보너스 | 합계1 | 합계2 |
| --- | --- | --- | --- | --- |
| 최영업 | 6800 | NULL | NULL | 6800 |
| 윤판매 | 5500 | 400 | 5900 | 5900 |
| 강매출 | 3200 | 0 | 3200 | 3200 |

- NULL 치환 함수: 표준 `COALESCE(a, b)`, MySQL `IFNULL(a, b)`, Oracle `NVL(a, b)`
- 보너스 0과 보너스 NULL은 다른 값이다

---

# DISTINCT 와 정렬

```sql
SELECT COUNT(이름), COUNT(DISTINCT 이름) FROM 학생;   -- 10, 9
SELECT DISTINCT 학년 FROM 학생 WHERE 학과코드 = 'D01'; -- 1, 2, 3
```

- `DISTINCT` 는 SELECT 한 컬럼 조합 전체의 중복을 제거한다

```sql
SELECT 이름, 보너스 FROM 사원 ORDER BY 보너스;
```

| DBMS | 오름차순에서 NULL 위치 |
| --- | --- |
| MySQL | 맨 앞 (가장 작은 값으로 취급) |
| Oracle | 맨 뒤 (가장 큰 값으로 취급) |

- 정렬 기준이 여러 개면 앞에서부터 차례로 적용한다

---

# CASE 와 NULL

```sql
SELECT 학번, 점수,
       CASE WHEN 점수 >= 90 THEN 'A'
            WHEN 점수 >= 80 THEN 'B'
            WHEN 점수 >= 70 THEN 'C'
            ELSE 'F' END AS 등급
FROM 수강 WHERE 과목코드 = 'C101';
```

| 학번 | 점수 | 등급 |
| --- | --- | --- |
| 1001 | 85 | B |
| 1002 | 92 | A |
| 1003 | NULL | **F** |
| 1007 | 85 | B |

- NULL은 어떤 WHEN 도 만족하지 못해 ELSE 로 떨어진다
- ELSE 가 없으면 결과는 NULL

---

# INSERT

```sql
INSERT INTO 학생 (학번, 이름, 학과코드) VALUES (1011, '홍길동', 'D01');
INSERT INTO 학생 VALUES (1012, '성춘향', 2, 'D03', '남원');
INSERT INTO 학생_백업 (학번, 이름) SELECT 학번, 이름 FROM 학생 WHERE 학년 = 1;
```

- 컬럼 목록을 생략하면 **테이블 정의 순서대로 모든 컬럼** 값을 줘야 한다
- 지정하지 않은 컬럼에는 DEFAULT 값, 없으면 NULL이 들어간다
  - 위 첫 문장의 결과: 학년 = 1 (DEFAULT), 주소 = NULL
- 서브쿼리로 넣을 때는 `VALUES` 를 쓰지 않는다

---

# UPDATE · DELETE

```sql
UPDATE 사원 SET 급여 = 급여 * 1.1 WHERE 직급 = '사원';      -- 3행 변경
UPDATE 학생 SET 학년 = 학년 + 1, 주소 = '서울' WHERE 학번 = 1006;

DELETE FROM 수강 WHERE 점수 IS NULL;                        -- 2행 삭제
```

- **WHERE 를 빼면 모든 행**이 대상이 된다
- 시험 답안 형식

```sql
UPDATE 테이블 SET 컬럼 = 값 WHERE 조건;
DELETE FROM 테이블 WHERE 조건;
INSERT INTO 테이블 (컬럼) VALUES (값);
```

- `DELETE FROM` 의 `FROM`, `INSERT INTO` 의 `INTO`, `UPDATE ~ SET` 을 빠뜨리지 않는다

---

# DELETE · TRUNCATE · DROP

| | DELETE | TRUNCATE | DROP |
| --- | --- | --- | --- |
| 분류 | DML | DDL | DDL |
| 대상 | 조건에 맞는 행 | 모든 행 | 테이블 자체 |
| WHERE | 가능 | 불가 | - |
| ROLLBACK | 가능 | 불가 | 불가 |
| 테이블 구조 | 남음 | 남음 | 사라짐 |

- TRUNCATE 는 AUTO_INCREMENT 값도 처음으로 되돌린다
- "테이블 구조는 남기고 데이터만 모두 삭제" → DELETE 또는 TRUNCATE
- "테이블을 제거" → DROP

---

# 표준 SQL 과 MySQL 차이

| 항목 | 표준·시험 | MySQL |
| --- | --- | --- |
| 상위 N행 | `FETCH FIRST n ROWS ONLY` | `LIMIT n` |
| NULL 치환 | `COALESCE` | `IFNULL`, `COALESCE` |
| 문자열 연결 | `\|\|` | `CONCAT()` (`\|\|` 는 OR) |
| 문자열 비교 | 대소문자 구분 | 기본 정렬 규칙에서는 구분 안 함 |
| 오름차순 NULL | DBMS마다 다름 | 맨 앞 |
| 문자열 따옴표 | 작은따옴표 | 작은따옴표, 큰따옴표 모두 |

- 시험 답안에서 문자열은 **작은따옴표**로 쓴다

---

# 정리 — 자주 틀리는 것

1. `= NULL` 은 항상 0행. `IS NULL` 을 쓴다
2. `<>` 조건은 NULL 행을 포함하지 않는다
3. NULL이 들어간 산술 연산의 결과는 NULL
4. BETWEEN 은 경계값을 포함한다
5. AND 가 OR 보다 먼저 묶인다
6. SELECT 별칭은 WHERE 에서 쓸 수 없다
7. `DELETE FROM`, `INSERT INTO`, `UPDATE ~ SET` 키워드를 정확히 쓴다
8. WHERE 없는 UPDATE·DELETE 는 전체 행에 적용된다
