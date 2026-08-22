# 5-1 PEFT(파라미터 효율적 튜닝) 실습 정리

> 대상 파일: `(실습-정답) 5-1_PEFT_파라미터_효율적_튜닝.ipynb`
> 이 문서는 노트북의 흐름(Step 1~5)을 따라가면서, 같은 폴더에 있는 보충 설명 마크다운 자료들의 내용을 관련 위치에 녹여 정리한 것입니다.

---

## 0. 실습 개요

### 학습 주제
- **Full Fine-tuning vs PEFT 비교**: 사전학습 모델을 새 태스크에 적응시키는 두 접근법의 메모리/연산 trade-off 비교
- **LoRA(Low-Rank Adaptation) 원리와 구현**: 가중치 행렬의 저차원 분해를 이용한 효율적 파인튜닝
- **QLoRA를 활용한 효율적 LLM 파인튜닝**: 양자화 + LoRA 결합으로 제한된 GPU 메모리에서도 대형 모델 학습

### 학습 목표
- LoRA 기반 PEFT로 **제한된 GPU 환경에서 LLM 파인튜닝**을 수행하고 결과를 저장/추론한다.
- Full Fine-tuning과 PEFT의 차이, PEFT가 필요한 이유를 설명할 수 있다.
- LoRA의 원리(저차원 분해, Adapter)를 이해하고 핵심 하이퍼파라미터(r, lora_alpha, target_modules)를 설정할 수 있다.
- Unsloth 기반 QLoRA 파인튜닝을 수행하고, 학습된 adapter의 파라미터 효율성을 Full FT와 비교할 수 있다.

### 핵심 개념 요약
| 개념 | 설명 |
|---|---|
| **PEFT** | 사전학습 가중치는 고정(freeze)하고 소수의 추가 파라미터(adapter)만 학습. Full FT 대비 10~1000배 적은 파라미터로 유사 성능 |
| **LoRA** | $W \in \mathbb{R}^{d\times k}$의 업데이트를 $\Delta W = BA$로 저차원 분해. $B \in \mathbb{R}^{d\times r}$, $A \in \mathbb{R}^{r\times k}$ ($r \ll \min(d,k)$). 최종 출력 $W' = W + BA$ |
| **QLoRA** | Base model을 4-bit NF4로 양자화해 로드하고, LoRA adapter만 BF16으로 학습 → 16GB VRAM에서도 7B급 모델 파인튜닝 가능 |
| **Unsloth** | Triton 기반 커스텀 GPU 커널로 FlashAttention2 대비 최대 30배 빠른 학습, 메모리 30% 절감 |
| **SFTTrainer** | HuggingFace TRL의 지도학습 파인튜닝 트레이너. 데이터 로딩~토큰화~학습 파이프라인을 자동 관리, PEFT와 통합 지원 |

### 실습 구성
- **진행 방식**: 문제/정답 코드가 병렬 제공되며, TODO 영역을 채우며 학습
- **데이터셋**: `Thytu/ChessInstruct` (체스 기보 예측 instruction-following, MIT License). 전체 중 5,000개만 사용 (학습용 0~4999, 테스트용 5000~5004로 분리하여 공정 비교)
- **필수 패키지**: `unsloth`, `transformers`, `peft`, `trl`(SFTTrainer), `torch`, `datasets`, `accelerate`, `bitsandbytes`, `matplotlib`
- **Step 구성**
  1. 환경 설정 — 라이브러리 설치, 모델 로드
  2. Full Fine-tuning 시도 — 메모리 부족 체감
  3. PEFT/LoRA 원리 이해
  4. LoRA 적용 및 학습
  5. 결과 확인 및 저장
- **TODO 목록**
  - TODO 1: Full FT 메모리 요구량 계산 및 시각화
  - TODO 2: LoRA 설정값(r, lora_alpha, target_modules 등) 채우기
  - TODO 3: `convert_to_chatml` 함수 작성 (데이터 → conversations 변환)
  - TODO 4: 추론용 테스트 입력 구성

---

## 1. Step 1: 환경 설정

### 1.1 Unsloth란?
효율적인 LLM 파인튜닝/RL 프레임워크로, 수작업 최적화된 GPU 커널을 사용해 FlashAttention2 대비 **최대 30배 빠른 학습 속도**와 **VRAM 30% 절감**을 제공한다. 16GB급 GPU로도 대형 모델 파인튜닝이 가능해지는 핵심 이유다.

