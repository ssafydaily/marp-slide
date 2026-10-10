---
marp: true
theme: dark-plus-code
paginate: true
---

# 10단계. 절차형 SQL 과 물리 설계, 종합

프로시저 · 사용자 정의 함수 · 트리거 / 인덱스 · 파티션 · 분산 DB

- 절차형 SQL 세 가지의 차이를 안다
- 물리 설계 관련 용어를 정리한다
- 전 범위를 모의 문제로 점검한다

> 실습지: `labs/lab10_모의문제.md`

---

# 절차형 SQL

SQL 에 변수, 조건문, 반복문을 더해 연속적인 작업을 처리할 수 있게 한 것.

| 종류 | 설명 | 호출 | 반환 값 |
| --- | --- | --- | --- |
| 프로시저 (Procedure) | 일련의 SQL 작업을 하나로 묶어 저장한 것 | `CALL`, `EXECUTE` 로 직접 호출 | 없음 (OUT 매개변수로 전달 가능) |
| 사용자 정의 함수 (Function) | 처리 결과를 **단일 값**으로 반환 | SQL 문 안에서 호출 | **있음** (`RETURN`) |
| 트리거 (Trigger) | 이벤트가 발생하면 **자동으로** 실행 | 호출하지 않음 | 없음 |

- 블록 구조: `DECLARE`(선언부) – `BEGIN`(실행부) – `EXCEPTION`(예외부) – `END`
- DBMS 마다 문법이 다르다. Oracle 은 PL/SQL, MySQL 은 저장 프로그램 문법

---

# 프로시저

```sql
DELIMITER //
CREATE PROCEDURE p_급여인상 (IN p_부서 INT, IN p_율 DECIMAL(4,2), OUT p_건수 INT)
BEGIN
    UPDATE 사원 SET 급여 = 급여 * (1 + p_율) WHERE 부서번호 = p_부서;
    SET p_건수 = ROW_COUNT();
END //
DELIMITER ;

CALL p_급여인상(40, 0.10, @cnt);
SELECT @cnt;        -- 1
```

| 매개변수 모드 | 의미 |
| --- | --- |
| `IN` | 호출하는 쪽에서 프로시저로 값을 전달 |
| `OUT` | 프로시저에서 호출한 쪽으로 값을 반환 |
| `INOUT` | 양방향 |

---

# 사용자 정의 함수

```sql
DELIMITER //
CREATE FUNCTION f_등급 (p_점수 INT) RETURNS CHAR(1) DETERMINISTIC
BEGIN
    DECLARE v_등급 CHAR(1);
    IF p_점수 IS NULL THEN SET v_등급 = '-';
    ELSEIF p_점수 >= 90 THEN SET v_등급 = 'A';
    ELSEIF p_점수 >= 80 THEN SET v_등급 = 'B';
    ELSE SET v_등급 = 'F';
    END IF;
    RETURN v_등급;
END //
DELIMITER ;

SELECT 학번, 점수, f_등급(점수) FROM 수강 WHERE 과목코드 = 'C101';
-- 85 B / 92 A / NULL - / 85 B
```

- 함수는 `RETURN` 으로 값을 하나 돌려주며 SELECT, WHERE 등에서 쓸 수 있다

---

# 트리거

테이블에 삽입·수정·삭제 이벤트가 발생할 때 자동으로 실행되는 절차형 SQL.

```sql
CREATE TRIGGER t_급여변경 AFTER UPDATE ON 사원 FOR EACH ROW
BEGIN
    IF OLD.급여 <> NEW.급여 THEN
        INSERT INTO 급여이력 (사번, 이전급여, 변경급여, 변경일시)
        VALUES (OLD.사번, OLD.급여, NEW.급여, NOW());
    END IF;
END
```

| 요소 | 값 |
| --- | --- |
| 시점 | `BEFORE`, `AFTER` |
| 이벤트 | `INSERT`, `UPDATE`, `DELETE` |
| `FOR EACH ROW` | 영향받는 행마다 실행 (행 트리거) |
| `OLD` / `NEW` | 변경 전 값 / 변경 후 값 |

---

# 트리거의 특징

| 이벤트 | `OLD` | `NEW` |
| --- | --- | --- |
| INSERT | 없음 | 삽입된 값 |
| UPDATE | 수정 전 값 | 수정 후 값 |
| DELETE | 삭제된 값 | 없음 |

- 용도: 데이터 변경 이력 기록, 무결성 유지, 파생 데이터 자동 갱신
- 트리거 안에서는 **TCL(COMMIT, ROLLBACK)을 쓸 수 없다**
- 사용자가 직접 호출할 수 없고 매개변수와 반환 값이 없다
- 트리거에서 오류가 나면 트리거를 일으킨 원래 문장도 실패한다

