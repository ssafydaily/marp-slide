# Lab 03. DDL

슬라이드: `03_DDL.md`

이 실습은 연습용 테이블 `도서` 를 만들어 진행하고, 끝에서 모두 지운다. DDL 은 자동으로 COMMIT 되어 ROLLBACK 할 수 없다는 점에 주의한다.

## 1. 따라 하기

### 1-1. 테이블 생성

```sql
CREATE TABLE 도서 (
    도서번호 INT NOT NULL AUTO_INCREMENT,
    제목     VARCHAR(50) NOT NULL,
    가격     INT DEFAULT 10000,
    출판일   DATE,
    PRIMARY KEY (도서번호),
    CONSTRAINT ck_도서_가격 CHECK (가격 >= 0)
);

DESC 도서;
```

| Field | Type | Null | Key | Default | Extra |
| --- | --- | --- | --- | --- | --- |
| 도서번호 | int | NO | PRI | NULL | auto_increment |
| 제목 | varchar(50) | NO | | NULL | |
| 가격 | int | YES | | 10000 | |
| 출판일 | date | YES | | NULL | |

### 1-2. 테이블 변경

```sql
ALTER TABLE 도서 ADD 저자 VARCHAR(20);
ALTER TABLE 도서 MODIFY 제목 VARCHAR(100) NOT NULL;
ALTER TABLE 도서 CHANGE 출판일 발행일 DATE;          -- 컬럼 이름 변경 (MySQL)
ALTER TABLE 도서 DROP COLUMN 발행일;
ALTER TABLE 도서 ADD CONSTRAINT uq_도서_제목 UNIQUE (제목);

DESC 도서;
```

| Field | Type | Null | Key | Default | Extra |
| --- | --- | --- | --- | --- | --- |
| 도서번호 | int | NO | PRI | NULL | auto_increment |
| 제목 | varchar(100) | NO | UNI | NULL | |
| 가격 | int | YES | | 10000 | |
| 저자 | varchar(20) | YES | | NULL | |

### 1-3. 제약조건 위반

한 문장씩 실행하면서 오류 메시지를 확인한다.

```sql
INSERT INTO 도서 (제목) VALUES ('SQL 첫걸음');           -- 성공. 가격은 DEFAULT 10000
INSERT INTO 도서 (제목) VALUES ('SQL 첫걸음');           -- ERROR 1062: Duplicate entry (UNIQUE)
INSERT INTO 도서 (제목, 가격) VALUES ('음수', -1);       -- ERROR 3819: Check constraint 'ck_도서_가격' is violated.
INSERT INTO 도서 (가격) VALUES (500);                    -- ERROR 1364: Field '제목' doesn't have a default value (NOT NULL)
INSERT INTO 도서 (제목, 가격) VALUES ('널가격', NULL);   -- 성공. CHECK 는 NULL을 통과시킨다

SELECT * FROM 도서;
```

| 도서번호 | 제목 | 가격 | 저자 |
| --- | --- | --- | --- |
| 1 | SQL 첫걸음 | 10000 | NULL |
| 3 | 널가격 | NULL | NULL |

도서번호가 1 다음에 3이다. 실패한 INSERT 가 AUTO_INCREMENT 번호를 이미 받아 갔고, 그 번호는 재사용되지 않기 때문이다.

### 1-4. 실습 스키마의 제약조건 확인

```sql
INSERT INTO 학생 (학번, 이름) VALUES (1001, '중복');                      -- ERROR 1062 (기본키 중복)
INSERT INTO 학생 (학번, 이름, 학과코드) VALUES (2000, '참조', 'D99');     -- ERROR 1452 (외래키)
INSERT INTO 학생 (학번, 이름, 학년) VALUES (2000, '학년', 5);             -- ERROR 3819 (CHECK)
INSERT INTO 수강 VALUES (1001, 'C103', 101);                              -- ERROR 3819 (CHECK)
```

### 1-5. 참조 무결성 옵션

DML 이므로 트랜잭션 안에서 실행하고 마지막에 되돌린다.

