#!/usr/bin/env bash
# 서버에서 실행되는 배포 스크립트
#   사용: IMAGE=ghcr.io/<owner>/todo-api IMAGE_TAG=<커밋SHA> bash deploy.sh
set -euo pipefail
cd "$(dirname "$0")"

COMPOSE="docker compose -f docker-compose.prod.yml"

# .env 의 KEY=VALUE 를 갱신 (없으면 추가)
set_env() {
    if grep -q "^$1=" .env; then
        sed -i "s|^$1=.*|$1=$2|" .env
    else
        echo "$1=$2" >> .env
    fi
}

if [ ! -f .env ]; then
    echo "[ERROR] .env 파일이 없습니다. .env.prod.example 을 참고해 ~/todo-api/.env 를 만드세요."
    exit 1
fi

IMAGE="${IMAGE:?IMAGE 환경변수가 필요합니다}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# 1) GHCR 로그인 (private 이미지 pull 용, 토큰이 전달된 경우에만)
if [ -n "${GHCR_TOKEN:-}" ]; then
    echo "$GHCR_TOKEN" | docker login ghcr.io -u "${GHCR_USER:?GHCR_USER 가 필요합니다}" --password-stdin
fi

# 2) 새 이미지 받기 — 실패하면(태그 없음, 권한 오류) .env 를 건드리지 않고 중단
#    (셸에서 export 한 값이 .env 보다 우선 적용된다)
export IMAGE IMAGE_TAG
echo "[DEPLOY] $IMAGE:$IMAGE_TAG"
$COMPOSE pull web

# 3) 롤백을 위해 현재 태그를 PREVIOUS_IMAGE_TAG 로 기록한 뒤 새 태그 저장
CURRENT_TAG="$(grep '^IMAGE_TAG=' .env | cut -d= -f2 || true)"
if [ -n "$CURRENT_TAG" ] && [ "$CURRENT_TAG" != "$IMAGE_TAG" ]; then
    set_env PREVIOUS_IMAGE_TAG "$CURRENT_TAG"
fi
set_env IMAGE "$IMAGE"
set_env IMAGE_TAG "$IMAGE_TAG"

# 4) 컨테이너 재기동 (마이그레이션은 web 컨테이너 entrypoint 가 수행)
$COMPOSE up -d --remove-orphans

# 5) 헬스체크: Nginx 를 거쳐 /health/ 가 200 을 반환할 때까지 대기 (최대 90초)
for i in $(seq 1 30); do
    if curl -fsS http://localhost/health/ > /dev/null 2>&1; then
        echo "[OK] 배포 성공: $IMAGE:$IMAGE_TAG"
        docker image prune -f > /dev/null
        exit 0
    fi
    echo "[WAIT] 헬스체크 대기 중... ($i/30)"
    sleep 3
done

echo "[ERROR] 헬스체크 실패. 로그 확인: $COMPOSE logs --tail=100 web"
echo "        이전 버전으로 되돌리기: bash rollback.sh"
exit 1
