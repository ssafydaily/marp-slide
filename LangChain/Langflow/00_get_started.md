# Langflow 완벽 학습 가이드

> **Langflow**는 LangChain 기반의 시각적 AI 워크플로우 빌더입니다.  
> 코드 없이 드래그 앤 드롭으로 LLM 파이프라인을 설계하고 배포할 수 있습니다.

---

## 목차

1. [Langflow란?](#1-langflow란)
2. [설치 및 환경 설정](#2-설치-및-환경-설정)
3. [UI 구성 및 기본 개념](#3-ui-구성-및-기본-개념)
4. [핵심 컴포넌트](#4-핵심-컴포넌트)
5. [기본 워크플로우 만들기](#5-기본-워크플로우-만들기)
6. [고급 기능](#6-고급-기능)
7. [API 활용](#7-api-활용)
8. [실전 예제](#8-실전-예제)
9. [자주 묻는 질문](#9-자주-묻는-질문)

---

## 1. Langflow란?

Langflow는 DataStax(구 Logspace)에서 개발한 **오픈소스 로우코드 AI 개발 플랫폼**입니다.

### 주요 특징

- **비주얼 플로우 빌더**: 노드와 엣지로 AI 파이프라인을 시각적으로 구성
- **LangChain 통합**: LangChain의 모든 컴포넌트를 GUI에서 사용 가능
- **다양한 LLM 지원**: OpenAI, Anthropic, Google, Ollama 등 주요 모델 통합
- **RAG 파이프라인**: 벡터 데이터베이스와 연동한 검색 증강 생성 구현
- **API 내보내기**: 완성된 플로우를 REST API로 즉시 배포

### 활용 사례

- 챗봇 및 대화형 AI 에이전트 구축
- 문서 Q&A 시스템 (RAG)
- 데이터 분석 자동화 파이프라인
- 멀티 에이전트 워크플로우
- 프롬프트 엔지니어링 및 테스트

---

## 2. 설치 및 환경 설정

### 방법 1: pip 설치 (권장)

```bash
# Python 3.10 이상 필요
pip install langflow

# 실행
langflow run
```

### 방법 2: uv 사용 (빠른 설치)

```bash
# uv 설치
pip install uv

# Langflow 설치 및 실행
uv pip install langflow
uv run langflow run
```

### 방법 3: Docker

```bash
# Docker Hub에서 이미지 가져오기
docker pull langflowai/langflow:latest

# 컨테이너 실행
docker run -p 7860:7860 langflowai/langflow:latest
```

### 방법 4: Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  langflow:
    image: langflowai/langflow:latest
    ports:
      - "7860:7860"
    environment:
      - LANGFLOW_SECRET_KEY=your_secret_key
    volumes:
      - langflow_data:/app/langflow

volumes:
  langflow_data:
```

```bash
docker-compose up -d
```

### 환경 변수 설정

```bash
# .env 파일 예시
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LANGFLOW_SECRET_KEY=your_secret_key
LANGFLOW_DATABASE_URL=sqlite:///./langflow.db
LANGFLOW_HOST=0.0.0.0
LANGFLOW_PORT=7860
```

### 실행 확인

설치 후 브라우저에서 `http://localhost:7860` 접속

---

## 3. UI 구성 및 기본 개념

### 화면 구성

```
┌─────────────────────────────────────────────────────┐
│  상단 메뉴 바 (저장, 실행, 설정)                      │
├──────────────┬──────────────────────────────────────┤
│              │                                      │
│  컴포넌트     │         캔버스 (플로우 편집 영역)      │
│  패널        │                                      │
│  (왼쪽)      │                                      │
│              │                                      │
├──────────────┴──────────────────────────────────────┤
│  하단 상태 바                                        │
└─────────────────────────────────────────────────────┘
```

### 핵심 개념

| 개념 | 설명 |
|------|------|
| **Flow** | 노드들이 연결된 전체 워크플로우 |
| **Node (Component)** | 특정 기능을 수행하는 개별 블록 |
| **Edge** | 노드 간 데이터 흐름을 나타내는 연결선 |
| **Port** | 노드의 입력/출력 연결 포인트 |
| **Playground** | 완성된 플로우를 바로 테스트하는 공간 |

### 노드 구조

```
┌─────────────────────┐
│   [컴포넌트 이름]    │
├─────────────────────┤
│ ● 입력 포트 1       │
│ ● 입력 포트 2       │
├─────────────────────┤
│   [설정 파라미터]   │
├─────────────────────┤
│       출력 포트 ●   │
└─────────────────────┘
```

---

## 4. 핵심 컴포넌트

### 4.1 Inputs (입력)

| 컴포넌트 | 기능 |
|---------|------|
| **Chat Input** | 사용자 채팅 메시지 수신 |
| **Text Input** | 정적 텍스트 입력 |
| **File** | 파일 업로드 처리 |
| **URL** | 웹 URL에서 콘텐츠 가져오기 |

### 4.2 Outputs (출력)

| 컴포넌트 | 기능 |
|---------|------|
| **Chat Output** | 채팅 형식으로 결과 출력 |
| **Text Output** | 텍스트 결과 표시 |

### 4.3 Models (LLM)

| 컴포넌트 | 지원 모델 |
|---------|---------|
| **OpenAI** | GPT-4o, GPT-4, GPT-3.5 |
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Opus |
| **Google Generative AI** | Gemini Pro, Gemini Flash |
| **Ollama** | Llama, Mistral, CodeLlama 등 로컬 모델 |
| **Azure OpenAI** | Azure 배포 OpenAI 모델 |

### 4.4 Prompts (프롬프트)

| 컴포넌트 | 기능 |
|---------|------|
| **Prompt** | 시스템/사용자 프롬프트 템플릿 작성 |
| **System Message** | 시스템 메시지 정의 |

**프롬프트 템플릿 변수 사용 예시:**

```
당신은 {role}입니다.
사용자의 질문: {question}
다음 언어로 답하세요: {language}
```

### 4.5 Vector Stores (벡터 스토어)

| 컴포넌트 | 특징 |
|---------|------|
| **Chroma** | 로컬 사용에 최적화, 빠른 프로토타이핑 |
| **Pinecone** | 클라우드 기반, 대용량 처리 |
| **Weaviate** | 멀티모달 지원 |
| **FAISS** | Meta의 고성능 유사도 검색 |
| **Astra DB** | DataStax 클라우드 벡터 DB |

### 4.6 Embeddings (임베딩)

| 컴포넌트 | 설명 |
|---------|------|
| **OpenAI Embeddings** | text-embedding-3-small/large |
| **HuggingFace** | 오픈소스 임베딩 모델 |
| **Ollama Embeddings** | 로컬 임베딩 모델 |

### 4.7 Document Loaders (문서 로더)

| 컴포넌트 | 지원 형식 |
|---------|---------|
| **File** | PDF, DOCX, TXT, CSV |
| **URL** | 웹페이지 |
| **YouTube** | YouTube 자막 |
| **GitLoader** | Git 저장소 코드 |

### 4.8 Text Splitters (텍스트 분할)

| 컴포넌트 | 특징 |
|---------|------|
| **Recursive Character Splitter** | 범용적, 구조 유지 |
| **Character Splitter** | 단순 문자 기준 분할 |
| **Token Splitter** | 토큰 수 기준 분할 |

### 4.9 Agents (에이전트)

| 컴포넌트 | 기능 |
|---------|------|
| **Agent** | 도구를 사용하는 자율 에이전트 |
| **ReAct Agent** | Reasoning + Acting 방식 |
| **Tool Calling Agent** | 함수 호출 기반 에이전트 |

### 4.10 Tools (도구)

| 컴포넌트 | 기능 |
|---------|------|
| **Search API** | 웹 검색 (SerpAPI, Tavily) |
| **Calculator** | 수학 계산 |
| **Python REPL** | Python 코드 실행 |
| **Wikipedia** | 위키피디아 검색 |

---

## 5. 기본 워크플로우 만들기

### 5.1 Hello World: 간단한 챗봇

**목표**: 사용자 입력을 받아 LLM이 응답하는 기본 챗봇

```
[Chat Input] → [Prompt] → [OpenAI] → [Chat Output]
```

**단계별 구성:**

1. **Chat Input 추가**
   - 컴포넌트 패널에서 `Inputs > Chat Input` 드래그
   - 기본 설정 유지

2. **Prompt 추가**
   - `Prompts > Prompt` 드래그
   - Template 입력:
     ```
     당신은 친절한 AI 어시스턴트입니다.
     
     사용자: {user_message}
     ```
   - `user_message` 변수에 Chat Input 연결

3. **OpenAI 모델 추가**
   - `Models > OpenAI` 드래그
   - Model: `gpt-4o-mini` 선택
   - API Key 입력
   - Prompt 출력을 OpenAI 입력에 연결

4. **Chat Output 추가**
   - `Outputs > Chat Output` 드래그
   - OpenAI 출력을 Chat Output 입력에 연결

5. **테스트**
   - 우측 상단 `▶ Playground` 클릭
   - 메시지 입력 후 응답 확인

---

### 5.2 RAG 시스템 구축

**목표**: PDF 문서를 기반으로 질문에 답하는 시스템

```
[File] → [Split Text] → [OpenAI Embeddings] → [Chroma]
                                                    ↓
[Chat Input] → [Prompt] → [OpenAI] → [Chat Output]
                  ↑
              [Chroma] (검색)
```

**단계별 구성:**

**① 문서 인덱싱 파이프라인**

1. `Inputs > File` 추가 → PDF 파일 업로드
2. `Text Splitters > Recursive Character Splitter` 추가
   - Chunk Size: `1000`
   - Chunk Overlap: `200`
3. `Embeddings > OpenAI Embeddings` 추가
   - Model: `text-embedding-3-small`
4. `Vector Stores > Chroma` 추가
   - Collection Name: `my_docs`

연결: `File → Splitter → Embeddings → Chroma`

**② 검색 및 응답 파이프라인**

1. `Inputs > Chat Input` 추가
2. 위 Chroma 컴포넌트의 Search 출력 포트 사용
3. `Prompts > Prompt` 추가
   ```
   다음 컨텍스트를 바탕으로 질문에 답하세요.
   
   컨텍스트: {context}
   
   질문: {question}
   
   모르면 "모른다"고 답하세요.
   ```
4. `Models > OpenAI` 추가
5. `Outputs > Chat Output` 추가

---

## 6. 고급 기능

### 6.1 Custom Component 작성

Python으로 커스텀 컴포넌트를 만들 수 있습니다.

```python
from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema import Data

class MyCustomComponent(Component):
    display_name = "나의 커스텀 컴포넌트"
    description = "텍스트를 대문자로 변환합니다."
    icon = "type"

    inputs = [
        MessageTextInput(
            name="input_text",
            display_name="입력 텍스트",
            info="변환할 텍스트를 입력하세요."
        ),
    ]

    outputs = [
        Output(
            display_name="출력 텍스트",
            name="output_text",
            method="transform_text"
        ),
    ]

    def transform_text(self) -> str:
        return self.input_text.upper()
```

### 6.2 Memory (대화 기억)

다중 턴 대화를 위한 메모리 설정:

1. `Memory > Conversation Buffer Memory` 추가
2. LLM 컴포넌트의 Memory 포트에 연결
3. Session ID로 대화 세션 구분

```python
# 외부에서 Session ID 지정 시
session_id = "user_123_session_1"
```

### 6.3 조건부 분기 (Conditional)

```
[Input] → [Router] → [경로 A: 긍정 응답]
                  ↘ [경로 B: 부정 응답]
```

- `Logic > Conditional Router` 컴포넌트 활용
- 조건에 따라 다른 처리 경로로 분기

### 6.4 반복 처리 (Loop)

```
[입력 리스트] → [Parse Data] → [반복 처리] → [결과 수집]
```

### 6.5 플로우 변수 활용

전역 변수를 설정하여 플로우 전반에서 재사용:
- 설정 > Global Variables에서 API 키, 공통 파라미터 관리

---

## 7. API 활용

### 7.1 REST API 사용

Langflow는 완성된 플로우를 즉시 API로 사용할 수 있습니다.

**플로우 실행 API:**

```bash
curl -X POST \
  "http://localhost:7860/api/v1/run/{flow_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "input_value": "안녕하세요!",
    "output_type": "chat",
    "input_type": "chat"
  }'
```

**Python으로 API 호출:**

```python
import requests

LANGFLOW_URL = "http://localhost:7860"
FLOW_ID = "your-flow-id"

def run_flow(message: str) -> str:
    url = f"{LANGFLOW_URL}/api/v1/run/{FLOW_ID}"
    
    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
    }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    result = response.json()
    return result["outputs"][0]["outputs"][0]["results"]["message"]["text"]

# 실행
answer = run_flow("Python이란 무엇인가요?")
print(answer)
```

**Node.js로 API 호출:**

```javascript
const axios = require('axios');

const LANGFLOW_URL = 'http://localhost:7860';
const FLOW_ID = 'your-flow-id';

async function runFlow(message) {
  const response = await axios.post(
    `${LANGFLOW_URL}/api/v1/run/${FLOW_ID}`,
    {
      input_value: message,
      output_type: 'chat',
      input_type: 'chat',
    },
    {
      headers: { 'Content-Type': 'application/json' }
    }
  );
  
  return response.data.outputs[0].outputs[0].results.message.text;
}

runFlow('안녕하세요!').then(console.log);
```

### 7.2 플로우 내보내기/가져오기

```bash
# 플로우 내보내기 (JSON)
# UI: Flow > Export > Download as JSON

# API로 내보내기
curl "http://localhost:7860/api/v1/flows/{flow_id}" \
  -H "Authorization: Bearer {token}"
```

### 7.3 Streaming API

```python
import httpx

async def stream_flow(message: str):
    url = f"{LANGFLOW_URL}/api/v1/run/{FLOW_ID}?stream=true"
    
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, json={
            "input_value": message,
            "output_type": "chat",
        }) as response:
            async for chunk in response.aiter_text():
                print(chunk, end="", flush=True)
```

---

## 8. 실전 예제

### 8.1 예제 1: 고객 지원 챗봇

```
[Chat Input]
     ↓
[프롬프트: 역할 설정 + 제품 컨텍스트]
     ↓
[Chroma 검색: 제품 매뉴얼]
     ↓
[OpenAI GPT-4o]
     ↓
[Chat Output]
```

**프롬프트 템플릿:**
```
당신은 {company_name}의 고객 지원 담당자입니다.
항상 친절하고 전문적으로 답변하세요.

관련 문서:
{context}

고객 질문: {question}

답변 시 다음을 지켜주세요:
- 문서에 없는 내용은 추측하지 마세요
- 불확실한 경우 담당자 연결을 안내하세요
```

---

### 8.2 예제 2: 자동 뉴스 요약 봇

```
[URL Input] → [URL Loader] → [Text Splitter]
                                    ↓
[Prompt: 요약 지시] ← [컨텍스트 통합]
       ↓
[Anthropic Claude]
       ↓
[Text Output]
```

**요약 프롬프트:**
```
다음 뉴스 기사를 한국어로 요약해주세요.

기사 내용:
{article_content}

요약 형식:
1. 핵심 요점 (3줄)
2. 상세 내용 (5줄)
3. 시사점 (2줄)
```

---

### 8.3 예제 3: 코드 리뷰 에이전트

```
[File Input: 코드 파일]
        ↓
[Python REPL: 코드 분석]
        ↓
[Prompt: 리뷰 기준]
        ↓
[OpenAI GPT-4o]
        ↓
[Chat Output: 리뷰 결과]
```

---

### 8.4 예제 4: 멀티 에이전트 파이프라인

```
[사용자 질문]
      ↓
[Router: 질문 분류]
   ↙        ↘
[에이전트A]  [에이전트B]
(검색 전문)  (계산 전문)
   ↘        ↙
[결과 통합 에이전트]
      ↓
[최종 답변]
```

---

## 9. 자주 묻는 질문

### Q1. Langflow와 n8n의 차이점은?

| 항목 | Langflow | n8n |
|------|---------|-----|
| 특화 | AI/LLM 워크플로우 | 일반 업무 자동화 |
| 기반 | LangChain | 자체 엔진 |
| 주요 용도 | RAG, 챗봇, AI 에이전트 | API 연동, 데이터 처리 |
| AI 통합 | 매우 강력 | 기본 수준 |

### Q2. 로컬에서 LLM을 무료로 사용하려면?

1. [Ollama](https://ollama.ai) 설치
2. 모델 다운로드: `ollama pull llama3`
3. Langflow에서 `Ollama` 컴포넌트 사용
4. Base URL: `http://localhost:11434`

### Q3. 플로우를 프로덕션에 배포하려면?

**Docker 배포:**
```bash
docker run -d \
  -p 7860:7860 \
  -e OPENAI_API_KEY=sk-... \
  -v /data/langflow:/app/langflow \
  langflowai/langflow:latest
```

**Kubernetes:** Helm 차트 지원  
**클라우드:** AWS, GCP, Azure 배포 가이드 공식 문서 참조

### Q4. API 요청 인증은 어떻게 하나요?

```bash
# API 키 생성 (UI: Settings > API Keys)
# 요청 시 헤더에 포함
curl -H "x-api-key: {your-api-key}" \
  "http://localhost:7860/api/v1/run/{flow_id}"
```

### Q5. 대용량 문서 처리 시 주의사항은?

- **Chunk Size**: 500~1500 토큰 사이 조정
- **Chunk Overlap**: Chunk Size의 10~20%
- **배치 처리**: 한 번에 너무 많은 문서 처리 시 Rate Limit 주의
- **비동기 처리**: 대용량은 백그라운드 작업으로 분리

---

## 참고 자료

- **공식 문서**: https://docs.langflow.org
- **GitHub**: https://github.com/langflow-ai/langflow
- **Discord 커뮤니티**: https://discord.gg/langflow
- **YouTube 튜토리얼**: Langflow 공식 채널

---

> 이 문서는 Langflow의 핵심 기능을 다루는 학습 자료입니다.  
> 최신 정보는 공식 문서를 참고하세요.