---
marp: true
theme: dark-plus-code
paginate: true
style: |
  
---




# 1단계: `FastAPI` import
<br>

- `FastAPI`는 API를 위한 모든 기능을 제공하는 파이썬 클래스

```python
from fastapi import FastAPI

```
> 참고
> - `FastAPI`는 `Starlette`와 `Pydantic`을 기반으로 구축된 프레임워크. 
> - `Starlette`는 웹 프레임워크로, 비동기 처리를 지원
> - `Pydantic`은 데이터 검증과 설정 관리를 위한 라이브러리.
-----------------
# 2단계: `FastAPI` 인스턴스(객체) 생성

```python
from fastapi import FastAPI

app = FastAPI()
```
- `app` 변수는 `FastAPI` 클래스의 **인스턴스**
- 모든 API를 생성하기 위한 상호작용의 주요 포인트
- `app` 객체는 API의 라우팅, 요청 처리, 응답 생성 등 다양한 기능을 제공
-----------------

# 3단계: 경로 처리 생성

## 경로

- **경로** 는 첫 번재 `/` 부터 시작하는 **URL** 의 뒷부분을 의미
- 아래와 같은 URL에서:
```
    http://localhost:8000/items/foo
```

- 경로는 다음과 같다.
```
    /items/foo
```
> 경로는 일반적으로 **엔드포인트** 혹은, **라우트** 라고 부름.

---------

## 작동(Operation)

- HTTP 메소드 중 하나를 의미

  - `GET` : 데이터 조회
  - `POST` : 데이터 생성
  - `PUT` : 데이터 수정
  - `DELETE`: 데이터 삭제
  - 그외...

---------

## 경로 처리 데코레이터 정의

```python
from fastapi import FastAPI

app = FastAPI()


@app.get('/')

```
- `@app.get("/")` 은 *FastAPI* 에게 바로 아래의 함수가 `/` 경로(URL)를 처리함을 알린다:
  - **메소드** : `get` 
  - **경로** : `/`

-------------

# 4단계: 경로 처리 함수 정의

```python
from fastapi import FastAPI

app = FastAPI()


@app.get('/')
async def root():
    pass
```

-------------

# 5단계: 콘텐츠 반환

```python
from fastapi import FastAPI

app = FastAPI()


@app.get('/')
async def root():
    return {"message": "Hello World"}
```
- `dict`, `list`, 단일값을 가진 `str`, `int` 등을 반환 가능.
- **Pydantic** 모델을 반환할 수도 있음.
- **JSON** 으로 자동 변환되는 객체들과 모델들(ORM 등을 포함해서)이 많이 있음.

-------------

# 6단계: 배포하기
한 번의 명령으로 FastAPI Cloud에 앱을 배포합니다: fastapi deploy. 🎉

FastAPI Cloud 소개¶
FastAPI Cloud는 FastAPI 뒤에 있는 동일한 작성자와 팀이 만들었습니다.

최소한의 노력으로 API를 빌드, 배포, 접근하는 과정을 간소화합니다.

FastAPI로 앱을 빌드할 때의 동일한 개발자 경험을 클라우드에 배포할 때도 제공합니다. 🎉

FastAPI Cloud는 FastAPI와 친구들 오픈 소스 프로젝트의 주요 스폰서이자 자금 제공자입니다. ✨

다른 클라우드 제공업체에 배포하기¶
FastAPI는 오픈 소스이며 표준을 기반으로 합니다. 선택한 어떤 클라우드 제공업체에도 FastAPI 앱을 배포할 수 있습니다.

클라우드 제공업체의 가이드를 따라 FastAPI 앱을 배포하세요. 














