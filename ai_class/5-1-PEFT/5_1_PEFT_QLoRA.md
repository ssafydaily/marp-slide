첨부된 `5-1 PEFT(파라미터 효율적 튜닝) 실습` 노트북을 전체적으로 분석하면, 이 실습은 **“Full Fine-tuning의 메모리 한계 → PEFT의 필요성 → LoRA 원리 → QLoRA 실습 → 학습 결과 저장 및 추론”**이라는 흐름으로 구성되어 있습니다. 

특히 이 실습의 핵심은 **QLoRA = 4-bit 양자화된 Base Model + LoRA Adapter**라는 구조를 실제 코드로 경험하는 것입니다. 

---

# 1. 실습 전체 흐름

| 단계              | 실습 내용                   | 핵심 학습 개념                               |
| --------------- | ----------------------- | -------------------------------------- |
| Step 1          | 환경 설정 및 모델 로드           | Unsloth, 4-bit 양자화, Chat Template      |
| Step 2          | Full Fine-tuning 메모리 분석 | 파라미터, Gradient, Optimizer, Activation  |
| Step 3          | PEFT/LoRA 원리            | Adapter, Low-Rank, Freeze              |
| Step 4          | LoRA 적용 및 학습            | LoRA 설정, 데이터 변환, SFTTrainer            |
| Step 5          | 저장 및 추론                 | Adapter 저장, Chat Template, Generation  |
| 마무리             | 성능/파라미터 비교              | Trainable Parameter 비율, Fine-tuning 효과 |
| Troubleshooting | 오류 해결                   | CUDA, VRAM, 패키지 버전                     |

실습에서는 `Thytu/ChessInstruct` 데이터셋의 처음 5,000개를 학습에 사용하고, 5,000~5,004번 데이터를 별도의 테스트 데이터로 사용하여 **학습 전 Base Model과 학습 후 모델을 비교**하도록 구성되어 있습니다.  

---

# 2. 왜 PEFT가 필요한가?

## 2.1 Full Fine-tuning이란?

Full Fine-tuning은 사전학습된 LLM의 **모든 파라미터를 학습시키는 방법**입니다.

예를 들어 7B 모델이라면 약 70억 개의 파라미터가 있습니다.

단순히 모델 가중치만 GPU에 올리면 되는 것이 아닙니다.

학습 과정에서는 대략 다음과 같은 메모리가 필요합니다.

```text
Full Fine-tuning

Base Model Weights
        +
Gradient
        +
Optimizer States
        +
Activations
        ↓
매우 큰 GPU 메모리 필요
```

노트북에서는 7B 모델의 FP16 Full Fine-tuning을 다음과 같이 설명합니다.

```text
Model Weights       14 GB
Gradient            14 GB
Optimizer States    28 GB
Activations         10~20 GB
---------------------------
총                  66~76 GB
```

따라서 16GB VRAM 환경에서는 현실적으로 어렵다는 것을 보여주는 것이 Step 2의 목적입니다. 

### 중요한 점

**모델 크기 = GPU 메모리 요구량**이 아닙니다.

학습에서는

> 모델 + Gradient + Optimizer + Activation

을 모두 고려해야 합니다.

이것이 LLM Fine-tuning에서 PEFT가 등장한 중요한 이유입니다.

---

# 3. PEFT란?

**PEFT(Parameter-Efficient Fine-Tuning)**는 말 그대로

> **파라미터를 효율적으로 사용하는 Fine-tuning 방법**

입니다.

기존 Full Fine-tuning은

```text
Pretrained Model
       ↓
모든 Weight 학습
       ↓
모든 Parameter 업데이트
```

하지만 PEFT는

```text
Pretrained Model
       ↓
Weight Freeze ❄️
       ↓
일부 Parameter만 학습 🔥
```

합니다.

첨부 파일에서도 PEFT의 핵심을 **Base Model은 고정하고 소수의 Adapter Parameter만 학습하는 방식**으로 설명하고 있습니다. 

---

# 4. PEFT의 장점과 단점

## 장점

### ① GPU 메모리 감소

학습해야 하는 파라미터가 매우 적어집니다.

### ② 학습 속도 향상

Gradient와 Optimizer가 필요한 파라미터가 감소합니다.

### ③ 저장 공간 감소

전체 LLM을 저장하는 대신 LoRA Adapter만 저장할 수 있습니다.

### ④ 여러 Task에 재사용 가능

