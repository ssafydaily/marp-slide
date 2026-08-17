---
marp: true
theme: blueprint
paginate: true
footer: 'LangGraph 풀코스 · v1.x'
---

<script type="module">
// ※ 이 스크립트는 preview.html 전용입니다.
//    preview.html 은 이 블록을 제거한 뒤 Mermaid 를 직접 초기화합니다.
//    HTML 내보내기는 `node build.js` 를 사용하세요 — build.js 가
//    marp --html 실행 후 Mermaid 스크립트를 <body> 레벨에 자동 주입합니다.
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
mermaid.initialize({
  startOnLoad: true,
  securityLevel: 'loose',
  theme: 'base',
  flowchart: { curve: 'basis', htmlLabels: true },
  themeVariables: {
    fontFamily: 'IBM Plex Mono, monospace', fontSize: '15px',
    primaryColor: '#ffffff', primaryBorderColor: '#3f5fc4', primaryTextColor: '#232a33',
    lineColor: '#8b94a3', secondaryColor: '#eef1fb', tertiaryColor: '#f7f8fa',
    clusterBkg: '#f7f8fa', clusterBorder: '#dce1e8', edgeLabelBackground: '#f7f8fa'
  }
});
</script>

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _footer: '' -->

<div class="nodes"><span class="n"></span><span class="ln"></span><span class="n fill"></span><span class="ln"></span><span class="n"></span></div>

# LangGraph

<span class="sub">상태 기반 LLM 에이전트를 그래프로 설계한다</span>

<div class="meta">

`Python 개발자를 위한 실습 중심 풀코스` `한국어 + English` `v1.x · 2026`

</div>

---

<!-- _header: 'About this course' -->
## 이 강의에서 배우는 것

- **그래프로 사고하기** — 체인을 넘어 상태(state)·분기·순환이 있는 흐름 설계
- **에이전트 직접 구현** — Tool calling과 ReAct 루프를 밑바닥부터
- **기억하는 시스템** — Checkpointer로 대화·상태를 영속화(persist)
- **사람과 협업** — Human-in-the-loop 승인 게이트
- **실전 아키텍처** — RAG, 그리고 멀티 에이전트 협업 시스템

> **사전 지식**: Python 함수 · 타입 힌트 · 딕셔너리에 익숙하면 충분합니다. LangChain 경험은 필요 없습니다.

---

<!-- _header: 'Curriculum map' -->
## 9개 모듈 · 한눈에 보기

| 모듈 | 주제 | 핵심 API |
| --- | --- | --- |
| 01 | 핵심 구성요소 | `StateGraph` `add_node` `add_edge` |
| 02 | 조건부 분기 | `add_conditional_edges` `Command` |
| 03 | 순환과 반복 | conditional edge로 cycle · `recursion_limit` |
| 04 | 도구와 에이전트 | `@tool` `ToolNode` `create_react_agent` |
| 05 | 영속성·메모리 | `MemorySaver` `thread_id` `Store` |
| 06 | Human-in-the-loop | `interrupt` `Command(resume=...)` |
| 07 | RAG 파이프라인 | retrieve → grade → generate |
| 08 | 멀티 에이전트 | Supervisor · Swarm · Subgraph |
| 09 | 운영·스트리밍·배포 | `stream_mode` · LangSmith · Platform |

---

<!-- _header: 'Setup' -->
## 사전 준비 — 설치와 키

<div class="cols">
<div>

#### 설치

```bash
pip install -U langgraph langchain
pip install -U "langchain[openai]"
# 선택: 영속성·멀티에이전트
pip install langgraph-checkpoint-sqlite
pip install langgraph-supervisor langgraph-swarm
```

</div>
<div>

#### 환경 변수

```bash
export OPENAI_API_KEY="sk-..."
# 추적/디버깅(권장)
export LANGSMITH_API_KEY="ls-..."
export LANGSMITH_TRACING=true
```

</div>
</div>

> 이 강의의 코드는 `init_chat_model("openai:gpt-4o")` 기준입니다. Anthropic·Ollama 등으로 바꿔도 그래프 구조는 동일합니다.

---

<!-- _header: 'Why a graph?' -->
## LangChain vs LangGraph

| 구분 | LangChain 체인 | LangGraph |
| --- | --- | --- |
| 흐름 | 대체로 **일방향** (A→B→C) | **그래프** — 분기·순환 가능 |
| 상태 | 단계 간 암묵적 전달 | **명시적 State** 객체 |
| 반복 | 직접 루프 작성 | 엣지로 자연스럽게 cycle |
| 제어 | 중간 개입 어려움 | **interrupt**로 일시정지·재개 |
| 적합 | 단순 파이프라인 | **에이전트 · 다단계 워크플로** |

> LangGraph는 LangChain을 **대체**하지 않습니다. LangChain의 모델·툴·메시지를 그대로 쓰되, **실행 흐름**을 그래프로 다룹니다.

