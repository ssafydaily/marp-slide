# Lab 08. DCL · TCL 과 트랜잭션

슬라이드: `08_DCL_TCL_트랜잭션.md`

권한 실습은 `root` 계정으로, 나머지는 `student` 계정으로 진행한다.

```bash
docker exec -it sql-study-mysql mysql -uroot -p study      # 비밀번호 root1234
```

## 1. 권한 부여와 회수 (root)

### 1-1. 사용자 생성과 GRANT

```sql
CREATE USER 'kim'@'%' IDENTIFIED BY 'kim1234';
SHOW GRANTS FOR 'kim'@'%';
```

```
GRANT USAGE ON *.* TO `kim`@`%`
```

`USAGE` 는 접속만 할 수 있고 아무 권한도 없다는 뜻이다.

```sql
GRANT SELECT, INSERT ON study.학생 TO 'kim'@'%';
GRANT UPDATE (주소) ON study.학생 TO 'kim'@'%';
GRANT SELECT ON study.학과 TO 'kim'@'%' WITH GRANT OPTION;
SHOW GRANTS FOR 'kim'@'%';
```

```
GRANT USAGE ON *.* TO `kim`@`%`
GRANT SELECT ON `study`.`학과` TO `kim`@`%` WITH GRANT OPTION
GRANT SELECT, INSERT, UPDATE (`주소`) ON `study`.`학생` TO `kim`@`%`
```

### 1-2. REVOKE

```sql
REVOKE INSERT ON study.학생 FROM 'kim'@'%';
REVOKE GRANT OPTION ON study.학과 FROM 'kim'@'%';     -- MySQL 문법
SHOW GRANTS FOR 'kim'@'%';
```

```
GRANT USAGE ON *.* TO `kim`@`%`
GRANT SELECT ON `study`.`학과` TO `kim`@`%`
GRANT SELECT, UPDATE (`주소`) ON `study`.`학생` TO `kim`@`%`
```

표준 문법의 `CASCADE` 는 MySQL 에서 오류다.

```sql
REVOKE SELECT ON study.학과 FROM 'kim'@'%' CASCADE;
-- ERROR 1064 (42000): You have an error in your SQL syntax ... near 'CASCADE'
```

### 1-3. 역할

```sql
CREATE ROLE 'r_조회';
GRANT SELECT ON study.* TO 'r_조회';
GRANT 'r_조회' TO 'kim'@'%';
SET DEFAULT ROLE 'r_조회' TO 'kim'@'%';
SHOW GRANTS FOR 'kim'@'%';
```

마지막 줄에 ``GRANT `r_조회`@`%` TO `kim`@`%` `` 가 추가된다.

### 1-4. kim 으로 접속해 확인

다른 터미널에서 접속한다.

```bash
docker exec -it sql-study-mysql mysql -ukim -p study      # 비밀번호 kim1234
```

```sql
SELECT CURRENT_USER(), CURRENT_ROLE();              -- kim@%, `r_조회`@`%`
SELECT COUNT(*) FROM 사원;                           -- 12 (역할로 받은 SELECT 권한)
UPDATE 학생 SET 주소 = '제주' WHERE 학번 = 1006;     -- 성공 (주소 컬럼 UPDATE 권한)
UPDATE 학생 SET 주소 = NULL WHERE 학번 = 1006;       -- 원래대로
UPDATE 학생 SET 학년 = 2 WHERE 학번 = 1006;
-- ERROR 1143 (42000): UPDATE command denied to user 'kim'@'localhost' for column '학년' in table '학생'
DELETE FROM 학생 WHERE 학번 = 1010;
-- ERROR 1142 (42000): DELETE command denied to user 'kim'@'localhost' for table '학생'
```

### 1-5. 정리 (root)

```sql
DROP ROLE 'r_조회';
DROP USER 'kim'@'%';
```

## 2. 트랜잭션 제어 (student)

