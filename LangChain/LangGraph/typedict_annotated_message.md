# TypedDict와 Annotated 완전 정복

## 1️⃣ TypedDict — 무엇인가?

**무엇인가?**
`TypedDict`는 파이썬의 **딕셔너리에 "타입이 정해진 설계도"를 씌운 것**입니다. 겉모습은 평범한 `dict`이지만, 어떤 키(key)에 어떤 타입의 값이 들어가야 하는지를 미리 선언해둡니다.

**왜 필요한가?**
일반 딕셔너리는 아무 키나 자유롭게 넣을 수 있어서 오타나 잘못된 타입이 들어가도 실행 전까지 알 수 없습니다.

```python
# 일반 dict - 오타를 내도 아무도 모름
state = {"topic": "AI 교육", "massages": []}  # "messages"를 "massages"로 오타!
```

`TypedDict`를 쓰면 IDE(VS Code 등)와 타입 체커(mypy 등)가 **코드를 실행하기 전에** "그런 키는 없는데요?"라고 미리 경고해줍니다. LangGraph처럼 여러 노드(함수)가 하나의 State를 주고받는 구조에서는 이 안전장치가 특히 중요합니다.

**어떻게 동작하는가?**
`TypedDict`는 런타임(실행 시점)에는 진짜 `dict`와 100% 동일하게 동작합니다. 즉 **실행 성능에는 전혀 영향이 없고**, 오직 개발 단계에서 타입 힌트 역할만 합니다.

```python
from typing import TypedDict

class State(TypedDict):
    topic: str

# 실제로는 그냥 dict
s: State = {"topic": "AI 교육"}
print(type(s))  # <class 'dict'>
```

**쉬운 비유**
서류 양식(폼)을 떠올려보세요. "이름 칸에는 문자, 나이 칸에는 숫자"라고 정해진 신청서 양식이 `TypedDict`이고, 실제로 그 양식에 손글씨로 채워 넣은 종이 한 장이 진짜 `dict` 인스턴스입니다.

---

## 2️⃣ Annotated — 무엇인가?

**무엇인가?**
`Annotated[타입, 추가정보]`는 **"이 타입에 부가 설명(메타데이터)을 하나 더 붙이겠다"**는 뜻입니다.

```python
Annotated[list[AnyMessage], add_messages]
#          ↑ 진짜 타입        ↑ 부가 정보(메타데이터)
```

**왜 필요한가?**
LangGraph의 State는 여러 노드가 "동시에 또는 순차적으로" 값을 반환하며 업데이트합니다. 이때 기본 동작은 **"덮어쓰기"**입니다.

```python
# 기본 규칙: 덮어쓰기
class State(TypedDict):
    topic: str  # 노드가 topic="새 주제"를 반환하면 → 그냥 통째로 교체됨
```

하지만 `messages`는 대화 기록이기 때문에, 새 메시지가 올 때마다 기존 리스트를 통째로 지우고 덮어써버리면 **이전 대화가 다 사라집니다.** 그래서 "덮어쓰기가 아니라 이어붙이기(병합)를 하라"는 규칙을 LangGraph에게 알려줘야 하는데, 그 규칙(함수)을 `Annotated`로 붙여주는 것입니다.

**어떻게 동작하는가?**
`Annotated[list[AnyMessage], add_messages]`에서 `add_messages`는 **reducer(리듀서) 함수**입니다. LangGraph는 노드가 `messages`를 반환할 때마다 다음처럼 처리합니다.

```python
# LangGraph 내부적으로 하는 일 (개념적 의사코드)
새_state["messages"] = add_messages(기존_state["messages"], 노드가_반환한_messages)
```

즉 `add_messages`가 "기존 리스트 + 새 메시지"를 **똑똑하게 병합**해줍니다. (같은 id의 메시지면 교체, 새 메시지면 append)

**쉬운 숫자 예제**

```python
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages

기존 = [HumanMessage(content="안녕")]
새로옴 = [AIMessage(content="안녕하세요!")]

결과 = add_messages(기존, 새로옴)
print(결과)
# [HumanMessage(content="안녕"), AIMessage(content="안녕하세요!")]
# → 덮어쓰기가 아니라 "이어붙이기"가 된 것을 확인!
```

만약 `Annotated` 없이 `messages: list[AnyMessage]`로만 썼다면, 두 번째 노드가 `[AIMessage(...)]`만 반환하는 순간 첫 번째 `HumanMessage`는 **증발**했을 겁니다.

