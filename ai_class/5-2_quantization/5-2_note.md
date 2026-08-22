# 5-2 Quantization 실습 분석 정리

Quantization을 처음 접하는 교육생 기준으로, **"문제 체감 → 해결"** 흐름을 따라가며 정리했습니다.

---

## 0. 실습 전체 그림

이 실습은 5단계로 구성되고, "왜 필요한지 몸으로 느낀 뒤 → 코드로 해결"하는 구조입니다.

| Step | 내용 | 문제 체감 or 해결 |
|---|---|---|
| 1 | 환경 설정, GPU 확인 | 준비 |
| 2 | FP16 모델 로딩 | **문제 체감**: 메모리를 많이 먹는다 |
| 3 | INT4 양자화 적용 | **해결**: bitsandbytes로 메모리 절감 |
| 4 | 오타/노이즈 입력 테스트 | **문제 체감**: 양자화 모델이 이상 입력에 약하다 |
| 5 | TTP(프롬프트 강화) 적용 | **해결**: 재학습 없이 품질 회복 |

5-1(QLoRA, **학습 시** 양자화)과 헷갈리기 쉬운데, 5-2는 **추론 시** 양자화(PTQ)를 다룹니다. 이 구분이 이 노트북의 핵심 개념 축입니다.

---

## 1. 필요 패키지

| 패키지 | 역할 |
|---|---|
| `torch` (>=2.0.0) | 텐서 연산, GPU 메모리 관리, dtype(FP32/FP16) 제어 |
| `transformers` (>=4.55.0) | 모델·토크나이저 로딩, `generate()` 추론 API |
| `bitsandbytes` (>=0.43.0) | INT8/INT4 양자화 커널 제공. `BitsAndBytesConfig`로 설정 |
| `accelerate` (>=0.30.0) | `device_map="auto"` 등 모델을 GPU에 자동 배치/분산 |

---

## 2. Step 1 — 환경 설정

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import time

if torch.cuda.is_available():
    gpu_stats = torch.cuda.get_device_properties(0)
    print(gpu_stats.name, gpu_stats.total_memory / 1024**3)
```

- **`torch.cuda.get_device_properties(0)`**: GPU 이름, VRAM 용량 확인. 실습 전 "내가 쓸 수 있는 메모리가 얼마인지" 파악하는 게 첫 단계라는 점이 중요합니다 — 이 제약이 이후 모든 선택(양자화 여부)의 근거가 됩니다.

**왜 필요한가?**
FP32(32비트) → 대형 모델은 로컬 GPU(16GB급)에 못 올라갑니다. 그래서 정밀도를 낮추는 **Quantization(양자화)** 개념이 등장합니다. 수식으로는:

```
Q(x) = round(x / scale) + zero_point
```

원본 실수값 x를 정수 격자에 반올림해서 매핑하는 것 — "정밀도를 낮춰서 저장 공간을 줄이는 것"이 본질입니다.

---

## 3. Step 2 — FP16 모델 로딩 (문제 체감)

### 핵심 코드
```python
model_fp16 = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto",
)
```

- **`AutoModelForCausalLM.from_pretrained`**: HuggingFace Hub에서 사전학습된 언어모델을 로딩하는 표준 진입점.
  - `torch_dtype=torch.float16`: 가중치를 16비트 부동소수점으로 로딩(기본은 FP32).
  - `device_map="auto"`: accelerate가 GPU/CPU에 레이어를 자동 배치.
- **`torch.cuda.memory_allocated()` / `max_memory_allocated()`**: 실제 GPU에 할당된 메모리(GB)를 측정 — "체감"을 숫자로 확인하는 도구.
- **`model.generate()`**: 텍스트 생성 추론 API. `max_new_tokens`(생성 길이), `do_sample`+`temperature`+`top_p`(샘플링 다양성) 파라미터로 제어.

### 왜 필요한가 / 장단점
- FP32는 1B 파라미터당 4GB, FP16은 2GB. 즉 FP16만 써도 절반 절감되지만, 7B 이상 모델은 여전히 16GB VRAM에 빠듯하거나 못 들어갑니다.
- **장점**: FP32 대비 정밀도 손실이 거의 없고 속도도 빠름(대부분 GPU 학습/추론 기본값).
- **단점**: 그래도 큰 모델엔 부족 → 다음 단계(INT4)가 필요해지는 이유.

이 단계에서 `del model_fp16; torch.cuda.empty_cache()`로 메모리를 명시적으로 비우는데, GPU 메모리는 파이썬 GC만으로는 즉시 안 비워지므로 실무에서 자주 쓰는 패턴입니다.

---

## 4. Step 3 — INT4 양자화 적용 (해결)

### 핵심 코드
```python
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)

