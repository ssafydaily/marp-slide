-- 실습 스키마. 다시 실행하면 테이블을 지우고 새로 만든다.
SET NAMES utf8mb4;
USE study;

DROP TABLE IF EXISTS 수강, 과목, 학생, 학과, 사원, 부서;

-- ---------------------------------------------------------------
-- 세트 1: 학과 - 학생 - 과목 - 수강
-- ---------------------------------------------------------------
CREATE TABLE 학과 (
    학과코드 CHAR(3)     NOT NULL,
    학과명   VARCHAR(20) NOT NULL,
    사무실   VARCHAR(20),
    CONSTRAINT pk_학과 PRIMARY KEY (학과코드),
    CONSTRAINT uq_학과_학과명 UNIQUE (학과명)
);

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

CREATE TABLE 과목 (
    과목코드 CHAR(4)     NOT NULL,
    과목명   VARCHAR(20) NOT NULL,
    학점     INT         NOT NULL,
    학과코드 CHAR(3),
    CONSTRAINT pk_과목 PRIMARY KEY (과목코드),
    CONSTRAINT fk_과목_학과 FOREIGN KEY (학과코드)
        REFERENCES 학과 (학과코드) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE 수강 (
    학번     INT     NOT NULL,
    과목코드 CHAR(4) NOT NULL,
    점수     INT,
    CONSTRAINT pk_수강 PRIMARY KEY (학번, 과목코드),
    CONSTRAINT ck_수강_점수 CHECK (점수 BETWEEN 0 AND 100),
    CONSTRAINT fk_수강_학생 FOREIGN KEY (학번)
        REFERENCES 학생 (학번) ON DELETE CASCADE,
    CONSTRAINT fk_수강_과목 FOREIGN KEY (과목코드)
        REFERENCES 과목 (과목코드) ON DELETE RESTRICT
);

-- ---------------------------------------------------------------
-- 세트 2: 부서 - 사원
-- ---------------------------------------------------------------
CREATE TABLE 부서 (
    부서번호 INT         NOT NULL,
    부서명   VARCHAR(20) NOT NULL,
    지역     VARCHAR(10),
    CONSTRAINT pk_부서 PRIMARY KEY (부서번호)
);

CREATE TABLE 사원 (
    사번     INT         NOT NULL,
    이름     VARCHAR(10) NOT NULL,
    직급     VARCHAR(10) NOT NULL,
    급여     INT         NOT NULL,
    보너스   INT,
    입사일   DATE        NOT NULL,
    부서번호 INT,
    상사사번 INT,
    CONSTRAINT pk_사원 PRIMARY KEY (사번),
    CONSTRAINT fk_사원_부서 FOREIGN KEY (부서번호) REFERENCES 부서 (부서번호),
    CONSTRAINT fk_사원_상사 FOREIGN KEY (상사사번) REFERENCES 사원 (사번)
);
