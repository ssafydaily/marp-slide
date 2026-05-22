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


# 준비

- 필수 라이브러리 설치
```bash
pip install fastapi uvicorn sqlalchemy
```
------------------



------------------
# 실행

1. 터미널에서 다음 명령어로 서버를 실행합니다.
- 실행
```bash
uvicorn main:app --reload
```
2. 서버가 켜지면 브라우저를 열고 **[http://127.0.0.1:8000/docs**로](http://127.0.0.1:8000/docs**로) 접속
3. **FastAPI**가 자동으로 생성해 준 **Swagger UI 인터페이스**를 통해 직접 데이터를 넣고(POST), 읽고(GET), 고치고(PUT), 지우는(DELETE) 테스트를 시각적으로 진행한다. 
  - 동일한 폴더 내에 test.db라는 파일이 생기면서 데이터가 쌓이는 것도 확인할 수 있습니다.