---

<!-- _header: 'Why a graph?' -->
## 체인의 한계, 그래프의 자유

<div class="mermaid">
flowchart LR
  subgraph CHAIN["체인 · 한 번 지나가면 끝"]
    a1([입력]) --> b1[LLM] --> c1([출력])
  end
</div>

<div class="mermaid">
flowchart LR
  subgraph GRAPH["그래프 · 판단하고 되돌아옴"]
    s([START]) --> ag[agent]
    ag -->|도구 필요| tl[tools]
    tl --> ag
    ag -->|완료| e([END])
  end
</div>

> "더 검색할까? 다시 시도할까? 사람에게 물어볼까?" — 이런 **판단과 반복**이 필요한 순간이 LangGraph가 빛나는 지점입니다.

---

<!-- _class: section -->
<!-- _paginate: false -->

<div class="modnum">MODULE 01</div>

# 핵심 구성요소

<div class="modsub">State · Node · Edge · Graph</div>

---

<!-- _header: 'Module 01 · The big picture' -->
## 그래프를 이루는 네 가지

<div class="mermaid">
flowchart LR
  S([START]) -->|State| N1[node A] -->|State| N2[node B] -->|State| E([END])
</div>

- **State** — 그래프 전체가 공유하는 데이터(딕셔너리). 매 노드를 거치며 갱신
- **Node** — State를 입력받아 **갱신분(diff)** 을 돌려주는 함수
- **Edge** — 노드와 노드를 잇는 흐름. 고정 엣지와 조건부 엣지
- **Graph** — 위를 조립해 `compile()` 한 실행 가능한 객체

---

<!-- _header: 'Module 01 · State' -->
## State — 그래프의 공유 메모리

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

- State는 보통 `TypedDict` (또는 Pydantic / dataclass)
- 노드는 State 전체가 아니라 **바꿀 필드만** 반환한다

---

<!-- _header: 'Module 01 · Reducers' -->
## Reducer — 상태를 어떻게 합칠까

<div class="cols">
<div>

기본값은 **덮어쓰기**. reducer를 지정하면 **누적/병합** 규칙이 된다.

```python
from operator import add
from typing import Annotated

class State(TypedDict):
    # 리스트를 이어붙임 [a] + [b] = [a, b]
    logs: Annotated[list[str], add]
```

</div>
<div>

`add_messages`는 메시지 전용 reducer:

```python
# 같은 id 면 교체, 새 id 면 추가.
# ("user", "..") 같은 튜플도 자동 변환
messages: Annotated[list, add_messages]
```

> 대부분의 챗봇은 이 패턴 하나로 충분합니다.

</div>
</div>

---

<!-- _header: 'Module 01 · MessagesState' -->
## MessagesState — 가장 흔한 지름길

```python
from langgraph.graph import MessagesState

# 아래 정의를 미리 만들어 둔 것과 동일하다:
#   class MessagesState(TypedDict):
#       messages: Annotated[list[AnyMessage], add_messages]

class State(MessagesState):
    # 필요하면 필드를 더 얹는다
    user_id: str
```

> 채팅 기반 그래프라면 `MessagesState`로 시작하세요. 직접 `TypedDict`를 쓰는 건 메시지 외 상태가 필요할 때입니다.

---

<!-- _header: 'Module 01 · Node' -->
## Node — 상태를 갱신하는 함수

```python
from langchain.chat_models import init_chat_model

llm = init_chat_model("openai:gpt-4o")

def chatbot(state: MessagesState) -> dict:
    # state["messages"] 를 읽고
    response = llm.invoke(state["messages"])
    # 바뀐 부분만 dict 로 반환 → add_messages 가 누적해 준다
    return {"messages": [response]}
```

- 노드는 그냥 **함수**다 (또는 callable). 입력 `state`, 출력 `dict`
- 반환한 dict가 State에 **병합**된다 (reducer 규칙대로)

---

<!-- _header: 'Module 01 · Edge & build' -->
## Edge — 흐름을 연결하고 컴파일

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)

builder.add_edge(START, "chatbot")   # 진입점
builder.add_edge("chatbot", END)     # 종료점

graph = builder.compile()
```

- `START` / `END`는 그래프의 가상 진입·종료 노드
- `compile()` 결과는 LangChain **Runnable** — `invoke`, `stream` 사용 가능

---

<!-- _header: 'Module 01 · Run it' -->
## 실행 — invoke 와 stream

<div class="cols">
<div>

#### 한 번에 (invoke)

```python
out = graph.invoke({
  "messages": [
    {"role": "user", "content": "안녕!"}
  ]
})
print(out["messages"][-1].content)
```

</div>
<div>

#### 흘려보며 (stream)

```python
for chunk in graph.stream(
    {"messages": [("user", "안녕!")]},
    stream_mode="values",
):
    chunk["messages"][-1].pretty_print()