> **보충: FlashAttention-2란?** (`Flash_attention2.md`)
> Tri Dao가 발표한 알고리즘으로, Attention 연산이 시퀀스 길이 제곱($N^2$)에 비례해 느려지고 메모리를 많이 쓰는 문제를 GPU 메모리 계층 구조(느리지만 큰 HBM ↔ 빠르지만 작은 SRAM)에 최적화해 해결한다.
> - **Tiling**: 데이터를 작은 블록으로 쪼개 SRAM 안에서 연산을 끝내고 최종 결과만 HBM에 기록 → HBM 왕복(병목) 최소화
> - **FlashAttention-2 개선점**: SM 간 작업 분할 최적화, Softmax 연산 순서 재배치 등으로 1세대 대비 약 2배 향상
> - 적용법: HuggingFace `transformers`는 `attn_implementation="flash_attention_2"`, Unsloth는 하드웨어 지원 시 자동 활성화
> - 하드웨어 요구사항: **Ampere 이후 GPU**(A100, RTX 30xx/40xx)에서만 지원, V100/T4/RTX 20xx는 미지원(`sdpa` 등 대체)
> - 파인튜닝 관점 이점: 긴 컨텍스트 학습 가능, 학습 시간 2~3배 단축, 근사가 아닌 수학적으로 동일한 결과라 성능 저하 없음

### 1.2 LoRA vs QLoRA — 무엇이 다른가?
이 실습은 **QLoRA**를 사용한다.

| 구분 | LoRA | QLoRA |
|---|---|---|
| Base Model | FP16/BF16(원본) | 4-bit 양자화 |
| LoRA Adapter | FP16/BF16 | FP16/BF16(동일) |
| 1B 모델 메모리 | ~2GB | ~0.5GB |
| 7B 모델 메모리 | ~14GB | ~4GB |

**QLoRA의 3대 핵심 기술**
1. **NF4(4-bit NormalFloat)** — 가중치 분포에 최적화된 양자화, 일반 INT4보다 정보 손실 적음
2. **Double Quantization(이중 양자화)** — 양자화 상수까지 재양자화하여 추가 절감 (7B 기준 약 0.5GB)
3. **Paged Optimizers** — GPU 메모리 부족 시 CPU로 자동 스왑, OOM 방지

> QLoRA = **Q**(양자화된 Base Model) + **LoRA**(저차원 Adapter). 코드에서 모델을 로드할 때 이름에 붙는 `bnb-4bit`가 바로 "Q" 부분이다.

> **보충: INT4 vs NF4, 무엇이 다른가?** (`INT4_NF4.md`)
> 4비트(16개 슬롯) 안에 원래 FP32 정보를 최대한 담기 위한 두 가지 방식이다.
> - **INT4(선형 양자화)**: min~max 구간을 동일 간격으로 16등분. $Q(x)=\text{round}(x/scale + zero\_point)$. 계산이 단순해 하드웨어 가속에 유리하지만, 가중치가 0 근처에 몰린 정규분포 특성상 데이터가 없는 양 끝단에도 동일 정밀도를 낭비하고 중앙부 세밀함을 잃어 오차가 커짐
> - **NF4(비선형 양자화, QLoRA에서 제안)**: 가중치가 $N(0,1)$을 따른다고 가정하고, 확률 밀도가 높은 0 근처에는 슬롯을 촘촘히, 양 끝단에는 슬롯을 넓게 배치(Quantile Quantization). CDF 기준으로 16개 최적값을 미리 계산해 매핑하며, 동일 4비트라도 INT4보다 정보 보존이 우수해 **LLM 파인튜닝(QLoRA)의 표준**으로 쓰인다.
> - 요약: INT4는 "모든 칸을 균등하게", NF4는 "데이터 밀도에 따라 촘촘하게" 나누는 방식.

> **보충: 이중 양자화(Double Quantization) 상세** (`이중양자화.md`)
> 1차로 가중치를 NF4로 양자화할 때, 블록(예: 64개)마다 FP32 양자화 상수(scale)가 필요한데 이 상수 자체도 메모리를 차지한다(블록 64 기준 파라미터당 약 0.5bit 오버헤드). 이중 양자화는 이 1차 양자화 상수들을 다시 묶어(예: 256개씩) **8bit(FP8)로 재양자화**함으로써 오버헤드를 약 0.127bit 수준까지 낮춘다.
> - 결과: 파라미터당 평균 약 0.37bit 절감 → 수십억 파라미터 모델 기준 수백 MB~수 GB VRAM 추가 확보, 성능(Perplexity) 손실은 거의 없음
> - QLoRA 3대 기술 중 하나로, NF4(가중치 압축) + 이중 양자화(스케일까지 압축) + Paged Optimizer(OOM 방지) 조합으로 48GB GPU 1장으로 65B 모델 파인튜닝이 가능해졌다.