하나의 Base Model에 여러 개의 Adapter를 만들 수 있습니다.

```text
             ┌── LoRA Adapter A : 번역
Base Model ──┼── LoRA Adapter B : 의료
             ├── LoRA Adapter C : 법률
             └── LoRA Adapter D : 체스
```

### 단점

* Full Fine-tuning보다 모델 전체를 자유롭게 변경하기 어렵습니다.
* Rank, target module 등의 하이퍼파라미터 선택이 필요합니다.
* 모든 Task에서 Full Fine-tuning과 동일한 성능을 보장하지 않습니다.
* 너무 작은 rank를 사용하면 표현력이 부족할 수 있습니다.
* 데이터 자체가 좋지 않으면 PEFT를 사용해도 좋은 모델이 만들어지지 않습니다.

---

# 5. LoRA란?

LoRA는 **Low-Rank Adaptation**입니다.

PEFT 방법 중 가장 대표적인 방법입니다.

핵심 아이디어는 매우 간단합니다.

### 기존 방식

기존 가중치

[
W
]

자체를 변경합니다.

### LoRA

기존 (W)는 그대로 둡니다.

그리고 별도의 작은 행렬을 학습합니다.

[
W' = W + \Delta W
]

여기서

[
\Delta W = BA
]

입니다.

첨부 파일에서도 이 구조를 다음과 같이 설명합니다. 

---

# 6. LoRA가 왜 효율적인가?

원래 가중치가

[
W \in R^{d \times d}
]

라고 해봅시다.

Full Fine-tuning에서는

```text
d × d
```

개의 파라미터를 학습합니다.

LoRA는

[
A \in R^{r \times d}
]

[
B \in R^{d \times r}
]

만 학습합니다.

따라서 학습 파라미터는

[
rd + dr = 2rd
]

입니다.

여기서 핵심은

[
r \ll d
]

입니다.

예를 들어

```text
d = 4096
r = 8
```

이면

```text
Full FT
4096 × 4096

LoRA
4096 × 8
+
8 × 4096
```

이므로 학습 파라미터 수가 극적으로 감소합니다. 노트북도 r=8일 때 원본 가중치 대비 약 1% 수준으로 설명합니다. 

---

# 7. LoRA의 실제 동작

입력을 (x)라고 하면 기존 모델은

[
h = Wx
]

입니다.

LoRA를 적용하면

[
h = Wx + BAx
]

가 됩니다.

즉,

```text
             ┌─────────────── W ───────────────┐
Input x ─────┤                                  ├──→ Output
             └──────────────────────────────────┘
                         +
             ┌── A ──┐     ┌── B ──┐
Input x ─────┤ d → r ├────→┤ r → d ├──→ Adapter
             └───────┘     └───────┘
```

### 핵심

**W는 학습하지 않습니다.**

```text
W   → Freeze ❄️
A,B → Train 🔥
```

이것이 LoRA의 핵심입니다.

---

# 8. LoRA의 주요 하이퍼파라미터

실습에서는 다음과 같이 설정합니다. 

```python
r = 8

lora_alpha = 16

target_modules = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj"
]

lora_dropout = 0.0
bias = "none"
```

## ① r

```python
r = 8
```

**Rank**입니다.

LoRA의 저차원 공간 크기입니다.

```text
r 작음
→ Parameter 적음
→ 메모리 적음
→ 표현력 감소 가능

r 큼
→ Parameter 많음
→ 메모리 증가
→ 표현력 증가
```

일반적으로 실습에서는 8, 16, 32, 64 등을 고려합니다. 

---

## ② lora_alpha

```python
lora_alpha = 16
```

LoRA 업데이트의 **스케일을 조절**합니다.

일반적으로

```text
alpha / r
```

형태로 영향력이 결정됩니다.

실습에서는

```text
r = 8
alpha = 16
```

으로 설정합니다.

즉,

[
\frac{\alpha}{r} = \frac{16}{8}=2
]

입니다.

---

## ③ target_modules

```python
target_modules = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj"
]
```

**어떤 Linear Layer에 LoRA를 적용할 것인지** 결정합니다.

### Attention

```text
q_proj
k_proj
v_proj
o_proj
```

### MLP

```text
gate_proj
up_proj
down_proj
```

따라서 이 실습에서는 Attention뿐만 아니라 MLP에도 LoRA를 적용합니다. 

---

# 9. LoRA와 QLoRA의 차이

이 부분이 이번 실습에서 **가장 중요합니다.**

