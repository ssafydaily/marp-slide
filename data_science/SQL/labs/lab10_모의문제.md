# Lab 10. 절차형 SQL 실습과 종합 모의 문제

슬라이드: `10_절차형SQL_종합.md`

## 1. 절차형 SQL 따라 하기

`mysql` 클라이언트에서는 본문 안의 `;` 때문에 문장이 중간에 끊기지 않도록 `DELIMITER` 로 구분자를 잠시 바꾼다. GUI 도구에서는 도구의 "스크립트 실행" 기능을 쓰거나 `DELIMITER` 줄을 그대로 포함해 실행한다.

### 1-1. 프로시저

```sql
DELIMITER //
CREATE PROCEDURE p_급여인상 (IN p_부서 INT, IN p_율 DECIMAL(4,2), OUT p_건수 INT)
BEGIN
    UPDATE 사원 SET 급여 = 급여 * (1 + p_율) WHERE 부서번호 = p_부서;
    SET p_건수 = ROW_COUNT();
END //
DELIMITER ;
```

### 1-2. 반복문이 있는 프로시저

```sql
DELIMITER //
CREATE PROCEDURE p_합계 (IN p_n INT, OUT p_sum INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    SET p_sum = 0;
    WHILE i <= p_n DO
        SET p_sum = p_sum + i;
        SET i = i + 1;
    END WHILE;
END //
DELIMITER ;

CALL p_합계(10, @s);
SELECT @s;          -- 55
```

### 1-3. 사용자 정의 함수

```sql
DELIMITER //
CREATE FUNCTION f_등급 (p_점수 INT) RETURNS CHAR(1) DETERMINISTIC
BEGIN
    DECLARE v_등급 CHAR(1);
    IF p_점수 IS NULL THEN SET v_등급 = '-';
    ELSEIF p_점수 >= 90 THEN SET v_등급 = 'A';
    ELSEIF p_점수 >= 80 THEN SET v_등급 = 'B';
    ELSEIF p_점수 >= 70 THEN SET v_등급 = 'C';
    ELSE SET v_등급 = 'F';
    END IF;
    RETURN v_등급;
END //
DELIMITER ;

SELECT 학번, 점수, f_등급(점수) AS 등급 FROM 수강 WHERE 과목코드 = 'C101';
```

| 학번 | 점수 | 등급 |
| --- | --- | --- |
| 1001 | 85 | B |
| 1002 | 92 | A |
| 1003 | NULL | - |
| 1007 | 85 | B |

### 1-4. 트리거

급여가 바뀔 때마다 이력을 남긴다.

```sql
CREATE TABLE 급여이력 (
    이력번호 INT AUTO_INCREMENT PRIMARY KEY,
    사번 INT, 이전급여 INT, 변경급여 INT, 변경일시 DATETIME
);

DELIMITER //
CREATE TRIGGER t_급여변경 AFTER UPDATE ON 사원 FOR EACH ROW
BEGIN
    IF OLD.급여 <> NEW.급여 THEN
        INSERT INTO 급여이력 (사번, 이전급여, 변경급여, 변경일시)
        VALUES (OLD.사번, OLD.급여, NEW.급여, NOW());
    END IF;
END //
DELIMITER ;
```

프로시저를 호출하면 그 안의 UPDATE 가 트리거를 일으킨다.

```sql
START TRANSACTION;

CALL p_급여인상(40, 0.10, @cnt);
SELECT @cnt;                                      -- 1
SELECT 사번, 이전급여, 변경급여 FROM 급여이력;
```

| 사번 | 이전급여 | 변경급여 |
| --- | --- | --- |
| 110 | 5200 | 5720 |

```sql
ROLLBACK;
SELECT COUNT(*) FROM 급여이력;                    -- 0
```

트리거가 넣은 이력 행도 같은 트랜잭션에 속하므로 함께 ROLLBACK 된다.

### 1-5. 확인과 정리

```sql
SHOW TRIGGERS\G
SELECT ROUTINE_NAME, ROUTINE_TYPE FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA = 'study';

DROP TRIGGER t_급여변경;
DROP PROCEDURE p_급여인상;
DROP PROCEDURE p_합계;
DROP FUNCTION f_등급;
DROP TABLE 급여이력;
```

## 2. 종합 모의 문제

기출 유형을 실습 스키마에 맞춰 재구성한 30문항이다. 결과 예측 문제는 손으로 먼저 풀고 실행해서 확인한다. 데이터는 `lab00` 의 표를 참고한다.