### 1.3 모델 및 토크나이저 로드 (Guided Build)
```python
from unsloth import FastModel

max_seq_length = 1024
model_name = "unsloth/gemma-3-1b-it-unsloth-bnb-4bit"

model, tokenizer = FastModel.from_pretrained(
    model_name=model_name,
    max_seq_length=max_seq_length,
)
```
`unsloth/gemma-3-1b-it-unsloth-bnb-4bit`는 Unsloth가 파인튜닝에 최적화하여 미리 4-bit로 양자화해둔 모델이다.

> **보충: `max_seq_length`의 역할** (`max_sequence_length.md`)
> 단순히 "문장 길이 제한"이 아니라 GPU 자원 할당과 연산 효율에 직접 영향을 준다.
> - **역할**: 모델이 한 번에 처리하는 최대 토큰 수 정의. 초과분은 truncation되며, 위치 인코딩(포지셔널 임베딩)의 범위도 이 값으로 결정
> - **VRAM(KV Cache)**: 값을 크게 잡을수록 캐시 공간을 더 많이 미리 확보해야 해 VRAM 점유가 커지고, 반대로 필요 이상 크면 배치 사이즈를 못 키워 비효율적
> - **RoPE 확장**: 모델 기본 지원 길이보다 크게 설정하면 Unsloth가 Linear/Dynamic NTK Scaling 등을 내부적으로 적용
> - **FlashAttention2와 시너지**: 설정된 길이에 맞춰 연산 커널이 튜닝되어 최적 속도 보장
> - 실무 팁: 무조건 크게 잡지 말고, 데이터셋 토큰 길이 분포의 95%를 커버하는 최소값으로 설정하는 것이 유리 (본 실습은 1024)

이어서 학습 전/후 비교를 위해 **베이스 모델의 응답을 미리 저장**해둔다(학습에 쓰지 않는 인덱스 5000~5004 데이터 사용). 이때 chat template이 적용된다.

```python
from unsloth.chat_templates import get_chat_template
tokenizer = get_chat_template(tokenizer, chat_template="gemma3")
```

> **보충: `get_chat_template`은 왜 필요한가?** (`chat_template.md`)
> LLM은 본질적으로 "다음 단어를 예측하는 기계"라서, user/assistant가 주고받는 대화 형식을 모델이 아는 특수 토큰 포맷(`<start_of_turn>user\n...<end_of_turn>\n<start_of_turn>model\n...`)으로 변환해줘야 한다.
> - `get_chat_template(tokenizer, chat_template="gemma3")`는 단순 문자열 변환기가 아니라, **tokenizer 객체 내부에 모델 전용 Jinja2 템플릿과 특수 토큰 설정을 주입**한다. 이후 `tokenizer.apply_chat_template()`을 바로 사용할 수 있게 된다.
> - `tokenizer`를 인자로 넘기는 이유: 모델마다(Llama/Gemma/Mistral 등) 특수 토큰 ID가 달라, 해당 토크나이저의 vocabulary를 확인·보정해야 하기 때문
> - 핵심: 학습과 추론에서 **동일한 템플릿**을 써야 한다. 형식이 어긋나면 모델이 혼란을 겪는다.

테스트 데이터에 대해 `apply_chat_template(..., add_generation_prompt=True).removeprefix('<bos>')`로 프롬프트를 만들고 `model.generate()`로 응답을 수집해 `base_model_responses`에 저장한다. (`add_generation_prompt`, `removeprefix('<bos>')`의 의미는 Step 5 추론 부분에서 함께 정리한다.)

---

## 2. Step 2: Full Fine-tuning 시도 (문제 체감)

### 2.1 Full Fine-tuning의 메모리 문제
Full FT는 모든 파라미터를 업데이트하므로 gradient를 전부 저장해야 해 메모리 사용량이 크다. 1B 모델 기준 FP32 개략치:
```
모델 파라미터: 1B × 4bytes = 4GB
Gradient:      1B × 4bytes = 4GB
Optimizer(AdamW): 1B × 8bytes = 8GB (momentum+variance)
Activations: ~4-16GB
총합: 약 20-32GB
```
→ 16GB VRAM에서는 Full FT가 사실상 불가능하다.

### 2.2 비트 정밀도(Bit Precision) 개념
| 정밀도 | 비트 | 파라미터당 메모리 | 용도 |
|---|---|---|---|
| FP32 | 32-bit | 4 bytes | 학습 기본값, Optimizer |
| FP16/BF16 | 16-bit | 2 bytes | Mixed Precision 학습 |
| INT8 | 8-bit | 1 byte | 추론 최적화 |
| NF4 | 4-bit | 0.5 bytes | QLoRA(극한 효율) |

