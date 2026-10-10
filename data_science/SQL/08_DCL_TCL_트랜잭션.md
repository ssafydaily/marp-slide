---
marp: true
theme: dark-plus-code
paginate: true
---

# 8단계. DCL · TCL 과 트랜잭션

GRANT · REVOKE / COMMIT · ROLLBACK · SAVEPOINT / 병행 제어 · 회복

- 권한 부여와 회수 구문을 정확히 쓴다
- 트랜잭션의 특성과 상태를 용어로 설명한다
- 격리 수준별로 생기는 현상을 구분한다

> 실습지: `labs/lab08_DCL_TCL.md`

---

# DCL — 데이터 제어어

| 명령 | 기능 |
| --- | --- |
| `GRANT` | 권한 부여 |
| `REVOKE` | 권한 회수 |
| `COMMIT` | 트랜잭션 결과를 확정 |
| `ROLLBACK` | 트랜잭션을 취소 |
| `SAVEPOINT` | 트랜잭션 안에 되돌아갈 지점을 지정 |

- DCL 의 역할: 보안, 무결성, 회복, 병행 제어
- `COMMIT`, `ROLLBACK`, `SAVEPOINT` 는 TCL 로 따로 분류하기도 한다

---

# GRANT

```sql
GRANT 권한 ON 개체 TO 사용자 [WITH GRANT OPTION];
```

```sql
GRANT SELECT, INSERT ON 학생 TO kim;
GRANT UPDATE (주소) ON 학생 TO kim;                -- 특정 컬럼만
GRANT ALL ON 학생 TO kim;                          -- 모든 권한
GRANT SELECT ON 학과 TO kim WITH GRANT OPTION;     -- 다른 사용자에게 다시 부여 가능
GRANT SELECT ON 학생 TO PUBLIC;                    -- 모든 사용자 (표준)
```

| 권한 | 대상 |
| --- | --- |
| `SELECT`, `INSERT`, `UPDATE`, `DELETE` | 테이블, 뷰 |
| `REFERENCES` | 외래키로 참조할 수 있는 권한 |
| `ALL` | 위 권한 전체 |

---

# REVOKE

```sql
REVOKE [GRANT OPTION FOR] 권한 ON 개체 FROM 사용자 [CASCADE];
```

```sql
REVOKE INSERT ON 학생 FROM kim;
REVOKE GRANT OPTION FOR SELECT ON 학과 FROM kim;   -- 재부여 권한만 회수
REVOKE SELECT ON 학과 FROM kim CASCADE;            -- kim 이 부여한 권한도 연쇄 회수
```

- `GRANT ~ TO`, `REVOKE ~ FROM`. 전치사를 바꿔 쓰지 않는다
- `GRANT OPTION FOR`: 권한 자체는 남기고 **다른 사람에게 줄 수 있는 권한만** 회수
- `CASCADE`: 해당 사용자가 다른 사용자에게 부여한 권한까지 연쇄적으로 회수

---

# MySQL 의 DCL

```sql
CREATE USER 'kim'@'%' IDENTIFIED BY 'kim1234';
GRANT SELECT, INSERT ON study.학생 TO 'kim'@'%';
SHOW GRANTS FOR 'kim'@'%';
```

```
GRANT USAGE ON *.* TO `kim`@`%`
GRANT SELECT, INSERT ON `study`.`학생` TO `kim`@`%`
```

| 항목 | 표준·시험 | MySQL |
| --- | --- | --- |
| 사용자 표기 | `kim` | `'kim'@'호스트'` |
| 재부여 권한 회수 | `REVOKE GRANT OPTION FOR 권한 ON ~` | `REVOKE GRANT OPTION ON ~ FROM ~` |
| `REVOKE ~ CASCADE` | 지원 | 문법 오류 |
| `PUBLIC` | 지원 | 미지원 |

---

# 역할 (ROLE)

여러 권한을 묶어 이름을 붙인 것. 사용자에게 역할을 부여해 권한을 한꺼번에 관리한다.

```sql
CREATE ROLE 'r_조회';
GRANT SELECT ON study.* TO 'r_조회';      -- 역할에 권한을 주고
GRANT 'r_조회' TO 'kim'@'%';              -- 사용자에게 역할을 준다
SET DEFAULT ROLE 'r_조회' TO 'kim'@'%';   -- MySQL: 접속 시 자동 활성화
```

- 사용자가 많을 때 권한을 사용자마다 주지 않고 역할 단위로 관리한다
- MySQL 은 역할을 부여해도 활성화하지 않으면 적용되지 않는다 (`SET DEFAULT ROLE` 또는 `SET ROLE`)

