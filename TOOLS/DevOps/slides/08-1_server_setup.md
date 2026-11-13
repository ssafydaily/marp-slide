---
marp: true
theme: dark-plus-code
paginate: true
style: |
  /* 첫 페이지(lead): 어두운 배경에서 잘 보이도록 밝은 글자색 */
  section.lead h1 {
    color: #ffffff;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  }
  section.lead h2 {
    color: #e3f2fd;
    background-color: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.3);
    opacity: 1;
  }
  section.lead p {
    color: #cbd5e1;
    opacity: 1;
  }
---

<!-- _class: lead -->

# Step 8-1. 배포 서버 준비

## AWS EC2 + Docker + Nginx

---

# 학습 목표

- AWS EC2 인스턴스를 생성하고 SSH 로 접속한다
- 보안그룹으로 **필요한 포트만** 연다
- 서버에 Docker 를 설치하고 배포 폴더를 준비한다
- 운영용 compose 구성(**Nginx → gunicorn → PostgreSQL**)을 이해한다
- 서버의 비밀값(.env)을 안전하게 관리한다

📁 실습 폴더: `practice/step08_cd/template/deploy`

---

# 운영 서버 구성도

```
  인터넷 사용자
       │  http://<EC2_IP>/api/todos/
       ▼
┌──────────────── AWS EC2 (Ubuntu) ─────────────────┐
│  보안그룹: 22(SSH), 80(HTTP) 만 허용                 │
│                                                    │
│   nginx :80  ──▶  web (gunicorn :8000)  ──▶  db    │
│   리버스 프록시     Django 앱                PostgreSQL│
│                                         (외부 비공개) │
│   ~/todo-api/                                      │
│     ├── docker-compose.prod.yml                    │
│     ├── nginx.conf                                 │
│     ├── deploy.sh / rollback.sh                    │
│     └── .env   ← 서버에만 존재 (비밀값)               │
└────────────────────────────────────────────────────┘
```

---

# 왜 Nginx 를 앞에 두나?

| 역할 | 설명 |
|------|------|
| 리버스 프록시 | 외부 요청을 내부 gunicorn 으로 전달 |
| 보안 | 앱 서버(8000)를 외부에 직접 노출하지 않음 |
| 성능 | 느린 클라이언트 처리, 연결 관리 |
| 확장 | HTTPS(인증서), 도메인, 여러 앱 라우팅 |

> gunicorn 은 "Python 코드 실행", Nginx 는 "웹 트래픽 처리" 전문가

---

# 1) EC2 인스턴스 생성

AWS 콘솔 → **EC2 → 인스턴스 시작**

| 항목 | 값 |
|------|-----|
| 이름 | `todo-api-server` |
| AMI | **Ubuntu Server 24.04 LTS** |
| 인스턴스 유형 | `t2.micro` 또는 `t3.micro` (프리티어) |
| 키 페어 | 새로 생성 → `todo-api-key.pem` 다운로드 (**재발급 불가!**) |
| 스토리지 | 20 GiB (gp3) |

<div class="callout warning">
<div class="callout-title">비용 주의</div>
실습이 끝나면 인스턴스를 <b>중지 또는 종료</b>하세요. 프리티어 한도를 넘으면 과금됩니다.
</div>

---

# 2) 보안그룹 (방화벽)

| 유형 | 포트 | 소스 | 용도 |
|------|------|------|------|
| SSH | 22 | **내 IP** (권장) / 0.0.0.0/0 | 서버 접속, GitHub Actions 배포 |
| HTTP | 80 | 0.0.0.0/0 | 서비스 접속 |
| (선택) HTTPS | 443 | 0.0.0.0/0 | 확장 과제 |

- **5432(PostgreSQL), 8000(gunicorn) 은 열지 않는다!**
- GitHub Actions 러너의 IP 는 매번 바뀜 → 실습에서는 SSH 를 0.0.0.0/0 으로 열고 **키 인증만 허용**

---

# 3) SSH 접속

```bash
# Git Bash / macOS / Linux
chmod 400 todo-api-key.pem
ssh -i todo-api-key.pem ubuntu@<EC2_PUBLIC_IP>
```

```powershell
# Windows PowerShell : 키 파일 권한 오류 시
icacls todo-api-key.pem /inheritance:r /grant:r "$($env:USERNAME):(R)"
ssh -i todo-api-key.pem ubuntu@<EC2_PUBLIC_IP>
```

```text
Welcome to Ubuntu 24.04 LTS ...
ubuntu@ip-172-31-xx-xx:~$
```

---

# 4) 서버 초기 설정 : server_setup.sh

```bash
# Docker Engine + Compose 플러그인 설치 (공식 설치 스크립트)
if ! command -v docker > /dev/null; then
    curl -fsSL https://get.docker.com | sudo sh
fi

# sudo 없이 docker 명령을 쓸 수 있도록
sudo usermod -aG docker "$USER"

# 메모리 1GB 인스턴스를 위한 2GB 스왑 (메모리 부족 방지)
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
    echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab
fi

mkdir -p ~/todo-api
```

---

# 서버 설정 실행

```bash
# 내 PC 에서 스크립트를 서버로 복사
scp -i todo-api-key.pem deploy/server_setup.sh ubuntu@<EC2_IP>:~

# 서버에서 실행
ssh -i todo-api-key.pem ubuntu@<EC2_IP>
bash server_setup.sh
exit                              # ⚠️ 그룹 권한 적용을 위해 재접속 필수
```

```bash
ssh -i todo-api-key.pem ubuntu@<EC2_IP>
docker run --rm hello-world       # "Hello from Docker!" 확인
docker compose version
```

---

# 5) 운영용 compose : db

`deploy/docker-compose.prod.yml`

