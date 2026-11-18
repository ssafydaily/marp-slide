---
marp: true
theme: dark-plus-code
paginate: true
style: |
  /* 첫 페이지(lead): 어두운 배경에서 잘 보이도록 밝은 글자색 */
  section.lead h1 {
    color: #ffffff;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  }
  section.lead h2 {
    color: #e3f2fd;
    background-color: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.3);
    opacity: 1;
  }
  section.lead p {
    color: #cbd5e1;
    opacity: 1;
  }
---

<!-- _class: lead -->

# Step 4. Git & GitHub 협업

## Issue → Branch → TDD → PR → Merge

---

# 학습 목표

- **GitHub Flow** 브랜치 전략으로 기능을 개발한다
- 의미 있는 **커밋 메시지** 규칙을 적용한다
- Issue / PR **템플릿**으로 협업 형식을 통일한다
- **Branch protection** 으로 main 브랜치를 보호한다
- 실습: `?search=` 검색 기능을 TDD + PR 로 추가한다

📁 실습 폴더: `practice/step04_git/template`

---

# DevOps 에서 Git 의 역할

- **Single Source of Truth** : 코드 · 설정 · 인프라 정의 모두 Git 에
- 모든 변경에 **누가 · 언제 · 왜** 가 기록됨
- PR 은 자동화(CI)와 사람(리뷰)이 만나는 **품질 관문**
- main 에 merge = **배포 트리거** (Step 8)

---

# GitHub Flow

```
main     ───●────────────────────●──────────────●───▶  (항상 배포 가능)
             \                  / merge          \
feature/search ●──●──●── PR ──●                   \
               test  impl  review                  feature/...
```

1. `main` 에서 **기능 브랜치** 생성
2. 작은 단위로 커밋
3. **Pull Request** 생성 → 리뷰 + 자동 테스트
4. 승인되면 `main` 에 merge → 브랜치 삭제

> 규칙은 단 하나: **main 은 언제나 배포 가능한 상태**

---

# 브랜치 이름 규칙

| 접두어 | 용도 | 예시 |
|--------|------|------|
| `feature/` | 새 기능 | `feature/search` |
| `fix/` | 버그 수정 | `fix/todo-ordering` |
| `refactor/` | 리팩터링 | `refactor/settings-split` |
| `docs/` | 문서 | `docs/readme` |
| `ci/` | CI/CD 설정 | `ci/github-actions` |

---

# 커밋 메시지 규칙 (Conventional Commits)

```text
<type>: <요약>   (50자 이내, 명령형)

<본문: 무엇을, 왜>  (선택)
```

| type | 의미 |
|------|------|
| `feat` | 새 기능 |
| `fix` | 버그 수정 |
| `test` | 테스트 추가/수정 |
| `refactor` | 동작 변경 없는 코드 개선 |
| `docs` / `chore` / `ci` | 문서 / 기타 / CI |

```bash
git commit -m "test: add search API tests"
git commit -m "feat: filter todos by title with ?search="
```

---

# 1) GitHub 저장소 만들기

```bash
# step04_git/template 내용을 새 폴더로 복사한 뒤
cd todo-api
git init -b main
git add .
git commit -m "chore: initial project setup"

# GitHub 에서 빈 저장소(todo-api) 생성 후
git remote add origin https://github.com/<내아이디>/todo-api.git
git push -u origin main
```

<div class="callout warning">
<div class="callout-title">push 전 확인</div>
<code>git status</code> 에 <code>.env</code> 가 보이면 안 됩니다! <code>.gitignore</code> 를 확인하세요.
</div>

---

# 2) Issue 로 작업 정의 (Plan)

GitHub → **Issues → New issue → 기능 요청**

```markdown
[Feature] 할 일 제목 검색

## 배경
할 일이 많아지면 원하는 항목을 찾기 어렵다.

## 요구사항
- [ ] GET /api/todos/?search=키워드 로 제목 검색
- [ ] 대소문자 구분 없음
- [ ] is_done 필터와 함께 사용 가능

## 완료 조건
- [ ] tests/test_search.py 통과
```

