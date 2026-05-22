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


## WSGI vs ASGI 

---

### 1. 탄생 배경

**WSGI** (Web Server Gateway Interface) — PEP 333, 2003년
- 당시 Python 웹 프레임워크(Django, Flask 등)마다 웹 서버 연동 방식이 제각각
- **표준 인터페이스**를 만들어 "어떤 프레임워크든 어떤 서버에서도 동작"하도록

**ASGI** (Asynchronous Server Gateway Interface) — 2019년
- 웹소켓, HTTP/2, 실시간 스트리밍 수요 증가
- WSGI는 구조적으로 `async/await` 지원 불가 → ASGI로 진화
- WSGI의 정신적 후계자이자 상위 호환

---

### 2. 핵심 개념과 원리

#### WSGI 동작 원리

```
클라이언트 요청
      ↓
 웹 서버 (Nginx)
      ↓
 WSGI 서버 (Gunicorn)         ← 요청을 Python 객체로 변환
      ↓
 WSGI App (Django/Flask)
      ↓  callable(environ, start_response)
 응답 반환 (Response)
      ↓
 클라이언트
```

-----------

WSGI 앱의 본질은 **하나의 콜러블(callable)**:

```python
# WSGI 앱의 가장 기본 형태
def application(environ, start_response):
    # environ : HTTP 요청 정보 담긴 딕셔너리
    # start_response : 응답 헤더 전송 콜백
    
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [b'Hello, World!']
    # 반드시 동기적으로 즉시 반환해야 함
```

- 요청 1개 → 처리 완료 → 응답, 이 사이클이 **블로킹(blocking)**
- 처리 중엔 해당 워커가 다른 요청 처리 **불가**

```
워커 1: [요청A ====처리중====] [요청D =====]
워커 2: [요청B ====처리중====] [요청E =====]
워커 3: [요청C ====처리중====] [요청F =====]
          ↑ DB 기다리는 동안도 워커가 점유됨
```

-----------

#### ASGI 동작 원리

```
클라이언트 요청
      ↓
 웹 서버 (Nginx)
      ↓
 ASGI 서버 (Uvicorn)          ← 이벤트 루프 위에서 동작
      ↓
 ASGI App (FastAPI/Django 4+)
      ↓  async callable(scope, receive, send)
 비동기 응답 / 스트리밍 / 웹소켓
      ↓
 클라이언트
```

----------

ASGI 앱의 본질은 **3개의 인자를 받는 async callable**:

```python
# ASGI 앱의 가장 기본 형태
async def application(scope, receive, send):
    # scope  : 연결 정보 (HTTP/WebSocket/Lifespan 타입 포함)
    # receive: 클라이언트로부터 이벤트를 받는 async 함수
    # send   : 클라이언트에게 이벤트를 보내는 async 함수

    if scope['type'] == 'http':
        await receive()  # 요청 body 수신 (비동기)
        await send({     # 응답 헤더 전송 (비동기)
            'type': 'http.response.start',
            'status': 200,
        })
        await send({     # 응답 body 전송 (비동기)
            'type': 'http.response.body',
            'body': b'Hello, World!',
        })
```

- `await` 지점에서 제어권을 이벤트 루프에 반환
- 그 사이 **다른 요청을 처리** 가능 → 논블로킹

-----------

```
이벤트 루프 (단일 스레드):

요청A: [시작]--[DB 대기중........]--[완료]
요청B:         [시작]--[API 대기..]--[완료]
요청C:                 [시작]--------[완료]
                ↑ DB 기다리는 동안 다른 요청 처리
```

-----------

#### ASGI의 scope 타입 — WSGI와 결정적 차이

```python
scope['type'] 값:
  'http'      → 일반 HTTP 요청/응답
  'websocket' → 웹소켓 연결 (WSGI는 불가)
  'lifespan'  → 앱 시작/종료 이벤트 (startup, shutdown)
```

WSGI는 HTTP 요청/응답만 처리할 수 있지만,  
ASGI는 **연결의 생명주기 전체**를 다룰 수 있음

---

### 3. 차이점 정리
<style scoped>
  * { font-size: 22px}
</style>

| 항목 | WSGI | ASGI |
|---|---|---|
| 표준 제정 | PEP 333 (2003) | 2019년~ |
| 처리 방식 | **동기 (Blocking)** | **비동기 (Non-blocking)** |
| 인터페이스 | `callable(environ, start_response)` | `async callable(scope, receive, send)` |
| HTTP 지원 | HTTP/1.1 | HTTP/1.1, **HTTP/2, HTTP/3** |
| WebSocket | ❌ 불가 | ✅ 네이티브 지원 |
| 스트리밍 | 제한적 | ✅ 완전 지원 |
| 동시 처리 | 워커 수 = 동시 처리 수 | 워커 1개로 수천 요청 처리 |
| 대표 서버 | Gunicorn, uWSGI | Uvicorn, Hypercorn, Daphne |
| 대표 프레임워크 | Django(구), Flask | FastAPI, Django 4+, Starlette |
| 구현 복잡도 | 단순 | 상대적으로 복잡 |
| 성숙도/생태계 | 매우 성숙 | 빠르게 성장 중 |

-------------

### 4. 장단점

#### WSGI
```
✅ 장점
  - 20년 이상의 검증된 안정성
  - 풍부한 미들웨어/라이브러리 생태계
  - 동기 코드 디버깅이 쉬움
  - Django, Flask 등 기존 자산 활용 가능

❌ 단점
  - WebSocket, SSE 불가
  - I/O 대기 시 워커 낭비 (DB 쿼리, 외부 API 호출)
  - 높은 동시성 처리에 많은 워커(= 메모리) 필요
  - async/await 사용 불가
```

-------------

#### ASGI
```
✅ 장점
  - WebSocket, SSE, 롱폴링 네이티브 지원
  - I/O 바운드 작업에서 압도적 동시 처리 성능
  - async/await 완전 활용
  - HTTP/2, HTTP/3 지원
  - 단일 워커로 수천 동시 연결 처리 가능

❌ 단점
  - 비동기 패러다임 학습 필요
  - 동기 라이브러리 혼용 시 주의 (블로킹 발생 위험)
  - 생태계가 WSGI 대비 아직 얕은 부분 존재
  - 디버깅이 상대적으로 복잡
```

-------------

### 5. 언제 무엇을 선택할까?

```
WSGI를 선택하는 경우:
  ✓ 기존 Django/Flask 레거시 프로젝트 유지보수
  ✓ 팀이 비동기에 익숙하지 않음
  ✓ 단순 CRUD API, 동시 접속자 적음
  ✓ CPU 집약적인 작업 (비동기 이점 없음)

ASGI를 선택하는 경우:
  ✓ 신규 프로젝트
  ✓ WebSocket / 실시간 기능 필요
  ✓ 높은 동시 접속자 처리 (채팅, 알림, 스트리밍)
  ✓ 외부 API 다수 호출 (I/O 바운드 작업)
  ✓ AI 응답 스트리밍 (ChatGPT 스타일 SSE)
```

-------------

### 한 줄 요약

> **WSGI**는 "한 번에 하나씩 처리하는 성실한 직원 여러 명",  
> **ASGI**는 "기다리는 동안 다른 일도 척척 처리하는 효율적인 직원 한 명"  
> — 현대 웹 개발의 방향은 명확히 **ASGI**로 향하고 있습니다.