| 구분          | LoRA      | QLoRA               |
| ----------- | --------- | ------------------- |
| Base Model  | FP16/BF16 | 4-bit               |
| Base Weight | Freeze    | Freeze              |
| Adapter     | FP16/BF16 | FP16/BF16           |
| 핵심          | Low Rank  | Quantization + LoRA |
| GPU 메모리     | 감소        | **더 크게 감소**         |

첨부 실습에서는 이 차이를 명확하게 설명하고 있습니다. 

---

# 10. QLoRA란?

QLoRA는

> **Quantized LoRA**

입니다.

즉,

[
\boxed{QLoRA = Quantization + LoRA}
]

입니다.

구조는 다음과 같습니다.

```text
                 Base Model
                    │
              4-bit Quantization
                    │
                    ▼
             Quantized Base
               Model ❄️
                    │
             ┌──────┴──────┐
             │             │
             │   LoRA      │
             │  Adapter 🔥 │
             │             │
             └──────┬──────┘
                    │
                    ▼
                Fine-tuning
```

즉,

**Base Model은 4-bit로 저장하고 고정하고, LoRA Adapter만 학습합니다.**

---

# 11. 왜 4-bit인가?

예를 들어 1개의 파라미터를 저장할 때

| 방식        |      메모리 |
| --------- | -------: |
| FP32      |  4 bytes |
| FP16/BF16 |  2 bytes |
| INT8      |   1 byte |
| 4-bit     | 0.5 byte |

따라서 7B 모델의 단순 weight 저장량은 대략

```text
FP32  → 28 GB
FP16  → 14 GB
INT8  → 7 GB
4-bit  → 3.5 GB
```

수준으로 감소합니다. 실습 자료도 이러한 비교를 통해 QLoRA의 필요성을 설명합니다. 

단, **실제 GPU 사용량은 이보다 더 큽니다.** KV cache, activation, temporary buffer, CUDA allocator 등의 영향이 있기 때문입니다.

---

# 12. QLoRA의 핵심 기술 3가지

실습에서는 QLoRA의 핵심 기술로 다음 세 가지를 설명합니다. 

## ① NF4

**NormalFloat 4-bit**

LLM 가중치의 분포 특성을 고려한 4-bit 양자화 방식입니다.

일반적인 INT4와 단순히 동일하다고 생각하면 안 됩니다.

핵심은

> **가중치 정보를 4-bit 수준으로 압축하면서 정보 손실을 줄이는 것**

입니다.

---

## ② Double Quantization

양자화할 때는 가중치뿐만 아니라 **양자화에 필요한 scaling constant 등의 정보**도 필요합니다.

QLoRA는 이 양자화 관련 정보까지 다시 양자화하여 메모리를 추가로 절약합니다.

```text
Weight
 ↓
Quantization
 ↓
Quantization Parameters
 ↓
다시 Quantization
```

---

## ③ Paged Optimizer

GPU 메모리가 부족한 상황에서 optimizer state를 효율적으로 관리하기 위한 방법입니다.

쉽게 말하면

```text
GPU VRAM
   ↕
CPU RAM
```

사이에 필요한 메모리를 관리하여 GPU 메모리 부족을 완화하는 방식입니다.

---

# 13. QLoRA의 가장 중요한 구조

교육할 때는 다음 그림으로 설명하면 이해가 쉽습니다.

```text
             QLoRA

        ┌─────────────────┐
        │   Base Model    │
        │                 │
        │     4-bit       │
        │      NF4        │
        │                 │
        │   Frozen ❄️     │
        └────────┬────────┘
                 │
                 │ Forward
                 ▼
        ┌─────────────────┐
        │  LoRA Adapter   │
        │                 │
        │   A + B         │
        │                 │
        │ Trainable 🔥    │
        └────────┬────────┘
                 │
                 ▼
              Output
```

**Q 부분은 Base Model의 양자화이고, LoRA 부분은 학습 가능한 Adapter입니다.**

---

# 14. Step 1 — 환경 설정

실습에서 사용하는 주요 패키지는 다음과 같습니다. 

| 패키지            | 역할                        |
| -------------- | ------------------------- |
| `unsloth`      | 효율적인 LLM Fine-tuning      |
| `transformers` | Hugging Face 모델/Tokenizer |
| `peft`         | PEFT/LoRA 구현              |
| `trl`          | SFTTrainer 등 학습 도구        |
| `torch`        | 딥러닝 프레임워크                 |
| `datasets`     | 데이터셋 로딩/처리                |
| `accelerate`   | GPU/분산 학습 지원              |
| `bitsandbytes` | 양자화 및 8-bit Optimizer     |
| `matplotlib`   | 메모리 시각화                   |

