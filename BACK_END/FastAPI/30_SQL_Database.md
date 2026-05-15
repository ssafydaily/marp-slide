---
marp: true
theme: default
paginate: true
style: |
  section {
    padding: 1.5rem; /* 원하는 여백 값으로 조절 */
  }
  h1 {
    font-size: 1.5rem;
    position: absolute;
    left: 50px;
    top: 50px;
  }
  h2 {
    font-size: 1.3rem;
  }
  h3 {
    font-size: 1rem;
  }
---

# SQL DB

- **FastAPI** 에서 *SQL(관계형) DB* 사용은 필수가 아나지만, 원하는 어떤 DB든 사용 가능하다.

- [SQLModel](https://sqlmodel.tiangolo.com/) 을 사용
  - *SQLModel* 은 [*SQLAlchemy*](https://www.sqlalchemy.org/)와 *Pydantic* 기반으로 구축
  - **FastAPI** 에플리케이션에 적용하기 위해 **FastAPI** 제작자가 작성

> [참고]
> - 다른 SQL 또는 NoSQL DB 라이브러리도 사용할 수 있다. (일부는 *ORMs*이라고 부름), 

----------

# SQL DB(cont.)

- SQLModel은 SQLAlchemy를 기반으로 하므로, SQLAlchemy가 지원하는 DB들 사용 가능
  - PostgreSQL, MySQL, SQLite, Oracle, Microsoft SQL Server 등.

> - 이후 내용에서는 **SQLite** 사용
> - SQLite는 단일 파일을 사용하고 Python에서 통합 지원하기 때문입니다. 

> 팁
> - 프론트엔드와 다양한 도구를 포함해서 FastAPI와 PostgreSQL을 포함한 공식 프로젝트 생성기 
> - https://github.com/fastapi/full-stack-fastapi-template

------------

# SQLModel 설치

- 가상환경 생성 및 활성화하고 설치

```bash
$ pip install sqlmodel
```

---------

# 모델 생성
<br>

- `SQLModel`을 가져와서 DB 모델을 생성

```python
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int = Field(default=None, index=True)
    secret_name: str
```

- `Hero` 클래스는 내부적으로 **Pydantic 모델**
- `table=True` : *테이블 모델*이며, SQL DB의 테이블
- `Field(primary_key=True)` : 기본키, [기본키에 대한 SQLModel의 문서](https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#primary-key-id)
- `Field(index=True)`: **SQL 인덱스** 생성하도록 지시. 조회 속도를 빠르게 함.

-----------

# 엔진 생성하기

- **SQLModel**의 engine : 내부적으로 *SQLAlchemy engine*이고, DB에 대한 연결을 유지하는 역할

- 코드 전체에서 동일한 DB에 연결하기 위해 **단일** engine 객체 사용

```python
sqlite_file_name = 'database.db'
sqlite_url = f'sqlite:///{sqlite_file_name}'

connect_args = {'check_same_thread': False}
engine = create_engine(sqlite_url, connect_args=connect_args)
```

- `check_same_thread=False` : 여러 스레드에서 동일한 SQLite DB를 사용
- **하나의 단일 요청**이 **둘 이상의 스레드를 사용**할 수 있기 때문에 필요

-----------

# 테이블 생성

-  `SQLModel.metadata.create_all(engine)`을 사용하여 모든 테이블 모델의 테이블을 생성하는 함수를 추가

```python
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

-------------

# 세션 의존성 생성하기

- **Session**은 메모리에 객체를 저장하고 데이터에 필요한 모든 변경 사항을 추적한 후, engine을 통해 DB와 통신

- `yield`를 사용해 FastAPI의 의존성을 생성하여 각 요청마다 새로운 Session을 제공
  - 요청당 하나의 세션만 사용되도록 보장

- 이 의존성을 사용하는 나머지 코드를 간소화하기 위해 `Annotated` 의존성 `SessionDep`을 생성

```python
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
```

--------------

# 시작 시 DB 테이블 생성

- 애플리케이션 시작 시 DB 테이블 생성

```python
app = FastAPI()

@app.on_event('startup')
def on_startup():
    create_db_and_tables()
```

- 애플리케이션 시작 이벤트 시 테이블 생성
- 프로덕션 환경에서는 애플리케이션을 시작하기 전에 실행되는 마이그레이션 스크립트를 사용할 가능성이 높음

> SQLModel은 Alembic을 감싸는 마이그레이션 유틸리티를 제공할 예정. 현재 Alembic을 직접 사용.

-------------
# Hero 생성

```python
@app.post('/heros/')
def create_hero(hero: Hero, session: SessionDep) -> Hero:
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero
```
- `SessionDep` 의존성(Session)을 사용하여 새로운 `Hero`를 `Session` 인스턴스에 추가
- DB에 변경 사항을 **커밋**하고, hero 데이터의 최신 상태를 갱신한 다음 반환

------------
# Heroes 조회

- `select()`를 사용하여 DB에서 `Hero`를 조회
- *Pagination*을 위해 `limit`과 `offset`을 포함

```python
@app.get('/heroes/')
def read_heroes(
    session: SessionDep, 
    offset: 
    int = 0, limit: Annotated[int, Query(le=1000)] = 100,
) -> list[Hero]:        # 반환형 주의

    heroes = session.exec(select(Hero).offset(offset).limit(limit).all())
    return heroes
```

----------

# 단일 Hero 조회

```python
@app.get('/heroes/{hero_id}/')
def read_hero(
    hero_id: int,
    session: SessionDep,     
) -> list[Hero]:      # 반환형 주의

    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail='Hero Not Found')
    return hero
```

--------------------

# Hero 삭제

```python
@app.delete('/heroes/{hero_id}/')
def delete_hero(
    hero_id: int,
    session: SessionDep,     
) -> list[Hero]:

    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail='Hero Not Found')
    session.delete(hero)
    session.commit()
    return hero
```

------------------

# 여러 모델로 애플리케이션 업데이트
- 이전 버전은 클라이언트가 생성할 Hero의 id를 결정할 수 있다. 
- DB에 이미 할당되어 있는 id를 변경해선 안된다.
- hero에 대한 `secret_name`을 생성하지만, 이 값을 어디에서나 반환하고 있다.


--------------
## 기본 클래스 - HeroBase
- 모든 모델에서 공유되는 필드를 가진 `HeroBase` 모델
  - `name`
  - `age`

```python
class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
```

----------------
## Hero
- 실제 테이블 모델인 `Hero` 생성
- 다른 모델에는 포함되지 않는 추가 필드를 포함
  - `id`
  - `secret_name`

```python
class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)

