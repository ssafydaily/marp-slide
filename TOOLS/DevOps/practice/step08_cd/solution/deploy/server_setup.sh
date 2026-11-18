#!/usr/bin/env bash
# EC2(Ubuntu) 최초 1회 실행: Docker 설치 및 배포 폴더 준비
#   사용: bash server_setup.sh   (실행 후 반드시 로그아웃 → 재접속)
set -euo pipefail

# 1) Docker Engine + Compose 플러그인 설치 (공식 설치 스크립트)
if ! command -v docker > /dev/null; then
    curl -fsSL https://get.docker.com | sudo sh
fi

# 2) sudo 없이 docker 명령을 쓸 수 있도록 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker "$USER"

# 3) 메모리 1GB 인스턴스(t2/t3.micro)를 위한 2GB 스왑 (메모리 부족으로 컨테이너가 죽는 것 방지)
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab
fi

# 4) 배포 폴더 준비
mkdir -p ~/todo-api

echo "[OK] 완료! exit 로 로그아웃 후 다시 접속하고 docker run hello-world 로 확인하세요."