model_int4 = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=quantization_config,
    device_map="auto",
)
```

**`BitsAndBytesConfig` 파라미터 설명**

| 파라미터 | 의미 |
|---|---|
| `load_in_4bit=True` | 가중치를 4비트로 양자화 |
| `bnb_4bit_compute_dtype=torch.float16` | 저장은 4비트지만 실제 행렬곱 연산은 FP16으로 복원해서 수행(정확도/속도 균형) |
| `bnb_4bit_quant_type="nf4"` | **NF4**(Normal Float 4) — LLM 가중치가 정규분포를 따른다는 가정하에 최적화된 4비트 표현. `"fp4"`(균등분포 가정)보다 LLM에서 품질이 좋음 |
| `bnb_4bit_use_double_quant=True` | 이중 양자화 — scale 상수 자체도 압축해 추가로 메모리 절감(~0.4bit/param) |

- **주의**: `BitsAndBytesConfig`는 "설정값"만 정의하고, 실제 양자화 변환은 `from_pretrained` 호출 시점에 일어납니다.

### 필요성 / 장단점
| 방식 | 메모리 절감 | 품질 | 특징 |
|---|---|---|---|
| INT8 | 50% | 높음 | 런타임에 이상치(outlier) 분리 처리 → 오버헤드 있음 |
| **INT4(NF4)** | **75%** | 중간 | 사전에 양자화 끝내고 FP16 연산 → 오버헤드 적어 더 빠름 |

노트북의 미니 시뮬레이션(Cell 28)에서 직접 확인시켜주는 부분이 좋은 교육 장치입니다: 같은 텐서를 INT8(256레벨)과 INT4(16레벨)로 양자화·역양자화해보면 INT4의 오차가 확연히 커지는 걸 숫자로 보여줍니다. 이게 "왜 INT4가 더 위험한 트레이드오프인지"를 체감시키는 핵심 대목입니다.

**중요 개념 — 모델 메모리 vs 피크 메모리**: 양자화는 **가중치**만 압축하고, 추론 중 활성화값(activation)·KV 캐시는 여전히 FP16으로 계산됩니다. 그래서 작은 모델(1.5B)일수록 피크 메모리 절감 체감이 작고, 큰 모델(70B)일수록 절감 효과가 커집니다 — 이게 "왜 초대형 모델에서 양자화가 필수인지"의 근거입니다.

---

## 5. Step 4 — 환경 변화 입력 테스트 (새로운 문제 체감)

```python
test_samples = [
    {"type": "정상", "prompt": "..."},
    {"type": "오타", "prompt": "..."},
    {"type": "노이즈", "prompt": "..."},
    {"type": "모호함", "prompt": "..."},
    {"type": "조건변화", "prompt": "..."},
]
```
동일한 `measure_inference` 함수를 재사용해 INT4 모델에 5가지 유형(정상/오타/노이즈/모호함/조건변화)의 입력을 흘려 응답 품질을 관찰합니다.

**왜 이런 문제가 생기는가 (노트북이 강조하는 3가지 원인)**
1. **정밀도 손실 누적**: 개별 가중치의 작은 반올림 오차가 수십억 번 연산을 거치며 누적.
2. **Attention score 미세 변화**: 오타처럼 학습 때 덜 본 토큰은 attention 계산이 미묘하게 흔들려 다른 곳에 집중하게 됨.
3. **경계 케이스 취약성**: 학습 데이터에 자주 나온 패턴일수록 가중치가 "강하게" 형성되어 양자화 오차에 강건하고, 드문 패턴(오타, 모호한 표현)일수록 약해서 취약함.

즉, **양자화의 트레이드오프는 평상시엔 안 보이다가 입력이 지저분해질 때 드러난다**는 게 이 Step의 교육 포인트입니다.

---

## 6. Step 5 — TTP(Test-time Prompting)로 해결

### 핵심 코드
```python
TTP_A_TEMPLATE = """... 규칙 1,2,3,4 ... {question} ..."""   # 형식/제약 강화
TTP_B_TEMPLATE = """... Q&A 예시 1개 ... {question} ..."""   # few-shot

