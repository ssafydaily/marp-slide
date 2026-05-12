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

# 요청 본문 Request Body

- **요청 본문**은 클라이언트에서 API로 보내지는 데이터
- **응답 본문**은 API가 클라이언트로 보내는 데이터

- 요청 본문을 선언하기 위해서 **Pydantic 모델** 을 사용


> [참고]
> - 데이터를 보내기 위해, POST, PUT, DELETE 혹은 PATCH 중 하나를 사용
> - GET 요청에 본문을 담아 보내는 것은 명세서에 정의되지 않은 행동
>   - 이 방식은 아주 복잡한/극한의 상황에서만 FastAPI에 의해 지원
>   - GET 요청에 본문을 담는 것은 권장되지 않음

----------------