---

# 15. Unsloth

실습에서는

```python
from unsloth import FastModel
```

을 사용합니다.

Unsloth는 LLM Fine-tuning을 보다 효율적으로 수행하기 위한 프레임워크입니다.

특히 이 실습에서는

```text
LoRA
QLoRA
4-bit
GPU Memory Optimization
```

등을 쉽게 사용할 수 있도록 해줍니다.

노트북에서는 GPU 커널 최적화를 통한 속도 및 메모리 효율 개선을 Unsloth의 주요 특징으로 제시합니다. 

---

# 16. 모델 로딩

핵심 코드는 다음입니다.

```python
model_name = "unsloth/gemma-3-1b-it-unsloth-bnb-4bit"

model, tokenizer = FastModel.from_pretrained(
    model_name=model_name,
    max_seq_length=max_seq_length,
)
```



### `FastModel.from_pretrained()`

사전학습된 모델과 Tokenizer를 로드합니다.

여기서 모델 이름에

```text
bnb-4bit
```

가 들어 있다는 것이 중요합니다.

즉,

```text
bnb
 ↓
bitsandbytes

4bit
 ↓
4-bit 양자화
```

를 의미합니다.

따라서 이미 **QLoRA의 Q 부분**을 준비한 것입니다.

---

# 17. Tokenizer와 Chat Template

LLM은 단순히

```python
"질문"
```

을 넣는 것이 아니라 모델이 학습한 **대화 형식**에 맞춰 입력해야 합니다.

실습에서는

```python
from unsloth.chat_templates import get_chat_template

tokenizer = get_chat_template(
    tokenizer,
    chat_template="gemma3"
)
```

를 사용합니다. 

---

# 18. Chat Template이 중요한 이유

원본 데이터는

```text
task
input
expected_output
```

형태입니다.

이를

```text
system
user
assistant
```

형태로 변경합니다.

```python
{
    "conversations": [
        {"role": "system", "content": task},
        {"role": "user", "content": input},
        {"role": "assistant", "content": expected_output}
    ]
}
```



즉,

```text
task             → system
input            → user
expected_output  → assistant
```

입니다.

---

# 19. `dataset.map()`의 역할

```python
dataset = dataset.map(convert_to_chatml)
```

여기서 `map()`은 Dataset의 각 샘플에 함수를 적용합니다.

즉,

```text
원본 데이터
    ↓
convert_to_chatml()
    ↓
conversations 데이터
```

로 변환합니다. 

---

# 20. Chat Template 적용

다음 코드도 중요합니다.

```python
def formatting_prompts_func(examples):
    convos = examples["conversations"]

    texts = [
        tokenizer.apply_chat_template(
            convo,
            tokenize=False,
            add_generation_prompt=False
        ).removeprefix('<bos>')
        for convo in convos
    ]

    return {"text": texts}
```

그리고

```python
dataset = dataset.map(
    formatting_prompts_func,
    batched=True
)
```

를 실행합니다. 

### `apply_chat_template()`

대화 데이터를 실제 모델이 학습할 **문자열 형식**으로 변환합니다.

예를 들어 개념적으로

```text
user
질문
model
정답
```

형태로 변환합니다.

---

# 21. 학습 시 `add_generation_prompt=False`

학습 데이터에는 이미 정답이 있습니다.

```text
User
 ↓
질문

Model
 ↓
정답
```

따라서

```python
add_generation_prompt=False
```

입니다.

반대로 추론에서는 정답이 없습니다.

```text
User
 ↓
질문

Model
 ↓
???
```

따라서

```python
add_generation_prompt=True
```

를 사용합니다.

노트북에서도 이 차이를 명시적으로 강조하고 있습니다. 

이 부분은 실습에서 **매우 중요한 주의사항**입니다.

---

# 22. LoRA 적용 코드

실습의 핵심 코드입니다.

```python
model = FastModel.get_peft_model(
    model,
    r=r,
    target_modules=target_modules,
    lora_alpha=lora_alpha,
    lora_dropout=lora_dropout,
    bias=bias,
)
```



### `FastModel.get_peft_model()`

기존 모델에 PEFT/LoRA Adapter를 추가합니다.