### 2-1. SAVEPOINT

```sql
START TRANSACTION;
UPDATE 사원 SET 급여 = 3100 WHERE 사번 = 107;
SAVEPOINT sp1;
UPDATE 사원 SET 급여 = 3300 WHERE 사번 = 109;
SAVEPOINT sp2;
DELETE FROM 사원 WHERE 사번 = 112;
SELECT COUNT(*) FROM 사원;                             -- 11

ROLLBACK TO sp1;
SELECT 사번, 급여 FROM 사원 WHERE 사번 IN (107, 109, 112);
```

| 사번 | 급여 |
| --- | --- |
| 107 | 3100 |
| 109 | 3200 |
| 112 | 2800 |

```sql
ROLLBACK TO sp2;
-- ERROR 1305 (42000): SAVEPOINT sp2 does not exist

COMMIT;
```

`sp1` 로 되돌아가면 그 뒤에 만든 `sp2` 는 사라진다. COMMIT 후 107번의 급여는 3100으로 확정된다. 다음 실습을 위해 되돌려 둔다.

```sql
UPDATE 사원 SET 급여 = 3000 WHERE 사번 = 107;
```

### 2-2. autocommit

```sql
SELECT @@autocommit;                              -- 1
SET autocommit = 0;
UPDATE 사원 SET 급여 = 1 WHERE 사번 = 107;
ROLLBACK;
SELECT 급여 FROM 사원 WHERE 사번 = 107;           -- 3000
SET autocommit = 1;
```

`autocommit = 0` 이면 `START TRANSACTION` 없이도 ROLLBACK 할 수 있다.

### 2-3. DDL 의 암묵적 COMMIT

```sql
START TRANSACTION;
UPDATE 사원 SET 급여 = 1 WHERE 사번 = 107;
CREATE TABLE tmp_ddl (a INT);
ROLLBACK;
SELECT 급여 FROM 사원 WHERE 사번 = 107;           -- 1 (되돌려지지 않았다)

UPDATE 사원 SET 급여 = 3000 WHERE 사번 = 107;
DROP TABLE tmp_ddl;
```

## 3. 격리 수준 (student, 터미널 2개)

터미널을 두 개 열어 각각 `student` 로 접속한다. 표의 순서대로 번갈아 실행한다.

### 3-1. Non-Repeatable Read

| 순서 | 세션 A | 세션 B |
| --- | --- | --- |
| 1 | `SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;` | |
| 2 | `START TRANSACTION;` | |
| 3 | `SELECT 급여 FROM 사원 WHERE 사번 = 107;` → 3000 | |
| 4 | | `UPDATE 사원 SET 급여 = 3500 WHERE 사번 = 107;` |
| 5 | `SELECT 급여 FROM 사원 WHERE 사번 = 107;` → **3500** | |
| 6 | `COMMIT;` | |
| 7 | | `UPDATE 사원 SET 급여 = 3000 WHERE 사번 = 107;` |

같은 트랜잭션 안에서 같은 조회의 결과가 달라졌다.

1번을 `REPEATABLE READ` 로 바꿔 다시 해 보면 5번의 결과가 **3000** 이다. 트랜잭션이 시작된 시점의 데이터를 계속 본다.

### 3-2. Dirty Read

| 순서 | 세션 A | 세션 B |
| --- | --- | --- |
| 1 | | `START TRANSACTION;` |
| 2 | | `UPDATE 사원 SET 급여 = 9999 WHERE 사번 = 107;` |
| 3 | `SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;` | |
| 4 | `SELECT 급여 FROM 사원 WHERE 사번 = 107;` → **9999** | |
| 5 | | `ROLLBACK;` |
| 6 | `SELECT 급여 FROM 사원 WHERE 사번 = 107;` → 3000 | |

4번에서 읽은 9999는 결국 존재한 적이 없는 값이다. 3번을 `READ COMMITTED` 로 바꾸면 4번의 결과는 3000 이다.

