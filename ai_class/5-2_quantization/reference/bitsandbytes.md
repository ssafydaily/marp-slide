**bitsandbytes**는 딥러닝 모델, 특히 거대 언어 모델(LLM)을 효율적으로 학습시키고 추론하기 위해 설계된 경량화 라이브러리입니다. NVIDIA GPU의 CUDA 가속을 활용하며, 주로 **양자화(Quantization)** 기술을 통해 메모리 사용량을 획기적으로 줄이는 데 사용됩니다.

---

## 1. bitsandbytes란?

일반적으로 딥러닝 모델은 **FP32**(32비트 부동 소수점)나 **FP16** 데이터를 사용합니다. 하지만 모델이 커질수록 일반적인 소비자용 GPU 메모리(VRAM)로는 감당하기 어려워집니다. bitsandbytes는 이를 해결하기 위해 다음과 같은 기능을 제공합니다.

* **8-bit & 4-bit 양자화:** 모델 가중치를 더 적은 비트로 변환하여 메모리 점유율을 1/4 ~ 1/8 수준으로 줄입니다.
* **8-bit Optimizer:** AdamW와 같은 최적화 알고리즘의 상태(State) 데이터를 8비트로 압축하여 학습 시 메모리를 절약합니다.
* **NF4(NormalFloat 4):** 4비트 양자화에서 발생하는 정보 손실을 최소화하기 위해 bitsandbytes가 도입한 특수 데이터 타입입니다.

---

## 2. INT4 (4-bit) 양자화 적용 원리

**INT4 양자화**는 모델의 가중치를 4비트로 표현하는 기술입니다. 단순히 정수로 변환하는 것을 넘어, 최근에는 **QLoRA(Quantized Low-Rank Adaptation)** 기법과 결합하여 널리 쓰입니다.

### 핵심 개념
1.  **양자화(Quantization):** 연속적인 소수점 값을 유한한 범위의 정수나 낮은 비트 형식으로 매핑합니다. 
2.  **이중 양자화(Double Quantization):** 양자화에 필요한 상수(Scale factor) 자체를 다시 양자화하여 메모리를 추가로 절약합니다.
3.  **NF4 데이터 타입:** 정규 분포를 따르는 모델 가중치의 특성을 반영해 최적화된 4비트 체계입니다.



---

## 3. 코드 적용 방법 (Hugging Face 활용)

Hugging Face의 `transformers`와 `bitsandbytes`를 사용하면 코드 몇 줄로 INT4 양자화를 적용할 수 있습니다.

### 사전 준비
```bash
pip install bitsandbytes accelerate transformers
```

### 모델 로드 예시
`BitsAndBytesConfig`를 설정하여 모델을 불러올 때 바로 4비트로 변환합니다.

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# 1. 4-bit 양자화 설정
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,              # 4비트로 로드
    bnb_4bit_quant_type="nf4",      # NF4 타입 사용
    bnb_4bit_compute_dtype=torch.float16, # 연산 시 사용할 데이터 타입
    bnb_4bit_use_double_quant=True,  # 이중 양자화 적용
)

# 2. 모델 및 토크나이저 로드
model_id = "facebook/opt-125m" # 예시 모델
model = AutoModelForCausalLM.from_pretrained(
    model_id, 
    quantization_config=bnb_config, 
    device_map="auto"
)

tokenizer = AutoTokenizer.from_pretrained(model_id)
```

---

## 4. INT4 적용 시의 장단점

| 특징 | 설명 |
| :--- | :--- |
| **메모리 절감** | FP16 대비 약 **3.5배~4배** 적은 VRAM을 사용합니다. |
| **성능 유지** | NF4와 QLoRA를 사용할 경우, FP16 모델과 유사한 정확도를 유지합니다. |
| **속도** | 메모리 대역폭은 이득을 보지만, 연산 시 다시 역양자화(Dequantization) 과정이 필요해 추론 속도는 약간 느려질 수 있습니다. |

**bitsandbytes** 덕분에 이제 RTX 3060이나 4060 같은 보급형 GPU에서도 수십억 개의 파라미터를 가진 거대 모델을 직접 돌려볼 수 있게 된 것이죠.

혹시 특정 모델(예: Llama-3나 Mistral)에 이 설정을 직접 적용해보고 싶으신가요? 원하신다면 구체적인 튜닝 코드를 작성해 드릴 수 있습니다.