결과적으로

```text
기존 Model
    ↓
PEFT 적용
    ↓
Base Model       → Freeze
LoRA Adapter     → Train
```

구조가 됩니다.

---

# 23. SFTTrainer

실제 학습에는

```python
from trl import SFTConfig, SFTTrainer
```

를 사용합니다.

그리고

```python
trainer = SFTTrainer(
    model=model,
    processing_class=tokenizer,
    train_dataset=dataset,
    args=SFTConfig(...)
)
```

를 사용합니다. 

## SFT란?

**Supervised Fine-Tuning**

입니다.

입력과 정답이 존재하는 데이터로 모델을 학습시키는 방식입니다.

이번 실습은

```text
Chess Input
     ↓
Expected Chess Move
```

라는 정답이 있으므로 SFT에 해당합니다.

---

# 24. 주요 SFTConfig

```python
SFTConfig(
    dataset_text_field="text",
    output_dir="outputs",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=5e-5,
    max_steps=100,
    logging_steps=10,
    fp16=False,
    bf16=True,
    optim="adamw_8bit",
    report_to="none",
)
```

### `per_device_train_batch_size`

GPU 한 장에서 한 번에 처리하는 샘플 수입니다.

```text
2
```

로 설정되어 있습니다.

VRAM이 부족하면 가장 먼저 줄여볼 수 있는 값입니다.

---

### `gradient_accumulation_steps`

```python
gradient_accumulation_steps=4
```

입니다.

실질적으로

```text
batch size = 2
accumulation = 4

effective batch size ≈ 2 × 4 = 8
```

의 효과를 얻습니다.

따라서 VRAM은 적게 사용하면서 더 큰 effective batch size를 구성할 수 있습니다.

---

### `learning_rate`

```python
learning_rate=5e-5
```

학습률입니다.

너무 크면

```text
Loss 발산
학습 불안정
```

이 발생할 수 있습니다.

노트북에서도 loss가 발산하면 learning rate를 낮추도록 안내합니다. 

---

### `optim="adamw_8bit"`

```python
optim="adamw_8bit"
```

8-bit AdamW Optimizer를 사용합니다.

이 역시 메모리 절약을 위한 선택입니다.

`bitsandbytes`가 이 부분을 지원합니다.

---

# 25. Response-only Training

다음 코드도 상당히 중요합니다.

```python
from unsloth.chat_templates import train_on_responses_only

trainer = train_on_responses_only(
    trainer,
    instruction_part="<start_of_turn>user\n",
    response_part="<start_of_turn>model\n",
)
```



의미는

> **사용자의 질문 부분보다는 모델의 답변 부분을 중심으로 Loss를 계산하자**

는 것입니다.

즉,

```text
User Instruction
     ↓
Loss 계산에서 제외

Assistant Response
     ↓
학습 대상
```

으로 이해하면 됩니다.

---

# 26. 실제 학습

```python
trainer_stats = trainer.train()
```

이 한 줄이 실제 학습을 시작합니다. 

내부적으로는 대략

```text
Dataset
 ↓
Tokenizer
 ↓
Batch
 ↓
Forward
 ↓
Loss
 ↓
Backward
 ↓
LoRA Gradient
 ↓
Optimizer
 ↓
LoRA Parameter Update
```

가 반복됩니다.

중요한 것은 **Base Model의 모든 파라미터를 업데이트하는 것이 아니라 LoRA Adapter의 파라미터를 업데이트한다는 것**입니다.

---

# 27. LoRA Adapter 저장

학습 후에는

```python
output_dir = "gemma3-lora-chess"

model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
```

를 사용합니다. 

여기서 중요한 점은 **전체 모델을 저장하는 것이 아니라 LoRA Adapter 중심으로 저장할 수 있다는 것**입니다.

---

# 28. Adapter 저장 vs Merge

## 방법 1. Adapter만 저장

```text
Base Model
+
LoRA Adapter
```

장점:

* 저장 공간 작음
* 여러 Adapter 관리 가능
* Base Model 재사용 가능

노트북에서도 Adapter만 저장하는 방법을 권장합니다. 

---

## 방법 2. Merge

```text
Base Model + LoRA
        ↓
    Merge
        ↓
 하나의 모델
```

대표적으로

```python
model.merge_and_unload()
```

을 사용할 수 있습니다.

장점:

* 추론 환경을 단순화할 수 있음
* 별도의 Adapter 관리가 필요 없음

