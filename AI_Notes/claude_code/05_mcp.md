---
marp: true
theme: default
paginate: true
style: |
  @import url("../../custom-theme.css")

---

# MCP

- *Claude Code* 는 기본적으로 로컬 파일과 터미널만 접근
- **MCP 서버** 를 추가하면 *외부 서비스* 에 대한 접근 능력이 추가


<div class="cols">
<div>

| 기본 상태 | 	MCP 추가 후 |
| -------- | ----------- |
| 파일 읽기/쓰기 | 	+ DB 쿼리 실행 |
| 터미널 명령어 | 	+ 외부 API 호출 |
| Git 작업 | 	+ 이슈 트래커 연동 |

</div>
<div>

- MCP 서버는 Claude Code와 외부 서비스 사이의 다리 역할
- Claude가 MCP 서버에 요청을 보내면, 서버가 해당 서비스의 API를 호출하고 결과를 돌려준다

</div>
</div>

---------------

# 실습 사전 준비

- Docker Desktop (Windows의 경우 WSL2 백엔드 권장)
- Node.js (npx 실행용, MySQL MCP 서버를 npx로 구동하기 위해 필요)
- Claude Code CLI 설치 및 로그인 완료

```sh
docker --version
node --version
claude --version
```

- 먼저 **Docker 데스크탑 실행**
  - [Docker 설치](https://www.docker.com/products/docker-desktop/) 
  
------------- 

## MySQL 8.0 컨테이너를 실행

<div class="cols">
<div>

- **Window powershell** 에서 실행
```sh
docker run -d `
  --name mysql-mcp-lab `
  -e MYSQL_ROOT_PASSWORD=root_password `
  -e MYSQL_DATABASE=mcp_lab `
  -e MYSQL_USER=mcp_user `
  -e MYSQL_PASSWORD=mcp_password `
  -p 3306:3306 `
  -v mysql-mcp-data:/var/lib/mysql `
  mysql:8.0
```

</div>
<div>

| 옵션 | 	설명 |
| --- | ---- |
| -d	 | 백그라운드(detached)로 컨테이너 실행 |
| --name	| 컨테이너 이름 지정 (이후 명령에서 참조) |
| -e	 | 컨테이너 환경 변수 설정 (root 비밀번호, 기본 DB, 계정 생성) |
| -p  | 3306:3306	호스트 3306 포트를 컨테이너 3306 포트로 매핑 |
| -v | 	데이터 영속화를 위한 볼륨 마운트 (컨테이너 삭제 후에도 데이터 유지)|
 mysql:8.0	| 사용할 이미지와 태그 |

</div>
</div>

- 컨테이너 실행 확인
```sh
docker ps
docker logs -f mysql-mcp-lab
```
- 로그에 `ready for connections`가 보이면 초기화가 끝난 것입니다. (Ctrl+C로 로그 추적 종료)

-----------------

#### **데스크톱 앱** 에서 확인
![](images/05_docker_container1.png)

------------------

## MySql 접속 및 예시 테이블 생성


```sh
docker exec -it mysql-mcp-lab mysql -u mcp_user -p'mcp_password'
```
- 접속 후 Database 연결

  ```sql
  USE 데이터베이스명;

  -- 예시
  USE mcp_lab;
  ```

- Database 목록 확인
  ```sql
  SHOW DATABASES;
  ```

-------------------

<div class="cols">
<div>

- 데이터 베이스 생성

  ```sql
  -- 기본 생성
  CREATE DATABASE 데이터베이스명;

  -- 한글 지원 포함 (권장)
  CREATE DATABASE 데이터베이스명
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

  -- 예시
  CREATE DATABASE mcp_lab
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
  ```

</div>
<div>

- 생성 후 바로 연결
  ```sql
  CREATE DATABASE mcp_lab;
  USE mcp_lab;
  ```

- 요약

  | 목적 | 명령어 |
  |------|--------|
  | DB 목록 확인 | `SHOW DATABASES;` |
  | DB 연결 | `USE db명;` |
  | DB 생성 | `CREATE DATABASE db명;` |
  | 현재 연결된 DB 확인 | `SELECT DATABASE();` |

</div>
</div>

> **팁:** `docker run` 시 `-e MYSQL_DATABASE=mcp_lab` 옵션을 주었다면 DB가 이미 자동 생성되어 있을 수 있다.

---------------

## 예시 테이블 생성

- employ 테이블 생성과 레코드 삽입

  ```sql
  CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50),
    salary DECIMAL(10,2),
    hired_at DATE
  );

  INSERT INTO employees (name, department, salary, hired_at) VALUES
  ('Kim', 'Engineering', 5500.00, '2023-03-01'),
  ('Lee', 'Sales',       4200.00, '2022-07-15'),
  ('Park', 'Engineering',6000.00, '2021-11-20');

  SELECT * FROM employees;
  ```

-------------------------

## Claude Code에 MySQL MCP 서버 등록
- MySQL용 커뮤니티 MCP 서버(`@benborla29/mcp-server-mysql`)를 `npx`로 실행하도록 등록
  - 설치 없이 실행 시점에 npx가 자동으로 패키지를 받아온다.

```sh
claude mcp add mysql `
  -e MYSQL_HOST=127.0.0.1 `
  -e MYSQL_PORT=3306 `
  -e MYSQL_USER=mcp_user `
  -e MYSQL_PASS=mcp_pass `
  -e MYSQL_DB=mcp_lab `
  -- npx -y @benborla29/mcp-server-mysql
```
- `-e KEY=VALUE` : MCP 서버 프로세스에 전달할 환경 변수 (MySQL 접속 정보)
- `-- 뒤` : 실제 MCP 서버를 구동할 명령어와 인자
- `-s project` 옵션을 추가하면 현재 프로젝트(`.mcp.json`)에만 저장되어 팀과 설정을 공유 
  - 생략 시 로컬(개인) 설정으로 등록

-------------------

- 등록된 내용은 직접 `.mcp.json` 또는 `~/.claude.json`을 열어 확인/수정 가능

  ```json
  // claude_desktop_config.json 또는 MCP 설정
  {
    "mcpServers": {
      "mcp_server_mysql": {
        "command": "npx",
        "args": ["-y", "@benborla29/mcp-server-mysql"],
        "env": {
          "MYSQL_HOST": "127.0.0.1",
          "MYSQL_PORT": "3306",
          "MYSQL_USER": "mcp_user",
          "MYSQL_PASS": "mcp_pass",
          "MYSQL_DB": "mcp_lab"
        }
      }
    }
  }
  ```

------------------

## 연동 확인

<div class="cols">
<div>

```sh
claude mcp list
claude mcp get mysql
```
![](images/05_check_mcp_mysql.png)

</div>
<div>

- Claude Code 세션 안에서는 다음 슬래시 명령으로 MCP 서버 연결 상태를 확인
![](images/05_check_mcp_mysql2.png)

- `connected` 로 보이면 정상

</div>
</div>

-------------------

## Claude Code에서 자연어로 MySQL 다뤄보기

- Claude Code 세션에서 자연어로 요청해봅니다.

  ```
  "mcp_lab 데이터베이스의 employees 테이블 스키마를 보여줘"

  "employees 테이블에서 department별 평균 salary를 구해줘"

  "employees 테이블에 projects 테이블을 새로 만들고 employee_id로 연결해줘"
  ```
- Claude가 MCP를 통해 실제 쿼리를 실행하고 결과를 보여준다. 
  - 서버 설정에 따라 쓰기 작업은 권한 설정이 필요할 수 있다.

--------------


## Docker 명령어 요약

| 명령어 | 설명 |
|---|---|
| `docker run` | 새 컨테이너를 생성하고 실행 |
| `docker ps` | 실행 중인 컨테이너 목록 확인 (`-a`로 전체) |
| `docker logs -f <name>` | 컨테이너 로그 실시간 확인 |
| `docker exec -it <name> <cmd>` | 실행 중인 컨테이너 내부에서 명령 실행 (대화형 셸/클라이언트 접속에 사용) |
| `docker stop <name>` | 컨테이너 정지 |
| `docker rm <name>` | 정지된 컨테이너 삭제 |
| `docker volume ls` / `docker volume rm` | 볼륨(영속 데이터) 조회/삭제 |

--------------

## MCP 명령어 요약

| 명령어 | 설명 |
|---|---|
| `claude mcp add <name> [-e KEY=VALUE...] -- <cmd>` | MCP 서버를 등록 |
| `claude mcp list` | 등록된 MCP 서버 목록 확인 |
| `claude mcp get <name>` | 특정 MCP 서버의 설정 상세 확인 |
| `claude mcp remove <name>` | 등록된 MCP 서버 제거 |
| `/mcp` (세션 내) | 현재 세션에서 연결된 MCP 서버 상태 확인 |

--------------

## 서버 Scope

- MCP 서버는 세 가지 스코프로 등록

| 스코프 | 	옵션 | 	설정 파일 위치 |	용도 |
| ----- | -----| -------------| ----- |
| user| 	--scope user| 	~/.claude.json |	모든 프로젝트에서 사용 |
| project| 	--scope project| 	.mcp.json (프로젝트 루트) |	팀과 공유 (Git 커밋) |
| local| 	--scope local| 	~/.claude.json (프로젝트별) |	개인 전용 |

- 팀 전체가 같은 MCP 서버를 사용해야 한다면 --scope project로 등록합니다.

  ```sh
  claude mcp add --scope project \
    postgres -- npx -y @modelcontextprotocol/server-postgres \
    postgresql://postgres:password@localhost/mydb
  ```

--------------

## 트러블슈팅

- **컨테이너가 `Restarting` 상태**: `docker logs mysql-mcp-lab`로 초기화 에러 확인 (대부분 비밀번호/볼륨 권한 문제)

- **MCP 서버가 `failed`로 표시**: 환경 변수(호스트/포트/계정 정보) 오타 확인, MySQL 컨테이너가 떠 있는지(`docker ps`) 확인

- **포트 충돌(3306 already in use)**: 로컬에 다른 MySQL이 떠 있는 경우, `-p 13306:3306`처럼 호스트 포트를 변경하고 MCP 환경 변수의 `MYSQL_PORT`도 동일하게 변경

- **npx 실행이 느림**: 최초 실행 시 패키지를 다운로드하므로 정상이며, 이후 캐시되어 빨라짐

- Node.js 18 이상이 설치되어 있어야 npx 명령어가 동작합니다