→ 이슈 번호 확인 (예: **#1**)

---

# 3) 기능 브랜치 생성

```bash
git switch main
git pull
git switch -c feature/search
```

```bash
git branch
# * feature/search
#   main
```

---

# 4) 🔴 테스트 먼저 : test_search.py

```python
@pytest.fixture
def sample_todos():
    Todo.objects.create(title="Django 공부")
    Todo.objects.create(title="장보기")
    Todo.objects.create(title="django 테스트 작성")


def test_search_by_title_is_case_insensitive(api_client, sample_todos):
    response = api_client.get(LIST_URL, {"search": "DJANGO"})

    titles = {item["title"] for item in response.json()}
    assert titles == {"Django 공부", "django 테스트 작성"}


def test_search_and_filter_combined(api_client):
    ...  # search + is_done 함께 사용
```

```bash
pytest tests/test_search.py     # 2 failed  → 커밋
git add tests/test_search.py && git commit -m "test: add search API tests"
```

---

# 5) 🟢 구현 : 검색 필터

`todos/views.py`

```python
    def get_queryset(self):
        queryset = super().get_queryset()

        is_done = self.request.query_params.get("is_done")
        if is_done is not None:
            queryset = queryset.filter(is_done=is_done.lower() == "true")

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(title__icontains=search.strip())

        return queryset
```

```bash
pytest                          # 26 passed
git commit -am "feat: filter todos by title with ?search="
```

---

# 6) PR 템플릿 : .github/PULL_REQUEST_TEMPLATE.md

```markdown
## 개요
<!-- 이 PR 이 무엇을, 왜 변경하는지 -->

## 관련 이슈
Closes #

## 변경 사항
-

## 테스트
- [ ] 새 기능/버그에 대한 테스트를 먼저 작성했습니다 (TDD)
- [ ] 로컬에서 `pytest` 가 모두 통과합니다
- [ ] 마이그레이션이 필요한 경우 포함했습니다

## 리뷰 포인트
```

> 이 파일이 있으면 PR 작성 시 **자동으로 본문이 채워짐**

---

# Issue 템플릿 : .github/ISSUE_TEMPLATE/

```markdown
---
name: 버그 리포트
about: 버그를 보고합니다
title: "[Bug] "
labels: bug
---

## 현상
## 재현 방법
1.
## 기대 결과
## 실제 결과 / 에러 메시지
## 환경
```

- `feature_request.md`, `bug_report.md` 두 가지 제공
- New issue 클릭 시 **템플릿 선택 화면**이 나타남

---

# 7) Push & Pull Request

```bash
git add .github
git commit -m "docs: add PR and issue templates"
git push -u origin feature/search
```

GitHub → **Compare & pull request**

- base: `main` ← compare: `feature/search`
- 본문에 **`Closes #1`** → merge 시 이슈 자동 종료
- Reviewer 지정 (팀원)

---

# 코드 리뷰 가이드

<div class="cols">
<div>

### 리뷰어
- 요구사항을 만족하는가?
- **테스트가 있는가?**
- 이해하기 쉬운가?
- 질문형 코멘트:
  "여기서 `strip()` 이 필요한 이유는?"

</div>
<div>

### 작성자
- PR 은 **작게** (300줄 이하 권장)
- 리뷰 코멘트에 답변 / 수정 커밋
- 리뷰 = 사람이 아닌 **코드**에 대한 의견

</div>
</div>

---

# 8) Merge & 정리

GitHub 에서 **Squash and merge** (커밋을 하나로 정리) → **Delete branch**

```bash
git switch main
git pull                      # 최신 main 받기
git branch -d feature/search  # 로컬 브랜치 삭제
```

| Merge 방식 | 특징 |
|------------|------|
| Create a merge commit | 모든 커밋 + merge 커밋 유지 |
| **Squash and merge** | PR 을 커밋 1개로 → main 기록이 깔끔 |
| Rebase and merge | 커밋을 main 위에 일렬로 |

---

# 9) Branch protection : main 보호

GitHub → **Settings → Branches → Add branch ruleset** (또는 classic rule)

- ✅ Require a pull request before merging
  - ✅ Require approvals (1명)
- ✅ Require status checks to pass ← **Step 7 CI 와 연결**
- ✅ Block force pushes

<div class="callout info">
<div class="callout-title">효과</div>
누구도 main 에 직접 push 할 수 없고, 리뷰 + 테스트 통과 후에만 merge 됩니다.
</div>

---

# 충돌(Conflict) 해결

```bash
git switch feature/search
git pull origin main          # main 의 최신 변경을 가져옴
# CONFLICT (content): Merge conflict in todos/views.py
```

```text
<<<<<<< HEAD
        search = self.request.query_params.get("search")
=======
        keyword = self.request.query_params.get("q")
>>>>>>> main
```

1. 표시된 부분을 직접 수정 (마커 삭제)
2. `pytest` 로 확인
3. `git add` → `git commit` → `git push`

---

# ✅ 체크포인트

- [ ] GitHub 저장소에 push 완료 (`.env` 미포함)
- [ ] Issue #1 생성 → `feature/search` 브랜치
- [ ] 테스트 커밋 → 구현 커밋 (TDD 순서가 기록에 남음)
- [ ] PR 템플릿으로 PR 작성 → `Closes #1` 로 merge
- [ ] main 브랜치 보호 규칙 설정

---

# 정리

- **GitHub Flow** : main 은 항상 배포 가능, 작업은 브랜치 + PR
- 커밋 메시지 규칙으로 **변경 이력을 읽기 쉽게**
- Issue / PR 템플릿 = 팀의 **협업 형식을 코드로**
- Branch protection + CI = 사람의 실수를 **시스템이 막는다**

### 다음 시간 ▶ Step 5. 코드 품질 자동화