단점:

* 모델 저장 용량이 다시 커짐
* 원래의 Adapter 구조처럼 여러 Task를 쉽게 교체하기 어려움

---

# 29. 추론 코드

실습의 추론 과정은 다음과 같습니다.

```python
test_messages = [
    {"role": "system", "content": test_sample["task"]},
    {"role": "user", "content": test_sample["input"]}
]

text = tokenizer.apply_chat_template(
    test_messages,
    tokenize=False,
    add_generation_prompt=True,
)
```

그리고

```python
_ = model.generate(
    **tokenizer(text, return_tensors="pt").to("cuda"),
    max_new_tokens=128,
    temperature=0.7,
    top_p=0.95,
    top_k=64,
    streamer=TextStreamer(tokenizer, skip_prompt=True),
)
```

를 사용합니다. 

---

# 30. `model.generate()`

Hugging Face Transformers에서 텍스트 생성을 담당하는 대표적인 메소드입니다.

### 주요 옵션

```python
max_new_tokens=128
```

최대 생성 토큰 수입니다.

```python
temperature=0.7
```

확률 분포의 무작위성을 조절합니다.

```text
낮음 → 보수적
높음 → 다양한 출력
```

```python
top_p=0.95
```

Nucleus Sampling입니다.

누적 확률이 일정 범위가 되는 후보들만 고려합니다.

```python
top_k=64
```

상위 K개의 토큰 후보를 대상으로 sampling합니다.

---

# 31. `TextStreamer`

```python
from transformers import TextStreamer
```

생성되는 텍스트를 한꺼번에 기다리지 않고 **생성되는 즉시 화면에 출력**하기 위한 클래스입니다.

```python
streamer=TextStreamer(
    tokenizer,
    skip_prompt=True
)
```

따라서 Jupyter Notebook에서도 ChatGPT처럼 응답이 실시간으로 출력되는 효과를 얻습니다.

---

# 32. LoRA 효과를 어떻게 측정하는가?

실습 마지막에는 다음 코드를 사용합니다.

```python
trainable_params = sum(
    p.numel()
    for p in model.parameters()
    if p.requires_grad
)

total_params = sum(
    p.numel()
    for p in model.parameters()
)

trainable_percentage = (
    trainable_params / total_params
) * 100
```



여기서 매우 중요한 PyTorch 개념이 나옵니다.

### `p.numel()`

Tensor가 가지고 있는 **전체 원소의 개수**를 반환합니다.

### `p.requires_grad`

해당 Parameter에 대해 gradient 계산을 수행할지 나타냅니다.

따라서

```python
if p.requires_grad
```

는

> **현재 학습 가능한 파라미터만 선택**

한다는 의미입니다.

---

# 33. 이 코드가 LoRA의 효과를 증명한다

예를 들어

```text
전체 Parameter
10억

Trainable Parameter
1천만
```

이라면

[
\frac{10,000,000}{1,000,000,000}\times100
=1%
]

입니다.

즉,

```text
전체 모델
████████████████████████████████

LoRA 학습 파라미터
█
```

정도의 차이가 발생합니다.

이것이 **Parameter-Efficient Fine-Tuning**이라는 이름의 의미입니다.

---

# 34. 실습에서 반드시 이해해야 할 핵심 개념

교육 관점에서 다음 8개는 반드시 연결해서 이해해야 합니다.

```text
Full Fine-tuning
       ↓
모든 Parameter 학습
       ↓
GPU Memory 문제
       ↓
PEFT
       ↓
Base Model Freeze
       ↓
LoRA Adapter 학습
       ↓
4-bit Quantization 추가
       ↓
QLoRA
```

즉,

> **PEFT는 문제를 해결하기 위한 큰 전략이고, LoRA는 대표적인 PEFT 방법이며, QLoRA는 LoRA에 4-bit 양자화를 결합한 방법입니다.**

이 관계가 가장 중요합니다.

---

# 35. LoRA vs QLoRA를 한 문장으로 구분

### LoRA

> **Base Model은 FP16/BF16으로 유지하면서 작은 LoRA Adapter만 학습한다.**

### QLoRA

> **Base Model을 4-bit로 양자화하고 고정한 뒤 LoRA Adapter만 학습한다.**

따라서

```text
LoRA
= Freeze + Low Rank

QLoRA
= Quantization + Freeze + Low Rank
```

라고 기억하면 좋습니다.

---

