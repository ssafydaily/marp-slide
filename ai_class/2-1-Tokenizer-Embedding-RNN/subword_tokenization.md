# Subword Tokenization 정리

**BPE · WordPiece · Unigram · Byte-level BPE — 원리와 차이점**

LLM은 문장을 그대로 이해하지 않는다. 먼저 **토큰(token)의 시퀀스**로 바꾼 뒤 각 토큰을 정수 ID로, 다시 벡터로 변환해 Transformer에 넣는다. 이 변환의 첫 단계가 토크나이징이며, 현재 대부분의 LLM은 **Subword(서브워드)** 방식을 쓴다.

```text
문장 → Tokenizer → Subword Tokens → Token ID → Embedding → Transformer → LLM
```

## 1. 세 가지 토큰화 방식

| 방식 | 예 (playing) | 특징 |
|---|---|---|
| Word | `playing → 1개 토큰` | 단어 단위. Vocabulary가 커지고 모르는 단어는 `[UNK]` 처리됨 |
| Character | `p·l·a·y·i·n·g → 7개 토큰` | 문자 단위. 모든 단어를 표현할 수 있지만 시퀀스가 길어짐 |
| **Subword** | `play + ing → 2개 토큰` | 둘의 절충. 자주 등장하는 문자열 조각을 하나의 토큰으로 묶음 |

Word 방식은 `play`, `playing`, `played`, `player`, `playground`를 전부 별도 토큰으로 등록해야 하고, 학습 때 못 본 단어(예: `playfulness`)는 `[UNK]`가 된다.

Character 방식은 미등록 단어 문제가 없지만 `Artificial Intelligence` 같은 문장도 글자 단위로 쪼개져 토큰 수가 급증한다.

Subword는 **"자주 같이 나타나는 문자 조각을 하나의 토큰으로 만든다"**는 아이디어로 이 둘의 단점을 절충한다.

## 2. Subword의 핵심 이점

1. **Vocabulary 축소** — `play/playing/played/player`를 모두 등록하는 대신 `play + ing/ed/er`로 재사용
2. **OOV(미등록 단어) 완화** — `unbelievable`을 한 번도 안 봤어도 `un + believe + able`로 분해 가능
3. **문자 단위보다 효율적** — 의미 있는 조각을 어느 정도 보존
4. **다국어 처리에 유리** — 특히 Byte-level 방식과 결합하면 한 모델로 여러 언어·이모지까지 처리

> **주의:** Subword ≠ 형태소(morpheme).  
> Subword의 경계는 언어학적 형태소와 일치하지 않는다.
>
> `unbelievable`이 항상 `un + believe + able`로 잘린다는 보장은 없고, 토크나이저마다 결과가 다르다. 한국어 `나는 학교에 갑니다`도 형태소 분석(`나+는`, `학교+에`, `가+ㅂ니다`)과 무관하게 토크나이저별로 전혀 다르게 쪼개질 수 있다.

## 3. BPE 동작 원리

**Byte Pair Encoding(BPE)**은 자주 등장하는 문자(또는 바이트) 쌍을 반복적으로 병합해 Subword를 만든다. GPT 계열에서 대표적으로 쓰인다.

학습 데이터:

```text
low, lower, lowest
```

초기 상태:

```text
l o w / l o w e r / l o w e s t
```

병합 과정의 예:

```text
1단계 병합: l+o가 자주 등장  → "lo"
2단계 병합: lo+w가 자주 등장 → "low"
3단계 병합: low+e가 자주 등장 → "lowe"
...
(목표 vocabulary 크기까지 반복)
```

이렇게 만들어진 Subword 목록이 **Vocabulary**다.

예를 들어 다음과 같이 각 조각에 ID가 부여될 수 있다.

```text
un(8), play(6), er(7), able(9), ing(5)
```

입력 `unplayable`은 다음과 같이 인코딩된다.

```text
unplayable
→ un + play + able
→ [8, 6, 9]
```

## 4. 대표 알고리즘 비교

| 특징 | BPE | WordPiece | Unigram |
|---|---|---|---|
| 대표 모델 | GPT 계열 등 | BERT | T5, SentencePiece 계열 |
| 기본 아이디어 | 자주 등장하는 쌍을 병합 | likelihood 기반으로 병합 | 큰 후보 집합에서 확률적으로 제거 |
| 학습 방향 | Bottom-up | 통계(빈도+우도) 기반 | Top-down |
| 한 줄 요약 | "작은 조각을 계속 합친다" | "언어모델에 더 도움되는 조각을 고른다" | "후보에서 필요 없는 조각을 뺀다" |

**SentencePiece**는 별도 알고리즘이라기보다 **Unigram/BPE를 문장 단위로 직접 처리하는 프레임워크**로 볼 수 있으며, T5·ALBERT·LLaMA 계열 등 여러 다국어 LLM이 사용한다.

