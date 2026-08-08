# Step 1. 토크나이저 이해 및 BPE 알고리즘 구현 — 설명서

## 1. 이 Step에서 하는 일
Step 1은 **"텍스트 → 토큰"** 으로 바꾸는 토크나이저의 원리를 이해하고, 그 학습 알고리즘인
**BPE(Byte Pair Encoding)** 를 직접 구현한 뒤, 실제 한국어 데이터셋(NSMC)으로 토크나이저를 학습시켜보는 단계입니다.

전체 흐름:
```
단어 단위 토큰화 확인
   ↓
WordPiece(BERT) 토크나이저로 서브워드 토큰화 확인 + [UNK] 문제 관찰
   ↓
BPE 알고리즘 원리 학습(get_stats, merge_vocab 직접 구현) — TODO 1
   ↓
간단한 corpus로 BPE 병합 10회 반복 실습
   ↓
NSMC 데이터 다운로드 → CharBPETokenizer로 실제 학습
   ↓
학습된 토크나이저로 토큰화/디코딩 테스트
```

---

## 2. 단어 단위 토큰화 vs 서브워드 토큰화 (셀 6~10)

- `word_tokenize()` : 정규식 `\w+|[^\w\s]` 로 단어와 특수기호를 분리하는 **직접 구현한 단어 단위 토크나이저**.
  - 예: `"I'm a student of SSAFY!"` → `["I", "'", "m", "a", "student", "of", "SSAFY", "!"]`
- `BertTokenizer` (WordPiece) : 사전 학습된 서브워드 토크나이저.
  - 같은 문장을 넣으면 `SSAFY`가 `SS`, `##AF`, `##Y`처럼 서브워드로 쪼개짐. `##`은 "앞 토큰과 한 단어로 이어진다"는 표시.
- 학습되지 않은 단어(예: 무작위 한글 `"놔뉸 쏴쁴 컄첌앺늬돠"`)를 넣으면 단어 단위 토크나이저는 `[UNK]`를 뱉지만, 서브워드 토크나이저는 글자 단위로라도 쪼개어 `[UNK]`를 줄인다.

**토큰화를 서브워드 단위로 하는 3가지 이유**
1. **OOV(Out of Vocabulary) 해결** — 모르는 단어도 아는 서브워드 조합으로 표현 가능
2. **형태소(접두사/접미사) 반영** — running/runner/run, 한국어 먹다/먹고/먹으니 같은 활용을 효율적으로 처리
3. **속도·메모리 균형** — 글자 단위(토큰 수 ↑, 속도 ↓)와 단어 단위(사전 크기 ↑, 메모리 ↓) 사이의 절충점

---

## 3. BPE 알고리즘의 원리 (셀 11)

BPE는 원래 데이터 압축 알고리즘으로, **"가장 자주 등장하는 인접 문자(토큰) 쌍을 찾아 하나의 새 토큰으로 합치는" 과정을 반복**하는 방식으로 학습합니다.

예시 말뭉치: `low, lower, newest, widest`

| 단계 | 내용 |
|---|---|
| 1. 초기화 | 모든 단어를 글자 단위로 쪼개 초기 vocab 구성 |
| 2. 쌍 빈도 계산 | 인접한 두 토큰의 등장 빈도를 전부 세어봄 (`get_stats`) |
| 3. 병합 | 빈도가 가장 높은 쌍을 하나의 새 토큰으로 합침 (`merge_vocab`), 예: `(e,s) → es` |
| 4. 반복 | 목표 vocab 크기에 도달하거나 더 합칠 쌍이 없을 때까지 2~3 반복 |

---

## 4. TODO 1: `get_stats` / `merge_vocab` 구현 (셀 13)

```python
def get_stats(vocab):
    pairs = collections.defaultdict(int)
    for word, freq in vocab.items():
        symbols = word.split()                 # "l o w </w>" → ["l","o","w","</w>"]
        for i in range(len(symbols)-1):
            pairs[symbols[i], symbols[i+1]] += freq
    return pairs

def merge_vocab(pair, v_in):
    v_out = {}
    bigram = ' '.join(pair)         # ('e','s') → "e s"
    replacement = ''.join(pair)     # "es"
    for word in v_in:
        w_out = word.replace(bigram, replacement)
        v_out[w_out] = v_in[word]
    return v_out
```

- **`get_stats`** : corpus(단어 문자열 → 빈도수 딕셔너리)를 순회하며, 각 단어를 공백 기준으로 나눈 토큰 리스트에서 **인접한 두 토큰(bigram)** 을 모두 뽑아 빈도수를 누적합니다. `</w>`는 단어의 끝을 표시하는 특수 토큰입니다.
- **`merge_vocab`** : 가장 빈도가 높았던 pair(예: `('e','s')`)를 문자열 치환(`"e s" → "es"`)으로 corpus 전체에 반영해, 다음 반복에서는 `es`가 하나의 토큰으로 취급되게 합니다.

셀 15에서는 이 두 함수를 이용해 `num_merges=10`회 반복하며 병합 과정을 직접 출력해서 확인합니다. 매 반복마다 `max(pairs, key=pairs.get)`로 최빈 pair를 찾고, `merge_vocab`으로 corpus를 갱신합니다.

---

## 5. 실제 데이터로 토크나이저 학습 (셀 17~26)

1. **데이터 준비**: NSMC(네이버 영화 리뷰, 약 20만 건, CC0 라이선스) `ratings.txt`를 다운로드
2. `document` 열만 추출하여 `naver_review.txt`로 저장 (BPE 학습용 순수 텍스트)
3. `CharBPETokenizer(suffix='</w>', split_on_whitespace_only=True)` 로 빈 토크나이저를 만들고,
   `tokenizer.train(files=..., vocab_size=30000, min_frequency=1)` 로 앞서 배운 BPE 알고리즘을 대량 데이터에 대해 학습시킴
   - `vocab_size` : 최종 단어사전 크기 (클수록 표현력↑, 메모리·계산량↑)
   - `min_frequency` : 이 빈도 미만으로 등장한 쌍은 병합하지 않음 (희귀 노이즈 제거)
4. 학습된 토크나이저로 `"I'm a student of SSAFY!"` 를 인코딩/디코딩하며 토큰, 정수 ID, 복원 텍스트를 확인

---

## 6. 핵심 요약
- 토크나이저는 텍스트를 모델이 처리할 수 있는 **정수 ID 시퀀스**로 바꾸는 전처리기이며, 그 경계(단어/서브워드/글자)는 학습 방식에 따라 달라진다.
- BPE는 **빈도 기반 그리디(greedy) 병합**을 반복하는 비지도 학습 알고리즘으로, `get_stats`(빈도 계산) → `merge_vocab`(최빈 쌍 병합)의 반복이 핵심이다.
- 실제 서비스에서는 대용량 코퍼스에 대해 BPE를 학습시켜 고정된 `vocab`과 `merge rules`를 얻고, 이를 이용해 어떤 새 문장이든 서브워드로 분해한다.
