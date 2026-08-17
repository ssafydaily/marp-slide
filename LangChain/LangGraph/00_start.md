<!-- ---
marp: true
theme: dark-plus-code
paginate: true
style: |

--- -->


# 그래프를 이루는 네 가 

- State — 그래프 전체가 공유하는 데이터(딕셔너리). 매 노드를 거치며 갱신
- Node — State를 입력받아 갱신분(diff) 을 돌려주는 함수
- Edge — 노드와 노드를 잇는 흐름. 고정 엣지와 조건부 엣지
- Graph — 위를 조립해 `compile()` 한 실행 가능한 객체


# State — 그 프의 공유 메모리
```python
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class State(TypedDict):
    # 일반 필드는 노드가 반환하면 "덮어쓰기"가 기본
    topic: str
    # Annotated + reducer 를 주면 "병합" 규칙을 지정할 수 있다
    messages: Annotated[list[AnyMessage], add_messages]
```
- State는 보통 TypedDict (또는 Pydantic / dataclass)
- 노드는 **State 전체가 아니라 변경할 필드만 반환한다**


# Reducer — 상태를 어떻게 합칠까
- 기본값은 덮어쓰기. reducer를 지정하면 누적/병합 규칙이 된다.
```python
from operator import add
from typing import Annotated

class State(TypedDict):
    # 리스트를 이어붙임 [a] + [b] = [a, b]
    logs: Annotated[list[str], add]
```
- `add_messages`는 메시지 전용 reducer:

```python
# 같은 id 면 교체, 새 id 면 추가.
# ("user", "..") 같은 튜플도 자동 변환
messages: Annotated[list, add_messages]
```
- 대부분의 챗봇은 이 패턴 하나로 충분합니다.


# MessagesState — 가장 흔한 지름길
```python
from langgraph.graph import MessagesState

# 아래 정의를 미리 만들어 둔 것과 동일하다:
#   class MessagesState(TypedDict):
#       messages: Annotated[list[AnyMessage], add_messages]

class State(MessagesState):
    # 필요하면 필드를 더 얹는다
    user_id: str
```
- 채팅 기반 그래프라면 `MessagesState`로 시작하세요. 
- 직접 `TypedDict`를 쓰는 건 메시지 외 상태가 필요할 때입니다.



# Node — 상태를 갱신하는 함수

```python
from langchain.chat_models import init_chat_model

llm = init_chat_model("openai:gpt-4o")

def chatbot(state: MessagesState) -> dict:
    # state["messages"] 를 읽고
    response = llm.invoke(state["messages"])
    # 바뀐 부분만 dict 로 반환 → add_messages 가 누적해 준다
    return {"messages": [response]}
```
- 노드는 그냥 함수다 (또는 *callable*). 
  - 입력: `state`, 출력: `dict`
- 반환한 `dict`가 `State`에 병합된다 (reducer 규칙대로)


# Edge — 흐름을 연결하고 컴파일

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)

builder.add_edge(START, "chatbot")   # 진입점
builder.add_edge("chatbot", END)     # 종료점

graph = builder.compile()
```

- **START** / **END** 는 그래프의 가상 진입·종료 노드
- `compile()` 결과는 LangChain **Runnable** — `invoke`, `stream` 사용 가능


# 실행 — invoke 와 stream
- 한 번에 (invoke)
```python
out = graph.invoke({
  "messages": [
    {"role": "user", "content": "안녕!"}
  ]
})
print(out["messages"][-1].content)
```
- 흘려보며 (stream)
```python
for chunk in graph.stream(
    {"messages": [("user", "안녕!")]},
    stream_mode="values",
):
    chunk["messages"][-1].pretty_print()
```
- stream_mode는 이후에 자세히 — values / updates / messages.


# 실습 01 에코 챗봇을 그래프로
```python
from langgraph.graph import (
    StateGraph, START, END, MessagesState)
from langchain.chat_models import init_chat_model

llm = init_chat_model("openai:gpt-4o")

def chatbot(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"])]}

g = StateGraph(MessagesState)
g.add_node("chatbot", chatbot)
g.add_edge(START, "chatbot")
g.add_edge("chatbot", END)
graph = g.compile()
```
## 해보기
1. graph.invoke 로 한 번 대화
2. stream_mode="values" 로 바꿔 출력
3. 노드를 하나 더 추가해 보기 (예: 입력 전처리 노드)
- 아직 **기억은 못 합니다**. 매 호출이 백지


# 조건부 분기