---

# 트랜잭션

데이터베이스의 상태를 변화시키는 **하나의 논리적 작업 단위**.

| 특성 | 의미 |
| --- | --- |
| 원자성 (Atomicity) | 모두 반영되거나 전혀 반영되지 않아야 한다 |
| 일관성 (Consistency) | 실행 전후로 데이터베이스가 일관된 상태를 유지한다 |
| 독립성·격리성 (Isolation) | 실행 중인 트랜잭션에 다른 트랜잭션이 끼어들 수 없다 |
| 영속성·지속성 (Durability) | 완료된 결과는 장애가 생겨도 영구히 반영된다 |

- 네 가지를 묶어 **ACID** 라고 한다
- 원자성 ↔ COMMIT·ROLLBACK, 독립성 ↔ 병행 제어, 영속성 ↔ 회복 기법

---

# 트랜잭션의 상태

```
          ┌──────────────→ 실패(Failed) ────→ 철회(Aborted)
          │                    ↑
활동(Active) ──→ 부분 완료(Partially Committed) ──→ 완료(Committed)
```

| 상태 | 설명 |
| --- | --- |
| 활동 | 실행 중 |
| 부분 완료 | 마지막 연산까지 실행했지만 COMMIT 전 |
| 완료 | COMMIT 으로 성공적으로 종료 |
| 실패 | 오류가 발생해 중단 |
| 철회 | ROLLBACK 을 수행해 실행 이전 상태로 복귀 |

---

# TCL — COMMIT · ROLLBACK · SAVEPOINT

```sql
START TRANSACTION;
UPDATE 사원 SET 급여 = 3100 WHERE 사번 = 107;
SAVEPOINT sp1;
UPDATE 사원 SET 급여 = 3300 WHERE 사번 = 109;
SAVEPOINT sp2;
DELETE FROM 사원 WHERE 사번 = 112;

ROLLBACK TO sp1;     -- sp1 이후의 UPDATE(109), DELETE(112) 취소
COMMIT;              -- 107번의 변경만 확정
```

| 사번 | 처음 | 결과 |
| --- | --- | --- |
| 107 | 3000 | **3100** |
| 109 | 3200 | 3200 |
| 112 | 있음 | 있음 |

- `ROLLBACK TO sp1` 을 하면 그 뒤에 만든 `sp2` 는 사라진다

---

# 자동 COMMIT

| 상황 | 동작 |
| --- | --- |
| MySQL `autocommit = 1` (기본값) | DML 한 문장마다 자동 COMMIT |
| `START TRANSACTION` 이후 | COMMIT·ROLLBACK 까지 하나의 트랜잭션 |
| DDL 실행 (CREATE, ALTER, DROP, TRUNCATE) | 그 시점에 **암묵적 COMMIT** |

```sql
START TRANSACTION;
UPDATE 사원 SET 급여 = 1 WHERE 사번 = 107;
CREATE TABLE tmp_ddl (a INT);      -- 여기서 UPDATE 가 COMMIT 된다
ROLLBACK;                          -- 되돌릴 것이 없다
SELECT 급여 FROM 사원 WHERE 사번 = 107;   -- 1
```

- Oracle 은 기본이 수동 COMMIT 이다. 시험 문제는 대개 명시적 COMMIT 을 전제로 한다

---

# 병행 제어

여러 트랜잭션을 동시에 실행하면서 일관성을 유지하는 기법.

병행 제어를 하지 않을 때의 문제

| 문제 | 설명 |
| --- | --- |
| 갱신 분실 (Lost Update) | 두 트랜잭션이 같은 데이터를 갱신해 한쪽 결과가 사라진다 |
| 비완료 의존성 (Uncommitted Dependency) | 실패한 트랜잭션의 중간 결과를 다른 트랜잭션이 참조한다 |
| 모순성 (Inconsistency) | 병행 수행 결과 데이터가 일관성 없는 상태가 된다 |
| 연쇄 복귀 (Cascading Rollback) | 한 트랜잭션의 취소로 다른 트랜잭션도 연쇄적으로 취소된다 |

---

# 병행 제어 기법

| 기법 | 설명 |
| --- | --- |
| 로킹 (Locking) | 데이터에 잠금을 걸어 다른 트랜잭션의 접근을 막는다 |
| 2단계 로킹 (2PL) | 잠금을 거는 확장 단계와 푸는 축소 단계로 나눈다. 직렬성 보장, 교착 상태 가능 |
| 타임스탬프 순서 | 트랜잭션에 시간표를 부여해 그 순서대로 실행. 교착 상태 없음 |
| 낙관적 검증 | 일단 수행하고 종료 시점에 검증한다 |
| 다중 버전 (MVCC) | 데이터의 여러 버전을 유지하고 타임스탬프로 알맞은 버전을 읽는다 |