```sql
START TRANSACTION;

-- CASCADE
DELETE FROM 학생 WHERE 학번 = 1001;
SELECT COUNT(*) FROM 수강 WHERE 학번 = 1001;          -- 0 (수강 2행이 함께 삭제됨)

-- SET NULL
DELETE FROM 학과 WHERE 학과코드 = 'D03';
SELECT 학번, 학과코드 FROM 학생 WHERE 학번 IN (1005, 1006, 1010);   -- 모두 NULL

-- ON UPDATE CASCADE
UPDATE 학과 SET 학과코드 = 'D09' WHERE 학과코드 = 'D02';
SELECT 학번, 학과코드 FROM 학생 WHERE 학번 IN (1003, 1004);         -- 모두 D09

-- RESTRICT
DELETE FROM 과목 WHERE 과목코드 = 'C101';   -- ERROR 1451
DELETE FROM 부서 WHERE 부서번호 = 10;       -- ERROR 1451
DELETE FROM 부서 WHERE 부서번호 = 50;       -- 성공 (참조하는 사원이 없음)

ROLLBACK;
```

### 1-6. 인덱스

```sql
CREATE INDEX idx_사원_이름 ON 사원 (이름);
SHOW INDEX FROM 사원;
```

`PRIMARY`, `fk_사원_부서`, `fk_사원_상사`, `idx_사원_이름` 네 개가 보인다. 기본키와 외래키에는 인덱스가 자동으로 만들어졌다.

```sql
EXPLAIN SELECT * FROM 사원 WHERE 이름 = '정코딩';
```

| type | possible_keys | key | rows |
| --- | --- | --- | --- |
| ref | idx_사원_이름 | idx_사원_이름 | 1 |

```sql
EXPLAIN SELECT * FROM 사원 WHERE 급여 = 5500;
```

| type | possible_keys | key | rows |
| --- | --- | --- | --- |
| ALL | NULL | NULL | 12 |

`type: ALL` 은 테이블 전체를 읽는다는 뜻이다.

```sql
DROP INDEX idx_사원_이름 ON 사원;
```

### 1-7. 뷰

```sql
CREATE VIEW v_서울사원 AS
SELECT e.사번, e.이름, e.급여, d.부서명
FROM 사원 e JOIN 부서 d ON e.부서번호 = d.부서번호
WHERE d.지역 = '서울';

SELECT * FROM v_서울사원 WHERE 급여 >= 7000;
```

| 사번 | 이름 | 급여 | 부서명 |
| --- | --- | --- | --- |
| 101 | 김대표 | 9000 | 기획부 |
| 102 | 이기획 | 7000 | 기획부 |
| 103 | 박개발 | 7200 | 개발부 |

```sql
CREATE VIEW v_고학년 AS
SELECT 학번, 이름, 학년 FROM 학생 WHERE 학년 >= 3
WITH CHECK OPTION;

UPDATE v_고학년 SET 학년 = 2 WHERE 학번 = 1003;     -- ERROR 1369: CHECK OPTION failed
INSERT INTO v_고학년 VALUES (3000, '뷰삽입', 1);    -- ERROR 1369: CHECK OPTION failed

CREATE VIEW v_부서통계 AS
SELECT 부서번호, COUNT(*) AS 인원, AVG(급여) AS 평균 FROM 사원 GROUP BY 부서번호;

UPDATE v_부서통계 SET 인원 = 0 WHERE 부서번호 = 10;  -- ERROR 1288: not updatable
```

### 1-8. DELETE 와 TRUNCATE

```sql
DELETE FROM 도서;
INSERT INTO 도서 (제목) VALUES ('새책');
SELECT 도서번호 FROM 도서;     -- 4 (번호가 이어진다)

TRUNCATE TABLE 도서;
INSERT INTO 도서 (제목) VALUES ('새책');
SELECT 도서번호 FROM 도서;     -- 1 (번호가 초기화된다)
```

### 1-9. DROP 과 CASCADE

```sql
CREATE TABLE 부모 (id INT PRIMARY KEY);
CREATE TABLE 자식 (id INT PRIMARY KEY, pid INT, FOREIGN KEY (pid) REFERENCES 부모 (id));

DROP TABLE 부모 CASCADE;   -- ERROR 3730: MySQL 은 CASCADE 를 무시한다
DROP TABLE 자식;
DROP TABLE 부모;
```

