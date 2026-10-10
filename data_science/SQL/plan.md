# 정보처리기사 실기 — 데이터베이스/SQL 학습 문서 작성 계획

> 이 문서는 계획만 담는다. 실제 학습 문서는 이 계획이 확정된 뒤 작성한다.

## 1. 확정된 방향

| 항목 | 결정 |
| --- | --- |
| 문서 형식 | 강의용 Marp 슬라이드 + 실습용 일반 Markdown을 분리해서 작성 |
| 실습 환경 | Docker 중심 (MySQL 컨테이너 + 설정 파일 마운트) |
| 범위 | SQL 전 범위 + 실기 출제 DB 이론 전체 |
| 대상 | SQL 경험자. 기본 문법은 빠르게 정리하고 기출 유형과 함정에 집중 |

## 2. 산출물 구조

```
data_science/SQL/
├── work_guide.md
├── plan.md
├── 00_실습환경_MySQL.md        # Marp 슬라이드 (단계별 1파일)
├── 01_DB_기초이론.md
├── ...
├── 10_기출유형_종합.md
├── labs/                        # 일반 Markdown 실습지 (슬라이드와 번호 1:1 대응)
│   ├── lab00_환경구축.md
│   ├── ...
│   └── lab10_모의문제.md
└── docker/
    ├── compose.yaml
    ├── Dockerfile               # mysql:8.4 + my.cnf (아래 9장 참고)
    ├── conf.d/my.cnf            # 서버 설정
    └── init/
        ├── 01_schema.sql        # 실습 스키마
        └── 02_data.sql          # 실습 데이터
```

- 슬라이드: 개념, 문법 요약, 기출 포인트, 함정. 한 장에 한 가지 주제만.
- 실습지: 직접 실행할 쿼리, 예상 결과 표, 연습 문제, 접어 둔 정답과 해설.
- 슬라이드 프런트매터는 `theme: dark-plus-code`, `paginate: true`를 쓴다 (코드 비중이 높아서 선택, `빅분기/` 문서와 동일).

## 3. 단계별 학습 구성

각 단계는 **개념 요약 → MySQL 실습 → 기출 유형 문제 → 함정 정리** 순서로 구성한다.

| 단계 | 주제 | 주요 내용 | 실습 핵심 |
| --- | --- | --- | --- |
| 0 | 실습 환경과 MySQL 서버 설정 | 4장 참조 | 컨테이너 기동, 접속, 설정 확인 |
| 1 | DB 기초 이론 | DBMS 기능, 스키마 3계층, 데이터 독립성, 릴레이션 용어(튜플·속성·차수·카디널리티·도메인), 키의 종류, 무결성 제약 | 실습 스키마에서 키와 차수·카디널리티 직접 세기 |
| 2 | 데이터 모델링과 정규화 | E-R 모델, 이상 현상, 함수 종속, 1NF~BCNF·4NF·5NF, 반정규화 | 비정규 테이블을 단계별로 분해하고 이상 현상 재현 |
| 3 | DDL | CREATE/ALTER/DROP/TRUNCATE, 제약조건(PK·FK·UNIQUE·CHECK·DEFAULT), CASCADE/RESTRICT, 인덱스, 뷰 | 제약 위반 오류 직접 발생시키기, 참조 동작 비교 |
| 4 | DML 기본 | SELECT 구문 순서와 실행 순서, WHERE, LIKE, IN, BETWEEN, NULL 처리, DISTINCT, ORDER BY, INSERT/UPDATE/DELETE | 결과 예측 후 실행해서 비교 |
| 5 | 집계와 그룹 | 집계 함수, GROUP BY, HAVING, ROLLUP, 윈도우 함수(RANK·DENSE_RANK·ROW_NUMBER) | COUNT(*)와 COUNT(컬럼) 차이, NULL과 집계 |
| 6 | JOIN과 집합 연산 | INNER/OUTER/CROSS/SELF JOIN, NATURAL·USING, UNION/UNION ALL/INTERSECT/EXCEPT | 조인별 결과 행 수 예측 |
| 7 | 서브쿼리 | 스칼라, 인라인 뷰, 상관 서브쿼리, IN/EXISTS/ANY/ALL | NOT IN과 NULL 함정 재현 |
| 8 | DCL·TCL과 트랜잭션 | GRANT/REVOKE, ROLE, COMMIT/ROLLBACK/SAVEPOINT, ACID, 격리 수준, 병행 제어(로킹·2PL·타임스탬프), 회복 기법(즉시·지연 갱신, REDO/UNDO) | 세션 2개로 격리 수준별 현상 관찰 |
| 9 | 관계 대수와 관계 해석 | 순수 관계 연산(σ·π·⋈·÷), 일반 집합 연산, 관계 해석 기호, SQL 대응 | 관계 대수식을 SQL로 옮기기 (디비전 포함) |
| 10 | 절차형 SQL과 물리 설계, 종합 | 프로시저·사용자 정의 함수·트리거, 인덱스 종류, 파티션, 분산 DB 투명성, 종합 모의 문제 | 트리거 작성, EXPLAIN 확인, 모의 문제 풀이 |

