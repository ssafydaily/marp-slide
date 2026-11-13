#!/usr/bin/env bash
# 이전 배포 버전으로 되돌린다
#   사용: bash rollback.sh            → 직전 버전(PREVIOUS_IMAGE_TAG)
#         bash rollback.sh <커밋SHA>  → 지정한 버전
set -euo pipefail
cd "$(dirname "$0")"

TARGET_TAG="${1:-$(grep '^PREVIOUS_IMAGE_TAG=' .env | cut -d= -f2 || true)}"
if [ -z "$TARGET_TAG" ]; then
    echo "[ERROR] 되돌릴 버전이 없습니다. 사용법: bash rollback.sh <이미지 태그>"
    exit 1
fi

IMAGE="$(grep '^IMAGE=' .env | cut -d= -f2)"
echo "[ROLLBACK] $IMAGE:$TARGET_TAG"

# deploy.sh 를 재사용 (태그만 바꿔서 다시 배포)
IMAGE="$IMAGE" IMAGE_TAG="$TARGET_TAG" bash deploy.sh