```

</div>
</div>

> `stream_mode`는 모듈 09에서 자세히 — `values` / `updates` / `messages`.

---

<!-- _header: 'Module 01 · Lab' -->
## <span class="lab">실습 01</span> 에코 챗봇을 그래프로

<div class="cols">
<div>

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

</div>
<div>

#### 해보기

1. `graph.invoke` 로 한 번 대화
2. `stream_mode="values"` 로 바꿔 출력
3. 노드를 하나 더 추가해 보기 (예: 입력 전처리 노드)

> 아직 **기억은 못 합니다**. 매 호출이 백지 — 모듈 05에서 해결합니다.

</div>
</div>

---

<!-- _class: section -->
<!-- _paginate: false -->

<div class="modnum">MODULE 02</div>

# 조건부 분기

<div class="modsub">Conditional Edges · Command</div>

---

<!-- _header: 'Module 02 · Branching' -->
## 흐름을 나누는 두 가지 방법

<div class="mermaid">
flowchart LR
  C[classifier] -->|order| O[order_node]
  C -->|chat| H[chat_node]
  O --> E([END])
  H --> E([END])
</div>

- **고정 엣지** `add_edge(a, b)` — 항상 a 다음 b
- **조건부 엣지** `add_conditional_edges(a, router)` — **router 함수**의 반환값으로 다음 노드를 결정

---

<!-- _header: 'Module 02 · Router function' -->
## 라우팅 함수 — 다음 노드를 고른다

```python
from typing import Literal

def route(state: State) -> Literal["order", "chat"]:
    text = state["messages"][-1].content
    if "주문" in text or "배송" in text:
        return "order"
    return "chat"

builder.add_conditional_edges(
    "classifier",          # 이 노드 다음에
    route,                 # 이 함수가 반환하는 키로 분기
    {"order": "order_node", "chat": "chat_node"},  # 키 → 노드 매핑
)
```

> 매핑 dict를 생략하면 **반환 문자열 = 노드 이름**으로 간주합니다.

---

<!-- _header: 'Module 02 · Lab' -->
## <span class="lab">실습 02</span> 의도 분류 라우터

<div class="cols">
<div>

```python
def classify(state: State):
    msg = state["messages"][-1].content
    prompt = f"다음을 order/chat 로만 답하라: {msg}"
    label = llm.invoke(prompt).content.strip()
    return {"intent": label}

def route(state) -> Literal["order", "chat"]:
    return "order" if "order" in state["intent"] else "chat"
```

</div>
<div>

```python
g.add_node("classify", classify)
g.add_node("order_node", handle_order)
g.add_node("chat_node", handle_chat)

g.add_edge(START, "classify")
g.add_conditional_edges("classify", route,
    {"order": "order_node", "chat": "chat_node"})
g.add_edge("order_node", END)
g.add_edge("chat_node", END)
```

</div>
</div>

---

<!-- _header: 'Module 02 · Command' -->
## Command — 갱신과 이동을 한 번에

`Command`를 반환하면 노드가 **상태 갱신**과 **다음 노드 지정**을 동시에 할 수 있다. 라우터 노드를 따로 둘 필요가 없어진다.

```python
from langgraph.types import Command
from typing import Literal

def classifier(state: State) -> Command[Literal["order_node", "chat_node"]]:
    text = state["messages"][-1].content
    target = "order_node" if "주문" in text else "chat_node"
    return Command(
        update={"intent": target},   # 상태 갱신
        goto=target,                 # 다음 노드로 이동
    )
```

> 멀티 에이전트의 **handoff**(제어 넘김)가 바로 이 `Command(goto=...)` 위에 세워집니다 — 모듈 08.

---

<!-- _class: section -->
<!-- _paginate: false -->

<div class="modnum">MODULE 03</div>

# 순환과 반복

<div class="modsub">Cycles · Loops · recursion_limit</div>

---

<!-- _header: 'Module 03 · Why cycles' -->
## 사이클 — 그래프의 진짜 힘

<div class="mermaid">
flowchart LR
  D[draft] --> CR[critic]
  CR -->|점수 낮음| RV[reviser]
  RV --> CR
  CR -->|충분함| E([END])
</div>

- 일반 DAG와 달리 LangGraph는 **노드로 되돌아오는 엣지**를 허용
- "조건을 만족할 때까지 반복" — 에이전트·자기수정 루프의 토대
- 되돌아가는 길은 보통 **조건부 엣지**로 만든다

---

<!-- _header: 'Module 03 · Build a loop' -->
## 루프 만들기 — 되돌리는 엣지

```python
from typing import Literal

def should_continue(state: State) -> Literal["reviser", "__end__"]:
    if state["score"] >= 0.8 or state["iterations"] >= 3:
        return "__end__"          # END 의 예약 키
    return "reviser"

builder.add_node("critic", critic)
builder.add_node("reviser", reviser)

