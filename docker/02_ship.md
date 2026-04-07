---
marp: true
theme: default
paginate: true
style: |
  section {
    padding: 1.5rem; /* 원하는 여백 값으로 조절 */
  }
  h1 {
    position: absolute;
    left: 50px;
    top: 50px;
  }
---


# Ship: 배포

- 빌드한 이미지를 다른 호스트에 배포하기
  - 빌드용 머신에서 작성한 이미지를 테스트 환경 도는 서비스 환경에서 실행
  - 팀 간에 공유해서 재사용

- 이미지는 **레지스트리** 라고 부르는 이미지 배포용 서버를 통해서 공유
  - **도커 허브(docker hub)** 가 대표적인 레지스트리 서비스
  - 이미지 저장소는 *리포지터리*
  - 이미지는 **태그** 문자열로 여러 버전으로 저장


---

# 실습 사전 준비

1. 도커 허브에 사용자 등록
2. 호스트에 로그인
3. 이미지 이름 변경하기
```bash
docker tag test-image:v1 algorian/test-image:v1

```

4. 이미지를 도커 허브에 업로드
```bash
docker push algorian/test_image:v1
```

---

# 도커 데스크탑에서 확인하기


---