### A. 결과 예측 (1~12)

**1.** 다음 쿼리의 결과를 쓰시오.

```sql
SELECT COUNT(*), COUNT(상사사번), COUNT(DISTINCT 상사사번) FROM 사원;
```

**2.** 다음 쿼리의 결과 값은?

```sql
SELECT COUNT(*) FROM 학생 WHERE 주소 <> '서울';
```

**3.** 다음 쿼리의 결과를 쓰시오.

```sql
SELECT 부서번호 FROM 사원 GROUP BY 부서번호 HAVING COUNT(*) >= 3;
```

**4.** 다음 쿼리의 결과를 쓰시오.

```sql
SELECT 학과코드, AVG(학년) FROM 학생 GROUP BY 학과코드 HAVING AVG(학년) >= 2.5;
```

**5.** 다음 두 쿼리의 결과 행 수를 각각 쓰시오.

```sql
SELECT 학년 FROM 학생 WHERE 학과코드 = 'D01' UNION ALL SELECT 학년 FROM 학생 WHERE 학과코드 = 'D02';
SELECT 학년 FROM 학생 WHERE 학과코드 = 'D01' UNION     SELECT 학년 FROM 학생 WHERE 학과코드 = 'D02';
```

**6.** 다음 쿼리의 결과 행 수는?

```sql
SELECT * FROM 사원 e RIGHT OUTER JOIN 부서 d ON e.부서번호 = d.부서번호;
```

**7.** 다음 쿼리의 결과에서 `한서버` 의 `r` 값은?

```sql
SELECT 이름, 급여, RANK() OVER (ORDER BY 급여 DESC) AS r
FROM 사원 WHERE 부서번호 = 20 OR 부서번호 = 30;
```

**8.** 다음 쿼리의 결과 값은?

```sql
SELECT COUNT(*) FROM 부서 WHERE 부서번호 NOT IN (SELECT 부서번호 FROM 사원);
```

**9.** 다음 쿼리의 결과 행 수와 마지막 행의 합계 값을 쓰시오.

```sql
SELECT 직급, SUM(급여) FROM 사원 WHERE 부서번호 = 20 GROUP BY 직급 WITH ROLLUP;
```

**10.** 다음 쿼리의 결과에서 '수학과' 의 학생수는?

```sql
SELECT d.학과명, COUNT(s.학번) AS 학생수
FROM 학과 d LEFT JOIN 학생 s ON d.학과코드 = s.학과코드
GROUP BY d.학과코드, d.학과명;
```

**11.** 다음 쿼리의 결과에서 '강하늘' 행의 `c`, `a` 값은?

```sql
SELECT s.이름, COUNT(e.과목코드) AS c, AVG(e.점수) AS a
FROM 학생 s LEFT JOIN 수강 e ON s.학번 = e.학번
WHERE s.학과코드 = 'D03'
GROUP BY s.학번, s.이름;
```

**12.** 다음 쿼리의 결과를 쓰시오.

```sql
SELECT 이름 FROM 사원
WHERE 급여 >= (SELECT AVG(급여) FROM 사원 WHERE 직급 = '과장')
  AND 직급 <> '과장';
```

<details>
<summary>A 정답과 해설</summary>

1. 12, 11, 6. 상사사번이 NULL 인 김대표가 빠져 11, 상사로 등장하는 사번은 101·102·103·104·105·108 의 6개.
2. 5. 서울 4명과 주소 NULL 1명을 뺀 나머지.
3. 10, 20, 30. 40번과 NULL 그룹은 1명씩이다.
4. D02, 3.0000. D02 는 (3 + 2 + 4) ÷ 3 = 3. D01 과 D03, NULL 그룹은 모두 평균 2.
5. 6행, 4행. D01 의 학년은 1·2·3, D02 는 3·2·4. 중복을 제거하면 1·2·3·4.
6. 12행. 부서가 있는 사원 11명 + 사원이 없는 연구소 1행.
7. 5. 7200(1), 6800(2), 5500·5500(공동 3), 그다음이 4200 이므로 4위를 건너뛰고 5.
8. 0. 서브쿼리 결과에 NULL(신수습의 부서번호)이 있어 `NOT IN` 이 항상 UNKNOWN 이다. 연구소가 나올 것 같지만 나오지 않는다.
9. 5행, 19900. 직급 4개(과장·대리·부장·사원) + 총계 1행.
10. 0. `COUNT(s.학번)` 은 NULL 을 세지 않는다. `COUNT(*)` 였다면 1.
11. c = 0, a = NULL. 값이 하나도 없을 때 COUNT 는 0, AVG 는 NULL.
12. 김대표, 이기획, 박개발, 최영업. 과장 평균은 (5500 + 5500 + 5200) ÷ 3 = 5400.

