---
marp: true
theme: dark-plus-code
paginate: true
---

# 3단계. DDL

CREATE · ALTER · DROP · TRUNCATE / 제약조건 · 인덱스 · 뷰

- 테이블 정의문을 제약조건까지 포함해 쓸 수 있다
- 참조 무결성 옵션(CASCADE, SET NULL, RESTRICT)의 동작을 안다
- 뷰와 인덱스의 정의문과 특징을 안다

> 실습지: `labs/lab03_DDL.md`

---

# DDL 의 대상과 명령

| 대상 | 생성 | 변경 | 삭제 |
| --- | --- | --- | --- |
| 스키마 | `CREATE SCHEMA` | | `DROP SCHEMA` |
| 도메인 | `CREATE DOMAIN` | `ALTER DOMAIN` | `DROP DOMAIN` |
| 테이블 | `CREATE TABLE` | `ALTER TABLE` | `DROP TABLE` |
| 뷰 | `CREATE VIEW` | (불가) | `DROP VIEW` |
| 인덱스 | `CREATE INDEX` | `ALTER INDEX` | `DROP INDEX` |

- DDL 은 실행 즉시 반영된다 (자동 COMMIT). ROLLBACK 으로 되돌릴 수 없다
- 도메인: 속성이 가질 수 있는 값의 범위를 정의한 사용자 정의 타입

---

# CREATE TABLE

```sql
CREATE TABLE 학생 (
    학번     INT         NOT NULL,
    이름     VARCHAR(10) NOT NULL,
    학년     INT         NOT NULL DEFAULT 1,
    학과코드 CHAR(3),
    주소     VARCHAR(20),
    CONSTRAINT pk_학생 PRIMARY KEY (학번),
    CONSTRAINT ck_학생_학년 CHECK (학년 BETWEEN 1 AND 4),
    CONSTRAINT fk_학생_학과 FOREIGN KEY (학과코드)
        REFERENCES 학과 (학과코드) ON DELETE SET NULL ON UPDATE CASCADE
);
```

- 실습 스키마의 실제 정의문이다. `SHOW CREATE TABLE 학생\G` 로 확인할 수 있다
- `CONSTRAINT 이름` 은 생략할 수 있다. 이름을 붙이면 나중에 그 이름으로 삭제한다

---

# 제약조건

| 제약조건 | 의미 | NULL | 테이블당 |
| --- | --- | --- | --- |
| `PRIMARY KEY` | 기본키. 유일 + NOT NULL | 불가 | 1개 |
| `UNIQUE` | 중복 불가 | 허용 | 여러 개 |
| `NOT NULL` | NULL 불가 | 불가 | 여러 개 |
| `FOREIGN KEY` | 다른 테이블의 키를 참조 | 허용 | 여러 개 |
| `CHECK` | 조건을 만족하는 값만 | 허용 | 여러 개 |
| `DEFAULT` | 값을 주지 않았을 때의 기본값 | - | - |

- `PRIMARY KEY` = `UNIQUE` + `NOT NULL`
- CHECK 조건의 결과가 UNKNOWN(NULL)이면 **위반이 아니다**. NULL은 통과한다

---

# 제약조건 위반 오류

```sql
INSERT INTO 학생 (학번, 이름) VALUES (1001, '중복');
-- ERROR 1062: Duplicate entry '1001' for key '학생.PRIMARY'        (개체 무결성)

INSERT INTO 학생 (학번, 이름, 학과코드) VALUES (2000, '참조', 'D99');
-- ERROR 1452: Cannot add or update a child row: a foreign key
--             constraint fails                                      (참조 무결성)

INSERT INTO 학생 (학번, 이름, 학년) VALUES (2000, '학년', 5);
-- ERROR 3819: Check constraint 'ck_학생_학년' is violated.          (도메인 무결성)
```

- 어떤 무결성을 위반했는지 용어로 답하는 문제가 나온다 (1단계 참고)

---

# 참조 무결성 옵션

부모 테이블의 행을 삭제·수정할 때 자식 테이블을 어떻게 처리할지 정한다.

```sql
FOREIGN KEY (컬럼) REFERENCES 부모 (컬럼)
    ON DELETE [CASCADE | SET NULL | SET DEFAULT | RESTRICT | NO ACTION]
    ON UPDATE [CASCADE | SET NULL | SET DEFAULT | RESTRICT | NO ACTION]
```