로킹 단위(잠금 대상의 크기)

| 로킹 단위 | 로크 수 | 관리 | 병행성 |
| --- | --- | --- | --- |
| 크다 | 적다 | 쉽다 | 낮다 |
| 작다 | 많다 | 어렵다 (오버헤드 증가) | 높다 |

---

# 격리 수준

| 격리 수준 | Dirty Read | Non-Repeatable Read | Phantom Read |
| --- | --- | --- | --- |
| READ UNCOMMITTED | 발생 | 발생 | 발생 |
| READ COMMITTED | - | 발생 | 발생 |
| REPEATABLE READ | - | - | 발생 |
| SERIALIZABLE | - | - | - |

| 현상 | 설명 |
| --- | --- |
| Dirty Read | COMMIT 되지 않은 데이터를 읽는다 |
| Non-Repeatable Read | 같은 조회를 반복했는데 값이 달라진다 |
| Phantom Read | 같은 조회를 반복했는데 없던 행이 나타난다 |

- 아래로 갈수록 격리성은 높고 동시 처리 성능은 낮다
- MySQL(InnoDB) 기본값은 REPEATABLE READ, Oracle 은 READ COMMITTED

---

# 격리 수준 — 실습 결과

세션 A가 사번 107의 급여를 두 번 읽는 사이에 세션 B가 3500으로 수정하고 COMMIT 한다.

| 세션 A의 격리 수준 | 첫 번째 조회 | 두 번째 조회 |
| --- | --- | --- |
| READ COMMITTED | 3000 | **3500** (Non-Repeatable Read) |
| REPEATABLE READ | 3000 | 3000 |

세션 B가 9999로 수정하고 COMMIT 하지 않은 상태에서 세션 A가 읽는다.

| 세션 A의 격리 수준 | 조회 결과 |
| --- | --- |
| READ UNCOMMITTED | **9999** (Dirty Read) |
| READ COMMITTED | 3000 |

```sql
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

---

# 회복 (Recovery)

장애로 손상된 데이터베이스를 손상 이전의 정상 상태로 복구하는 작업.

| 연산 | 의미 |
| --- | --- |
| REDO | 로그를 이용해 **완료된** 트랜잭션의 작업을 다시 실행 |
| UNDO | 로그를 이용해 **완료되지 않은** 트랜잭션의 변경을 취소 |

| 회복 기법 | 설명 | 필요한 연산 |
| --- | --- | --- |
| 지연 갱신 | COMMIT 전까지 DB에 반영하지 않고 로그에만 기록 | REDO |
| 즉시 갱신 | 변경을 즉시 DB에 반영하고 로그에도 기록 | REDO, UNDO |
| 검사점 (Checkpoint) | 검사점 이후의 트랜잭션만 회복 대상으로 삼는다 | REDO, UNDO |
| 그림자 페이징 | 페이지의 복사본(그림자)을 두고 장애 시 교체 | 로그 불필요 |

---

# 교착 상태 (Deadlock)

둘 이상의 트랜잭션이 서로가 가진 잠금을 기다리며 무한히 대기하는 상태.

| 발생 조건 | 설명 |
| --- | --- |
| 상호 배제 | 자원을 한 번에 하나만 사용할 수 있다 |
| 점유와 대기 | 자원을 가진 채 다른 자원을 기다린다 |
| 비선점 | 다른 트랜잭션의 자원을 빼앗을 수 없다 |
| 환형 대기 | 대기 관계가 원형을 이룬다 |

- 네 조건이 **모두** 성립해야 발생한다
- 해결 방법: 예방, 회피(은행원 알고리즘), 발견, 회복
- InnoDB 는 교착 상태를 감지하면 한쪽 트랜잭션을 자동으로 ROLLBACK 시킨다

---

# 정리 — 자주 틀리는 것

1. `GRANT ~ ON ~ TO`, `REVOKE ~ ON ~ FROM`
2. `WITH GRANT OPTION` 은 부여, `GRANT OPTION FOR` 는 회수
3. `CASCADE` 는 연쇄 회수
4. ACID: 원자성, 일관성, 독립성, 영속성
5. `ROLLBACK TO 저장점` 은 저장점 이후만 취소하고 트랜잭션은 계속된다
6. DDL 은 암묵적으로 COMMIT 한다
7. 지연 갱신은 REDO 만, 즉시 갱신은 REDO 와 UNDO
8. 로킹 단위가 크면 병행성이 낮고 관리가 쉽다
