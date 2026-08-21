ReAct 패턴은 모델이 "생각(Reason) → 행동(Act, 도구 호출) → 관찰(Observe) → 다시 생각..."을 반복하는 구조이기 때문에, 시스템 프롬프트는 이 루프가 잘 돌아가도록 **역할, 도구 사용 원칙, 종료 조건, 실패 처리**를 명확히 짚어줘야 합니다. `create_agent`/`create_react_agent`류를 쓰면 도구 호출 자체의 포맷팅(JSON tool call 등)은 프레임워크가 알아서 처리하므로, 프롬프트는 "언제/왜/어떻게" 도구를 쓸지에 집중하면 됩니다.

## 1. 기본 구조

```
1. 역할과 목표 정의 (Role & Goal)
2. 사용 가능한 도구와 사용 시점 (Tool usage policy)
3. 추론 방식 안내 (Reasoning guidance) — 필요할 때만
4. 종료/답변 조건 (When to stop and answer)
5. 실패·불확실성 처리 (Error/uncertainty handling)
6. 출력 형식 (Output format, 필요 시)
```

## 2. 각 항목별 작성 요령

**① 역할/목표**
- 짧고 구체적으로. "너는 유능한 비서다" 같은 막연한 문장보다 "너는 고객 주문 상태를 조회하고 답하는 지원 에이전트다"처럼 도메인을 명시.

**② 도구 사용 원칙 — 가장 중요한 부분**
- 도구 설명(docstring)에 의존하지 말고, *언제 써야 하는지* 정책을 프롬프트에 명시:
  - "확실하지 않은 사실 정보는 반드시 도구로 검증한 후 답하라"
  - "같은 도구를 반복 호출하기 전에 이전 결과를 재확인하라"
  - "도구 호출 결과가 비어있으면 다른 검색어로 한 번 더 시도하고, 그래도 없으면 사용자에게 없다고 말하라"
- 도구 간 우선순위가 있으면 명시 (예: "내부 DB 조회가 가능하면 웹 검색보다 우선").

**③ 추론 방식**
- 최신 모델(특히 Claude, GPT-4급)은 "Thought:", "Action:" 같은 전통적 ReAct 텍스트 포맷을 강제로 흉내 내라고 시킬 필요가 거의 없습니다. 프레임워크가 tool_calls를 구조화해서 처리하기 때문입니다.
- 대신 "복잡한 작업은 단계를 나눠 처리하라", "다음 행동을 정하기 전에 지금까지의 결과를 요약해보라" 같은 **가벼운 지침**만 주는 게 실전에서 더 안정적입니다. 과도하게 "반드시 Thought/Action/Observation 형식으로 출력하라"고 강제하면 오히려 구조화된 tool calling과 충돌하거나 불필요한 장황함(verbosity)을 유발할 수 있습니다.

**④ 종료 조건**
- 무한 루프나 불필요한 도구 호출을 막기 위해 명시:
  - "필요한 정보를 모두 얻었으면 더 이상 도구를 호출하지 말고 최종 답변을 하라"
  - "최대 N번 도구를 호출해도 답을 못 찾으면, 아는 한도 내에서 최선의 답을 제시하고 한계를 밝혀라"

**⑤ 실패/불확실성 처리**
- 도구 에러, 빈 결과, 모순되는 정보에 대한 대응 방침을 미리 정의해두면 프로덕션에서 안정성이 크게 올라갑니다.
  - "도구 호출이 실패하면 한 번 재시도하고, 계속 실패하면 사용자에게 알려라"
  - "여러 출처 정보가 상충하면 최신 것을 우선하고 불확실성을 명시하라"

**⑥ 출력 형식** (필요한 경우만)
- 최종 답변의 톤, 언어, 인용 방식, 길이 제한 등.

## 3. 실전 팁

- **너무 길게 쓰지 마세요.** ReAct 에이전트 프롬프트는 도구 목록이 이미 컨텍스트를 차지하므로, 시스템 프롬프트는 "정책" 위주로 간결하게 유지하는 게 낫습니다. 장황한 프롬프트는 오히려 도구 호출 판단을 흐릴 수 있습니다.
- **긍정문으로 지시하세요.** "~하지 마라"보다 "~할 때만 도구를 써라" 식으로 원하는 행동을 직접 지정하는 편이 모델이 따르기 쉽습니다.
- **예시(few-shot)가 필요하면 짧게.** 도구 호출 패턴이 특이하거나 도메인 특화된 경우, 1~2개의 좋은 예시가 긴 설명보다 효과적일 때가 많습니다.
- **`create_agent`의 미들웨어와 역할 분담을 고려하세요.** 예를 들어 "대화가 길어지면 요약하라" 같은 로직은 프롬프트에 글로 쓰기보다 `SummarizationMiddleware` 같은 미들웨어로 처리하는 게 더 안정적입니다. 즉 *정책/의도*는 프롬프트에, *메커니즘*(재시도, 요약, 사람 확인 등)은 미들웨어에 맡기는 식으로 역할을 나누면 유지보수가 쉬워집니다.
- **반복 테스트가 필수.** ReAct 에이전트는 실행 경로가 비결정적이므로, 실제 여러 케이스로 굴려보면서 "불필요한 도구 호출", "조기 종료", "무한 루프" 같은 실패 패턴을 찾아 프롬프트를 다듬는 과정이 거의 항상 필요합니다.

## 예시 템플릿

```
You are a support agent that answers questions about customer orders.

Tool usage:
- Use the `lookup_order` tool whenever the user references a specific order number or asks about order status.
- Use `search_faq` only when the question is about policy, not a specific order.
- Never guess order details — always verify via tools before stating them as fact.

Stopping condition:
- Once you have the information needed, answer directly without further tool calls.
- If a tool call fails twice, tell the user you couldn't retrieve the info and suggest they try again later.

Tone: concise, friendly, in the user's language.
```

더 구체적인 도메인(예: 코딩 에이전트, 검색 에이전트, 멀티에이전트 오케스트레이션 등)을 알려주시면 그에 맞춰 프롬프트 예시를 다듬어드릴 수 있어요.


```
당신은 고객 주문에 대한 질문에 답변하는 상담 에이전트입니다.

도구 사용 원칙:
- 사용자가 특정 주문 번호를 언급하거나 주문 상태를 물어볼 때는 항상 `lookup_order` 도구를 사용하세요.
- `search_faq`는 특정 주문이 아니라 정책 관련 질문일 때만 사용하세요.
- 주문 세부 정보를 추측하지 마세요 — 사실로 답하기 전에 반드시 도구로 확인하세요.

종료 조건:
- 필요한 정보를 얻었으면 더 이상 도구를 호출하지 말고 바로 답변하세요.
- 도구 호출이 두 번 실패하면, 사용자에게 정보를 가져올 수 없다고 알리고 나중에 다시 시도해달라고 안내하세요.

어조: 간결하고 친절하게, 사용자가 사용하는 언어로 답변하세요.
```