| 옵션 | 동작 |
| --- | --- |
| `CASCADE` | 자식 행도 함께 삭제·수정 |
| `SET NULL` | 자식의 외래키를 NULL로 |
| `SET DEFAULT` | 자식의 외래키를 기본값으로 |
| `RESTRICT` | 자식이 있으면 거부 |
| `NO ACTION` | 아무 조치도 하지 않음 (결과적으로 거부, 기본값) |

---

# 참조 옵션 — 실습 스키마에서

| 외래키 | 옵션 | 부모 행을 지우면 |
| --- | --- | --- |
| 수강.학번 → 학생 | `ON DELETE CASCADE` | 수강 행도 삭제 |
| 학생.학과코드 → 학과 | `ON DELETE SET NULL` | 학생의 학과코드가 NULL |
| 수강.과목코드 → 과목 | `ON DELETE RESTRICT` | 거부 |
| 사원.부서번호 → 부서 | (지정 안 함) | 거부 |

```sql
DELETE FROM 학생 WHERE 학번 = 1001;      -- 수강 2행도 함께 삭제
DELETE FROM 학과 WHERE 학과코드 = 'D03';  -- 학생 3명의 학과코드가 NULL
DELETE FROM 과목 WHERE 과목코드 = 'C101'; -- ERROR 1451: Cannot delete or update a parent row
DELETE FROM 부서 WHERE 부서번호 = 50;     -- 성공 (참조하는 사원이 없음)
```

---

# ALTER TABLE

```sql
ALTER TABLE 도서 ADD 저자 VARCHAR(20);                    -- 컬럼 추가
ALTER TABLE 도서 MODIFY 제목 VARCHAR(100) NOT NULL;       -- 타입·제약 변경 (MySQL, Oracle)
ALTER TABLE 도서 DROP COLUMN 발행일;                      -- 컬럼 삭제
ALTER TABLE 도서 ADD CONSTRAINT uq_도서_제목 UNIQUE (제목);
ALTER TABLE 도서 DROP CONSTRAINT uq_도서_제목;
```

| 작업 | 표준·시험 | MySQL |
| --- | --- | --- |
| 추가 | `ADD` | `ADD` |
| 변경 | `ALTER` (Oracle 은 `MODIFY`) | `MODIFY`, `CHANGE` |
| 삭제 | `DROP` | `DROP` |

- 기존 데이터가 새 제약을 위반하면 제약 추가가 거부된다

---

# DROP · TRUNCATE

```sql
DROP TABLE 테이블 [CASCADE | RESTRICT];
TRUNCATE TABLE 테이블;
```

| 옵션 | 의미 |
| --- | --- |
| `CASCADE` | 이 테이블을 참조하는 다른 개체도 함께 제거 |
| `RESTRICT` | 참조하는 개체가 있으면 제거 거부 |

MySQL 은 `CASCADE`, `RESTRICT` 를 **문법만 받아들이고 무시**한다.

```sql
DROP TABLE 부모 CASCADE;
-- ERROR 3730: Cannot drop table '부모' referenced by a foreign key constraint
```

- MySQL 에서는 자식 테이블을 먼저 지워야 한다. 시험 답안은 표준대로 `CASCADE` 를 쓴다

---

# 인덱스

검색 속도를 높이기 위한 `<키 값, 포인터>` 쌍의 자료 구조.

```sql
CREATE [UNIQUE] INDEX 인덱스명 ON 테이블 (컬럼 [ASC | DESC], ...);
DROP INDEX 인덱스명;              -- MySQL: DROP INDEX 인덱스명 ON 테이블;
```

```sql
CREATE INDEX idx_사원_이름 ON 사원 (이름);
EXPLAIN SELECT * FROM 사원 WHERE 이름 = '정코딩';   -- type: ref, key: idx_사원_이름
EXPLAIN SELECT * FROM 사원 WHERE 급여 = 5500;       -- type: ALL (전체 검색)
```

- 기본키와 UNIQUE 제약에는 인덱스가 자동으로 만들어진다
- 조회는 빨라지지만 INSERT·UPDATE·DELETE 는 인덱스 갱신 때문에 느려진다
- 인덱스의 종류와 선정 기준은 10단계에서 다룬다

---

# 뷰

하나 이상의 테이블에서 유도된 **가상 테이블**. 데이터를 저장하지 않고 정의만 저장한다.

