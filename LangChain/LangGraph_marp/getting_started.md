# LangSmith 완전 가이드: Trace · Debug · Observer

> **LangSmith**는 LangChain이 제공하는 LLM 애플리케이션 관측·평가·디버깅 플랫폼입니다.  
> 프로덕션 환경에서 AI 파이프라인의 내부 동작을 추적하고 품질을 측정하는 데 특화되어 있습니다.

---

## 목차

1. [LangSmith 개요](#1-langsmith-개요)
2. [환경 설정](#2-환경-설정)
3. [Tracing — 실행 흐름 추적](#3-tracing--실행-흐름-추적)
4. [Debugging — 문제 진단](#4-debugging--문제-진단)
5. [Observer (Feedback & Evaluation)](#5-observer-feedback--evaluation)
6. [Projects & Dataset 관리](#6-projects--dataset-관리)
7. [실전 예시: RAG 파이프라인 완전 추적](#7-실전-예시-rag-파이프라인-완전-추적)
8. [자주 발생하는 문제와 해결책](#8-자주-발생하는-문제와-해결책)
9. [참고 자료](#9-참고-자료)

---

## 1. LangSmith 개요

### 1.1 왜 LangSmith인가?

LLM 애플리케이션은 일반 소프트웨어와 달리 **비결정적(non-deterministic)** 입니다. 같은 입력에도 출력이 달라질 수 있고, 복잡한 체인·에이전트 내부에서 무슨 일이 일어나는지 `print()`로는 파악하기 어렵습니다. LangSmith는 이 문제를 해결합니다.

| 문제 | LangSmith 해결책 |
|------|-----------------|
| "LLM이 왜 이런 답변을 했지?" | **Trace** — 모든 LLM 호출·도구 실행을 트리 구조로 시각화 |
| "어느 단계에서 오류가 발생했지?" | **Debug** — 입·출력, 지연시간, 오류 메시지를 단계별로 확인 |
| "품질이 괜찮은지 어떻게 측정하지?" | **Observer** — 자동·수동 평가(Evaluator) 및 사용자 피드백 수집 |

### 1.2 핵심 개념

```
Run (실행 단위)
 ├── Root Run        — 전체 파이프라인의 최상위 실행
 ├── Chain Run       — LangChain Chain 한 번의 실행
 ├── LLM Run         — 실제 LLM API 호출
 └── Tool Run        — 도구(Tool) 한 번의 실행

Trace  — Run들의 계층적 트리 전체
Project — Trace를 그룹화하는 논리적 단위
Dataset — 입·출력 예시의 컬렉션 (평가·회귀 테스트에 사용)
```

---

## 2. 환경 설정

### 2.1 패키지 설치

```bash
pip install langsmith langchain langchain-openai
```

### 2.2 환경 변수 설정

```bash
# .env 파일 또는 터미널에서 설정
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY="ls__xxxxxxxxxxxxxxxx"   # LangSmith API 키
export LANGCHAIN_PROJECT="my-project"              # 프로젝트 이름 (기본값: default)
export OPENAI_API_KEY="sk-..."
```

> **팁**: `python-dotenv`를 사용하면 `.env` 파일을 자동으로 로드할 수 있습니다.

```python
from dotenv import load_dotenv
load_dotenv()
```

### 2.3 LangSmith Client 초기화

```python
from langsmith import Client

client = Client()
# API 키가 환경변수에 있으면 자동 감지됩니다.
```

---

## 3. Tracing — 실행 흐름 추적

Tracing은 LangSmith의 핵심 기능입니다. LLM 애플리케이션이 실행되는 동안 **모든 단계의 입력·출력·지연시간·토큰 사용량**을 자동으로 수집합니다.

### 3.1 자동 Tracing (LangChain 사용 시)

환경변수만 설정하면 LangChain의 모든 컴포넌트가 자동으로 추적됩니다.

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "ls__..."

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 별도 코드 없이 자동 추적됩니다.
llm = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_template("다음 주제를 한 문단으로 설명해줘: {topic}")
chain = prompt | llm

result = chain.invoke({"topic": "양자 컴퓨팅"})
print(result.content)
# → LangSmith UI에 자동으로 Trace가 생성됩니다.
```

### 3.2 수동 Tracing — `@traceable` 데코레이터

LangChain을 사용하지 않는 일반 Python 함수도 추적할 수 있습니다.

```python
from langsmith import traceable
from openai import OpenAI

openai_client = OpenAI()

@traceable(name="문서 요약", run_type="llm")
def summarize(text: str) -> str:
    """긴 문서를 3줄로 요약하는 함수"""
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "문서를 3줄로 요약해줘."},
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content

@traceable(name="키워드 추출", run_type="tool")
def extract_keywords(text: str) -> list[str]:
    """텍스트에서 핵심 키워드를 추출하는 함수"""
    # 간단한 예시
    words = text.split()
    return [w for w in words if len(w) > 4][:5]

@traceable(name="문서 분석 파이프라인")
def analyze_document(document: str) -> dict:
    """요약 + 키워드 추출을 합쳐서 반환"""
    summary = summarize(document)
    keywords = extract_keywords(document)
    return {"summary": summary, "keywords": keywords}

# 실행 — 중첩된 Trace가 계층적으로 기록됩니다.
result = analyze_document("인공지능은 컴퓨터 과학의 한 분야로...")
```

### 3.3 Context Manager로 Trace 제어

```python
from langsmith import trace

with trace(
    name="사용자 쿼리 처리",
    run_type="chain",
    inputs={"query": "서울 날씨 알려줘"},
    tags=["production", "weather"],
    metadata={"user_id": "user_42", "session_id": "sess_001"},
) as run:
    # 내부 로직 실행
    answer = "오늘 서울 날씨는 맑고 기온은 28도입니다."
    
    # 출력을 명시적으로 기록
    run.end(outputs={"answer": answer})
```

### 3.4 Trace에서 볼 수 있는 정보

LangSmith UI에서 각 Trace를 열면 다음을 확인할 수 있습니다.

```
Trace 상세 화면
├── 실행 시간 (타임스탬프 및 지속시간)
├── 입력 (Inputs)
│   ├── 프롬프트 전체 내용
│   └── 변수 값
├── 출력 (Outputs)
│   └── LLM 응답 전체
├── 토큰 사용량
│   ├── Prompt tokens: 120
│   ├── Completion tokens: 85
│   └── Total tokens: 205
├── 모델 파라미터 (temperature, max_tokens 등)
├── 지연시간 (latency)
├── 오류 메시지 (실패 시)
└── 자식 Run 목록 (중첩 구조)
```

---

## 4. Debugging — 문제 진단

### 4.1 오류 Trace 식별

LangSmith UI에서 **빨간색** Run은 오류가 발생한 실행입니다. 클릭하면 전체 스택 트레이스와 오류 발생 시점의 입·출력을 확인할 수 있습니다.

```python
from langsmith import traceable

@traceable(name="검색 도구")
def search_web(query: str) -> str:
    if not query:
        raise ValueError("검색어가 비어 있습니다.")  # 이 오류가 LangSmith에 기록됩니다.
    return f"'{query}'에 대한 검색 결과..."

@traceable(name="QA 체인")
def qa_chain(question: str) -> str:
    try:
        context = search_web(question)
        return f"답변: {context}"
    except ValueError as e:
        # 오류가 상위 Run에도 전파되어 Trace 트리 전체가 실패로 표시됩니다.
        raise
```

### 4.2 Run 필터링으로 문제 Run 찾기

```python
from langsmith import Client
from datetime import datetime, timedelta

client = Client()

# 최근 24시간 내 오류가 발생한 Run 조회
error_runs = client.list_runs(
    project_name="my-project",
    error=True,
    start_time=datetime.now() - timedelta(hours=24),
)

for run in error_runs:
    print(f"[{run.start_time}] Run ID: {run.id}")
    print(f"  오류: {run.error}")
    print(f"  입력: {run.inputs}")
    print()
```

### 4.3 특정 Run 상세 조회

```python
# Run ID로 직접 조회
run = client.read_run("run-id-xxxx-xxxx")

print("=== Run 상세 정보 ===")
print(f"이름: {run.name}")
print(f"상태: {run.status}")  # 'success' or 'error'
print(f"입력: {run.inputs}")
print(f"출력: {run.outputs}")
print(f"오류: {run.error}")
print(f"소요시간: {run.end_time - run.start_time}")
print(f"총 토큰: {run.total_tokens}")
```

### 4.4 지연시간(Latency) 분석

```python
from langsmith import Client
import statistics

client = Client()

runs = list(client.list_runs(
    project_name="my-project",
    run_type="llm",
    limit=100,
))

latencies = [
    (r.end_time - r.start_time).total_seconds()
    for r in runs
    if r.end_time and r.start_time
]

print(f"평균 지연시간: {statistics.mean(latencies):.2f}초")
print(f"중앙값: {statistics.median(latencies):.2f}초")
print(f"최대값: {max(latencies):.2f}초")
print(f"최소값: {min(latencies):.2f}초")
```

### 4.5 프롬프트 비교 디버깅

LangSmith UI의 **Playground** 기능을 사용하면, 기록된 Run의 프롬프트를 바로 수정하고 재실행해볼 수 있습니다.

1. LangSmith UI에서 특정 Run 클릭
2. 우측 상단 **"Open in Playground"** 버튼 클릭
3. 프롬프트 수정 후 **Run** 버튼으로 즉시 재실행
4. 원본과 수정 버전 결과를 나란히 비교

---

## 5. Observer (Feedback & Evaluation)

Observer 기능은 **AI 출력의 품질을 정량적으로 측정**합니다. 사람의 평가(Human Feedback)와 자동 평가(Automated Evaluation)를 모두 지원합니다.

### 5.1 Human Feedback — 사용자 피드백 수집

```python
from langsmith import Client, traceable

client = Client()

@traceable(name="챗봇 응답")
def chatbot_response(user_message: str) -> str:
    # ... LLM 호출 ...
    return "안녕하세요! 무엇을 도와드릴까요?"

# Run 실행 후 run_id를 받아서 피드백을 기록합니다.
import langsmith

with langsmith.trace("사용자 세션") as run_tree:
    response = chatbot_response("안녕")
    run_id = run_tree.id

# 사용자가 👍를 누른 경우 피드백 기록
client.create_feedback(
    run_id=run_id,
    key="user_satisfaction",     # 피드백 키 (자유롭게 지정)
    score=1,                     # 1 = 긍정, 0 = 부정
    comment="답변이 정확하고 도움이 됐어요.",
)

# 별점(1~5) 형태의 피드백
client.create_feedback(
    run_id=run_id,
    key="rating",
    score=4.5,
    comment="거의 완벽하지만 조금 더 구체적이면 좋겠어요.",
)
```

### 5.2 Automated Evaluation — 자동 평가

#### 방법 1: LangChain Evaluator 사용

```python
from langchain.evaluation import load_evaluator
from langsmith import Client

client = Client()
evaluator = load_evaluator("criteria", criteria="helpfulness")

# 평가할 Run 목록 조회
runs = client.list_runs(project_name="my-project", limit=10)

for run in runs:
    if run.outputs and "output" in run.outputs:
        result = evaluator.evaluate_strings(
            input=str(run.inputs),
            prediction=str(run.outputs["output"]),
        )
        
        # 평가 결과를 LangSmith에 기록
        client.create_feedback(
            run_id=run.id,
            key="helpfulness",
            score=result["score"],
            comment=result.get("reasoning", ""),
        )
        print(f"Run {run.id}: helpfulness = {result['score']}")
```

#### 방법 2: LLM-as-Judge 평가

```python
from langsmith import Client, evaluate
from langchain_openai import ChatOpenAI

client = Client()

# 평가 함수 정의
def correctness_evaluator(run, example):
    """LLM을 사용해서 정확도를 평가하는 Evaluator"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    prompt = f"""다음 질문에 대한 답변의 정확도를 0~1 사이 점수로 평가하세요.
    
질문: {example.inputs['question']}
정답: {example.outputs['answer']}
모델 답변: {run.outputs['output']}

0.0 ~ 1.0 사이 숫자만 반환하세요."""
    
    response = llm.invoke(prompt)
    score = float(response.content.strip())
    
    return {"key": "correctness", "score": score}


# Dataset에 대해 평가 실행
results = evaluate(
    lambda inputs: {"output": my_chain(inputs["question"])},
    data="my-qa-dataset",          # Dataset 이름
    evaluators=[correctness_evaluator],
    experiment_prefix="gpt4o-mini-test",
)
```

### 5.3 Run Rules — 실시간 자동 평가 트리거

LangSmith UI에서 **Rules**를 설정하면, 새로운 Run이 들어올 때마다 자동으로 평가가 실행됩니다.

설정 경로: `Project → Rules → + New Rule`

```
Rule 예시 설정:
- 이름: "긴 응답 품질 평가"
- 트리거: run.total_tokens > 500
- 액션: LLM Evaluator 실행 (criteria: coherence)
- 샘플링: 20% (모든 Run에 적용하면 비용 증가)
```

### 5.4 Feedback 집계 조회

```python
from langsmith import Client

client = Client()

# 특정 프로젝트의 피드백 통계 조회
feedbacks = client.list_feedback(
    run_ids=None,  # None이면 프로젝트 전체
)

scores = {}
for fb in feedbacks:
    key = fb.key
    if key not in scores:
        scores[key] = []
    if fb.score is not None:
        scores[key].append(fb.score)

for key, score_list in scores.items():
    avg = sum(score_list) / len(score_list)
    print(f"{key}: 평균 {avg:.2f} (n={len(score_list)})")
```

---

## 6. Projects & Dataset 관리

### 6.1 Project 생성 및 전환

```python
from langsmith import Client
import os

client = Client()

# 프로젝트 생성
client.create_project(
    project_name="production-chatbot",
    description="프로덕션 챗봇 모니터링",
)

# 실행 중 프로젝트 전환
os.environ["LANGCHAIN_PROJECT"] = "production-chatbot"

# 또는 traceable에서 직접 지정
from langsmith import traceable

@traceable(project_name="production-chatbot")
def my_function(input: str) -> str:
    return input
```

### 6.2 Dataset 생성 및 관리

Dataset은 **평가·회귀 테스트**에 사용되는 입·출력 예시 컬렉션입니다.

```python
from langsmith import Client

client = Client()

# Dataset 생성
dataset = client.create_dataset(
    dataset_name="FAQ 데이터셋",
    description="자주 묻는 질문과 정답 모음",
)

# 예시 데이터 추가
examples = [
    {
        "inputs": {"question": "LangSmith란 무엇인가요?"},
        "outputs": {"answer": "LangSmith는 LLM 애플리케이션을 위한 관측·평가 플랫폼입니다."},
    },
    {
        "inputs": {"question": "Trace와 Run의 차이는?"},
        "outputs": {"answer": "Run은 단일 실행 단위이고, Trace는 계층적으로 연결된 Run의 전체 트리입니다."},
    },
    {
        "inputs": {"question": "LangSmith 비용은?"},
        "outputs": {"answer": "Developer 플랜은 무료이며, 월 5,000 Trace까지 제공됩니다."},
    },
]

client.create_examples(
    inputs=[e["inputs"] for e in examples],
    outputs=[e["outputs"] for e in examples],
    dataset_id=dataset.id,
)

print(f"Dataset '{dataset.name}' 생성 완료 (ID: {dataset.id})")
```

### 6.3 실패한 Run에서 Dataset 자동 생성

```python
from langsmith import Client
from datetime import datetime, timedelta

client = Client()

# 오류 Run들을 Dataset으로 저장 (디버깅용)
error_dataset = client.create_dataset("오류 케이스 모음")

error_runs = client.list_runs(
    project_name="my-project",
    error=True,
    start_time=datetime.now() - timedelta(days=7),
)

for run in error_runs:
    if run.inputs:
        client.create_examples(
            inputs=[run.inputs],
            dataset_id=error_dataset.id,
        )

print("오류 케이스 Dataset 생성 완료")
```

---

## 7. 실전 예시: RAG 파이프라인 완전 추적

실제 RAG(Retrieval-Augmented Generation) 파이프라인에 LangSmith를 통합하는 전체 예시입니다.

```python
import os
from langsmith import traceable, Client
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate

# LangSmith 활성화
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "rag-pipeline-demo"

client = Client()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings()

# 샘플 문서 (실제로는 외부 소스에서 로드)
DOCUMENTS = [
    "LangSmith는 LLM 애플리케이션의 디버깅과 평가를 돕는 플랫폼입니다.",
    "Trace 기능으로 복잡한 LLM 체인의 실행 흐름을 단계별로 확인할 수 있습니다.",
    "Dataset을 만들어 회귀 테스트와 자동 평가를 수행할 수 있습니다.",
    "피드백(Feedback) API로 사용자 만족도를 정량적으로 측정합니다.",
]


@traceable(name="벡터 검색", run_type="retriever", tags=["rag"])
def retrieve_documents(query: str, k: int = 3) -> list[str]:
    """쿼리와 가장 유사한 문서를 벡터 DB에서 검색합니다."""
    vectorstore = FAISS.from_texts(DOCUMENTS, embeddings)
    docs = vectorstore.similarity_search(query, k=k)
    return [doc.page_content for doc in docs]


@traceable(name="프롬프트 구성", run_type="chain", tags=["rag"])
def build_prompt(query: str, context_docs: list[str]) -> str:
    """검색된 문서를 바탕으로 프롬프트를 구성합니다."""
    context = "\n".join(f"- {doc}" for doc in context_docs)
    return f"""다음 컨텍스트를 참고하여 질문에 답하세요.

컨텍스트:
{context}

질문: {query}
답변:"""


@traceable(name="LLM 생성", run_type="llm", tags=["rag"])
def generate_answer(prompt: str) -> str:
    """LLM으로 최종 답변을 생성합니다."""
    response = llm.invoke(prompt)
    return response.content


@traceable(
    name="RAG 파이프라인",
    run_type="chain",
    tags=["rag", "production"],
    metadata={"version": "v1.2"},
)
def rag_pipeline(query: str, user_id: str = "anonymous") -> dict:
    """전체 RAG 파이프라인 실행"""
    
    # 1단계: 문서 검색
    docs = retrieve_documents(query)
    
    # 2단계: 프롬프트 구성
    prompt = build_prompt(query, docs)
    
    # 3단계: 답변 생성
    answer = generate_answer(prompt)
    
    return {
        "query": query,
        "retrieved_docs": docs,
        "answer": answer,
    }


# ────────────────────────────────────────────
# 실행 및 피드백 기록
# ────────────────────────────────────────────
import langsmith

if __name__ == "__main__":
    query = "LangSmith의 Trace 기능은 무엇인가요?"
    
    with langsmith.trace("사용자 요청 처리", metadata={"user_id": "user_123"}) as run_tree:
        result = rag_pipeline(query, user_id="user_123")
        run_id = run_tree.id
    
    print("=== RAG 파이프라인 결과 ===")
    print(f"질문: {result['query']}")
    print(f"검색된 문서: {len(result['retrieved_docs'])}개")
    print(f"답변: {result['answer']}")
    
    # 사용자 피드백 시뮬레이션
    client.create_feedback(
        run_id=run_id,
        key="relevance",
        score=0.95,
        comment="답변이 질문과 매우 관련성이 높습니다.",
    )
    
    print(f"\nLangSmith에서 Trace 확인: https://smith.langchain.com")
    print(f"Run ID: {run_id}")
```

### 실행 시 LangSmith UI에서 보이는 Trace 구조

```
RAG 파이프라인                    [chain]  ✅  1.23s
├── 벡터 검색                     [retriever]  ✅  0.31s
│   └── OpenAIEmbeddings          [llm]  ✅  0.28s
├── 프롬프트 구성                 [chain]  ✅  0.001s
└── LLM 생성                     [llm]  ✅  0.91s
    └── ChatOpenAI               
        ├── prompt_tokens: 187
        ├── completion_tokens: 72
        └── total_tokens: 259
```

---

## 8. 자주 발생하는 문제와 해결책

### 문제 1: Trace가 LangSmith에 나타나지 않는다

**원인 확인 체크리스트**:

```python
import os

# 환경변수 확인
print("TRACING:", os.getenv("LANGCHAIN_TRACING_V2"))  # "true"여야 함
print("API KEY:", os.getenv("LANGCHAIN_API_KEY"))      # "ls__..." 형태
print("PROJECT:", os.getenv("LANGCHAIN_PROJECT"))      # 프로젝트 이름

# API 키 유효성 확인
from langsmith import Client
client = Client()
try:
    projects = list(client.list_projects())
    print(f"연결 성공: {len(projects)}개 프로젝트")
except Exception as e:
    print(f"연결 실패: {e}")
```

### 문제 2: `@traceable` 함수가 비동기 환경에서 작동하지 않는다

```python
from langsmith import traceable
import asyncio

# ❌ 잘못된 방법 (동기 traceable을 비동기에서 사용)
@traceable
def sync_function(x):
    return x

# ✅ 올바른 방법 (비동기 함수에도 traceable 적용 가능)
@traceable
async def async_function(x: str) -> str:
    await asyncio.sleep(0.1)  # 비동기 작업
    return x.upper()

async def main():
    result = await async_function("hello")
    print(result)

asyncio.run(main())
```

### 문제 3: 토큰 사용량이 Trace에 기록되지 않는다

```python
from langsmith import traceable

# run_type="llm"을 명시해야 토큰 정보가 기록됩니다.
@traceable(run_type="llm")  # ← 반드시 지정
def call_llm(prompt: str) -> dict:
    # openai 클라이언트 직접 사용 시
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return {
        "output": response.choices[0].message.content,
        "usage": {  # 수동으로 usage 반환 시 LangSmith가 인식합니다.
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
        }
    }
```

### 문제 4: 배치(Batch) 처리 시 Trace가 섞인다

```python
from langsmith import traceable
from concurrent.futures import ThreadPoolExecutor

@traceable(name="단일 처리")
def process_one(item: str) -> str:
    return item.upper()

# 멀티스레드 환경에서는 각 스레드가 독립적인 Trace를 가집니다.
# 부모-자식 관계를 유지하려면 langsmith_extra를 사용하세요.
@traceable(name="배치 처리")
def process_batch(items: list[str]) -> list[str]:
    results = []
    for item in items:
        result = process_one(item)  # 자동으로 부모 Trace 하위에 기록됩니다.
        results.append(result)
    return results
```

---

## 9. 참고 자료

| 자료 | 링크 |
|------|------|
| LangSmith 공식 문서 | https://docs.smith.langchain.com |
| LangSmith Python SDK | https://github.com/langchain-ai/langsmith-sdk |
| LangSmith UI | https://smith.langchain.com |
| LangChain 공식 문서 | https://python.langchain.com |
| Evaluation 가이드 | https://docs.smith.langchain.com/evaluation |
| Cookbook (예제 모음) | https://github.com/langchain-ai/langsmith-cookbook |

---

## 빠른 참조 치트시트

```python
# ① 환경 설정
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "ls__..."
os.environ["LANGCHAIN_PROJECT"] = "my-project"

# ② 자동 추적 (LangChain 컴포넌트는 자동)
chain = prompt | llm
chain.invoke(inputs)

# ③ 수동 추적 (일반 함수)
@traceable(name="함수명", run_type="llm|chain|tool|retriever")
def my_func(input): ...

# ④ Context Manager
with trace(name="...", inputs={...}, tags=[...]) as run:
    ...
    run.end(outputs={...})

# ⑤ 피드백 기록
client.create_feedback(run_id=..., key="quality", score=0.9)

# ⑥ 오류 Run 조회
client.list_runs(project_name="...", error=True)

# ⑦ Dataset 생성
dataset = client.create_dataset("이름")
client.create_examples(inputs=[...], outputs=[...], dataset_id=dataset.id)

# ⑧ 평가 실행
evaluate(my_app, data="dataset-name", evaluators=[my_evaluator])
```

---

*최종 업데이트: 2026-08-19 | LangSmith SDK 0.1.x 기준*