충분한 정보를 모았으니 정리해서 설명드릴게요. 둘 다 **LangChain/LangGraph 생태계에서 "도구를 쓰는 에이전트(ReAct 패턴)"를 손쉽게 만들어주는 팩토리 함수**인데, 하나가 다른 하나를 대체하는 관계입니다.

## 1. 개요

| | `create_react_agent` | `create_agent` |
|---|---|---|
| 소속 패키지 | `langgraph.prebuilt` | `langchain.agents` |
| 상태 | **v1부터 deprecated** (구버전) | **신규 표준** (LangGraph v1 / LangChain v1부터) |
| 내부 동작 | LangGraph의 `StateGraph` 위에서 동작 | 마찬가지로 LangGraph 위에서 동작 (내부적으로 `create_react_agent`의 후속 구현) |
| 확장 방식 | 제한적인 hook (`pre_model_hook`, `post_model_hook` 등) | **미들웨어(middleware) 시스템**으로 확장 |

LangGraph v1은 create_react_agent를 폐지(deprecate)하고, 미들웨어 시스템을 추가한 LangChain의 create_agent를 사용하도록 안내합니다. 즉 **`create_agent`가 `create_react_agent`의 공식 후속(successor)** 입니다.

두 함수 모두 **ReAct 패턴**(모델이 추론 → 도구 호출 → 결과 관찰 → 다시 추론... 을 반복하다가 최종 답을 내는 루프)을 자동으로 그래프로 구성해줍니다.

## 2. 기본 사용법

**구버전 (`create_react_agent`, deprecated)**
```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model,
    tools,
    prompt="You are a helpful assistant.",
)
```

**신버전 (`create_agent`, 권장)**
```python
from langchain.agents import create_agent

agent = create_agent(
    model,
    tools,
    system_prompt="You are a helpful assistant.",
)

result = agent.invoke({"messages": [{"role": "user", "content": "..."}]})
```

거의 동일한 시그니처지만 `prompt=` 파라미터 이름이 `system_prompt=`로 바뀌었습니다.

## 3. 주요 차이점

- **확장성**: `create_agent`는 before/after agent, before/after model, wrap model/tool calls 등 여러 지점에서 개입할 수 있는 미들웨어 아키텍처를 제공합니다. 이를 통해 human-in-the-loop, PII 필터링, 대화 요약(컨텍스트 관리), 동적 프롬프트 생성 같은 기능을 재사용 가능한 컴포넌트로 붙일 수 있습니다.
- **모델 파라미터**: "provider:model" 형태의 문자열이나 초기화된 모델 인스턴스를 model로 전달할 수 있는 건 동일하지만, 동적 모델 선택 같은 기능은 미들웨어 기반으로 더 유연해졌습니다.
- **구조화된 출력(response_format)**: v1부터는 프롬프트 기반 JSON 출력 방식을 지원하지 않고, Pydantic/TypedDict/JSON Schema 같은 명시적 스키마만 지원합니다.
- **툴 검증**: 구버전의 `ValidationNode`가 하던 역할이 create_agent에서는 도구가 자동으로 입력을 검증하는 방식으로 흡수되었습니다.
- **State 클래스**: `AgentState`, `AgentStateWithStructuredResponse` 등도 `langgraph.prebuilt`가 아닌 `langchain.agents` 쪽으로 이전되었습니다 (pydantic 기반 상태는 더 이상 지원 안 함).

## 4. 주의사항

1. **Python 버전**: LangChain v1부터 Python 3.10 이상이 필요합니다 (3.9는 2025년 10월 EOL).
2. **미들웨어 사용 시 제약**: 미들웨어를 쓸 경우 model 파라미터는 문자열이나 BaseChatModel만 가능하고, prompt는 문자열 또는 None만 가능합니다 (커스텀 callable 불가).
3. **일부 기능 누락 이슈 보고됨**: create_react_agent에서 지원되던 "상태 함수로 메시지 히스토리를 재작성하는" 기능이 create_agent에는 아직 없다는 포럼 이슈가 있습니다. 세밀한 커스터마이징을 하던 프로젝트라면 마이그레이션 전에 필요한 기능이 미들웨어로 대체 가능한지 확인이 필요합니다.
4. **마이그레이션은 대체로 쉬움**: LangGraph v1은 대체로 하위 호환되며, 핵심 변경은 create_react_agent → create_agent 전환 정도라 대부분의 기존 코드는 import 경로와 `prompt`→`system_prompt` 정도만 바꾸면 동작합니다.
5. **신규 프로젝트는 `create_agent`로 시작 권장**: deprecated 함수는 당장은 동작하더라도 향후 버전에서 제거될 수 있으므로, 신규 개발은 처음부터 `langchain.agents.create_agent`를 쓰는 것이 안전합니다.
6. **Deep Agents와의 관계**: Deep Agents는 create_agent를 기반으로 planning, 파일시스템 도구, 서브에이전트, 메모리 등을 미리 구성해둔 것이며, 직접 harness를 세밀하게 제어하고 싶다면 `create_agent`를, 이미 구성된 고급 기능이 필요하면 Deep Agents를 고려하면 됩니다.

## 요약

- 지금 새 프로젝트를 시작한다면 → **`langchain.agents.create_agent`** 사용
- 기존에 `langgraph.prebuilt.create_react_agent`로 만든 코드가 있다면 → 여전히 동작은 하지만 **deprecated**이므로 위 표의 매핑을 참고해 마이그레이션 권장
- 핵심 차이는 "미들웨어 시스템 유무"이며, 이것이 human-in-the-loop, 컨텍스트 관리, 가드레일 등 실무 기능 확장의 표준 방식이 되었습니다.