# 36. Full FT / LoRA / QLoRA 비교

| 항목             | Full FT     | LoRA            | QLoRA                |
| -------------- | ----------- | --------------- | -------------------- |
| Base Model     | 학습          | Freeze          | Freeze               |
| Base Precision | FP16/BF16 등 | FP16/BF16       | **4-bit**            |
| Adapter        | 없음          | 사용              | 사용                   |
| 학습 Parameter   | 100%        | 매우 적음           | 매우 적음                |
| VRAM           | 매우 큼        | 감소              | **가장 작음**            |
| 저장 공간          | 큼           | 작음              | 작음                   |
| 구현 난이도         | 보통          | 보통              | 다소 높음                |
| 제한된 GPU        | 어려움         | 가능              | **매우 유리**            |
| 대표 목적          | 모델 전체 재학습   | 효율적 Fine-tuning | **저사양 GPU에서 LLM FT** |

---

# 37. 실습에서 주의해야 할 사항

## ① VRAM 부족

노트북에서도 다음을 권장합니다. 

```python
per_device_train_batch_size ↓
```

또는

```python
gradient_accumulation_steps ↑
```

를 고려합니다.

---

## ② Sequence Length

```python
max_seq_length = 1024
```

로 설정되어 있습니다. 

Sequence Length가 증가하면 일반적으로 Activation Memory도 증가합니다.

따라서 VRAM이 부족하다면

```text
1024
 ↓
512
```

처럼 줄이는 것도 방법입니다.

---

## ③ Learning Rate

Loss가 발산하면

```python
learning_rate
```

를 낮추는 것이 좋습니다.

---

## ④ Chat Template 일치

학습할 때 사용한 Template과 추론할 때 사용하는 Template이 달라지면 성능이 크게 떨어질 수 있습니다.

특히

```python
add_generation_prompt=False
```

와

```python
add_generation_prompt=True
```

를 학습/추론에 맞게 구분해야 합니다.

---

## ⑤ Train/Test 데이터 분리

이 실습은

```text
Train
0 ~ 4999

Test
5000 ~ 5004
```

로 분리합니다. 

이것은 중요한 설계입니다.

학습에 사용한 데이터를 다시 평가하면 **Fine-tuning 효과를 제대로 측정하기 어렵기 때문**입니다.

---

# 38. 첨부 파일 내용에서 특히 주의해서 설명해야 할 부분

실습 자료의 일부 메모리 수치는 **교육을 위한 대략적인 추정치**로 이해하는 것이 좋습니다.

예를 들어 노트북에서는 1B 모델의 Full FT 메모리를 계산할 때 Activation을 `model_memory * 2`로 추정합니다. 

하지만 실제 Activation Memory는

```text
Batch Size
Sequence Length
Hidden Size
Number of Layers
Attention 구현
Gradient Checkpointing
Flash Attention
```

등에 따라 크게 달라집니다.

따라서

> **“7B 모델 Full FT는 정확히 66~76GB가 필요하다”**

라고 암기하기보다는

> **“Full Fine-tuning은 Weight 외에 Gradient와 Optimizer State, Activation까지 필요하므로 모델 크기가 커질수록 GPU 메모리가 급격하게 증가한다.”**

라고 이해하는 것이 정확합니다.

---

# 39. 또 하나의 중요한 주의점: 4-bit라고 GPU 메모리가 정확히 1/4이 되는 것은 아니다

이론적으로

```text
FP16 = 16 bit
4bit  = 4 bit
```

이므로 weight 자체는 1/4 수준이 됩니다.

하지만 실제 GPU 메모리는

```text
Quantized Weight
+ Quantization Metadata
+ LoRA Adapter
+ Gradient
+ Optimizer
+ Activation
+ CUDA Workspace
+ KV Cache 등
```

이 필요합니다.

따라서

> **4-bit = 실제 GPU 사용량이 정확히 1/4**

이라고 생각하면 안 됩니다.

실습의 수치는 **개념을 이해하기 위한 근사치**로 보는 것이 적절합니다.

---

# 40. 패키지 → 클래스 → 메소드 관계

이번 실습의 코드를 계층적으로 정리하면 다음과 같습니다.

