Responses API의 `previous_response_id`를 활용하면 매 요청마다 전체 히스토리를 다시 보낼 필요 없이, 서버가 이전 대화 맥락을 기억하게 만들 수 있습니다. 대화 세션을 관리하는 클래스 형태로 만들어 드릴게요.**핵심 아이디어**

- 매 요청마다 `store=True`를 넘겨서 서버에 응답이 저장되게 하고, 응답 객체의 `response.id`를 다음 요청의 `previous_response_id`로 넘기면 서버가 이전 대화 맥락(그리고 reasoning까지)을 이어받습니다.
- 클라이언트가 메시지 배열을 직접 관리할 필요가 없어서, 기존 Chat Completions 방식보다 코드가 단순해지고 토큰도 절약됩니다.
- `ChatSession.reset()`을 호출하면 `previous_response_id`를 `None`으로 되돌려 새 대화를 시작할 수 있습니다.

**참고**

- 만약 `gms.ssafy.io` 프록시가 `previous_response_id`나 `store` 파라미터를 지원하지 않는다면(호환 프록시라 일부 기능이 막혀 있을 수 있음), 대신 직접 `input`에 전체 메시지 리스트(`[{"role": "user", ...}, {"role": "assistant", ...}, ...]`)를 매번 담아 보내는 전통적인 방식으로 폴백해야 합니다. 필요하시면 그 방식으로도 만들어 드릴 수 있어요.


```python
from openai import OpenAI

# 1. OpenAI 클라이언트 생성
client = OpenAI(
    api_key=GMS_KEY,
    base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1/"
)


class ChatSession:
    """
    Responses API의 previous_response_id를 이용해
    멀티턴 대화를 관리하는 클래스.

    매 턴마다 전체 히스토리를 다시 보낼 필요 없이,
    서버가 이전 대화 맥락(추론 내용 포함)을 기억합니다.
    """

    def __init__(self,
                 system_prompt: str = None,
                 model: str = "gpt-5-mini"):
        self.model = model
        self.system_prompt = system_prompt
        self.previous_response_id = None  # 이전 응답 ID 저장

    def send(self, prompt: str) -> str:
        """
        사용자 메시지를 보내고 응답을 반환합니다.
        내부적으로 previous_response_id를 이어붙여
        대화 맥락을 유지합니다.
        """
        kwargs = {
            "model": self.model,
            "input": prompt,
            "store": True,  # 상태 저장 (previous_response_id 사용을 위해 필수)
        }

        if self.system_prompt:
            kwargs["instructions"] = self.system_prompt

        if self.previous_response_id:
            kwargs["previous_response_id"] = self.previous_response_id

        response = client.responses.create(**kwargs)

        # 다음 턴을 위해 이번 응답의 ID 저장
        self.previous_response_id = response.id

        return response.output_text

    def reset(self):
        """대화 맥락을 초기화합니다 (새로운 대화 시작)."""
        self.previous_response_id = None


# ------------------------------
# 사용 예시
# ------------------------------
if __name__ == "__main__":
    session = ChatSession(
        system_prompt="당신은 친절하고 간결하게 답변하는 한국어 비서입니다."
    )

    # 첫 번째 턴
    r1 = session.send("안녕하세요! 제 이름은 민수입니다.")
    print("assistant:", r1)

    # 두 번째 턴 - 이전 대화(이름)를 기억하는지 테스트
    r2 = session.send("제 이름이 뭐라고 했죠?")
    print("assistant:", r2)

    # 세 번째 턴
    r3 = session.send("그 이름으로 삼행시 지어주세요.")
    print("assistant:", r3)
```