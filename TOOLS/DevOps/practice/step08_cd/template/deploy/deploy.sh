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

# 2) TODO 1: IMAGE, IMAGE_TAG 를 export 하고 새 이미지를 pull 하세요.
#    (pull 이 실패하면 set -e 에 의해 .env 를 바꾸기 전에 중단됩니다)
#   export IMAGE IMAGE_TAG
#   $COMPOSE pull web

# 3) 롤백을 위해 현재 태그를 PREVIOUS_IMAGE_TAG 로 기록한 뒤 새 태그 저장
CURRENT_TAG="$(grep '^IMAGE_TAG=' .env | cut -d= -f2 || true)"
if [ -n "$CURRENT_TAG" ] && [ "$CURRENT_TAG" != "$IMAGE_TAG" ]; then
    set_env PREVIOUS_IMAGE_TAG "$CURRENT_TAG"
fi
set_env IMAGE "$IMAGE"
set_env IMAGE_TAG "$IMAGE_TAG"

# 4) TODO 2: 컨테이너를 재기동하세요.
#   $COMPOSE up -d --remove-orphans

# 5) TODO 3: curl 로 http://localhost/health/ 를 최대 30번(3초 간격) 확인하고
#    성공하면 "[OK] 배포 성공" 출력 후 exit 0

echo "[ERROR] 헬스체크 실패. 로그 확인: $COMPOSE logs --tail=100 web"
echo "        이전 버전으로 되돌리기: bash rollback.sh"
exit 1