## 4. MySQL 서버 설정 (0단계) 상세

- **기동**: `compose.yaml`로 MySQL 8.4 LTS 컨테이너 실행, 데이터 볼륨, 포트 매핑, 루트 비밀번호와 실습 계정 환경 변수
- **초기화**: `init/` 스크립트로 스키마와 데이터 자동 적재, 초기화 재실행 방법(볼륨 삭제)
- **`my.cnf` 설정 항목과 의미**
  - 문자셋·정렬: `character-set-server=utf8mb4`, `collation-server` (한글 데이터와 대소문자 비교에 미치는 영향)
  - `sql_mode`: `ONLY_FULL_GROUP_BY`, `STRICT_TRANS_TABLES`를 켠 상태로 실습 (표준 SQL 동작에 가깝게)
  - `default-time-zone`, `lower_case_table_names`
  - `transaction_isolation`, `autocommit` (8단계 실습에서 값을 바꿔 가며 사용)
  - 로그: general log, slow query log
- **설정 확인**: `SHOW VARIABLES`, `SELECT @@변수`, `SET SESSION`과 `SET GLOBAL`의 차이
- **접속**: `docker exec`로 mysql 클라이언트 사용, GUI 도구(VS Code 확장 또는 Workbench) 연결
- **계정과 권한**: 실습용 사용자 생성, 권한 부여 (8단계 DCL의 사전 준비)
- **백업과 복원**: `mysqldump`
- **문제 해결**: 포트 충돌, 한글 깨짐, 초기화 스크립트 미실행

## 5. 실습 스키마

- 시험 문제와 같은 형태로 **학생·학과·과목·수강**, **사원·부서** 두 세트를 사용한다.
- 테이블명과 컬럼명은 기출 표기와 맞추기 위해 한글로 둔다 (`학생`, `학번`, `성적` 등).
- 데이터는 작게(테이블당 10행 안팎) 유지하고 NULL, 중복 값, 조인 불일치 행을 의도적으로 포함해 결과 예측 문제에 쓸 수 있게 한다.

## 6. 기출 반영 방침

- 기출 복원 문제를 그대로 싣지 않고 **유형을 재구성한 문제**로 작성한다.
- 유형 분류: 쿼리 작성형, 결과 예측형(행 수·출력 값), 빈칸 채우기형, 용어 서술형.
- 단계마다 "표준 SQL(시험 답안) vs MySQL 동작" 차이를 별도 박스로 정리한다. 예상 항목:
  - `FULL OUTER JOIN` 미지원 → `UNION`으로 대체
  - `MINUS` 대신 `EXCEPT`
  - `DROP TABLE ... CASCADE`가 문법만 허용되고 동작하지 않음
  - `REVOKE ... CASCADE`, `CREATE DOMAIN` 미지원
  - `GRANT ... WITH GRANT OPTION` 등 권한 구문 차이
- 출제 빈도와 최근 출제 경향은 문서 작성 단계에서 조사해 반영한다. 조사 전에는 특정 회차를 인용하지 않는다.

## 7. 작업 순서

1. `docker/` 구성(compose, my.cnf, 스키마·데이터)을 먼저 만들고 실제로 기동해서 검증
2. 0단계 슬라이드와 실습지 작성
3. 4~7단계(SQL 작성 핵심) 작성. 모든 예제 쿼리를 컨테이너에서 실행해 결과 표를 채움
4. 3·8·10단계(DDL, DCL/TCL, 절차형) 작성
5. 1·2·9단계(이론) 작성
6. 종합 모의 문제 작성, 전체 번호와 상호 참조 정리, Marp 렌더링 확인

## 8. 확인이 필요한 사항

- 테이블명·컬럼명을 한글로 두는 방침 (영문 식별자를 선호하면 변경)
- 슬라이드 테마 `dark-plus-code` 사용
- MySQL 버전 8.4 LTS 사용

## 9. 진행 결과 (2026-10-11)

계획대로 슬라이드 11개, 실습지 11개, Docker 구성을 작성했다. 계획과 달라진 점은 다음과 같다.

- **설정 파일 적용 방식**: Windows 에서 `my.cnf` 를 볼륨으로 마운트하면 권한 문제로 서버가 설정을 무시한다. 마운트 대신 `Dockerfile` 로 이미지에 복사하도록 바꿨다.
- **호스트 포트**: 이 PC 에 로컬 MySQL 서비스가 3306 을 쓰고 있어 컨테이너는 3307 로 연다.
- **`lower_case_table_names`**: 초기화 시점에만 정할 수 있고 한글 식별자에는 영향이 없어 설정하지 않고 설명만 넣었다.
- **기출 조사**: 회차별 출제 빈도는 조사하지 않았다. 문서에는 특정 회차를 인용하지 않고 유형을 재구성한 문제만 실었다.
- **Marp 렌더링**: 슬라이드를 실제로 렌더링해 넘침 여부를 확인하지는 않았다.

문서에 실린 SQL 과 결과 표는 MySQL 8.4.11 컨테이너에서 실행해 확인한 값이다.
