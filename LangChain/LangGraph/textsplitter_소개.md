공식 문서와 참고 자료를 바탕으로 정리하면 다음과 같습니다.

## 왜 필요한가

문서 로더로 불러온 텍스트는 보통 LLM의 context window보다 훨씬 큽니다. Text splitter는 큰 문서를 개별적으로 검색 가능하면서도 모델의 context window 제한에 맞는 작은 청크로 쪼개주는 역할을 합니다. 단순히 자르는 게 아니라 의미 있는 단위를 최대한 보존하는 게 핵심입니다.

## 동작 방식의 큰 축: 두 가지 기준

길이 기반 분할에는 토큰 기반과 문자 기반이 있는데, 토큰 기반은 언어 모델 작업 시 유용하고, 문자 기반은 텍스트 종류에 상관없이 더 일관된 결과를 냅니다.

---

## 주요 Splitter 종류

### 1. CharacterTextSplitter
가장 단순한 형태입니다. 지정한 구분자(기본값은 문단 구분인 "\n\n")를 사용해 텍스트를 나누며, 청크 길이는 문자 수로 측정합니다. 정확한 문자 수에서 임의로 자르는 대신, 제한 이전의 가장 가까운 구분자를 찾아서 자연스러운 경계(문단, 문장 등)에서 끊어 의미를 보존합니다.

```python
from langchain_text_splitters import CharacterTextSplitter

splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=200,
    chunk_overlap=20
)
chunks = splitter.split_text(text)
```

한계: 지정한 구분자 하나만 사용하기 때문에, 그 구분자가 텍스트에 잘 없으면 chunk_size를 잘 못 지킵니다.

### 2. RecursiveCharacterTextSplitter (기본 권장)
대부분의 use case에는 이 splitter로 시작하는 것을 권장하며, context를 유지하면서 chunk 크기를 관리하는 데 균형 잡힌 성능을 제공합니다. 이 기본 전략은 그 자체로 잘 작동하며, 특정 애플리케이션에 맞춰 성능을 미세 조정해야 할 때만 조정을 고려하면 됩니다.

동작 원리: 여러 구분자 리스트를 순서대로(재귀적으로) 확인하면서 결과 청크가 지정된 크기 제한 이내가 될 때까지 분할합니다. 기본 구분자 리스트는 ["\n\n", "\n", " ", ""]입니다.

즉 동작 순서는:
1. 먼저 `"\n\n"`(문단)으로 나눠본다
2. 그래도 청크가 너무 크면, 그 청크 안에서 `"\n"`(줄바꿈)으로 다시 나눈다
3. 그래도 크면 `" "`(단어)로 나눈다
4. 마지막엔 `""`(글자 단위)로 강제로 자른다

이렇게 문단 → 문장 → 단어 순으로 우선순위를 두고 재귀적으로 분할하기 때문에 의미와 가독성을 보존합니다. `chunk_overlap`을 주면 청크 사이에 일부 텍스트가 겹치게 해서 문맥 단절을 줄일 수 있습니다.

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)
texts = text_splitter.split_text(document)
```

### 3. 토큰 기반 Splitter (TokenTextSplitter 등)
문자 수가 아니라 **토큰 수** 기준으로 자릅니다. OpenAI 등 LLM은 문자가 아닌 토큰으로 과금/제한되므로, 실제 모델 context 제한과 더 정확히 맞출 수 있습니다. tiktoken 기반 구현체 등을 사용하며, `langchain_text_splitters`에서 `tiktoken` 등의 추가 설치가 필요할 수 있습니다.

### 4. 구조 인식 Splitter (문서 포맷별)
Markdown 형식의 제목(heading)을 기준으로 분할하거나, 지정한 헤더로 markdown 파일을 나누는 splitter들이 있고, Latex 형식의 레이아웃 요소를 따라 나누는 splitter도 있습니다. 이 외에도:
- **MarkdownHeaderTextSplitter**: `#`, `##` 같은 헤더 구조를 인식해 섹션별로 나누고 메타데이터로 헤더 정보를 붙임
- **HTMLHeaderTextSplitter / HTMLSectionSplitter**: 지정한 헤더를 기준으로 HTML 콘텐츠를 구조화된 Document로 분할
- **LatexTextSplitter**: LaTeX 문법(섹션, 수식 등)을 인식
- **PythonCodeTextSplitter / 언어별 splitter**: 함수, 클래스 단위로 코드를 분할 (`RecursiveCharacterTextSplitter.from_language()`로도 지원)
- **JSON splitter**: JSON 데이터를 계층 구조를 보존하면서 작은 구조화된 청크로 분할

### 5. NLP 기반 Splitter
NLTK 패키지를 이용해 텍스트를 분할하거나, 한국어의 경우 Konlpy 패키지를 이용해 분할하는 splitter, 문장 모델 토크나이저를 이용해 텍스트를 토큰으로 분할하는 splitter도 있습니다. 문장 경계를 언어학적으로 더 정확히 인식하고 싶을 때 사용합니다.

---

## 정리 표

| Splitter | 기준 | 특징 |
|---|---|---|
| CharacterTextSplitter | 문자 수 + 단일 구분자 | 가장 단순, 구분자 없으면 크기 못 맞춤 |
| RecursiveCharacterTextSplitter | 문자 수 + 여러 구분자 재귀 시도 | **기본 권장**, 문단→문장→단어 순 우선순위 |
| Token 기반 (tiktoken 등) | 토큰 수 | LLM 실제 제한과 정확히 일치 |
| Markdown/HTML/Latex Header Splitter | 문서 구조(헤더) | 섹션·헤더 메타데이터 보존 |
| Language(Python 등) Splitter | 코드 구문 단위 | 함수/클래스 단위 보존 |
| NLTK/Konlpy 기반 | 언어학적 문장 경계 | 문장 분리 정확도 높음 |
| JSON Splitter | JSON 계층 구조 | 중첩 구조 보존하며 분할 |

**실무 팁**: 특별한 이유가 없다면 `RecursiveCharacterTextSplitter`로 시작하고, `chunk_size`(예: 500~1000자)와 `chunk_overlap`(전체의 10~20% 정도)을 조정하며 검색 품질을 보는 게 일반적인 시작점입니다.