## 5. WordPiece와 BPE의 차이점

둘 다 문자에서 시작해 쌍을 병합하며 Subword Vocabulary를 만든다는 점은 같다. 차이는 **"어떤 쌍을 병합할지 결정하는 기준"**에 있다.

| 항목 | BPE | WordPiece |
|---|---|---|
| **병합 기준** | 가장 **빈도(frequency)**가 높은 인접 쌍을 병합 | 병합했을 때 **언어모델 likelihood(우도) 증가량**이 가장 큰 쌍을 병합 |
| **계산 방식** | 단순 빈도 카운트 → 가장 많이 등장하는 쌍 선택 | 병합 전/후 두 유닛의 결합 확률을 점수화 — 대략 `score = freq(AB) / (freq(A) × freq(B))` 형태로, 각각 따로 있을 때보다 붙어 있을 때 통계적으로 얼마나 더 의미있는지 봄 |
| **미등록 조각 표기** | 보통 별도 표시 없이 조각을 이어붙임(구현에 따라 공백/문두 기준 표시) | 단어 중간 조각에 `##` 접두어를 붙임 (예: `playing → play + ##ing`) |
| **대표 사용처** | GPT-2 등(원문자 BPE), 다수의 오픈소스 LLM | BERT, DistilBERT 등 Google 계열 모델 |
| **직관** | "그냥 자주 붙어 나오면 합친다" | "합쳤을 때 모델링에 통계적으로 더 유리하면 합친다" |

즉 BPE는 **빈도 최대화**가 유일한 기준이라 구현이 단순하고 빠르며, WordPiece는 **우도 기반 점수**를 쓰기 때문에 단순 빈도만으로는 안 뽑혔을 조합도 "모델에 도움이 되면" 선택될 수 있다. 결과 Vocabulary는 비슷한 크기와 성격을 갖지만, 병합 순서와 최종 분리 경계가 달라질 수 있다.

## 6. BPE와 Byte-level BPE의 차이

둘 다 병합 알고리즘(BPE)은 동일하다. 차이는 **"무엇을 최소 단위로 놓고 병합을 시작하는가"**에 있다.

| 항목 | (문자 기반) BPE | Byte-level BPE |
|---|---|---|
| **최소 단위** | 유니코드 문자(character) | 바이트(byte) — UTF-8로 인코딩된 0~255 값 |
| **초기 Vocabulary** | 말뭉치에 등장하는 문자 집합(언어·문자셋에 따라 커질 수 있음) | 항상 256개 바이트 값으로 고정 시작 |
| **미등록 문자 처리** | 학습 때 못 본 문자·이모지는 `[UNK]`가 될 수 있음 | 모든 문자는 결국 바이트로 쪼개지므로 이론상 `[UNK]`가 발생하지 않음 |
| **다국어·이모지** | 언어마다 별도 처리 필요, 문자 집합이 클수록 초기 vocab 부담↑ | 한국어·중국어·이모지(😀)까지 동일한 방식으로 처리 — 문자 자체가 여러 바이트로 표현되면 그 바이트들을 병합해 하나의 토큰으로 학습 |
| **대표 사용처** | 초기 BPE 연구, 일부 문자 기반 구현 | GPT-2/GPT-3/GPT-4 계열 등 현재 주류 LLM 토크나이저 |

즉 Byte-level BPE는 **"문자 병합"을 "바이트 병합"으로 바꾼 버전**이다.

시작점을 바이트로 내리면 최초 Vocabulary가 문자셋 크기와 무관하게 항상 **256개**로 고정되고, 그 위에서 자주 등장하는 바이트 쌍을 병합해 점점 큰 단위(결국 흔한 단어나 조각)를 만들어간다.

이 덕분에 사실상 모든 입력을 `[UNK]` 없이 표현할 수 있다는 것이 가장 큰 실용적 장점이며, GPT 계열이 여러 언어·특수문자·이모지를 하나의 vocabulary로 다루는 근거가 된다.

## 7. 정리

| 방식/비교 | 핵심 |
|---|---|
| **Word** | 단어 단위 — Vocabulary가 너무 커지고 OOV 취약 |
| **Character** | 문자 단위 — OOV는 없지만 시퀀스가 너무 길어짐 |
| **Subword (BPE/WordPiece/Unigram)** | 둘의 절충 — 빈도 또는 우도 기반으로 자주 쓰이는 조각을 병합/vocabulary화 |
| **BPE vs WordPiece** | 병합 기준이 다름 — 빈도 최대화 vs 우도 기반 점수 |
| **BPE vs Byte-level BPE** | 시작 단위가 다름 — 문자 vs 바이트(항상 256개), Byte-level은 UNK를 사실상 없앰 |
