# Step 8. 서버 배포 & CD

- 슬라이드: `slides/08-1_server_setup.md, 08-2_cd.md`
- `template/` : 실습 시작 코드 / `solution/` : 완성 코드

## 실습 순서

1. EC2 생성 → `deploy/server_setup.sh` 실행
2. 서버 `~/todo-api/.env` 작성 (`deploy/.env.prod.example` 참고)
3. GitHub Secrets: `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`
4. `.github/workflows/cd.yml` TODO 1~6
5. `deploy/docker-compose.prod.yml` TODO 1~2, `deploy/deploy.sh` TODO 1~3
6. main 에 merge → 자동 배포 → `http://<EC2_IP>/health/` 확인

## 주요 명령

```bash
# 서버에서
cd ~/todo-api
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=100 web
bash rollback.sh
```