### 1-10. 정리

```sql
DROP VIEW v_서울사원, v_고학년, v_부서통계;
DROP TABLE 도서;
SHOW TABLES;   -- 과목, 부서, 사원, 수강, 학과, 학생
```

## 2. 쿼리 작성

시험 답안 형식(표준 SQL)으로 작성한다.

**Q1.** 다음 조건의 `회원` 테이블을 생성하시오.

- `회원번호`: 정수, 기본키
- `이름`: 가변 문자 20, NULL 불가
- `등급`: 고정 문자 1, 기본값 'C', 'A'·'B'·'C' 중 하나만 허용
- `추천인`: 정수, `회원` 테이블의 `회원번호` 를 참조하고, 참조되는 회원이 삭제되면 NULL로 변경

**Q2.** `학생` 테이블에 가변 문자 15의 `전화번호` 컬럼을 추가하시오.

**Q3.** `학생` 테이블에서 `주소` 컬럼을 삭제하시오.

**Q4.** `사원` 테이블의 `부서번호` 컬럼에 `idx_부서` 라는 이름의 인덱스를 생성하시오.

**Q5.** `학생` 테이블에서 학과코드가 'D01' 인 학생의 학번과 이름으로 구성된 뷰 `v_컴공` 을 생성하시오. 뷰를 통해 조건에 맞지 않는 데이터가 삽입·수정되지 않도록 한다.

**Q6.** `학과` 테이블을 제거하되, 이 테이블을 참조하는 다른 개체도 함께 제거하시오.

**Q7.** `수강` 테이블의 모든 행을 삭제하되 테이블 구조는 남기시오. DDL 을 사용한다.

<details>
<summary>정답과 해설</summary>

```sql
-- Q1
CREATE TABLE 회원 (
    회원번호 INT NOT NULL,
    이름     VARCHAR(20) NOT NULL,
    등급     CHAR(1) DEFAULT 'C',
    추천인   INT,
    PRIMARY KEY (회원번호),
    CHECK (등급 IN ('A', 'B', 'C')),
    FOREIGN KEY (추천인) REFERENCES 회원 (회원번호) ON DELETE SET NULL
);

-- Q2
ALTER TABLE 학생 ADD 전화번호 VARCHAR(15);

-- Q3
ALTER TABLE 학생 DROP COLUMN 주소;

-- Q4
CREATE INDEX idx_부서 ON 사원 (부서번호);

-- Q5
CREATE VIEW v_컴공 AS
SELECT 학번, 이름 FROM 학생 WHERE 학과코드 = 'D01'
WITH CHECK OPTION;

-- Q6
DROP TABLE 학과 CASCADE;

-- Q7
TRUNCATE TABLE 수강;
```

- Q5의 뷰는 SELECT 목록에 `학과코드` 가 없어서, 실제로 이 뷰에 INSERT 하면 학과코드가 NULL이 되어 CHECK OPTION 에 걸린다. 문제의 요구는 옵션을 붙이는 것까지다.
- Q6은 MySQL 에서 오류가 난다(슬라이드 참고). 실행해서 확인하려면 자식 테이블의 외래키부터 정리해야 한다.
- Q2~Q7을 실제로 실행했다면 `lab00` 의 초기화 명령으로 스키마를 되돌린다.

</details>

## 3. 확인 문제

**Q8.** 다음 설명에 해당하는 참조 무결성 옵션을 쓰시오.

1. 부모 테이블의 행이 삭제되면 그 행을 참조하는 자식 테이블의 행도 함께 삭제한다.
2. 자식 테이블에 참조하는 행이 있으면 부모 테이블의 행 삭제를 거부한다.

**Q9.** `DELETE`, `TRUNCATE`, `DROP` 중 ROLLBACK 으로 되돌릴 수 있는 것은?

**Q10.** 뷰의 단점을 두 가지 쓰시오.

<details>
<summary>정답</summary>

- **Q8.** 1. CASCADE, 2. RESTRICT
- **Q9.** DELETE
- **Q10.** 독립적인 인덱스를 가질 수 없다. ALTER 로 정의를 변경할 수 없다. 삽입·삭제·갱신 연산에 제약이 있다. (이 중 두 가지)

</details>
