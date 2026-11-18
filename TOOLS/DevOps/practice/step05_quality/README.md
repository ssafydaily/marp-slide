# Step 5. 코드 품질 자동화

- 슬라이드: `slides/05_code_quality.md`
- `template/` : 실습 시작 코드 / `solution/` : 완성 코드

## 실습 순서

1. `config/settings/dev.py`, `prod.py` TODO 1~4: 설정 분리
2. `pyproject.toml` TODO 5: ruff 규칙
3. `.pre-commit-config.yaml` TODO 6: ruff 훅
4. `todos/views.py` TODO 7: ruff 로 코드 정리

## 주요 명령

```bash
pip install -r requirements-dev.txt
ruff check .
ruff check --fix .
ruff format .
pre-commit install
pre-commit run --all-files
pytest
```