builder.add_conditional_edges("critic", should_continue)
builder.add_edge("reviser", "critic")   # 다시 평가하러 돌아감
```

> `"__end__"` 는 `END`를 가리키는 문자열 키. 매핑 없이 쓸 때 편리합니다.

---

<!-- _header: 'Module 03 · Safety' -->
## 무한 루프 방어 — recursion_limit

```python
# 한 번의 실행에서 거칠 수 있는 "슈퍼스텝" 상한
graph.invoke(inputs, config={"recursion_limit": 10})
```

- 기본값은 **25**. 넘으면 `GraphRecursionError` 발생
- 루프에는 항상 **종료 조건 두 개**를 두자:
  - 품질 조건 (예: `score >= 0.8`)
  - 횟수 조건 (예: `iterations >= 3`)
- 카운터는 State에 두고 노드에서 `+1` 갱신

> "수렴하지 않으면 멈춘다" — 안전한 루프의 기본기.

---

<!-- _header: 'Module 03 · Lab' -->
## <span class="lab">실습 03</span> 반복 정제 루프

<div class="cols">
<div>

```python
class State(TypedDict):
    task: str
    draft: str
    score: float
    iterations: int

def reviser(state):
    new = llm.invoke(
        f"개선하라:\n{state['draft']}").content
    return {"draft": new,
            "iterations": state["iterations"] + 1}
```

</div>
<div>

```python
def critic(state):
    s = grade(state["draft"])   # 0~1
    return {"score": s}

def keep_going(state) -> Literal["reviser","__end__"]:
    if state["score"] >= 0.8 or \
       state["iterations"] >= 3:
        return "__end__"
    return "reviser"
```

> 초안 → 평가 → (부족하면) 수정 → 다시 평가. 자기수정 에이전트의 축소판.

</div>
</div>

---

<!-- _class: section -->
<!-- _paginate: false -->

<div class="modnum">MODULE 04</div>

# 도구와 에이전트

<div class="modsub">Tool calling · ToolNode · ReAct</div>

---

<!-- _header: 'Module 04 · Tools' -->
## 도구 정의 — @tool

```python
from langchain_core.tools import tool

@tool
def search(query: str) -> str:
    """웹에서 query 를 검색해 결과 요약을 반환한다."""  # docstring = 도구 설명
    return web_search(query)

@tool
def calculator(expression: str) -> str:
    """수식을 계산한다. 예: '2 * (3 + 4)'."""
    return str(eval(expression))

# 모델에 도구를 "바인딩" — 모델이 호출 여부/인자를 결정
llm_with_tools = llm.bind_tools([search, calculator])
```

> docstring과 타입 힌트가 곧 **모델이 읽는 명세**입니다. 또렷하게 쓰세요.

---

<!-- _header: 'Module 04 · The ReAct loop' -->
## ReAct — 생각하고, 도구 쓰고, 반복

<div class="mermaid">
flowchart TD
  S([START]) --> AG["agent · LLM"]
  AG -->|tool_calls 있음| TN[ToolNode]
  TN --> AG
  AG -->|tool_calls 없음| E([END])
</div>

- 모델이 **도구를 호출**하면 → 도구 실행 → 결과를 다시 모델에게
- 더 호출할 게 없으면 → 최종 답변 후 종료
- 이 순환이 **에이전트**의 본질 — LangGraph의 cycle로 자연스럽게 표현

---

<!-- _header: 'Module 04 · ToolNode' -->
## ToolNode · tools_condition

LangGraph 내장 부품으로 ReAct 루프를 손쉽게 조립한다.

```python
from langgraph.prebuilt import ToolNode, tools_condition

