docker-compose를 쓰신다면 훨씬 간단하게 해결됩니다. `docker-compose.yml`의 `volumes` 항목에 추가하면 됩니다.

## 방법 1: Named Volume 사용 (Windows에서 가장 추천)

Windows 경로 문제를 신경 쓸 필요가 없어서 가장 편합니다.

```yaml
services:
  jupyter:
    image: your-image
    ports:
      - "8888:8888"
    volumes:
      - jupyter_config:/root/.jupyter
      - ./notebooks:/home/notebooks   # 작업 파일용 (선택)

volumes:
  jupyter_config:
```

`docker-compose up` 하면 Docker가 자체 관리 영역(보통 `C:\ProgramData\docker\volumes\...` 또는 WSL2 내부)에 볼륨을 만들어줍니다. 폴더를 미리 만들 필요가 없습니다.

볼륨 위치 확인은:
```bash
docker volume inspect <프로젝트명>_jupyter_config
```

## 방법 2: 상대 경로 바인드 마운트

`~/jupyter_config` 같은 홈 디렉토리 경로 대신, **compose 파일이 있는 위치 기준 상대 경로**를 쓰면 폴더가 없어도 자동으로 생성됩니다.

```yaml
services:
  jupyter:
    image: your-image
    ports:
      - "8888:8888"
    volumes:
      - ./jupyter_config:/root/.jupyter
      - ./notebooks:/home/notebooks
```

`docker-compose up` 실행 시 `docker-compose.yml`이 있는 폴더 안에 `jupyter_config` 폴더가 없으면 Docker가 자동으로 만들어줍니다 (Docker Desktop이 파일 공유 권한을 가진 드라이브라면).

> ⚠️ 주의: Windows에서 바인드 마운트 시 파일 공유(File Sharing) 설정이 안 되어 있으면 오류가 날 수 있습니다. Docker Desktop → Settings → Resources → File Sharing에서 해당 드라이브가 공유되어 있는지 확인하세요.

## 방법 3: 절대 경로 지정 (홈 폴더를 굳이 쓰고 싶다면)

폴더가 없어서 문제라면, 먼저 폴더를 만들거나 compose가 자동 생성하게 두면 됩니다.

```yaml
services:
  jupyter:
    image: your-image
    volumes:
      - C:/Users/사용자명/jupyter_config:/root/.jupyter
```

Windows 경로는 `C:/Users/...` 처럼 슬래시(`/`)를 쓰는 게 안전합니다 (백슬래시 `\` 대신).

## 정리 및 추천

| 방법 | 장점 | 단점 |
|---|---|---|
| Named Volume | 경로 문제 없음, Windows에 가장 안전 | 호스트에서 직접 파일 보기 불편 |
| 상대 경로 바인드 | 파일 직접 확인/편집 쉬움, 자동 생성됨 | Docker Desktop 파일 공유 설정 필요 |
| 절대 경로 바인드 | 경로 명확 | 사용자마다 경로 달라 이식성 낮음 |

**Windows에서 docker-compose를 쓰신다면 방법 1(Named Volume)이나 방법 2(상대 경로)**를 추천합니다. 둘 다 폴더를 미리 만들 필요 없이 `docker-compose up` 한 번으로 자동 처리됩니다.

설정 후 컨테이너 내부에서 만들어진 실제 파일이 잘 저장되는지 확인하려면:

```bash
docker-compose exec jupyter find /root/.jupyter -name "*.jupyterlab-settings"
```