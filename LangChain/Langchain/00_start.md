---
marp: true
theme: dark-plus-code
paginate: true
style: |

---

# LangChain이란?

##### LangChain은 LLM을 활용한 애플리케이션을 빠르게 만들도록 돕는 프레임워크입니다. 프롬프트 관리, 모델 호출, 출력 처리, 외부 데이터 연결, 에이전트 같은 기능을 표준화된 조립식 블록으로 제공합니다.

<div class="callout info">
<div class="callout-title">
  왜 필요할까? 
</div>

  - LLM API를 직접 호출해도 되지만, 프롬프트·검색·도구를 매번 손으로 엮으면 코드가 금방 복잡해집니다. 
  - LangChain은 이 조각들을 레고 블록처럼 끼울 수 있게 만들어 줍니다.

</div>

-----------------

# 세 가지 핵심 블록
### ProptTemplate
- 사용자 입력을 모델이 이해할 메시지로 변환

### ChatModel
- 메시지를 받아 LLM 응답을 생성 (예: ChatOpenAI)

### OutputParser
- 모델 응답을 원하는 형식(문자열·JSON)으로 변환

-----------------
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1) 프롬프트 템플릿
prompt = ChatPromptTemplate.from_template(
    "다음 질문에 한국어로 답해줘: {question}"
)
# 2) 모델
model = ChatOpenAI(model="gpt-o-mini", temperature=0)
# 3) 출력 파서
parser = StrOutputParser()

# 블록을 차례로 직접 실행
messages = prompt.invoke({"question": "프랑스의 수도는?"})
response = model.invoke(messages)
print(parser.invoke(response))   # 프랑스의 수도는 파리입니다.
```

--------------------

## 핵심 정리
- **LangChain** 은 **LLM** 앱을 위한 조립식 블록 프레임워크입니다.
- 가장 기본은 **Prompt** → **Model** → **OutputParser** 흐름입니다.
- 각 블록은 `.invoke()` 로 실행됩니다


---------------------

# LCEL — 표현 언어

> 파이프(|)로 연결하기

- LCEL(LangChain Expression Language)은 파이썬의 파이프 연산자 | 로 컴포넌트를 이어 붙이는 선언적 방식입니다. 
- 유닉스 파이프처럼 앞 블록의 출력이 뒤 블록의 입력이 됩니다.


- 파이프로 연결된 모든 것은 `Runnable` 이 되어 `invoke`(한 번), `stream`(토큰 단위), `batch`(여러 입력)를 모두 지원합니다.


-----------------------