</details>

### B. SQL 작성 (13~21)

표준 SQL 로 작성한다.

**13.** 사원 테이블에서 보너스가 300 이상인 사원의 이름을 보너스가 많은 순으로 조회하시오.

**14.** 학과명과 학과별 학생 수를 조회하시오. 학생이 없는 학과도 0으로 표시한다.

**15.** 부서명이 '개발부' 인 부서에 속한 사원의 급여를 5% 인상하시오.

**16.** 수강 테이블에서 학과코드가 'D02' 인 학생의 수강 내역을 모두 삭제하시오.

**17.** 다음 조건의 `프로젝트` 테이블을 생성하시오.

- `프로젝트번호`: 정수, 기본키
- `프로젝트명`: 가변 문자 30, NULL 불가, 중복 불가
- `예산`: 정수, 0 이상
- `담당사번`: 정수, `사원` 테이블의 `사번` 참조, 참조되는 사원이 삭제되면 함께 삭제

**18.** 부서 테이블에 가변 문자 15의 `전화번호` 컬럼을 추가하시오.

**19.** 급여가 5000 이상인 사원의 사번, 이름, 급여로 구성된 뷰 `v_고액` 을 생성하시오. 뷰를 통한 수정 시 조건을 벗어나지 않도록 한다.

**20.** (1) 사용자 `choi` 에게 `부서` 테이블의 SELECT 권한을 부여하되 다른 사용자에게 다시 부여할 수 있게 하시오. (2) 사용자 `choi` 로부터 `부서` 테이블의 SELECT 권한을 회수하되 `choi` 가 부여한 권한도 연쇄적으로 회수하시오.

**21.** 학생 테이블의 `이름` 컬럼에 `idx_학생_이름` 인덱스를 생성하시오.

<details>
<summary>B 정답과 해설</summary>

```sql
-- 13 (박개발, 이기획, 윤판매, 정코딩)
SELECT 이름 FROM 사원 WHERE 보너스 >= 300 ORDER BY 보너스 DESC;

-- 14 (컴퓨터공학과 3, 전자공학과 3, 경영학과 3, 수학과 0)
SELECT d.학과명, COUNT(s.학번) AS 학생수
FROM 학과 d LEFT OUTER JOIN 학생 s ON d.학과코드 = s.학과코드
GROUP BY d.학과코드, d.학과명;

-- 15 (4행)
UPDATE 사원 SET 급여 = 급여 * 1.05
WHERE 부서번호 = (SELECT 부서번호 FROM 부서 WHERE 부서명 = '개발부');

-- 16 (5행)
DELETE FROM 수강
WHERE 학번 IN (SELECT 학번 FROM 학생 WHERE 학과코드 = 'D02');

-- 17
CREATE TABLE 프로젝트 (
    프로젝트번호 INT NOT NULL,
    프로젝트명   VARCHAR(30) NOT NULL UNIQUE,
    예산         INT CHECK (예산 >= 0),
    담당사번     INT,
    PRIMARY KEY (프로젝트번호),
    FOREIGN KEY (담당사번) REFERENCES 사원 (사번) ON DELETE CASCADE
);

-- 18
ALTER TABLE 부서 ADD 전화번호 VARCHAR(15);

-- 19
CREATE VIEW v_고액 AS
SELECT 사번, 이름, 급여 FROM 사원 WHERE 급여 >= 5000
WITH CHECK OPTION;

-- 20
GRANT SELECT ON 부서 TO choi WITH GRANT OPTION;
REVOKE SELECT ON 부서 FROM choi CASCADE;

-- 21
CREATE INDEX idx_학생_이름 ON 학생 (이름);
```

- 13번에서 보너스가 NULL 인 사원은 `보너스 >= 300` 이 UNKNOWN 이라 자동으로 빠진다.
- 14번에서 `COUNT(*)` 를 쓰면 수학과가 1로 나온다.
- 20번의 `choi`, `CASCADE` 는 MySQL 에서 그대로 실행되지 않는다(8단계 슬라이드 참고).
- 15~19, 21번을 실행했다면 `lab00` 의 초기화 명령으로 되돌린다.

</details>

### C. 이론 (22~30)

**22.** 다음 SQL 의 결과 릴레이션의 차수와 카디널리티를 쓰시오.

