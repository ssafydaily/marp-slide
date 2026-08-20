---
marp: true
theme: dark-plus-code
paginate: true
style: |

---


# LangGraph의 노드 함수의 반환

## 1. 반환값은 dict(또는 Command)여야 한다

노드 함수는 **State 전체를 새로 만드는 것이 아니라, 업데이트할 부분(partial update)만 담은 dict**를 반환해야 합니다.

```python
def BBQ(state: State):
    return {"messages": [llm.invoke(state["messages"])]}  # ✅ dict 반환
```

만약 dict가 아닌 다른 타입(예: 문자열, 리스트, None 등)을 반환하면 LangGraph가 이를 State 업데이트로 해석하지 못해 에러가 발생합니다.

> 참고: 최신 버전에서는 `Command(update={...}, goto="다음노드")` 형태로 반환해서 상태 업데이트와 다음 노드 라우팅을 동시에 지정할 수도 있습니다.

-----------------------

## 2. 반환하는 key는 State에 정의된 key여야 한다

LangGraph는 `graph.compile()` 시점에 State 스키마(`TypedDict`)를 보고 각 필드마다 **channel**이라는 내부 저장소를 만듭니다. 노드가 반환한 dict의 key들은 이 channel에 매핑되어 병합(merge)됩니다.

```python
class State(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

def BBQ(state: State):
    return {"messages": [...]}   # ✅ State에 정의된 key
    # return {"foo": "bar"}      # ❌ State에 없는 key → channel이 없어서 에러 발생
```

- `"messages"`처럼 State에 정의된 key만 반환할 수 있습니다.
- 정의되지 않은 key를 반환하면 해당 key에 대한 channel이 없기 때문에 `InvalidUpdateError` 류의 에러가 발생합니다.

-----------------------

## 3. 모든 key를 다 반환할 필요는 없다 (partial update)

State에 필드가 여러 개 있어도, **해당 노드에서 실제로 업데이트하는 key만** 반환하면 됩니다.

```python
class State(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    count: int

def BBQ(state: State):
    # count는 안 건드리고 messages만 업데이트
    return {"messages": [llm.invoke(state["messages"])]}
```

`count`를 반환하지 않으면 그냥 이전 값이 그대로 유지됩니다(변경 없음).

-----------------------

## 4. key별 병합 방식은 Annotated의 reducer가 결정

- `messages: Annotated[list[AnyMessage], operator.add]`처럼 reducer가 지정된 필드는 **기존 값에 append(누적)** 됩니다. (예제 코드에서 `BBQ`가 반환한 메시지가 기존 `messages` 리스트에 추가되는 이유)
- reducer가 없는 일반 필드(`count: int`)는 기본적으로 **덮어쓰기(overwrite)** 됩니다.

-----------------------

## 정리

| 규칙 | 설명 |
|---|---|
| 반환 타입 | dict (또는 Command) |
| key 제약 | State 스키마에 정의된 key만 가능 |
| 전체 key 필요 여부 | 아니오, 업데이트할 key만 partial하게 반환 |
| 병합 방식 | key별 Annotated reducer(없으면 overwrite) 따름 |

- "State에 정의된 key만 dict로 반환해야 한다"
- 없는 key를 넣으면 에러, 있는 key 중 일부만 넣는 건 정상 동작

---------------------

## 공식 문서 링크

**Graph API overview** — https://docs.langchain.com/oss/python/langgraph/graph-api

이 페이지의 "Reducers" 섹션에서 노드의 반환값이 State에 어떻게 병합되는지 정확히 설명하고 있습니다:

> 노드가 부분 업데이트(partial update)를 반환하면, LangGraph는 업데이트된 각 key마다 reducer를 호출해서 반환값을 새로운 state 값으로 저장한다: new_value = reducer(left=current_state[key], right=node_update[key])

즉 여기서 `key`가 State 스키마에 정의되어 있어야 reducer(채널)를 찾을 수 있다는 점이 핵심입니다.

---------------------

## 정리하면

| 확인하고 싶은 내용 | 공식 문서 위치 |
|---|---|
| 노드는 partial dict를 반환해야 함 | Graph API overview → "Reducers" 섹션 |
| 반환 key는 State 스키마의 key여야 함 (아니면 InvalidUpdateError) | 같은 페이지 + GitHub Discussion #1387 |
| reducer 없는 필드는 overwrite, 있으면 병합 | 같은 페이지 → "Overwrite" 섹션 |

전체 문서를 직접 보고 싶으시면 https://docs.langchain.com/oss/python/langgraph/graph-api 페이지의 "State" → "Reducers" 챕터를 확인하시면 됩니다.