---

# Oracle PL/SQL 과 MySQL 문법 비교

시험 지문은 Oracle 문법으로 나오는 경우가 많다.

| 항목 | Oracle PL/SQL | MySQL |
| --- | --- | --- |
| 생성 | `CREATE OR REPLACE PROCEDURE 이름 (매개변수 IN 타입)` | `CREATE PROCEDURE 이름 (IN 매개변수 타입)` |
| 본문 시작 | `IS` 또는 `AS` 뒤에 `BEGIN` | `BEGIN` |
| 대입 | `변수 := 값;` | `SET 변수 = 값;` |
| 조건문 | `IF ~ THEN ~ ELSIF ~ ELSE ~ END IF;` | `IF ~ THEN ~ ELSEIF ~ ELSE ~ END IF;` |
| 반복문 | `LOOP`, `WHILE ~ LOOP`, `FOR ~ LOOP` | `LOOP`, `WHILE ~ DO`, `REPEAT ~ UNTIL` |
| 실행 | `EXECUTE 이름(값);` `CALL 이름(값);` | `CALL 이름(값);` |
| 트리거 변수 | `:OLD.컬럼`, `:NEW.컬럼` | `OLD.컬럼`, `NEW.컬럼` |
| 삭제 | `DROP PROCEDURE 이름;` | `DROP PROCEDURE 이름;` |

---

# 인덱스의 종류

| 인덱스 | 설명 |
| --- | --- |
| 트리 기반 인덱스 | B-트리, B+ 트리 구조. 가장 일반적 |
| 비트맵 인덱스 | 컬럼 값을 0과 1의 비트로 변환해 저장. 값의 종류가 적을 때 유리 |
| 함수 기반 인덱스 | 컬럼 값 대신 함수나 수식의 결과로 만든 인덱스 |
| 비트맵 조인 인덱스 | 다수의 조인된 객체로 구성된 인덱스 |
| 도메인 인덱스 | 개발자가 필요에 따라 만든 확장형 인덱스 |

| | 클러스터드 인덱스 | 넌클러스터드 인덱스 |
| --- | --- | --- |
| 데이터 저장 순서 | 인덱스 키 순서로 **정렬되어 저장** | 정렬되지 않음 |
| 테이블당 개수 | 1개 | 여러 개 |
| 검색 속도 | 빠르다 | 상대적으로 느리다 |

---

# 인덱스 선정 기준과 실행 계획

인덱스를 만들면 좋은 컬럼

- WHERE 조건, 조인 조건, ORDER BY 에 자주 쓰이는 컬럼
- 값의 종류가 많은(분포도가 좋은) 컬럼
- 수정이 잦지 않은 컬럼

```sql
EXPLAIN SELECT * FROM 사원 WHERE 사번 = 105;   -- type: const, key: PRIMARY
EXPLAIN SELECT * FROM 사원 WHERE 급여 = 5500;  -- type: ALL (테이블 전체 검색)
```

| 옵티마이저 | 기준 |
| --- | --- |
| RBO (규칙 기반) | 미리 정해 둔 규칙의 우선순위 |
| CBO (비용 기반) | 통계 정보를 이용해 계산한 예상 비용 |

---

# 파티션

대용량 테이블을 작은 논리적 단위로 나누는 것.

| 종류 | 분할 기준 |
| --- | --- |
| 범위 분할 (Range) | 지정한 열의 값 범위 (날짜, 숫자 구간) |
| 해시 분할 (Hash) | 해시 함수를 적용한 결과 값 |
| 목록 분할 (List) | 지정한 값의 목록 (지역, 분류 코드) |
| 조합 분할 (Composite) | 범위 분할 후 해시 함수로 다시 분할 |
| 라운드 로빈 분할 | 레코드를 균일하게 순차 분배 |

- 장점: 데이터 접근 범위가 줄어 성능 향상, 파티션별 백업·복구 가능
- 단점: 테이블 간 조인 비용 증가

---

# 분산 데이터베이스

논리적으로는 하나지만 물리적으로는 네트워크로 연결된 여러 곳에 분산된 데이터베이스.

| 투명성 | 의미 |
| --- | --- |
| 위치 투명성 | 데이터의 실제 위치를 몰라도 접근할 수 있다 |
| 중복 투명성 | 데이터가 여러 곳에 중복되어 있어도 하나인 것처럼 사용한다 |
| 병행 투명성 | 여러 트랜잭션이 동시에 실행되어도 결과에 영향이 없다 |
| 장애 투명성 | 장애가 발생해도 트랜잭션을 정확하게 처리한다 |
| 분할 투명성 | 테이블이 분할되어 있어도 하나인 것처럼 사용한다 |

