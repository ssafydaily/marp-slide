---
marp: true
theme: dark-plus-code
paginate: true
style: |

---

# 환경 설정

## 가상 환경 

- 가상 환경 생성

```bash
python -m venv baseline
```
- 가상 환경 활성화
```bash
source baseline/Scripts/activate
```

- 가상환경 생성후 터미널에 `(baseline)` 표시 확인하기

-----------------
## 패키지 설치

### `pip` 업데이트

```bash
python -m pip install -U pip
```

### `jupyter` 설치하기

```bash
pip install jupyter ipykernel ipywidgets
```


### 필요 패키지 설치하기

```bash
pip install -U "langgraph-cli[inmem]"
pip install -qU langgraph langchain langsmith langchain-openai python-dotenv
```

-----------------

## `jupyter` 서버 실행하기

```bash
python -m jupyter lab --ContentsManager.allow_hidden=True
```
> 숨김 파일 설정
- **settings > Settings Editor** 메뉴 선택하고, **hidden** 검색

<div class="cols">
<div>

![h:300](images/settings_editor.png)
</div>
<div>

- `Show Hiddens Files` 선택

![](images/show_hidden.png){width=500px}

</div>
</div>


-----------------
## LangSmith API key 발급
- [LangSmith 가입하기](https://smith.langchain.com/)
- 로그인 후 `settings` > `API keys` > `+API key` 버튼 클릭

![h:400](images/langsmith_key1.png)

-----------------

### Key 생성하고 복사
<div class="cols">
<div>

![](images/langsmith_key2.png)

</div>
<div>

![](images/langsmith_key3.png)

- key를 복사해서 저장하기

</div>
</div>


-----------------

## `.env` 파일 작성하기

```
GMS_KEY="your-key"
OPENAI_BASE_URL=https://gms.ssafy.io/gmsapi/api.openai.com/v1

# important!!!
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY="your-key"

# optional
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_PROJECT="my-first-project"
```
- [중요] `git` 저장소 사용한다면 `.gitignore` file 작성합니다.

-----------------

## `langgraph.json` 작성

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./app.py:agent"
  },
  "env": ".env"
}
```
------------------------
## 코드 작성하기
- `app.py` 이름으로 코드 작성하기

<div class="cols">
<div>

```python
# llm.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
# graph.py
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",  # 사용 가능한 모델명은 SSAFY 문서 확인
    api_key=os.getenv("GMS_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)
```
</div>
<div>

```python
# 1) 상태(State) 정의
class GraphState(TypedDict):
    question: str
    answer: str

# 2) 노드 함수 정의
def call_model(state: GraphState) -> GraphState:
    response = llm.invoke(state["question"])
    return {"question": state["question"], "answer": response.content}

# 3) 그래프 빌드
builder = StateGraph(GraphState)
builder.add_node("call_model", call_model)
builder.add_edge(START, "call_model")
builder.add_edge("call_model", END)

graph = builder.compile()

result = graph.invoke({"question": "LangGraph가 뭐야?", "answer": ""})
print(result["answer"])
```

</div>
</div>


-----------------

## `langgraph` 실행하기

<div class="cols">
<div>

- 터미널 실행하기

![](images/run_terminal.png)

</div>
<div>

- langgraph 실행
```bash
lagngraph dev
```

![](images/langgraph_dev.png)

</div>
</div>

<div class="callout tip">
<div class="callout-title">
  TIP - 인코딩 문제 발생 시 실행 하기
</div>

  ```
  python -X utf8 -m langgraph_cli dev
  ```
</div>

-----------------

#### [참고] docker의 jupyter lab에서 숨김 파일 다루기
> - `docker-compose.yml` 파일에 다음 내용 추가
```
command: > 
      jupyter lab --ip=0.0.0.0 --allow-root --ContentsManager.allow_hidden=True
```

- 이미지 첨부>

![](images/docker_hidden_file.png){width=500px}


#### 

> - 무한루프가 돌거나, 이전 실행결과만 나오는 경우

```
taskkill /F /IM python.exe
```

