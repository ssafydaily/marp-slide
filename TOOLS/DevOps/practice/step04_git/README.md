# Step 4. Git & GitHub 협업

- 슬라이드: `slides/04_git_github.md`
- `template/` : 실습 시작 코드 / `solution/` : 완성 코드

## 실습 순서

1. GitHub 저장소 생성 & push
2. Issue 생성 → `feature/search` 브랜치
3. `tests/test_search.py` 실패 확인 → `todos/views.py` 검색 TODO 구현
4. `.github/` PR·Issue 템플릿 작성
5. PR 생성 → 리뷰 → Merge (Closes #이슈)

## 주요 명령

```bash
git switch -c feature/search
pytest tests/test_search.py
git push -u origin feature/search
```