### 3-3. 잠금 대기

| 순서 | 세션 A | 세션 B |
| --- | --- | --- |
| 1 | `START TRANSACTION;` | |
| 2 | `UPDATE 사원 SET 급여 = 3100 WHERE 사번 = 107;` | |
| 3 | | `UPDATE 사원 SET 급여 = 3200 WHERE 사번 = 107;` (멈춘다) |
| 4 | `ROLLBACK;` | (3번이 이제 실행된다) |
| 5 | | `UPDATE 사원 SET 급여 = 3000 WHERE 사번 = 107;` |

세션 A가 행에 건 잠금이 풀릴 때까지 세션 B가 기다린다. 이것이 로킹이다.

## 4. 쿼리 작성

시험 답안 형식(표준 SQL)으로 작성한다.

**Q1.** 사용자 `lee` 에게 `사원` 테이블에 대한 SELECT, UPDATE 권한을 부여하시오. `lee` 가 이 권한을 다른 사용자에게 부여할 수 있어야 한다.

**Q2.** 사용자 `lee` 로부터 `사원` 테이블에 대한 UPDATE 권한을 회수하시오. `lee` 가 다른 사용자에게 부여한 권한도 함께 회수한다.

**Q3.** 사용자 `park` 에게 `학생` 테이블에 대한 모든 권한을 부여하시오.

**Q4.** 사용자 `lee` 가 `사원` 테이블에 대한 SELECT 권한을 다른 사용자에게 부여할 수 있는 권한만 회수하시오.

<details>
<summary>정답</summary>

```sql
-- Q1
GRANT SELECT, UPDATE ON 사원 TO lee WITH GRANT OPTION;

-- Q2
REVOKE UPDATE ON 사원 FROM lee CASCADE;

-- Q3
GRANT ALL ON 학생 TO park;

-- Q4
REVOKE GRANT OPTION FOR SELECT ON 사원 FROM lee;
```

</details>

## 5. 확인 문제

**Q5.** 다음을 순서대로 실행한 뒤 `SELECT 급여 FROM 사원 WHERE 사번 IN (105, 106)` 의 결과는?

```sql
START TRANSACTION;
UPDATE 사원 SET 급여 = 6000 WHERE 사번 = 105;
SAVEPOINT a;
UPDATE 사원 SET 급여 = 5000 WHERE 사번 = 106;
ROLLBACK TO a;
UPDATE 사원 SET 급여 = 급여 + 100 WHERE 사번 = 105;
COMMIT;
```

**Q6.** 트랜잭션의 특성 네 가지 중 "트랜잭션의 연산은 모두 반영되거나 전혀 반영되지 않아야 한다" 에 해당하는 것은?

**Q7.** COMMIT 되지 않은 데이터를 다른 트랜잭션이 읽는 현상의 이름과, 이 현상이 발생하는 격리 수준을 쓰시오.

**Q8.** 회복 기법 중 트랜잭션이 COMMIT 되기 전까지 변경 내용을 로그에만 기록하고 데이터베이스에는 반영하지 않는 기법의 이름과, 장애 시 필요한 연산을 쓰시오.

**Q9.** 로킹 단위가 커질 때 로크의 수, 병행성 수준, 오버헤드는 각각 어떻게 되는가?

<details>
<summary>정답</summary>

- **Q5.** 105번 6100, 106번 4200. 106번의 변경은 저장점 이후라 취소되고, 105번은 6000에 100이 더해진다. (실행했다면 105번의 급여를 5500으로 되돌린다.)
- **Q6.** 원자성 (Atomicity)
- **Q7.** Dirty Read, READ UNCOMMITTED
- **Q8.** 지연 갱신 기법, REDO (UNDO 는 필요 없다)
- **Q9.** 로크의 수는 줄고, 병행성 수준은 낮아지고, 오버헤드는 줄어든다.

</details>