```text
PyTorch
 └─ torch
     ├─ Tensor
     ├─ no_grad()
     └─ cuda

Hugging Face Transformers
 ├─ tokenizer
 │   └─ apply_chat_template()
 ├─ model
 │   └─ generate()
 └─ TextStreamer

Hugging Face Datasets
 └─ load_dataset()
     └─ Dataset.map()

PEFT
 └─ LoRA
     └─ Adapter

TRL
 ├─ SFTConfig
 └─ SFTTrainer
     └─ train()

Unsloth
 ├─ FastModel
 │   ├─ from_pretrained()
 │   └─ get_peft_model()
 └─ chat_templates
     ├─ get_chat_template()
     └─ train_on_responses_only()

bitsandbytes
 └─ 4-bit Quantization
 └─ AdamW 8-bit Optimizer
```

---

# 41. 실습 전체를 코드 관점에서 압축하면

결국 이 실습의 핵심 코드는 다음 흐름입니다.

```python
# 1. 4-bit Base Model
model, tokenizer = FastModel.from_pretrained(
    model_name="...bnb-4bit",
    max_seq_length=1024,
)

# 2. Chat Template
tokenizer = get_chat_template(
    tokenizer,
    chat_template="gemma3"
)

# 3. LoRA Adapter
model = FastModel.get_peft_model(
    model,
    r=8,
    lora_alpha=16,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    lora_dropout=0.0,
    bias="none",
)

# 4. Dataset
dataset = load_dataset(
    "Thytu/ChessInstruct",
    split="train[:5000]"
)

# 5. Chat Format
dataset = dataset.map(convert_to_chatml)

# 6. Text Format
dataset = dataset.map(
    formatting_prompts_func,
    batched=True
)

# 7. SFT Trainer
trainer = SFTTrainer(
    model=model,
    processing_class=tokenizer,
    train_dataset=dataset,
    args=SFTConfig(...)
)

# 8. Train
trainer.train()

# 9. Save Adapter
model.save_pretrained("gemma3-lora-chess")

# 10. Inference
model.generate(...)
```

이 코드의 핵심적인 의미는 한 줄로 표현하면 다음과 같습니다.

> **“4-bit로 압축해서 Base Model을 고정하고, 작은 LoRA Adapter만 SFT 방식으로 학습한다.”**

---

# 42. 교육용 핵심 정리

학생들에게 이 실습을 설명한다면 다음처럼 정리하는 것이 가장 효과적입니다.

### ① Full Fine-tuning

```text
모든 파라미터 학습
       ↓
성능은 좋지만
       ↓
VRAM/시간/저장공간 매우 큼
```

### ② PEFT

```text
Base Model Freeze
       ↓
일부 Parameter만 학습
       ↓
메모리/시간 절약
```

### ③ LoRA

```text
W를 직접 수정하지 않고
ΔW = BA
       ↓
작은 저차원 Adapter만 학습
```

### ④ QLoRA

```text
Base Model
   ↓
4-bit Quantization
   ↓
Freeze
   +
LoRA Adapter
   ↓
Adapter만 학습
```

### ⑤ 결과

```text
Full FT
100% Parameter 학습
        ↓
        ❌ 높은 VRAM

QLoRA
매우 적은 Parameter 학습
        +
4-bit Base Model
        ↓
        ✅ 제한된 GPU에서도 LLM Fine-tuning 가능
```

---

## 최종적으로 반드시 기억할 5가지

1. **PEFT는 하나의 특정 알고리즘이 아니라 효율적인 Fine-tuning을 위한 방법론/범주이다.**
2. **LoRA는 대표적인 PEFT 기법으로, Base Weight를 고정하고 저차원 Adapter를 학습한다.**
3. **LoRA의 핵심 수식은 `ΔW = BA`이다.**
4. **QLoRA는 4-bit 양자화된 Base Model + LoRA Adapter를 사용하는 방법이다.**
5. **이번 실습의 핵심 목적은 “Full FT를 할 수 없는 제한된 GPU에서 QLoRA를 이용해 LLM을 Fine-tuning할 수 있다”는 것을 코드와 메모리 측면에서 직접 체험하는 것이다.**

첨부된 노트북은 특히 **Step 2에서 메모리 문제를 먼저 체감시키고 Step 3~4에서 LoRA/QLoRA로 해결하는 교육 구조**가 잘 설계되어 있습니다. 따라서 수업에서는 단순히 LoRA 수식을 설명하기보다 **“왜 LoRA가 필요한가 → LoRA가 무엇인가 → 왜 여기에 4-bit 양자화를 추가하는가 → 실제로 16GB VRAM에서 학습되는가”** 순서로 설명하는 것이 가장 효과적입니다. 