7B 모델 Full FT(FP16 Mixed) vs QLoRA 비교:
```
Full FT: 모델14GB + Grad14GB + Optimizer28GB + Activations~10-20GB = 66-76GB (A100 80GB 필요)
QLoRA  : 모델(NF4)3.5GB + LoRA Grad~0.1GB + Optimizer~0.2GB + Activations~4-8GB = 8-12GB (RTX 4090/5060ti로 가능)
```
> 실무 결론: 4-bit 양자화는 성능 손실이 1~3% 수준으로 작지만 메모리는 8배 절감된다 — QLoRA가 인기 있는 이유.

### 2.3 TODO 1 — 메모리 요구량 계산 및 시각화 (구현 내용)
`compare_precision_memory()`로 7B 모델 기준 FP32/FP16/INT8/NF4별 메모리를 막대그래프로 시각화하고, `calculate_full_ft_memory(model)`로 **현재 로드된 모델**의 Full FT 예상 메모리(모델+Gradient+Optimizer+Activation)를 계산한다.

```python
def calculate_full_ft_memory(model):
    total_params = sum(p.numel() for p in model.parameters())
    model_memory = (total_params * 2) / (1024**3)   # FP16
    grad_memory  = (total_params * 2) / (1024**3)   # FP16
    optim_memory = (total_params * 8) / (1024**3)   # FP32 optimizer states
    activation_memory = model_memory * 2             # 보수적 추정
    total_memory = model_memory + grad_memory + optim_memory + activation_memory
    return total_params, {...}
```

**확인 결과**
- 현재 1B급 모델은 16GB에 들어갈 수 있지만, 7B 모델은 그 7배(약 66GB 이상) 필요해 사실상 불가능
- 무엇보다, **현재 로드된 모델은 이미 4-bit 양자화 상태**이므로 gradient 계산 자체가 불가능(`requires_grad=True` 시 RuntimeError) → 이것이 QLoRA가 "LoRA adapter만" 학습하는 이유. Base model(4-bit)은 고정 ❄️, LoRA adapter(FP16)만 학습 🔥.

---

## 3. Step 3: PEFT/LoRA 원리 이해

### 3.1 PEFT가 필요한 이유
Step 2에서 확인했듯 Full FT는 메모리 폭발 문제가 있다. PEFT는 사전학습 가중치를 **고정(freeze)**하고 적은 수의 **추가 파라미터(adapter)**만 학습해 메모리·시간을 절감하면서 Full FT에 준하는 성능을 노린다.

### 3.2 LoRA의 원리
기존 가중치 $W \in \mathbb{R}^{d\times d}$는 직접 업데이트하지 않고, 저차원 행렬 $B\in\mathbb{R}^{d\times r}$, $A\in\mathbb{R}^{r\times d}$ ($r\ll d$)만 학습한다.

$$h = Wx + BAx$$

| 단계 | 연산 | 차원 변화 |
|---|---|---|
| 1 | $x$ | $(d\times1)$ |
| 2 | $Ax$ | $(r\times d)\times(d\times1)=(r\times1)$ — 차원 축소 |
| 3 | $B(Ax)$ | $(d\times r)\times(r\times1)=(d\times1)$ — 차원 복원 |
| 4 | $Wx+BAx$ | $(d\times1)$ — 원본+adapter 합산 |

가중치 관점에서 $BA=(d\times r)\times(r\times d)=(d\times d)$로 $W$와 동일 차원이라 $W'=W+BA$로 병합 가능하다. $r\ll d$이므로 $A,B$의 파라미터 수는 $2rd$로, 원본 $d\times d$ 대비 약 $2r/d$배(예: r=8, d=4096이면 약 0.4%)에 불과하다.

> **보충: LoRA가 학습 파라미터 수를 줄이는 구조적 이유** (`LoRA_학습파라미터감소.md`)
> - **파라미터 수 비교**: Full FT는 $d\times d$ 전체를, LoRA는 $2\times d\times r$만 학습 → 보통 전체의 **0.1~1% 미만**
> - **역전파 효율**: 동결된 $W$는 미분이 필요 없고, 오직 작은 $A, B$에 대해서만 gradient를 계산
> - **Optimizer State 절감이 더 큰 이득**: AdamW는 파라미터마다 momentum/variance를 저장해 학습 파라미터 수의 3~4배 메모리를 추가로 먹는데, LoRA는 학습 대상이 적어 이 메모리가 거의 0에 가깝게 줄어듦
> - **체크포인트 용량**: Full FT는 수십 GB, LoRA는 수십 MB(어댑터만)로 저장/배포가 훨씬 용이