def agent(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

builder.add_node("agent", agent)
builder.add_node("tools", ToolNode([search, calculator]))  # 도구 실행 노드

builder.add_edge(START, "agent")
# tools_condition: tool_calls 있으면 "tools", 없으면 END 로 라우팅
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")     # 도구 결과를 다시 모델로

graph = builder.compile()
```

---

<!-- _header: 'Module 04 · Prebuilt' -->
## create_react_agent — 한 줄 에이전트

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model=llm,
    tools=[search, calculator],
    prompt="너는 꼼꼼한 리서치 어시스턴트다.",
)

agent.invoke({"messages": [("user", "오늘 서울 날씨와 그 두 배 온도는?")]})
```

> **v1 참고**: 앞으로는 `from langchain.agents import create_agent` 가 권장됩니다. 인터페이스는 거의 동일하니, 직접 조립(`ToolNode`)을 이해한 뒤 prebuilt로 넘어가세요.

---

<!-- _header: 'Module 04 · Lab' -->
## <span class="lab">실습 04</span> 도구 쓰는 에이전트

<div class="cols">
<div>

```python
from langgraph.prebuilt import (
    ToolNode, tools_condition)

tools = [search, calculator]
llm_t = llm.bind_tools(tools)

def agent(state: MessagesState):
    return {"messages":[llm_t.invoke(state["messages"])]}
```

</div>
<div>

```python
g = StateGraph(MessagesState)
g.add_node("agent", agent)
g.add_node("tools", ToolNode(tools))
g.add_edge(START, "agent")
g.add_conditional_edges("agent", tools_condition)
g.add_edge("tools", "agent")
graph = g.compile()
```

> 도구를 직접 만든 버전과 `create_react_agent` 버전의 출력을 비교해 보세요.

</div>
</div>

---

<!-- _class: section -->
<!-- _paginate: false -->

<div class="modnum">MODULE 05</div>

# 영속성과 메모리

<div class="modsub">Checkpointer · thread_id · Store</div>

---

<!-- _header: 'Module 05 · Checkpointer' -->
## Checkpointer — 상태를 저장한다

- 그래프 실행의 **매 단계 상태**를 자동 저장하는 장치
- `thread_id`로 구분된 **대화 스레드**별로 상태가 쌓임
- 효과: **대화 기억** · 중단 후 재개 · 과거로 되감기(time travel) · Human-in-the-loop

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()                       # 인메모리(개발용)
graph = builder.compile(checkpointer=checkpointer) # 컴파일 시 연결
```

> `interrupt`(모듈 06)도 checkpointer가 있어야 동작합니다 — 상태를 저장해 둬야 재개가 가능하니까요.

---

<!-- _header: 'Module 05 · Memory in action' -->
## thread_id — 대화를 기억하다

```python
config = {"configurable": {"thread_id": "user-42"}}

graph.invoke({"messages": [("user", "내 이름은 지호야")]}, config)
graph.invoke({"messages": [("user", "내 이름이 뭐였지?")]}, config)
# → "지호" 라고 답한다. 같은 thread_id 의 이전 상태를 이어받기 때문
```

- 같은 `thread_id` → 이전 메시지가 State에 그대로 남아 있음
- 다른 `thread_id` → 완전히 새 대화 (격리됨)

> 멀티 유저 서비스라면 보통 `thread_id = 사용자/세션 ID`.

---

<!-- _header: 'Module 05 · Production stores' -->
## 저장소 — 개발에서 운영으로

| 체크포인터 | 패키지 | 용도 |
| --- | --- | --- |
| `MemorySaver` | langgraph | 개발·테스트 (프로세스 종료 시 소멸) |
| `SqliteSaver` | langgraph-checkpoint-sqlite | 로컬·소규모 영속 |
| `PostgresSaver` | langgraph-checkpoint-postgres | 운영 환경 |

```python
from langgraph.checkpoint.sqlite import SqliteSaver

with SqliteSaver.from_conn_string("chat.db") as cp:
    graph = builder.compile(checkpointer=cp)
    graph.invoke(inputs, config)
```

---

<!-- _header: 'Module 05 · Time travel' -->
## 되감기 — 과거 상태에서 다시

```python
# 이 스레드의 모든 체크포인트 이력
history = list(graph.get_state_history(config))

# 특정 시점(checkpoint)부터 다시 실행 (분기)
past = history[2]
graph.invoke(None, past.config)

# 현재 상태 들여다보기 / 직접 수정
snapshot = graph.get_state(config)
graph.update_state(config, {"topic": "새 주제"})
```

> 디버깅·what-if 분석·HITL에서 모두 쓰이는 강력한 기능.

---

<!-- _header: 'Module 05 · Long-term memory' -->
## Store — 스레드를 넘는 장기 기억

`Checkpointer`가 **한 대화의 상태**라면, `Store`는 **대화를 넘어** 사용자 선호·사실을 기억한다.

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
graph = builder.compile(checkpointer=checkpointer, store=store)

def remember(state, *, store):   # 노드에서 store 주입받기
    store.put(("user-42", "facts"), "diet", {"text": "비건"})
    hits = store.search(("user-42", "facts"), query="식습관")
    return {...}
```

> 운영에선 `PostgresStore` + 임베딩 검색으로 "기억하는 비서"를 만듭니다.

---

<!-- _header: 'Module 05 · Lab' -->
## <span class="lab">실습 05</span> 기억하는 챗봇

<div class="cols">
<div>

```python
from langgraph.checkpoint.memory import MemorySaver

graph = builder.compile(
    checkpointer=MemorySaver())

cfg = {"configurable": {"thread_id": "demo"}}
```

</div>
<div>

```python
def chat(text):
    out = graph.invoke(
        {"messages": [("user", text)]}, cfg)
    print(out["messages"][-1].content)

chat("내 취미는 등산이야")
chat("내 취미에 맞는 책 추천해줘")  # 등산 기억함
```

> `thread_id`를 바꿔 호출하면 기억이 사라지는 걸 확인해 보세요.

</div>
</div>

---

<!-- _class: section -->
<!-- _paginate: false -->

<div class="modnum">MODULE 06</div>

# Human-in-the-loop

<div class="modsub">interrupt · 승인 게이트 · resume</div>

---

<!-- _header: 'Module 06 · The pattern' -->
## 사람을 흐름 안에 넣기

<div class="mermaid">
flowchart LR
  P[plan] --> H{{"human · interrupt"}}
  H -->|resume: yes| X[execute] --> E([END])
  H -->|resume: edit| P
</div>

- 민감한 행동(결제·삭제·발송) **직전에 멈추고** 사람의 승인을 받는다
- `interrupt()`로 그래프를 **일시정지** → 사람이 결정 → `Command(resume=...)`로 재개
- 상태가 checkpointer에 저장돼 있으니, 몇 분/며칠 뒤 재개해도 OK

---

<!-- _header: 'Module 06 · interrupt' -->
## interrupt() — 멈추고 물어본다

```python
from langgraph.types import interrupt, Command

def approval(state: State):
    # 실행이 여기서 멈추고, payload 가 클라이언트로 전달된다
    decision = interrupt({
        "action": state["next_action"],
        "question": "이 작업을 승인하시겠습니까? (yes/no)",
    })
    # 재개되면 decision 에 resume 값이 들어온다
    return {"approved": decision == "yes"}
```

- `interrupt(payload)` — payload는 사람에게 보여줄 정보
- **checkpointer 필수** (멈춘 상태를 저장해야 하므로)

---

<!-- _header: 'Module 06 · Resume' -->
## 재개 — Command(resume=...)

```python
config = {"configurable": {"thread_id": "t1"}}

# 1) 첫 실행 — approval 노드의 interrupt 에서 멈춤
graph.invoke({"messages": [("user", "100만원 송금해줘")]}, config)

# 2) 사람의 결정을 확인한다
state = graph.get_state(config)
print(state.next)                 # ('approval',) — 멈춰 있는 위치

# 3) 결정을 주입하며 재개
graph.invoke(Command(resume="yes"), config)
```

> `update_state`로 상태를 **고친 뒤** 재개할 수도 있습니다 — "승인 + 금액 수정" 같은 패턴.

---

<!-- _header: 'Module 06 · Lab' -->
## <span class="lab">실습 06</span> 승인 게이트

<div class="cols">
<div>

```python
from langgraph.types import interrupt, Command

def plan(state):
    return {"next_action": "send_email"}

def gate(state):
    ok = interrupt({"action": state["next_action"]})
    return {"approved": ok == "yes"}

def execute(state):
    return {"messages":[("ai","실행 완료")]}
```

</div>
<div>

```python
g.add_edge(START, "plan")
g.add_edge("plan", "gate")
g.add_edge("gate", "execute")
g.add_edge("execute", END)
graph = g.compile(checkpointer=MemorySaver())

graph.invoke(inputs, cfg)          # gate 에서 멈춤
graph.invoke(Command(resume="yes"), cfg)  # 재개
```

</div>
</div>

---

<!-- _class: section -->
<!-- _paginate: false -->

<div class="modnum">MODULE 07</div>

# RAG with LangGraph

<div class="modsub">retrieve · grade · generate · self-correct</div>

---

<!-- _header: 'Module 07 · RAG as a graph' -->
## RAG 파이프라인을 그래프로

<div class="mermaid">
flowchart LR
  Q([질문]) --> R[retrieve]
  R --> G{관련성 평가}
  G -->|관련 있음| GEN[generate]
  G -->|관련 없음| RW[rewrite]
  RW --> R
  GEN --> A([답변])
</div>

- 단순 RAG = retrieve → generate (직선)
- **Corrective RAG** = 검색 결과를 **평가**하고, 부실하면 질문을 고쳐 **다시 검색**
- 조건부 엣지 + 사이클 = LangGraph가 RAG에 잘 맞는 이유

---

<!-- _header: 'Module 07 · Nodes' -->
## 노드: retrieve · grade · generate

```python
class RAGState(TypedDict):
    question: str
    documents: list
    answer: str

def retrieve(state: RAGState):
    docs = retriever.invoke(state["question"])      # 벡터 검색
    return {"documents": docs}

def generate(state: RAGState):
    ctx = "\n\n".join(d.page_content for d in state["documents"])
    ans = llm.invoke(f"문맥:\n{ctx}\n\n질문: {state['question']}")
    return {"answer": ans.content}
```

---

<!-- _header: 'Module 07 · Self-correction' -->
## 자기교정 — grade & rewrite

```python
from typing import Literal

def grade(state: RAGState) -> Literal["generate", "rewrite"]:
    ctx = format_docs(state["documents"])
    verdict = llm.invoke(
        f"문서가 질문에 답하기 충분한가? yes/no\n질문:{state['question']}\n{ctx}"
    ).content
    return "generate" if "yes" in verdict.lower() else "rewrite"

def rewrite(state: RAGState):
    better = llm.invoke(f"검색이 잘 되도록 질문을 다시 써라: {state['question']}")
    return {"question": better.content}

builder.add_conditional_edges("retrieve", grade)
builder.add_edge("rewrite", "retrieve")   # 고친 질문으로 재검색
```

---

<!-- _header: 'Module 07 · Lab' -->
## <span class="lab">실습 07</span> 문서 QA 그래프

<div class="cols">
<div>

```python
g = StateGraph(RAGState)
g.add_node("retrieve", retrieve)
g.add_node("rewrite", rewrite)
g.add_node("generate", generate)

g.add_edge(START, "retrieve")
g.add_conditional_edges("retrieve", grade)
g.add_edge("rewrite", "retrieve")
g.add_edge("generate", END)
rag = g.compile()
```

</div>
<div>

#### 확장 과제

- `rewrite` 횟수 상한 (모듈 03의 루프 방어)
- 생성 답변의 **환각 검사** 노드 추가 → 실패 시 재생성
- `retriever`를 실제 벡터스토어(FAISS·Chroma)로 교체

> 평가·재시도 노드를 더할수록 "Self-RAG"에 가까워집니다.

</div>
</div>

---

<!-- _class: section -->
<!-- _paginate: false -->

<div class="modnum">MODULE 08</div>

# 멀티 에이전트

<div class="modsub">Supervisor · Swarm · Subgraph</div>

---

<!-- _header: 'Module 08 · When' -->
## 언제 여러 에이전트로 나눌까

- 한 에이전트의 **도구·프롬프트가 너무 비대**해질 때
- 역할이 뚜렷이 갈릴 때 (리서치 / 코딩 / 작문)
- 도메인별 **전문화**가 품질을 높일 때

| 패턴 | 제어 방식 | 적합한 경우 |
| --- | --- | --- |
| **Supervisor** | 중앙 관리자가 위임·취합 | 명확한 분업, 추적 용이 |
| **Swarm** | 에이전트끼리 직접 handoff | 동적 협업, 대화 이관 |
| **Network** | 자유로운 상호 호출 | 복잡·비정형 (제어 어려움) |

---

<!-- _header: 'Module 08 · Supervisor' -->
## Supervisor — 관리자가 위임한다

<div class="mermaid">
flowchart TD
  S{{supervisor}} --> R[researcher]
  S --> C[coder]
  R --> S
  C --> S
  S --> E([END])
</div>

- 관리자 노드가 **다음에 누구를 부를지** 결정하고, 결과를 받아 다시 판단
- 모듈 02의 `Command(goto=...)` 라우팅이 그대로 확장된 형태

---

<!-- _header: 'Module 08 · Supervisor' -->
## langgraph-supervisor — prebuilt

```python
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent

researcher = create_react_agent(llm, [web_search], name="researcher",
                                prompt="너는 리서치 전문가다.")
coder = create_react_agent(llm, [run_python], name="coder",
                           prompt="너는 파이썬 코더다.")

app = create_supervisor(
    agents=[researcher, coder],
    model=llm,
    prompt="리서치는 researcher, 코드는 coder 에게 위임하라.",
).compile()

app.invoke({"messages": [("user", "최근 환율을 찾아 그래프 그리는 코드를 써줘")]})
```

---

<!-- _header: 'Module 08 · Swarm' -->
## Swarm — 에이전트끼리 넘긴다

<div class="mermaid">
flowchart LR
  A[flight_agent] <-->|handoff| B[hotel_agent]
  A <-->|handoff| C[refund_agent]
  B <-->|handoff| C
</div>

```python
from langgraph_swarm import create_swarm, create_handoff_tool

flight = create_react_agent(llm, [book_flight,
    create_handoff_tool(agent_name="hotel")], name="flight")
hotel  = create_react_agent(llm, [book_hotel,
    create_handoff_tool(agent_name="flight")], name="hotel")

app = create_swarm([flight, hotel], default_active_agent="flight").compile()
```

> 중앙 관리자 없이, **현재 활성 에이전트**가 필요할 때 동료에게 제어를 넘깁니다.

---

<!-- _header: 'Module 08 · Subgraph' -->
## Subgraph — 그래프를 부품으로

```python
# 1) 작은 그래프를 컴파일
sub = sub_builder.compile()

# 2) 부모 그래프의 "노드"로 그대로 끼운다
parent.add_node("research_team", sub)
parent.add_edge(START, "research_team")
```

<div class="mermaid">
flowchart LR
  P1[intake] --> SUB[["research_team (subgraph)"]] --> P2[report]
</div>

- 복잡한 시스템을 **모듈 단위**로 쪼개 재사용·테스트
- 부모와 자식이 State를 공유하거나, 입출력만 변환해 연결

---

<!-- _header: 'Module 08 · Lab' -->
## <span class="lab">실습 08</span> 리서치 협업 시스템

<div class="cols">
<div>

```python
researcher = create_react_agent(
    llm, [web_search], name="researcher",
    prompt="사실을 수집하고 출처를 남겨라.")

writer = create_react_agent(
    llm, [], name="writer",
    prompt="수집된 내용을 보고서로 정리하라.")

team = create_supervisor(
    agents=[researcher, writer], model=llm,
    prompt="먼저 researcher, 그다음 writer.",
).compile()
```

</div>
<div>

#### 해보기

1. `team.stream(..., stream_mode="updates")` 로 누가 말하는지 추적
2. `writer`에게 도구를 빼고 **취합만** 시키기
3. Supervisor 버전을 **Swarm**으로 바꿔 차이 체감

> 모듈 09의 스트리밍으로 멀티에이전트의 내부 대화를 들여다봅니다.

</div>
</div>

---

<!-- _class: section -->
<!-- _paginate: false -->

<div class="modnum">MODULE 09</div>

# 운영 · 스트리밍 · 마무리

<div class="modsub">stream_mode · 디버깅 · 배포</div>

---

<!-- _header: 'Module 09 · Streaming' -->
## 스트리밍 — stream_mode

```python
for chunk in graph.stream(inputs, config, stream_mode="updates"):
    print(chunk)   # {노드이름: 그 노드가 반환한 갱신분}
```

| mode | 무엇이 흘러오나 | 쓰임 |
| --- | --- | --- |
| `values` | 매 단계 **전체 State** | 최종/누적 상태 표시 |
| `updates` | 노드별 **갱신분** | 진행 상황·디버깅 |
| `messages` | LLM **토큰 단위** | 챗 UI 타이핑 효과 |
| `debug` | 상세 이벤트 | 심층 디버깅 |

> 리스트로 여러 모드를 동시에: `stream_mode=["updates", "messages"]`.

---

<!-- _header: 'Module 09 · Debugging' -->
## 디버깅 — 그래프를 들여다보기

<div class="cols">
<div>

#### 구조 시각화

```python
# Mermaid 텍스트로
print(graph.get_graph().draw_mermaid())

# PNG 로
graph.get_graph().draw_mermaid_png()
```

</div>
<div>

#### 추적 · 스튜디오

- **LangSmith** — 모든 실행/토큰/지연을 추적 (`LANGSMITH_TRACING=true`)
- **LangGraph Studio** — 그래프를 시각적으로 실행·중단·되감기

```bash
pip install -U "langgraph-cli[inmem]"
langgraph dev   # 로컬 스튜디오 실행
```

</div>
</div>

---

<!-- _header: 'Module 09 · Deploy' -->
## 배포 — 그래프를 서비스로

```python
# langgraph.json 으로 그래프를 선언
{
  "dependencies": ["."],
  "graphs": { "agent": "./app.py:graph" }
}
```

- `langgraph dev` — 로컬 개발 서버 (API + 스튜디오)
- **LangGraph Platform** — 영속성·스케일링·스케줄링 포함 매니지드 배포
- 직접 배포 시: 컴파일된 그래프는 **Runnable** → FastAPI 등에 그대로 탑재

> 핵심은 같습니다 — **상태 + 노드 + 엣지**. 배포는 그 위의 얇은 껍데기일 뿐.

---

<!-- _header: 'Recap' -->
## 전체 그림 다시 보기

<div class="mermaid">
flowchart LR
  S([START]) --> AG["agent (LLM + tools)"]
  AG -->|도구 호출| TN[ToolNode]
  TN --> AG
  AG -->|승인 필요| HI{{human}}
  HI -->|resume| AG
  AG -->|완료| E([END])
  CP[(checkpointer)] -.기억·재개.- AG
</div>

- **State**에 흐르고 · **Node**가 갱신하고 · **Edge**가 잇고 · **Cycle**로 반복
- 도구·메모리·사람·여러 에이전트는 모두 이 위에 얹는 레이어

---

<!-- _header: 'Next steps' -->
## 다음 단계 & 리소스

<div class="cols">
<div>

#### 직접 만들어 볼 것

- 도구 3개짜리 ReAct 에이전트 + 메모리
- Corrective RAG에 환각 검사 추가
- Supervisor ↔ Swarm 같은 과제로 비교

</div>
<div>

#### 더 보기

- 공식 문서 · 튜토리얼 (LangGraph)
- LangSmith로 내 에이전트 추적
- `langgraph-supervisor` · `langgraph-swarm` 레포 예제

</div>
</div>

> 막히면 그래프를 그려 보세요. **흐름이 그려지면, 코드는 따라옵니다.**

---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _footer: '' -->

<div class="nodes"><span class="n"></span><span class="ln"></span><span class="n fill"></span><span class="ln"></span><span class="n"></span></div>

# 감사합니다

<span class="sub">이제 당신의 아이디어를 그래프로 그릴 차례입니다.</span>

<div class="meta">

`LangGraph 풀코스` `State · Node · Edge · Graph`

</div>