```sql
SELECT 사번, 이름, 직급 FROM 사원 WHERE 부서번호 = 30;
```

**23.** 다음 설명의 빈칸을 채우시오.

- ( ① ) 는 릴레이션의 튜플을 유일하게 식별할 수 있는 속성 집합으로 유일성은 만족하지만 최소성은 만족하지 못할 수 있다.
- ( ② ) 는 유일성과 최소성을 모두 만족한다.
- ( ② ) 중 기본키로 선택되지 않은 것을 ( ③ ) 라고 한다.

**24.** "외래키 값은 NULL 이거나 참조 릴레이션의 기본키 값과 동일해야 한다" 는 규칙의 이름을 쓰시오.

**25.** 릴레이션 R(A, B, C, D) 의 기본키는 {A, B} 이고 함수적 종속은 다음과 같다. R 은 몇 정규형이며, 다음 정규형이 되려면 무엇을 제거해야 하는가?

```
{A, B} → C
A → D
```

**26.** 정규화되지 않은 릴레이션에서 데이터의 중복 때문에 삽입, 삭제, 갱신 시 발생하는 예기치 못한 문제를 무엇이라 하는가? 세 가지 종류도 쓰시오.

**27.** 트랜잭션의 특성 네 가지를 쓰고, 그중 "트랜잭션이 성공적으로 완료되면 그 결과는 시스템에 장애가 발생하더라도 영구적으로 반영된다" 에 해당하는 것을 쓰시오.

**28.** 다음 빈칸을 채우시오.

- 회복 기법 중 ( ① ) 갱신 기법은 트랜잭션이 완료되기 전에는 데이터베이스에 반영하지 않으므로 UNDO 가 필요 없다.
- 병행 제어 기법 중 ( ② ) 은 트랜잭션이 사용하는 데이터에 잠금을 걸어 다른 트랜잭션의 접근을 막는 기법이다.
- 격리 수준 중 ( ③ ) 는 Dirty Read, Non-Repeatable Read, Phantom Read 가 모두 발생하지 않는다.

**29.** 다음 관계 대수 연산자의 기호를 쓰고, "학생 릴레이션에서 학년이 2 인 학생의 이름" 을 구하는 관계 대수식을 쓰시오.

- Select, Project, Join, Division

**30.** 다음 빈칸을 채우시오.

- 절차형 SQL 중 ( ① ) 는 테이블에 삽입, 갱신, 삭제 이벤트가 발생할 때 자동으로 실행된다.
- ( ② ) 는 처리 결과를 단일 값으로 반환하며 SQL 문 안에서 호출할 수 있다.
- 분산 데이터베이스의 투명성 중 ( ③ ) 투명성은 데이터의 실제 위치를 알 필요 없이 논리적 명칭만으로 접근할 수 있는 성질이다.

<details>
<summary>C 정답과 해설</summary>

22. 차수 3, 카디널리티 3 (최영업, 윤판매, 강매출).
23. ① 슈퍼키, ② 후보키, ③ 대체키
24. 참조 무결성
25. 1NF. D 가 기본키의 일부인 A 에만 종속되므로 부분 함수적 종속을 제거해야 2NF 가 된다. R1(A, B, C), R2(A, D) 로 분해한다.
26. 이상(Anomaly). 삽입 이상, 삭제 이상, 갱신 이상.
27. 원자성, 일관성, 독립성(격리성), 영속성(지속성). 설명에 해당하는 것은 영속성(Durability).
28. ① 지연, ② 로킹, ③ SERIALIZABLE
29. σ, π, ⋈, ÷. `π 이름 ( σ 학년=2 (학생) )`
30. ① 트리거, ② 사용자 정의 함수, ③ 위치

</details>

## 3. 채점 후

| 틀린 영역 | 돌아갈 곳 |
| --- | --- |
| 1, 2, 13 | 4단계 (NULL, 조건) |
| 3, 4, 7, 9 | 5단계 (집계, ROLLUP, 순위) |
| 5, 6, 10, 11, 14 | 6단계 (JOIN, 집합 연산) |
| 8, 12, 15, 16 | 7단계 (서브쿼리) |
| 17, 18, 19, 21 | 3단계 (DDL) |
| 20, 27, 28 | 8단계 (DCL, 트랜잭션) |
| 22, 23, 24 | 1단계 (기초 이론) |
| 25, 26 | 2단계 (정규화) |
| 29 | 9단계 (관계 대수) |
| 30 | 10단계 (절차형 SQL, 분산 DB) |