### 3.3 LoRA 핵심 하이퍼파라미터
| 파라미터 | 설명 | 권장값 |
|---|---|---|
| **r (rank)** | 저차원 행렬 차원. 클수록 표현력↑, 메모리↑ | 8, 16, 32, 64 |
| **lora_alpha** | 스케일링 값(α/r을 출력에 곱함). 클수록 adapter 영향↑ | r×2 (r=8 → alpha=16) |
| **target_modules** | LoRA 적용 레이어 | q/k/v/o_proj 등 |
| **lora_dropout** | 드롭아웃 비율 | 0.0~0.1 |

- **Attention**: `q_proj, k_proj, v_proj, o_proj`
- **MLP**: `gate_proj, up_proj, down_proj`

> **보충: 각 레이어(q/k/v/o, gate/up/down)는 정확히 무슨 역할인가?** (`LoRA_학습_레이어.md`)
> Transformer 내부 Linear 레이어는 **Attention**과 **Feed-Forward(FFN/MLP)** 파트로 나뉜다.
>
> **Attention 레이어 — 토큰 간 '관계' 파악**
> - `q_proj`(Query): "내가 찾는 정보는 뭐야?"라는 질의 생성
> - `k_proj`(Key): "나는 이런 정보를 가지고 있어"라는 이정표
> - `v_proj`(Value): Query·Key로 계산된 연관성(Score)만큼 가져오는 실제 값
> - `o_proj`(Output): 여러 헤드(Multi-head)의 결과를 하나로 합쳐 다음 레이어에 전달
>
> **FFN(MLP) 레이어 — 토큰이 가진 '지식' 처리** (SwiGLU 구조, 3개 레이어)
> - `up_proj`: 더 높은 차원으로 확장해 표현력↑
> - `gate_proj`: 확장된 정보 중 중요한 것을 고르는 '문지기'(활성화 함수 적용)
> - `down_proj`: 처리된 고차원 정보를 원래 차원으로 압축
>
> **왜 7개 레이어 모두에 LoRA를 적용하나?** 초기 LoRA 논문은 `q_proj`, `v_proj`만 제안했지만, QLoRA 이후 실무에서는 **모든 Linear 레이어**를 타겟하는 것이 표준이다. 특히 '체스 규칙'처럼 모델이 잘 모르던 새 지식을 주입할 때는 FFN(gate/up/down) 업데이트가 필수적이며, r을 낮게 잡아도 전 레이어를 건드리는 편이 일반화 성능이 좋다. (Unsloth에서는 `target_modules="all-linear"`로 한 번에 지정 가능)

---

## 4. Step 4: LoRA 적용 및 학습

### 4.1 Chat Template 개념
Gemma-3 chat template 형식:
```
<bos><start_of_turn>user
질문 내용<end_of_turn>
<start_of_turn>model
답변 내용<end_of_turn>
```
Unsloth의 `get_chat_template`으로 다양한 템플릿을 지원한다 (1.3절 보충 참고).

### 4.2 TODO 2 — LoRA 설정값
```python
r = 8
lora_alpha = 16          # r * 2 권장
target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                   "gate_proj", "up_proj", "down_proj"]
lora_dropout = 0.0
bias = "none"

model = FastModel.get_peft_model(
    model, r=r, target_modules=target_modules,
    lora_alpha=lora_alpha, lora_dropout=lora_dropout, bias=bias,
)
```

### 4.3 데이터셋 로드 및 Chat Template 적용
- 학습 데이터: `Thytu/ChessInstruct` `train[:5000]`
- 테스트 데이터(`train[5000:5005]`)는 Step 1에서 이미 분리 로드되어 학습에서 제외 → 공정한 전후 비교 가능

### 4.4 데이터 변환 패턴 이해 (task/input/expected_output → conversations)
원본 데이터는 `task`(작업 지시), `input`(체스 기보), `expected_output`(정답 수) 3개 필드로 구성된다. 이를 system/user/assistant 역할의 `conversations`로 매핑한다:

```python
{
    "conversations": [
        {"role": "system", "content": task},
        {"role": "user", "content": input},
        {"role": "assistant", "content": expected_output},
    ]
}
```

### 4.5 TODO 3 — `convert_to_chatml` 함수
```python
def convert_to_chatml(example):
    return {
        "conversations": [
            {"role": "system", "content": example["task"]},
            {"role": "user", "content": example["input"]},
            {"role": "assistant", "content": example["expected_output"]},
        ]
    }

dataset = dataset.map(convert_to_chatml)
```