- CAP 이론: 일관성(Consistency), 가용성(Availability), 분할 허용성(Partition tolerance) 중 **두 가지만** 동시에 만족할 수 있다

---

# 전 범위 요약 — SQL 작성

```sql
SELECT [DISTINCT] 컬럼 FROM 테이블
 WHERE 행 조건 GROUP BY 그룹 HAVING 그룹 조건 ORDER BY 정렬 [ASC | DESC];

INSERT INTO 테이블 (컬럼) VALUES (값);
UPDATE 테이블 SET 컬럼 = 값 WHERE 조건;
DELETE FROM 테이블 WHERE 조건;

CREATE TABLE 테이블 (컬럼 타입, PRIMARY KEY (컬럼),
    FOREIGN KEY (컬럼) REFERENCES 테이블 (컬럼) ON DELETE CASCADE);
ALTER TABLE 테이블 ADD 컬럼 타입;
DROP TABLE 테이블 CASCADE;
CREATE [UNIQUE] INDEX 인덱스 ON 테이블 (컬럼);
CREATE VIEW 뷰 AS SELECT ... [WITH CHECK OPTION];

GRANT 권한 ON 테이블 TO 사용자 [WITH GRANT OPTION];
REVOKE [GRANT OPTION FOR] 권한 ON 테이블 FROM 사용자 [CASCADE];
```

---

# 전 범위 요약 — 결과 예측 체크리스트

문제를 풀 때 이 순서로 확인한다.

1. **NULL 이 있는가** — 비교는 UNKNOWN, 연산은 NULL, 집계에서는 제외
2. **`COUNT(*)` 인가 `COUNT(컬럼)` 인가**
3. **조인 종류** — INNER 면 짝 없는 행과 NULL 키가 빠진다
4. **OUTER JOIN 의 조건이 ON 에 있는가 WHERE 에 있는가**
5. **WHERE 가 먼저, HAVING 이 나중** — WHERE 에서 빠진 행은 그룹에 없다
6. **`NOT IN` 서브쿼리에 NULL 이 있는가** — 있으면 0행
7. **`UNION` 인가 `UNION ALL` 인가**
8. **AND 와 OR 의 우선순위, 괄호**
9. **`RANK` 인가 `DENSE_RANK` 인가**
10. **BETWEEN 은 경계 포함, LIKE 의 `%` 와 `_`**

---

# 전 범위 요약 — 용어

| 주제 | 키워드 |
| --- | --- |
| 스키마 | 외부, 개념, 내부 |
| 키 | 슈퍼키(유일성), 후보키(유일성 + 최소성), 기본키, 대체키, 외래키 |
| 무결성 | 개체, 참조, 도메인, 사용자 정의 |
| 이상 | 삽입, 삭제, 갱신 |
| 정규화 | 도 → 부 → 이 → 결 → 다 → 조 |
| 트랜잭션 | 원자성, 일관성, 독립성, 영속성 |
| 병행 제어 | 로킹, 2단계 로킹, 타임스탬프, 낙관적 검증, 다중 버전 |
| 회복 | 지연 갱신(REDO), 즉시 갱신(REDO·UNDO), 검사점, 그림자 페이징 |
| 관계 대수 | σ, π, ⋈, ÷ / ∪, ∩, −, × |
| 절차형 SQL | 프로시저, 사용자 정의 함수, 트리거 |
| 분산 DB 투명성 | 위치, 중복, 병행, 장애 |

---

# 마무리

- `labs/lab10_모의문제.md` 의 모의 문제 30문항으로 전 범위를 점검한다
- 틀린 문제는 해당 단계의 슬라이드 마지막 장("자주 틀리는 것")으로 돌아가 확인한다
- 결과 예측 문제는 **반드시 손으로 먼저 풀고** 실행해서 비교한다
- 시험 답안은 MySQL 전용 문법이 아니라 **표준 SQL** 로 쓴다

| MySQL 에서 실습할 때 | 시험 답안 |
| --- | --- |
| `LIMIT`, `IFNULL` | 문제에서 요구하지 않으면 쓰지 않는다 |
| LEFT `UNION` RIGHT | `FULL OUTER JOIN` |
| `MODIFY` | `ALTER TABLE ~ ALTER` 또는 문제의 DBMS 표기 |
| `'kim'@'%'` | `kim` |
| `REVOKE GRANT OPTION ON` | `REVOKE GRANT OPTION FOR 권한 ON` |
