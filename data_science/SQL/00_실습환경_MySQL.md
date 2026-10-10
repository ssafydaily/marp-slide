---
marp: true
theme: dark-plus-code
paginate: true
---

# 0단계. 실습 환경과 MySQL 서버 설정

정보처리기사 실기 — 데이터베이스/SQL

- Docker로 MySQL 8.4 서버를 띄운다
- 서버 설정(`my.cnf`)이 SQL 동작에 주는 영향을 이해한다
- 실습 스키마를 확인한다

> 실습지: `labs/lab00_환경구축.md`

---

# 전체 학습 흐름

| 단계 | 주제 | 단계 | 주제 |
| --- | --- | --- | --- |
| 0 | 실습 환경, 서버 설정 | 6 | JOIN, 집합 연산 |
| 1 | DB 기초 이론 | 7 | 서브쿼리 |
| 2 | 모델링, 정규화 | 8 | DCL·TCL, 트랜잭션 |
| 3 | DDL | 9 | 관계 대수·해석 |
| 4 | DML 기본 | 10 | 절차형 SQL, 종합 |
| 5 | 집계, 그룹, 윈도우 함수 | | |

- 슬라이드로 개념과 함정을 정리하고, 같은 번호의 실습지에서 직접 실행한다
- SQL을 빨리 익히려면 **4 → 5 → 6 → 7** 을 먼저 보고 나머지를 돌아와도 된다

---

# 구성 파일

```
docker/
├── compose.yaml        # 컨테이너 정의
├── Dockerfile          # mysql:8.4 + my.cnf
├── conf.d/my.cnf       # 서버 설정
└── init/
    ├── 01_schema.sql   # 테이블 6개
    └── 02_data.sql     # 실습 데이터
```

| 항목 | 값 |
| --- | --- |
| 호스트 포트 | `3307` (컨테이너 내부는 3306) |
| 데이터베이스 | `study` |
| 실습 계정 | `student` / `student1234` |
| 관리자 계정 | `root` / `root1234` |

---

# 기동과 종료

```bash
cd data_science/SQL/docker

docker compose up -d --build   # 빌드 후 백그라운드 기동
docker compose ps              # STATUS 가 healthy 인지 확인
docker compose logs mysql      # 서버 로그

docker compose stop            # 정지 (데이터 유지)
docker compose down            # 컨테이너 삭제 (데이터 유지)
docker compose down -v         # 볼륨까지 삭제 (데이터 초기화)
```

- 데이터는 `mysql-data` 볼륨에 저장되므로 컨테이너를 지워도 남는다
- `init/` 의 SQL은 **볼륨이 비어 있는 최초 기동 때 한 번만** 실행된다

---

# 접속

```bash
# 실습 계정으로 접속 (비밀번호 student1234)
docker exec -it sql-study-mysql mysql -ustudent -p study

# 관리자 계정 (권한 실습용)
docker exec -it sql-study-mysql mysql -uroot -p
```

GUI 클라이언트(VS Code Database Client 확장, MySQL Workbench, DBeaver 등)에 입력할 값. **브라우저 주소가 아니다**

| Host | Port | User | Password | Database |
| --- | --- | --- | --- | --- |
| `127.0.0.1` | `3307` | `student` | `student1234` | `study` |

---

# 설정 파일이 무시되는 문제 (Windows)

Windows에서 `my.cnf` 를 볼륨으로 마운트하면 권한이 777로 보여 서버가 읽지 않는다.

```
mysqld: [Warning] World-writable config file
        '/etc/mysql/conf.d/my.cnf' is ignored.
```

그래서 이 실습 환경은 마운트하지 않고 **이미지에 복사**한다.

```dockerfile
FROM mysql:8.4
COPY --chmod=644 conf.d/my.cnf /etc/mysql/conf.d/my.cnf
```

- `my.cnf` 를 고친 뒤에는 `docker compose up -d --build` 로 다시 빌드한다

---

# my.cnf — 문자셋과 정렬 규칙

```ini
[mysqld]
character-set-server = utf8mb4
collation-server     = utf8mb4_0900_ai_ci
```

- `utf8mb4`: 한글과 이모지까지 저장하는 4바이트 UTF-8
- 정렬 규칙 이름 읽는 법: `ai` = 악센트 구분 안 함, `ci` = 대소문자 구분 안 함

```sql
SELECT 'abc' = 'ABC';   -- 1 (참)
```

- 문자열 비교에서 대소문자를 구분하지 않는다는 점은 **MySQL 설정의 결과**다
- 시험 문제의 문자열 비교는 값 그대로 비교한다고 생각하고 푼다

---

# my.cnf — sql_mode

```ini
sql_mode = ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,...
```

| 모드 | 켰을 때 |
| --- | --- |
| `ONLY_FULL_GROUP_BY` | GROUP BY 에 없는 일반 컬럼을 SELECT 하면 오류 |
| `STRICT_TRANS_TABLES` | 길이 초과, 타입 불일치 값을 넣으면 오류 (끄면 잘라서 저장) |
| `ERROR_FOR_DIVISION_BY_ZERO` | 0으로 나누는 INSERT/UPDATE 는 오류 |

- 두 모드를 끄면 표준 SQL에서는 틀린 쿼리가 실행되어 **잘못된 습관**이 든다
- 이 실습 환경은 모두 켜 둔다 (MySQL 8.4 기본값과 같다)

---

# my.cnf — 시간대, 격리 수준, 로그

```ini
default-time-zone     = '+09:00'
transaction-isolation = REPEATABLE-READ
skip-log-bin
slow_query_log  = ON
long_query_time = 1
```

