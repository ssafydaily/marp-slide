# Lab 00. 실습 환경 구축

슬라이드: `00_실습환경_MySQL.md`

## 준비물

- Docker Desktop (실행 중이어야 한다)
- 터미널 (PowerShell, Git Bash 어느 쪽이든 가능)

## 1. 서버 기동

```bash
cd data_science/SQL/docker
docker compose up -d --build
docker compose ps
```

`STATUS` 가 `Up ... (healthy)` 로 나오면 준비가 끝난 것이다. 처음에는 이미지를 내려받느라 몇 분 걸린다.

설정 파일이 정상적으로 읽혔는지 확인한다. 아래 명령의 결과가 `0` 이어야 한다.

```bash
docker logs sql-study-mysql 2>&1 | grep -c "World-writable"
```

PowerShell에서는 다음과 같이 확인한다.

```powershell
(docker logs sql-study-mysql 2>&1 | Select-String "World-writable").Count
```

## 2. 접속

```bash
docker exec -it sql-study-mysql mysql -ustudent -p study
```

비밀번호 `student1234` 를 입력한다. 프롬프트가 `mysql>` 로 바뀌면 성공이다. 나갈 때는 `exit`.

### GUI 도구로 접속하기

`127.0.0.1:3307` 은 **브라우저에 입력하는 주소가 아니다**. MySQL 서버는 웹 페이지(HTTP)가 아니라 MySQL 전용 프로토콜로 통신하므로 브라우저로는 열리지 않는다. MySQL 프로토콜을 쓰는 **데이터베이스 클라이언트 프로그램**에 아래 접속 정보를 입력해야 한다.

| 항목 | 값 |
| --- | --- |
| Host | `127.0.0.1` |
| Port | `3307` |
| Username | `student` |
| Password | `student1234` |
| Database | `study` |

**VS Code 의 Database Client 확장** (`cweijan.vscode-database-client2`) 을 쓰는 경우

1. 왼쪽 액티비티 바에서 원통 모양의 **Database** 아이콘을 누른다.
2. 패널 위쪽의 **+ (Create Connection)** 를 누른다.
3. Server Type 으로 **MySQL** 을 고르고 위 표의 값을 입력한다. Port 기본값이 3306 이므로 **3307 로 고친다**.
4. **Connect** 를 누른다. 왼쪽 트리에 `study` 와 테이블 6개가 보이면 성공이다.
5. 연결 이름 옆의 **Open Query** (새 쿼리) 버튼으로 SQL 편집 창을 열고, 쿼리를 쓴 뒤 `Ctrl+Enter` 로 실행한다.

MySQL Workbench, DBeaver 같은 다른 클라이언트도 같은 값을 입력하면 된다. DBeaver 에서 `Public Key Retrieval is not allowed` 오류가 나면 연결 설정의 Driver properties 에서 `allowPublicKeyRetrieval` 을 `true` 로 바꾼다.

접속이 안 될 때는 다음을 확인한다.

- `docker compose ps` 에서 컨테이너가 `healthy` 인가
- Port 를 3306 이 아니라 **3307** 로 입력했는가 (3306 은 PC 에 따로 설치된 MySQL 일 수 있다)
- Host 를 `localhost` 대신 `127.0.0.1` 로 입력했는가

## 3. 서버 설정 확인

```sql
SELECT VERSION();
SELECT @@character_set_server, @@collation_server;
SELECT @@time_zone, NOW();
SELECT @@transaction_isolation, @@autocommit;
SELECT @@sql_mode;
```

기대 결과

| 항목 | 값 |
| --- | --- |
| `VERSION()` | `8.4.x` |
| `@@character_set_server` | `utf8mb4` |
| `@@collation_server` | `utf8mb4_0900_ai_ci` |
| `@@time_zone` | `+09:00` |
| `@@transaction_isolation` | `REPEATABLE-READ` |
| `@@autocommit` | `1` |
| `@@sql_mode` | `ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION` |

## 4. 스키마와 데이터 확인

```sql
SHOW TABLES;
DESC 학생;
SHOW CREATE TABLE 수강\G

SELECT * FROM 학과;
SELECT * FROM 학생;
SELECT * FROM 과목;
SELECT * FROM 수강;
SELECT * FROM 부서;
SELECT * FROM 사원;
```

테이블별 행 수는 학과 4, 학생 10, 과목 6, 수강 14, 부서 5, 사원 12 이다.

### 전체 데이터

**학과**

| 학과코드 | 학과명 | 사무실 |
| --- | --- | --- |
| D01 | 컴퓨터공학과 | 공학관 301 |
| D02 | 전자공학과 | 공학관 201 |
| D03 | 경영학과 | 경상관 101 |
| D04 | 수학과 | 자연관 401 |

**학생**

| 학번 | 이름 | 학년 | 학과코드 | 주소 |
| --- | --- | --- | --- | --- |
| 1001 | 김철수 | 1 | D01 | 서울 |
| 1002 | 이영희 | 2 | D01 | 부산 |
| 1003 | 박민수 | 3 | D02 | 서울 |
| 1004 | 최지은 | 2 | D02 | 대전 |
| 1005 | 정우성 | 4 | D03 | 서울 |
| 1006 | 한소희 | 1 | D03 | NULL |
| 1007 | 오세훈 | 3 | D01 | 광주 |
| 1008 | 윤아름 | 2 | NULL | 부산 |
| 1009 | 김철수 | 4 | D02 | 인천 |
| 1010 | 강하늘 | 1 | D03 | 서울 |

**과목**