### 4.6 텍스트 포맷팅(`formatting_prompts_func`)
```python
def formatting_prompts_func(examples):
    convos = examples["conversations"]
    texts = [
        tokenizer.apply_chat_template(
            convo, tokenize=False, add_generation_prompt=False
        ).removeprefix('<bos>')
        for convo in convos
    ]
    return {"text": texts}

dataset = dataset.map(formatting_prompts_func, batched=True)
```

> **보충: `batched=True`일 때 함수 내부에서 실제로 무슨 일이 일어나나?** (`chat_template_batch.md`)
> `dataset.map(..., batched=True)`를 쓰면 함수에 전달되는 데이터 구조가 **"리스트를 품은 딕셔너리"**로 바뀐다.
> - 기본(False): `{"conversations": [메시지들]}` — 단일 샘플
> - 배치(True): `{"conversations": [[메시지들1], [메시지들2], ...]}` — N개 샘플이 한 번에 전달
>
> 코드상 `examples["conversations"]`를 꺼내면 이미 **리스트의 리스트**이고, 리스트 컴프리헨션(`for convo in convos`)이 그 안에서 하나씩 순회하며 처리한다. `map`이 성공하려면 **입력 개수 = 출력 리스트 개수**가 일치해야 하며(예: 1,000개 입력 → `{"text": [...]}` 1,000개 출력), 결과는 기존 데이터셋에 `"text"`라는 새 컬럼으로 **한 번에(Bulk)** 붙는다. 하나씩 처리·추가하는 것보다 훨씬 빠르기 때문에 대량 데이터 전처리 시 `batched=True`를 쓴다.

### 4.7 SFTTrainer 설정 및 학습
```python
from trl import SFTConfig, SFTTrainer

trainer = SFTTrainer(
    model=model, tokenizer=tokenizer, train_dataset=dataset,
    args=SFTConfig(
        dataset_text_field="text", output_dir="outputs",
        per_device_train_batch_size=2, gradient_accumulation_steps=4,  # 실효 배치=8
        learning_rate=5e-5, max_steps=100, logging_steps=10,
        fp16=False, bf16=True, optim="adamw_8bit", report_to="none",
    ),
)

from unsloth.chat_templates import train_on_responses_only
trainer = train_on_responses_only(
    trainer,
    instruction_part="<start_of_turn>user\n",
    response_part="<start_of_turn>model\n",
)

trainer_stats = trainer.train()
```
- `gradient_accumulation_steps=4` × `per_device_train_batch_size=2` = 실효 배치 크기 8
- `optim="adamw_8bit"`: Unsloth/bitsandbytes의 8-bit Optimizer로 메모리 절약
- `train_on_responses_only`: instruction(질문) 부분은 학습에서 제외하고 **assistant 응답 부분만** loss 계산 → 학습 효율 향상
- 학습 전/후 `torch.cuda.max_memory_reserved()`로 VRAM 사용량을 확인해 16GB로도 학습이 가능함을 확인

---

## 5. Step 5: 결과 확인 및 저장

### 5.1 LoRA Adapter 저장 방식 (개념)
1. **Adapter만 저장(권장)** — 수 MB, 추론 시 base model + adapter를 함께 로드, 저장 용량 작음
2. **Merged 저장** — base와 adapter를 병합해 저장, 단일 모델 로드, 저장 용량 큼(원본 모델 크기)

```python
output_dir = "gemma3-lora-chess"
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
```

> **보충: 저장된 폴더 안에는 실제로 무엇이 들어있나?** (`save_LoRA.md`)
> `model.save_pretrained()`는 Base Model 전체가 아니라 **LoRA 어댑터(A, B 행렬 가중치)와 설정만** 저장한다.
> - `adapter_model.safetensors`(또는 `.bin`): 행렬 A, B 가중치. 보통 수십~수백 MB
> - `adapter_config.json`: 학습 당시 설정(r, alpha, target_modules 등) 기록
> - `tokenizer.json` / `tokenizer_config.json`: 토크나이저 설정
> - Base model을 다시 저장하지 않는 이유: LoRA 철학 자체가 "원본은 건드리지 않는다(freeze)"이므로, 이미 캐시/허브에 있는 원본 모델에 "이 adapter를 끼워 쓰라"는 레시피만 저장하면 충분
> - 장점: 용량 효율(8B 모델 기준 Full 저장 15GB vs LoRA 200MB), 공유/배포 용이(adapter 폴더만 올리면 됨), 나중에 필요할 때만 `merge_and_unload()`로 병합 가능
> - 재사용 예시:
>   ```python
>   model, tokenizer = FastModel.from_pretrained(
>       model_name="gemma3-lora-chess", max_seq_length=2048, load_in_4bit=True,
>   )
>   FastModel.for_inference(model)
>   ```