def apply_ttp(template, question):
    return template.format(question=question)
```

- **`str.format()`**: `{question}` 플레이스홀더에 실제 질문을 삽입하는 파이썬 표준 문자열 포매팅. 모델이나 가중치는 전혀 건드리지 않습니다.
- **TTP-A (규칙 명시형)**: "오타가 있어도 의도를 파악하라", "시간 단위로 답하라" 등 명시적 규칙 부여.
- **TTP-B (few-shot형)**: 질문-답변 예시 1개를 프롬프트에 포함시켜 원하는 출력 형식을 "보여주는" 방식.

### 필요성 / 장단점
| 방법 | 모델 변경 | 적용 시간 | 비용 | 유연성 |
|---|---|---|---|---|
| Fine-tuning | O | 시간~일 | 높음 | 낮음 |
| RLHF | O | 일~주 | 매우 높음 | 낮음 |
| **TTP** | **X (재학습 없음)** | **즉시** | **없음** | **높음** |

TTP는 "모델의 지식"이 아니라 "추론 방향"을 프롬프트로 안내하는 전략입니다. 양자화로 약해진 추론 여유를 명확한 지시·예시로 보완하는 것 — 재학습 비용 없이 즉시 적용 가능하다는 게 최대 장점이나, 근본적인 정밀도 손실 자체를 없애는 건 아니므로 복잡한 조건(예: "조건변화" 유형)에서는 개선 폭이 제한적이라는 점(Cell 55의 점수표에서 "조건변화"만 TTP-A로 개선이 거의 없는 것)도 확인할 수 있습니다.

---

## 7. 전체 핵심 요약 (교육생이 기억해야 할 것)

1. **왜 양자화가 필요한가**: 제한된 GPU(VRAM)에서 더 큰 모델을 돌리기 위해 — FP16→INT4로 가중치 메모리 최대 75% 절감.
2. **트레이드오프**: 메모리·속도 ↑ vs 정확도 ↓, 특히 "정상적이지 않은" 입력(오타/노이즈/모호함)에서 품질 저하가 두드러짐.
3. **bitsandbytes 사용법**: `BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", ...)` → `from_pretrained(quantization_config=...)` 두 줄이 핵심 패턴.
4. **모델 메모리 ≠ 피크 메모리**: 양자화는 가중치만 압축하고, 활성화/KV캐시는 그대로 FP16이라 작은 모델일수록 체감 효과가 작음.
5. **TTP는 사후 보완책**: 근본적 정밀도 손실은 못 없애지만, 재학습 없이 프롬프트만으로 품질을 상당히 회복시킬 수 있음.

이 흐름 자체가 실무 시나리오와 정확히 일치합니다: *"모델을 배포해야 하는데 GPU가 부족하다 → 양자화한다 → 실제 서비스에선 사용자 입력이 지저분하다 → 품질이 떨어진다 → 프롬프트로 보완한다."*
