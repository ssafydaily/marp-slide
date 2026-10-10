# Lab 01. 데이터베이스 기초 이론

슬라이드: `01_DB_기초이론.md`

이론 단계지만 실습 스키마에서 직접 확인하면서 용어를 익힌다.

## 1. 따라 하기

### 1-1. 차수와 카디널리티

```sql
DESC 사원;                    -- 출력된 행 수가 차수
SELECT COUNT(*) FROM 사원;    -- 카디널리티
```

사원 릴레이션의 차수는 8, 카디널리티는 12 다.

카탈로그에서 한 번에 확인할 수도 있다.

```sql
SELECT TABLE_NAME, COUNT(*) AS 차수
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'study'
GROUP BY TABLE_NAME;
```

| TABLE_NAME | 차수 |
| --- | --- |
| 과목 | 4 |
| 부서 | 3 |
| 사원 | 8 |
| 수강 | 3 |
| 학과 | 3 |
| 학생 | 5 |

### 1-2. 키 확인

```sql
SELECT TABLE_NAME, CONSTRAINT_NAME, CONSTRAINT_TYPE
FROM information_schema.TABLE_CONSTRAINTS
WHERE TABLE_SCHEMA = 'study'
ORDER BY TABLE_NAME, CONSTRAINT_TYPE;
```

`PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `CHECK` 가 테이블별로 나온다. 학과 테이블에는 `PRIMARY KEY` 와 `UNIQUE`(`uq_학과_학과명`)가 있다. 학과명이 대체키다.

유일성을 데이터로 확인해 본다. 전체 행 수와 서로 다른 값의 수가 같으면 현재 데이터에서는 유일하다.

```sql
SELECT COUNT(*), COUNT(DISTINCT 이름), COUNT(DISTINCT 학번) FROM 학생;   -- 10, 9, 10
```

이름은 동명이인(김철수) 때문에 유일하지 않으므로 키가 될 수 없다.

> 주의: 현재 데이터에서 우연히 중복이 없다고 해서 키인 것은 아니다. 키는 "앞으로도 중복될 수 없다" 는 업무 규칙으로 정한다. 사원의 이름은 지금 12명 모두 다르지만 키가 아니다.

### 1-3. 무결성 위반

```sql
INSERT INTO 학생 (학번, 이름) VALUES (1001, '중복');                    -- 개체 무결성
INSERT INTO 학생 (학번, 이름) VALUES (NULL, '널키');                    -- 개체 무결성
INSERT INTO 학생 (학번, 이름, 학과코드) VALUES (2000, '참조', 'D99');   -- 참조 무결성
INSERT INTO 학생 (학번, 이름, 학년) VALUES (2000, '학년', 5);           -- 도메인 무결성
INSERT INTO 학생 (학번) VALUES (2000);                                  -- NULL 무결성 (이름 NOT NULL)
INSERT INTO 학과 VALUES ('D05', '수학과', NULL);                        -- 고유 무결성 (학과명 UNIQUE)
```

모두 오류가 나야 한다. 각 오류 메시지가 어떤 제약을 가리키는지 읽어 본다.

### 1-4. 시스템 카탈로그는 직접 수정할 수 없다

```sql
DELETE FROM information_schema.TABLES WHERE TABLE_NAME = '학생';
-- ERROR 1044 (42000): Access denied for user 'student'@'%' to database 'information_schema'
```

## 2. 확인 문제

**Q1.** 다음 SQL 의 결과로 만들어지는 릴레이션의 차수와 카디널리티를 쓰시오.

```sql
SELECT 학번, 이름, 주소 FROM 학생 WHERE 학과코드 = 'D01';
```

**Q2.** 다음 SQL 의 결과로 만들어지는 릴레이션의 차수와 카디널리티를 쓰시오.

```sql
SELECT DISTINCT 직급 FROM 사원;
```

**Q3.** 사원(사번, 이름, 직급, 급여, 보너스, 입사일, 부서번호, 상사사번) 릴레이션에서 {사번, 이름} 은 슈퍼키인가, 후보키인가? 이유를 쓰시오.

**Q4.** 다음 빈칸에 알맞은 용어를 쓰시오.

- 스키마의 종류 중 ( ① ) 스키마는 사용자나 응용 프로그래머가 각자의 입장에서 필요로 하는 데이터베이스의 논리적 구조를 정의한 것이다.
- ( ② ) 스키마는 데이터베이스의 전체적인 논리적 구조로, 하나만 존재한다.
- ( ③ ) 스키마는 물리적 저장 장치의 입장에서 본 데이터베이스 구조다.

**Q5.** "기본키를 구성하는 속성은 NULL 값이나 중복 값을 가질 수 없다" 는 규칙의 이름을 쓰시오.

**Q6.** 학생 릴레이션에서 학과코드가 NULL 인 튜플이 존재한다. 이것은 참조 무결성 위반인가?

**Q7.** 데이터베이스 설계 단계 중 다음 작업이 이루어지는 단계를 각각 쓰시오.

1. E-R 다이어그램 작성
2. 정규화
3. 인덱스 설계, 저장 레코드 양식 설계

**Q8.** DBMS 의 필수 기능 세 가지를 쓰시오.

**Q9.** 응용 프로그램에 영향을 주지 않고 데이터베이스의 물리적 구조(내부 스키마)를 변경할 수 있는 성질을 무엇이라 하는가?

**Q10.** 데이터베이스의 정의 네 가지 중 "자료의 중복을 배제한 데이터의 모임" 에 해당하는 것은?

<details>
<summary>정답과 해설</summary>

- **Q1.** 차수 3, 카디널리티 3. SELECT 한 컬럼이 3개, D01 학생이 3명(1001, 1002, 1007).
- **Q2.** 차수 1, 카디널리티 5. 사장, 부장, 과장, 대리, 사원.
- **Q3.** 슈퍼키. 유일성은 만족하지만 이름을 빼도 {사번} 만으로 유일하므로 최소성을 만족하지 못한다.
- **Q4.** ① 외부, ② 개념, ③ 내부
- **Q5.** 개체 무결성
- **Q6.** 아니다. 외래키는 NULL 이거나 참조 릴레이션의 기본키 값이면 된다.
- **Q7.** 1. 개념적 설계, 2. 논리적 설계, 3. 물리적 설계
- **Q8.** 정의 기능, 조작 기능, 제어 기능
- **Q9.** 물리적 데이터 독립성
- **Q10.** 통합된 데이터 (Integrated Data)

</details>