| 과목코드 | 과목명 | 학점 | 학과코드 |
| --- | --- | --- | --- |
| C101 | 데이터베이스 | 3 | D01 |
| C102 | 자료구조 | 3 | D01 |
| C103 | 회로이론 | 3 | D02 |
| C104 | 회계원리 | 2 | D03 |
| C105 | 운영체제 | 3 | D01 |
| C106 | 선형대수 | 3 | D04 |

**수강**

| 학번 | 과목코드 | 점수 |
| --- | --- | --- |
| 1001 | C101 | 85 |
| 1001 | C102 | 90 |
| 1002 | C101 | 92 |
| 1002 | C105 | 78 |
| 1003 | C101 | NULL |
| 1003 | C103 | 88 |
| 1004 | C102 | 60 |
| 1004 | C103 | 95 |
| 1005 | C104 | 70 |
| 1006 | C104 | 85 |
| 1007 | C101 | 85 |
| 1007 | C105 | NULL |
| 1008 | C102 | 77 |
| 1009 | C103 | 55 |

**부서**

| 부서번호 | 부서명 | 지역 |
| --- | --- | --- |
| 10 | 기획부 | 서울 |
| 20 | 개발부 | 서울 |
| 30 | 영업부 | 부산 |
| 40 | 인사부 | 대전 |
| 50 | 연구소 | 판교 |

**사원**

| 사번 | 이름 | 직급 | 급여 | 보너스 | 입사일 | 부서번호 | 상사사번 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 101 | 김대표 | 사장 | 9000 | NULL | 2010-03-01 | 10 | NULL |
| 102 | 이기획 | 부장 | 7000 | 500 | 2012-05-10 | 10 | 101 |
| 103 | 박개발 | 부장 | 7200 | 600 | 2011-09-15 | 20 | 101 |
| 104 | 최영업 | 부장 | 6800 | NULL | 2013-01-20 | 30 | 101 |
| 105 | 정코딩 | 과장 | 5500 | 300 | 2016-07-01 | 20 | 103 |
| 106 | 한서버 | 대리 | 4200 | NULL | 2019-03-11 | 20 | 105 |
| 107 | 오신입 | 사원 | 3000 | NULL | 2023-01-02 | 20 | 105 |
| 108 | 윤판매 | 과장 | 5500 | 400 | 2015-11-23 | 30 | 104 |
| 109 | 강매출 | 사원 | 3200 | 0 | 2022-06-13 | 30 | 108 |
| 110 | 조인사 | 과장 | 5200 | NULL | 2017-04-03 | 40 | 101 |
| 111 | 문기획 | 대리 | 4200 | 200 | 2020-08-17 | 10 | 102 |
| 112 | 신수습 | 사원 | 2800 | NULL | 2024-09-02 | NULL | 102 |

## 5. 세션 변수와 전역 변수

```sql
SELECT @@session.transaction_isolation, @@global.transaction_isolation;

SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;

SELECT @@session.transaction_isolation, @@global.transaction_isolation;
```

세션 값만 `READ-COMMITTED` 로 바뀌고 전역 값은 `REPEATABLE-READ` 그대로다. 접속을 끊었다가 다시 들어오면 세션 값도 원래대로 돌아온다.

## 6. sql_mode 가 동작을 바꾸는 것 확인

```sql
SELECT 이름, 부서번호, AVG(급여) FROM 사원 GROUP BY 부서번호;
```

```
ERROR 1055 (42000): Expression #1 of SELECT list is not in GROUP BY clause and contains
nonaggregated column 'study.사원.이름' ... incompatible with sql_mode=only_full_group_by
```

모드를 끄고 다시 실행해 본다.

```sql
SET SESSION sql_mode = '';
SELECT 이름, 부서번호, AVG(급여) FROM 사원 GROUP BY 부서번호;
```

오류 없이 실행되지만 `이름` 에는 그룹 안의 아무 값이나 나온다. 이 결과는 의미가 없고 표준 SQL에서는 오류다. 확인했으면 접속을 끊었다가 다시 들어와 모드를 되돌린다.

## 7. 데이터 초기화

실습 중에 데이터를 바꿨다면 언제든 처음 상태로 되돌릴 수 있다.

```bash
docker exec sql-study-mysql sh -c "mysql -uroot -proot1234 < /docker-entrypoint-initdb.d/01_schema.sql"
docker exec sql-study-mysql sh -c "mysql -uroot -proot1234 < /docker-entrypoint-initdb.d/02_data.sql"
```

`Using a password on the command line interface can be insecure` 경고는 무시해도 된다.

## 8. 백업

```bash
docker exec sql-study-mysql sh -c "mysqldump -uroot -proot1234 --no-tablespaces study > /tmp/study.sql"
docker cp sql-study-mysql:/tmp/study.sql ./study.sql
```

`study.sql` 을 열어 `CREATE TABLE` 과 `INSERT` 문으로 이루어져 있는지 확인한다.

## 확인 문제

1. `docker compose down` 과 `docker compose down -v` 의 차이는 무엇인가?
2. `init/02_data.sql` 을 수정하고 `docker compose restart` 를 했는데 데이터가 바뀌지 않았다. 이유는?
3. `SET GLOBAL` 로 바꾼 값은 서버를 재시작하면 어떻게 되는가?

<details>
<summary>정답</summary>

1. `down` 은 컨테이너만 지우고 데이터 볼륨은 남긴다. `down -v` 는 볼륨까지 지워서 다음 기동 때 초기화 스크립트가 다시 실행된다.
2. 초기화 스크립트는 데이터 볼륨이 비어 있을 때만 실행된다. 볼륨이 남아 있으면 건너뛴다. 7번의 초기화 명령을 직접 실행하거나 `down -v` 후 다시 기동해야 한다.
3. 사라진다. 영구적으로 바꾸려면 `my.cnf` 에 적고 이미지를 다시 빌드해야 한다.

</details>