class Hero(HeroBase, table=True):
  id: int | None = Field(default=None, primary_key=True)
  secret_name: str

```

----------------
## HeroPublic - 공개 데이터 모델

- **API 클라이언트**에 반환되는 모델입니다.
- `HeroPublic`은 `HeroBase`와 동일한 필드를 가지므로, `secret_name`은 포함하지 않음.
- 또한, `id: int`를 다시 선언. API 클라이언트와 계약을 맺어 id가 항상 존재하며 항상 int 타입이라는 것을 보장(None이 될 수 없음)
- 필드: `id`, `name`, `age`

```python
class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)

class HeroPublic(HeroBase):
    id: int
```
- `HeroPublic`은 `table=True` 가 없다.

------------

## HeroCreate - 생성용 데이터 모델

- 클라이언트로부터 받은 데이터를 검증하는 역할
- `HeroCreate`는 `HeroBase`와 동일한 필드를 가지며, `secret_name`도 포함합니다.
- 클라이언트가 새 `hero`를 생성할 때 `secret_name`을 보내면, 데이터베이스에 저장되지만, 그 비밀 이름은 API를 통해 클라이언트에게 반환되지 않는다.
> [참고]
> - 이 방식은 비밀번호를 처리하는 방법과 동일
> - 비밀번호 값을 저장하기 전에 **해싱**하여 저장

```python
class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)

class HeroCreate(HeroBase):
    secret_name: str
```

--------------------

## HeroUpdate - 수정용 모델

- `HeroUpdate`는 `hero`를 생성할 때 필요한 동일한 필드들을 가지지만, 모든 필드가 선택적(기본값이 있음)입니다.
- 수정 시 필요한 필드만 보낸다.
- 모든 필드가 실제로 변경되므로(None을 포함, 기본값도 None), 필드를 다시 선언
  - `HeroBase`를 상속할 필요 없음. 

```python
class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)

class HeroUpdate(HeroBase):
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None
```

-------------------

## HeroCreate로 생성 / HeroPublic 반환

```python
@app.post('/heros/', response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: SessionDep):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    sess.refresh(db_hero)
    return db_hero
```

- 반환 타입 어노테이션 `-> HeroPublic` 대신 `response_model=HeroPublic`을 사용
- 반환하는 값이 실제로 `HeroPublic`이 아님
- `-> HeroPublic`으로 선언하면, 에디터와 린터에서 `HeroPublic` 대신 `Hero`를 반환해야 한다고 지적함
- `response_model` 작성으로 **FastAPI**가 처리하도록 한다

-------

## HeorPublic 으로 조회
```python
# 전체 조회                          ################
@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes
```
```python
# 단일 조회                                   ##########
@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero
```

-----------

## HeroUpdate로 수정

- `HTTP PATCH` 메소드
- 클라이언트가 보낸 데이터가 담긴 `dict`를 가져온다.
- 클라이언트가 보낸 데이터만 포함, 기본값이라 포함된 값은 제외
- 이를 위해 `exclude_unset=True`를 사용
- `hero_db.sqlmodel_update(hero_data)`를 사용하여 `hero_data`의 데이터로 `hero_db`를 업데이트

----------------

## update 

```python
@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero: HeroUpdate, session: SessionDep):

    hero_db = session.get(Hero, hero_id)

    if not hero_db:
        raise HTTPException(status_code=404, detail="Hero not found")
    
    hero_data = hero.model_dump(exclude_unset=True)

    hero_db.sqlmodel_update(hero_data)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)

    return hero_db
```

-----------------------

## Hero 삭제
- 삭제는 이전과 거의 동일

```python
@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
  
    hero = session.get(Hero, hero_id)

    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    session.delete(hero)
    session.commit()
    return {"ok": True}
```