```sql
CREATE VIEW 뷰명 [(컬럼, ...)] AS SELECT문 [WITH CHECK OPTION];
DROP VIEW 뷰명 [CASCADE | RESTRICT];
```

```sql
CREATE VIEW v_서울사원 AS
SELECT e.사번, e.이름, e.급여, d.부서명
FROM 사원 e JOIN 부서 d ON e.부서번호 = d.부서번호
WHERE d.지역 = '서울';

SELECT * FROM v_서울사원 WHERE 급여 >= 7000;   -- 김대표, 이기획, 박개발
```

- 뷰를 조회하면 뷰 정의의 SELECT 가 실행된다
- 뷰 위에 또 다른 뷰를 정의할 수 있다

---

# 뷰의 특징

| 장점 | 단점 |
| --- | --- |
| 논리적 데이터 독립성 제공 | 독립적인 인덱스를 가질 수 없다 |
| 사용자의 데이터 관리 단순화 | 정의를 변경할 수 없다 (삭제 후 재생성) |
| 필요한 데이터만 보여 주어 보안에 유리 | 삽입·삭제·갱신에 제약이 있다 |

- 집계 함수, GROUP BY, DISTINCT, 조인 등이 들어간 뷰는 대개 갱신할 수 없다

```sql
UPDATE v_부서통계 SET 인원 = 0 WHERE 부서번호 = 10;
-- ERROR 1288: The target table v_부서통계 of the UPDATE is not updatable
```

- 기본 테이블을 삭제하면 그 위에 정의된 뷰도 쓸 수 없게 된다
- MySQL 은 `ALTER VIEW`, `CREATE OR REPLACE VIEW` 를 지원한다. 이론 문제에서는 "변경 불가" 로 답한다

---

# WITH CHECK OPTION

뷰의 조건을 벗어나는 삽입·수정을 막는다.

```sql
CREATE VIEW v_고학년 AS
SELECT 학번, 이름, 학년 FROM 학생 WHERE 학년 >= 3
WITH CHECK OPTION;

UPDATE v_고학년 SET 학년 = 2 WHERE 학번 = 1003;
-- ERROR 1369: CHECK OPTION failed 'study.v_고학년'

INSERT INTO v_고학년 VALUES (3000, '뷰삽입', 1);
-- ERROR 1369: CHECK OPTION failed 'study.v_고학년'
```

- 옵션이 없으면 수정이 성공하고, 수정된 행은 뷰에서 사라진다

---

# 표준 SQL 과 MySQL 차이

| 항목 | 표준·시험 | MySQL |
| --- | --- | --- |
| 컬럼 변경 | `ALTER TABLE ~ ALTER` / `MODIFY` | `MODIFY`, `CHANGE` |
| `DROP TABLE ~ CASCADE` | 참조 개체까지 제거 | 무시됨 |
| `CREATE DOMAIN` | 지원 | 미지원 (문법 오류) |
| `DROP INDEX` | `DROP INDEX 인덱스명` | `ON 테이블` 필요 |
| 뷰 변경 | 불가 | `ALTER VIEW` 가능 |
| `SET DEFAULT` 참조 옵션 | 지원 | InnoDB 미지원 |
| `CHECK` | 지원 | 8.0.16 이상에서 실제로 검사 |

---

# 정리 — 답안 형식

```sql
CREATE TABLE 테이블 (컬럼 타입 [제약], ..., PRIMARY KEY (컬럼),
    FOREIGN KEY (컬럼) REFERENCES 테이블 (컬럼) ON DELETE CASCADE);
ALTER TABLE 테이블 ADD 컬럼 타입;
ALTER TABLE 테이블 DROP COLUMN 컬럼;
DROP TABLE 테이블 CASCADE;
CREATE [UNIQUE] INDEX 인덱스 ON 테이블 (컬럼);
CREATE VIEW 뷰 AS SELECT ... WITH CHECK OPTION;
```

1. `PRIMARY KEY`, `FOREIGN KEY ~ REFERENCES`, `ON DELETE CASCADE` 철자를 정확히 쓴다
2. `CHECK` 는 NULL을 통과시킨다
3. `CASCADE` 는 연쇄, `RESTRICT` 는 거부
4. 뷰는 가상 테이블이고 `ALTER` 로 변경할 수 없다
5. `DELETE` 는 DML, `TRUNCATE`·`DROP` 은 DDL
