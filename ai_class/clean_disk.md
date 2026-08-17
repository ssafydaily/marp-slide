# 디스크 정리

- 전에 프로님께서 공유하신 클린 방식 가이드 PDF는 윈도우 기준으로 설명
- WSL2 Ubuntu 내부에서는 경로가 다릅니다.

> 해당 경로 파일들을 삭제하시면 되겠습니다 :grinning: 

## 04.Ch0_3_클린_방식_가이드

| **항목** | **윈도우 경로 (예시)** | **우분투 (Ubuntu) 경로** |
| --- | --- | --- |
| **프로젝트 데이터** | `.\data` | `./data` (현재 작업 디렉토리 기준) |
| **모델 가중치 파일** | `*.pt`,`*.pth`,`*.ckpt`,`*.safetensors`,`*.bin` 등 | 동일 (확장자 기반 검색 필요) |
| **Hugging Face 캐시** | `\.cache\huggingface` | **`~/.cache/huggingface`** |
| **HF 로컬 데이터** | `...\AppData\Local\huggingface` | **`~/.local/share/huggingface`** (또는 위와 통합) |
| **PyTorch 캐시** | `\.cache\torch` | **`~/.cache/torch`** |
| **pip 캐시 삭제** | `python -m pip cache purge` | **`python3 -m pip cache purge`** |