> **보충: 추론 속도를 위한 `merge_and_unload()`** (`merge_and_unload.md`)
> LoRA 연산은 $h = W_0x + \Delta Wx$로, 원본 경로와 adapter 경로 두 번을 계산해 더하는 구조다. Merge는 이를 $W_{new} = W_0 + \Delta W$로 **미리 한 번 계산해 하나로 합치는 것**이다.
> - 효과: 연산 횟수 감소(2회→1회), 메모리 대역폭 이득( $W_0$와 $A,B$를 각각 읽는 대신 합쳐진 $W_{new}$ 한 번만 읽음), 추가 레이어(Add/Scale) 오버헤드 제거 → **추론 속도가 원본 모델과 동일**해짐
> - `model.merge_and_unload()` = `merge()`(adapter 가중치를 base에 수학적으로 더함) + `unload()`(LoRA 전용 레이어 삭제로 VRAM 확보)
> - 선택 기준: 여러 adapter를 바꿔 끼우며 서빙한다면 분리 로드가 유리하고, 특정 서비스(예: 체스 AI)에 단일 모델로 배포한다면 merge 후 배포가 정석

### 5.2 학습 vs 추론에서 `apply_chat_template()`의 차이
| 구분 | `add_generation_prompt` | 설명 |
|---|---|---|
| 학습 | `False` | assistant 응답이 이미 포함되어 있어 생성 프롬프트 불필요 |
| 추론 | `True` | assistant 응답을 모델이 생성해야 하므로 생성 프롬프트 필요 |

```python
test_messages = [
    {"role": "system", "content": test_sample["task"]},
    {"role": "user", "content": test_sample["input"]},
]
text = tokenizer.apply_chat_template(
    test_messages, tokenize=False, add_generation_prompt=True,
).removeprefix('<bos>')
```

> **보충: `add_generation_prompt=True`는 왜 필수인가?** (`add_generation_prompt.md`)
> 이 옵션은 대화 리스트 마지막에 "이제 모델이 답할 차례"임을 알리는 특수 토큰을 자동으로 붙여준다.
> - `False`(또는 생략): `...<end_of_turn>`에서 끝나 모델이 "문장이 끝난 건지, 자기가 답할 차례인지" 헷갈릴 수 있음
> - `True`: 끝에 `<start_of_turn>model\n`이 붙어 모델이 그 다음 토큰부터 응답을 생성하도록 명확히 유도
> - 필요성: 환각(엉뚱한 발화/사용자 역할을 이어 연기) 방지, LLM이 이전 텍스트를 이어쓰는 특성을 이용한 형식 완성
> - 실전 팁: **학습 시에는 보통 False**(정답이 데이터에 이미 있으므로), **추론 시에는 반드시 True**로 설정해야 모델이 멈칫하지 않고 바로 답한다.

> **보충: 왜 `.removeprefix('<bos>')`로 BOS 토큰을 제거하나?** (`remove_prefix.md`)
> `apply_chat_template(..., tokenize=False, ...)`는 결과 문자열 맨 앞에 `<bos>`를 자동으로 붙인다. 그런데 이후 `tokenizer(text, return_tensors="pt")`를 호출하면 토크나이저가 **기본 설정(`add_special_tokens=True`)으로 다시 `<bos>`를 앞에 붙인다.**
> - 제거하지 않으면 최종 입력이 `<bos><bos><start_of_turn>user...`처럼 **BOS가 중복**된다.
> - 모델은 학습 때 본 적 없는 이 패턴에 당황해 답변을 이상하게 시작하거나 환각을 일으킬 수 있고, 심하면 user/model 구분 구조까지 무너질 수 있다.
> - 따라서 1단계(`apply_chat_template`)에서 붙은 `<bos>`를 문자열 단계에서 미리 제거해두면, 2단계(`tokenizer(...)`)에서 새로 붙는 **단 하나의 정결한 `<bos>`**만 남는다.
> - 진단 팁: 모델이 공백만 뱉거나 이상한 기호를 출력한다면 BOS 중복을 의심할 것.

> **보충: 프롬프트 → 텐서까지, 토크나이징 단계 정리** (`tokenizing_단계.md`)
> 1. **`apply_chat_template`**: `[{"role":"user","content":"안녕"}]` 같은 파이썬 객체를 특수 토큰이 포함된 **문자열**(`<start_of_turn>user\n안녕<end_of_turn>\n<start_of_turn>model\n`)로 구조화. `removeprefix`로 중복 BOS 방지(위 항목 참고)
> 2. **`tokenizer(text, return_tensors="pt").to("cuda")`**: 문자열을 vocabulary 기준 토큰 ID들로 수치화하고, PyTorch 텐서로 변환한 뒤 GPU로 이동. 이 단계에서 앞서 제거했던 `<bos>`가 토큰 ID로 다시 정확히 한 번 붙는다.
> - 결과적으로 모델은 `[BOS] + [Gemma 특수 토큰들] + [질문 토큰들]` 순으로 정렬된 입력을 받고, 마지막 `<start_of_turn>model\n` 바로 다음 토큰부터 생성을 시작한다.