```yaml
name: todo-api

services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped                 # 서버 재부팅 시 자동 시작
    environment:
      POSTGRES_DB: ${POSTGRES_DB:?POSTGRES_DB 를 .env 에 설정하세요}
      POSTGRES_USER: ${POSTGRES_USER:?POSTGRES_USER 를 .env 에 설정하세요}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?POSTGRES_PASSWORD 를 .env 에 설정하세요}
    # 운영 DB 포트는 외부에 공개하지 않는다 (ports 없음)
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
```

> `${VAR:?메시지}` : 값이 없으면 **실행 전에 오류** → 빈 비밀번호로 뜨는 사고 방지

---

# 🛠 TODO 1 : 운영용 compose : web

```yaml
  web:
    image: ${IMAGE:?IMAGE 를 .env 에 설정하세요}:${IMAGE_TAG:-latest}
    restart: unless-stopped
    env_file: .env
    environment:
      DJANGO_SETTINGS_MODULE: config.settings.prod
      POSTGRES_HOST: db
      POSTGRES_PORT: "5432"
    expose:
      - "8000"                   # 내부 네트워크에만 공개 (nginx 만 접근)
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c",
             "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')"]
```

- 서버에서 **빌드하지 않고** GHCR 의 이미지를 받아서 실행 (`build` 없음)

---

# 🛠 TODO 2 : 운영용 compose : nginx

```yaml
  nginx:
    image: nginx:1.27-alpine
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      web:
        condition: service_healthy

volumes:
  pgdata:
```

| | `ports` | `expose` |
|---|---|---|
| 외부(인터넷) 접근 | ✅ | ❌ |
| 컨테이너 간 접근 | ✅ | ✅ |

---

# nginx.conf

```nginx
upstream django {
    server web:8000;               # compose 서비스 이름으로 접근
}

server {
    listen 80;
    server_name _;
    client_max_body_size 10M;

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

- `Host` 헤더 전달 → Django 의 `ALLOWED_HOSTS` 검사에 사용

---

# 6) 서버의 .env (비밀값)

`deploy/.env.prod.example` → 서버 `~/todo-api/.env`

```bash
DJANGO_SECRET_KEY=change-me-to-a-long-random-string
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,<EC2_PUBLIC_IP>
DJANGO_CSRF_TRUSTED_ORIGINS=http://<EC2_PUBLIC_IP>

POSTGRES_DB=todo_db
POSTGRES_USER=todo_user
POSTGRES_PASSWORD=change-me-strong-password

IMAGE=ghcr.io/<github-id-소문자>/todo-api
# IMAGE_TAG, PREVIOUS_IMAGE_TAG 는 deploy.sh 가 자동으로 추가
```

```bash
# 서버에서 랜덤 키 생성
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
nano ~/todo-api/.env && chmod 600 ~/todo-api/.env
```

---

# 비밀값은 어디에 두나?

| 비밀값 | 위치 | 이유 |
|--------|------|------|
| `DJANGO_SECRET_KEY`, DB 비밀번호 | **서버 `.env`** | 앱 실행 시에만 필요 |
| SSH 키, 서버 주소 | **GitHub Secrets** | 배포(Actions)에서만 필요 |
| GHCR 토큰 | `GITHUB_TOKEN` (자동 발급) | 매 실행마다 새로 발급, 자동 만료 |

<div class="callout warning">
<div class="callout-title">절대 금지</div>
비밀값을 코드, Dockerfile, 이미지, 커밋, 슬랙 메시지에 넣지 않기.
<code>localhost</code> 는 헬스체크용으로 <code>ALLOWED_HOSTS</code> 에 꼭 포함하세요.
</div>

---

# 7) GitHub Actions 전용 SSH 키 (권장)

개인 `.pem` 대신 **배포 전용 키**를 만들어 등록

```bash
# 내 PC 에서
ssh-keygen -t ed25519 -f deploy_key -N "" -C "github-actions-deploy"
# → deploy_key (개인키, GitHub Secret 에 등록)
# → deploy_key.pub (공개키, 서버에 등록)

# 공개키를 서버에 추가
cat deploy_key.pub | ssh -i todo-api-key.pem ubuntu@<EC2_IP> \
  "cat >> ~/.ssh/authorized_keys"

# 접속 테스트
ssh -i deploy_key ubuntu@<EC2_IP> "echo ok"
```

> 키가 유출되면 이 키만 서버에서 삭제하면 됨 (개인 키는 안전)

---

# 서버 준비 상태 확인

```bash
ssh -i todo-api-key.pem ubuntu@<EC2_IP>

docker --version && docker compose version
ls -la ~/todo-api/              # .env 존재 확인
free -h                         # Swap: 2.0Gi 확인
```

```text
-rw------- 1 ubuntu ubuntu  512 Nov 13 10:00 .env
```

- compose 파일, nginx.conf, deploy.sh 는 **Step 8-2 의 CD 가 자동으로 복사**합니다

---

# ✅ 체크포인트

- [ ] EC2 인스턴스 생성, SSH 접속 성공
- [ ] 보안그룹: 22, 80 만 허용 (5432, 8000 미개방)
- [ ] `docker run --rm hello-world` 성공 (sudo 없이)
- [ ] `~/todo-api/.env` 작성 완료 (권한 600)
- [ ] 배포 전용 SSH 키 생성 & 서버 등록

---

# 정리

- 운영 구성 : **Nginx(80) → gunicorn(8000, 내부) → PostgreSQL(내부)**
- 외부 공개 포트는 **최소한으로**
- 서버는 이미지를 **빌드하지 않고 받아서 실행**
- 비밀값은 **서버 .env** 와 **GitHub Secrets** 로 분리 관리

### 다음 시간 ▶ Step 8-2. CD – 자동 배포