| 설정 | 의미 |
| --- | --- |
| `default-time-zone` | `NOW()`, `CURRENT_TIMESTAMP` 의 기준 시간대 |
| `transaction-isolation` | 트랜잭션 격리 수준 기본값 (8단계에서 바꿔 본다) |
| `skip-log-bin` | 바이너리 로그 끔. 일반 계정이 함수·트리거를 만들 수 있다 |
| `slow_query_log` | `long_query_time` 초 이상 걸린 쿼리 기록 |

---

# 설정 값 확인과 변경

```sql
SHOW VARIABLES LIKE 'character_set%';
SELECT @@sql_mode, @@time_zone, @@transaction_isolation;
SELECT @@autocommit;          -- 1: 문장마다 자동 COMMIT
```

| 범위 | 문법 | 적용 |
| --- | --- | --- |
| 세션 | `SET SESSION 변수 = 값` | 현재 접속에만, 끊으면 사라짐 |
| 전역 | `SET GLOBAL 변수 = 값` | 이후 새 접속부터, 서버 재시작 시 사라짐 |
| 영구 | `my.cnf` 수정 후 재시작 | 항상 |

- `SET GLOBAL` 은 관리자 권한이 필요하다

---

# 대소문자 구분 — lower_case_table_names

| 값 | 테이블명 대소문자 | 기본 OS |
| --- | --- | --- |
| 0 | 구분함 | Linux (이 실습 환경) |
| 1 | 구분 안 함 (소문자로 저장) | Windows |
| 2 | 저장은 그대로, 비교는 구분 안 함 | macOS |

- 이 값은 **데이터 디렉터리를 초기화할 때만** 정할 수 있다
- 키워드(`SELECT`, `select`)와 컬럼명은 어느 OS에서나 대소문자를 구분하지 않는다
- 이 실습은 한글 식별자를 쓰므로 영향을 받지 않는다

---

# 계정과 권한

```sql
-- root 로 접속해서 실행
SELECT user, host FROM mysql.user;
SHOW GRANTS FOR 'student'@'%';
```

```
GRANT USAGE ON *.* TO `student`@`%`
GRANT ALL PRIVILEGES ON `study`.* TO `student`@`%`
```

- MySQL의 계정은 `'사용자'@'접속 호스트'` 쌍이다. `%` 는 모든 호스트
- `USAGE` 는 "권한 없음(접속만 가능)" 이라는 뜻
- `student` 는 `study` 데이터베이스 안에서만 모든 권한을 가진다
- 계정 생성과 권한 부여는 8단계(DCL)에서 다룬다

---

# 데이터 초기화, 백업, 복원

```bash
# 실습 데이터를 처음 상태로 되돌리기
docker exec sql-study-mysql sh -c "mysql -uroot -proot1234 < /docker-entrypoint-initdb.d/01_schema.sql"
docker exec sql-study-mysql sh -c "mysql -uroot -proot1234 < /docker-entrypoint-initdb.d/02_data.sql"

# 백업 (컨테이너 안에 덤프 후 호스트로 복사)
docker exec sql-study-mysql sh -c "mysqldump -uroot -proot1234 --no-tablespaces study > /tmp/study.sql"
docker cp sql-study-mysql:/tmp/study.sql ./study.sql
```

- 리다이렉션(`<`, `>`)을 컨테이너 안에서 실행하므로 PowerShell에서도 한글이 깨지지 않는다
- 복원은 덤프 파일을 같은 방식으로 `mysql` 에 넣으면 된다

---

# 실습 스키마 — 학사

```
학과(학과코드, 학과명, 사무실)
학생(학번, 이름, 학년, 학과코드→학과, 주소)
과목(과목코드, 과목명, 학점, 학과코드→학과)
수강(학번→학생, 과목코드→과목, 점수)
```

| 테이블 | 행 수 | 일부러 넣어 둔 것 |
| --- | --- | --- |
| 학과 | 4 | 학생이 없는 학과(수학과) |
| 학생 | 10 | 동명이인, 주소 NULL, 학과 NULL, 수강 없는 학생 |
| 과목 | 6 | 수강생 없는 과목(선형대수) |
| 수강 | 14 | 점수 NULL 2건, 같은 점수 |

---

# 실습 스키마 — 인사

```
부서(부서번호, 부서명, 지역)
사원(사번, 이름, 직급, 급여, 보너스, 입사일, 부서번호→부서, 상사사번→사원)
```

| 테이블 | 행 수 | 일부러 넣어 둔 것 |
| --- | --- | --- |
| 부서 | 5 | 사원이 없는 부서(연구소) |
| 사원 | 12 | 보너스 NULL 6건, 부서 NULL 1건, 같은 급여, 자기 참조 |

- NULL, 중복, 짝이 없는 행은 **결과 예측 문제의 단골 함정**이다
- 문제를 풀기 전에 이 표를 떠올릴 수 있을 만큼 데이터를 눈에 익혀 둔다

---

# 문제 해결

| 증상 | 원인과 조치 |
| --- | --- |
| `port is already allocated` | 3307을 다른 프로그램이 사용 중. `compose.yaml` 의 포트를 바꾼다 |
| 설정이 적용되지 않음 | `--build` 없이 기동함. `docker compose up -d --build` |
| 테이블이 없음 | 볼륨이 남아 초기화 스크립트가 건너뛰어짐. 초기화 명령을 직접 실행하거나 `down -v` |
| 한글이 `???` 로 보임 | 클라이언트 문자셋 문제. `SET NAMES utf8mb4;` |
| 한글이 입력되지 않음 | 컨테이너 로캘 문제. `compose.yaml` 의 `LANG: C.UTF-8` 확인 |
| `Access denied` | 계정, 비밀번호, 포트(3307) 확인 |