### 5.3 TODO 4 — 추론 실행 및 결과
```python
from transformers import TextStreamer

_ = model.generate(
    **tokenizer(text, return_tensors="pt").to("cuda"),
    max_new_tokens=128, temperature=0.7, top_p=0.95, top_k=64,
    streamer=TextStreamer(tokenizer, skip_prompt=True),
)
```

### 5.4 파인튜닝 전후 비교
Step 1에서 저장해둔 **베이스 모델 응답**과 파인튜닝 후 응답을 학습에 사용하지 않은 테스트 데이터(5000~5004)로 나란히 비교한다. 관찰 포인트:
1. 학습 전: 체스 기보(notation) 해석이 어려움
2. 학습 후: 체스 도메인 지식이 향상되어 더 정확한 응답
3. 단 100 step만으로도 도메인 적응 효과가 확인됨

### 5.5 LoRA 효율성 요약
```python
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
total_params = sum(p.numel() for p in model.parameters())
trainable_percentage = (trainable_params / total_params) * 100
```
→ 전체 파라미터의 **약 1% 미만**만 학습하여 16GB VRAM으로도 파인튜닝을 완료했다는 것이 최종 결론이다.

---

## 6. 트러블슈팅 가이드 (노트북 부록)

**GPU/CUDA**
| 증상 | 원인 | 해결 |
|---|---|---|
| `CUDA out of memory` | GPU 메모리 부족 | 커널 재시작, `torch.cuda.empty_cache()` |
| `CUDA not available` | 드라이버 미설치 | `nvidia-smi` 확인 후 재설치 |
| bitsandbytes 설치 오류 | CUDA 버전 불일치 | `pip install bitsandbytes --prefer-binary` |

**모델**
| 증상 | 원인 | 해결 |
|---|---|---|
| `OSError: Can't load tokenizer` | 접근 권한 없음 | `huggingface-cli login` |
| 모델 다운로드 중단 | 네트워크 불안정 | `resume_download=True` |
| 시스템 RAM OOM | 메모리 부족 | 프로세스 종료 또는 배치 축소 |

**패키지 / 일반**
| 증상 | 원인 | 해결 |
|---|---|---|
| `ModuleNotFoundError` | 패키지 미설치 | Step 1 `%pip install` 재실행 |
| `ImportError: cannot import name` | 버전 불일치 | `%pip install --upgrade <패키지>` |
| `NameError` | 이전 셀 미실행 | Step 1부터 순서대로 재실행 |
| loss가 줄지 않음 | 학습률/에폭 설정 | `learning_rate`, `num_train_epochs` 조정 |

---

## 7. 자가 체크리스트
- [ ] Full Fine-tuning의 메모리 문제를 이해했는가?
- [ ] LoRA의 원리(저차원 분해)를 설명할 수 있는가?
- [ ] LoRA 하이퍼파라미터(r, lora_alpha, target_modules)의 의미를 이해했는가?
- [ ] Unsloth를 사용하여 QLoRA 학습을 수행할 수 있는가?
- [ ] 파인튜닝된 모델을 저장하고 추론할 수 있는가?

---

## 8. 더 보기 (참고 자료)
(`참고문헌.md` 기준)
- [Hugging Face Blog — Making LLMs even more accessible](https://huggingface.co/blog/4bit-transformers-bitsandbytes): QLoRA 저자진과 협력한 공식 가이드. FP32/FP16/NF4 메모리 점유율 비교 차트와 QLoRA 연산 흐름도 제공
- [Maarten Grootendorst — A Visual Guide to Quantization](https://www.maartengrootendorst.com/blog/quantization/): 선형(INT4) vs 비선형(NF4) 양자화를 수직선 눈금 간격으로 비교, NF4가 0 근처에서 왜 더 촘촘한지 시각적으로 설명
- Chris McCormick — QLoRA and 4-bit Quantization: 가중치가 NF4 bin으로 매핑되는 과정과 이중 양자화 단계를 스텝별로 시각화

**학습 팁**: Grootendorst 블로그에서 분포도 차이를 먼저 확인한 뒤, Hugging Face 블로그로 전체 아키텍처를 보는 순서를 추천.