---

## 3️⃣ State 클래스 안에서의 정리

```python
class State(TypedDict):
    topic: str
    # → 노드가 topic 값을 반환하면 "덮어쓰기" (기본 규칙)

    messages: Annotated[list[AnyMessage], add_messages]
    # → 노드가 messages를 반환하면 add_messages 함수가
    #    "기존 리스트에 이어붙이는" 방식으로 병합
```

| 필드 | 타입 | 업데이트 방식 |
|---|---|---|
| `topic` | `str` | 덮어쓰기 (기본값) |
| `messages` | `list[AnyMessage]` | `add_messages`로 병합 (이어붙이기) |

**실제 활용**: 챗봇처럼 여러 턴(turn)에 걸쳐 대화가 이어지는 그래프에서, `topic`(현재 주제 같은 단발성 정보)은 최신 값으로 교체하고, `messages`(대화 기록)는 계속 쌓아가는 것이 자연스럽기 때문에 이렇게 필드별로 다른 규칙을 지정합니다.

---

## 4️⃣ AnyMessage 외 다른 메시지 타입들

`AnyMessage`는 사실 특정 클래스가 아니라 **아래 메시지 타입들의 Union(합집합) 타입**입니다. "이 중 아무거나 올 수 있다"는 뜻이죠.

| 클래스 | 역할 | 비유 |
|---|---|---|
| `HumanMessage` | 사람(사용자)이 보낸 메시지 | 손님이 한 말 |
| `AIMessage` | AI(LLM)가 응답한 메시지 | 직원이 한 대답 |
| `SystemMessage` | AI의 역할·규칙을 지정하는 메시지 | 직원 교육 매뉴얼 |
| `ToolMessage` | 도구(함수) 실행 결과를 담는 메시지 | 직원이 계산기 두드려서 나온 결과 |
| `FunctionMessage` | (구버전) ToolMessage의 이전 형태 | 지금은 ToolMessage 권장 |

**예시 코드로 전체 흐름 이해하기**

```python
from langchain_core.messages import (
    SystemMessage, HumanMessage, AIMessage, ToolMessage
)

conversation = [
    SystemMessage(content="너는 친절한 AI 교육 조교야."),   # 1. 역할 지정
    HumanMessage(content="TypedDict가 뭐야?"),              # 2. 사용자 질문
    AIMessage(                                               # 3. AI가 도구 호출을 결정
        content="",
        tool_calls=[{"name": "search_docs", "args": {"query": "TypedDict"}, "id": "call_1"}]
    ),
    ToolMessage(content="TypedDict는 typing 모듈의...", tool_call_id="call_1"),  # 4. 도구 실행 결과
    AIMessage(content="TypedDict는 딕셔너리에 타입을 지정하는 도구예요."),        # 5. 최종 답변
]

for msg in conversation:
    print(f"{type(msg).__name__}: {msg.content[:30]}")
```

**출력 결과 & 의미**

```
SystemMessage: 너는 친절한 AI 교육 조교야.
HumanMessage: TypedDict가 뭐야?
AIMessage: 
ToolMessage: TypedDict는 typing 모듈의...
AIMessage: TypedDict는 딕셔너리에 타입을 지정하는...
```

→ 이 리스트 전체가 바로 `State`의 `messages` 필드에 들어가는 값입니다. 새로운 대화 턴이 생길 때마다 `add_messages` reducer가 이 리스트 **뒤에** 새 메시지를 계속 이어 붙여, 대화 맥락(context)이 끊기지 않고 유지됩니다.

---

## 💡 핵심 요약 (누군가에게 다시 설명한다면)

1. **TypedDict** = "딕셔너리에 타입 설계도를 씌운 것" — 실행 시엔 그냥 dict, 개발 시엔 타입 체크용
2. **Annotated[타입, 메타데이터]** = "타입에 부가 규칙을 붙이는 것" — LangGraph에서는 이 메타데이터가 **reducer(병합 규칙)** 역할
3. **State에서**: 일반 필드는 덮어쓰기, `Annotated + add_messages` 필드는 이어붙이기
4. **AnyMessage**는 `SystemMessage / HumanMessage / AIMessage / ToolMessage` 등을 통틀어 부르는 타입 — 대화의 "누가 무엇을 말했는지"를 구분하는 역할