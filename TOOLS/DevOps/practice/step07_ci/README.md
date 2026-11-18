# Step 7. CI - GitHub Actions

- 슬라이드: `slides/07_ci.md`
- `template/` : 실습 시작 코드 / `solution/` : 완성 코드

## 실습 순서

1. `.github/workflows/ci.yml` TODO 1~9
2. PR 을 올려 Actions 결과 확인
3. 일부러 테스트를 깨뜨려 실패 시나리오 확인
4. Branch protection 에 CI 상태체크 필수 지정

## 주요 명령

```bash
git switch -c ci/setup
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions workflow"
git push -u origin ci/setup
```
