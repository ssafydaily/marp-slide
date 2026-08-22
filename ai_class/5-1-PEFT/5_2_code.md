# 5-2 Quantization 실습 — 코드셀 상세 주석 정리

`(실습-정답) 5-2_Quantization.ipynb`에서 **코드 셀(Code Cell)만 추출**하여, 각 줄/블록에 상세 설명 주석을 추가했습니다. 마크다운 셀(개념 설명)은 제외했습니다.

---

## Step 1. 환경 설정

### Cell 1 — 라이브러리 설치 (주석 처리됨: 로컬 환경 1회 실행용)

```python
# %%capture
# # 로컬 환경용 설치 (RTX 5060ti, 16GB VRAM)
# %pip install "transformers>=4.55.0" "bitsandbytes>=0.43.0"
# %pip install "torch>=2.0.0" "accelerate>=0.30.0"

# ▶ %%capture: 이 셀의 pip 설치 로그(긴 출력)를 노트북 화면에서 숨기는 매직 커맨드
# ▶ transformers>=4.55.0 : HuggingFace 모델/토크나이저 로딩 및 generate() 추론 API 제공
# ▶ bitsandbytes>=0.43.0 : INT8/INT4 양자화 커널(NF4 등)을 제공하는 핵심 라이브러리
# ▶ torch>=2.0.0        : 텐서 연산, GPU 메모리 관리, dtype(fp32/fp16) 제어
# ▶ accelerate>=0.30.0  : device_map="auto" 등 모델을 GPU/CPU에 자동 배치·분산
# ▶ 이미 환경 구성이 끝난 상태(Colab/사전 설치)라면 이 셀은 실행하지 않아도 됨 → 주석 처리
```

### Cell 2 — 필수 모듈 import 및 GPU 확인

```python
import torch                                                        # 텐서 연산 / GPU 메모리 API 전체
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
# ▶ AutoModelForCausalLM : "다음 토큰 예측" 방식의 언어모델(GPT류)을 자동으로 불러오는 클래스
# ▶ AutoTokenizer        : 모델과 짝을 이루는 토크나이저(문장 ↔ 토큰 ID 변환)를 자동으로 불러오는 클래스
# ▶ BitsAndBytesConfig   : INT8/INT4 양자화 옵션을 정의하는 설정 객체 (Step 3에서 사용)
import time                                                          # 추론 시간(latency) 측정용

# GPU 확인
if torch.cuda.is_available():
    # ▶ torch.cuda.is_available(): 현재 환경에 CUDA GPU를 사용할 수 있는지 boolean으로 반환
    gpu_stats = torch.cuda.get_device_properties(0)
    # ▶ get_device_properties(0): 0번 GPU 장치의 스펙(이름, 총 메모리 등)을 담은 객체 반환
    print(f"GPU: {gpu_stats.name}")
    print(f"최대 메모리: {gpu_stats.total_memory / 1024**3:.2f} GB")
    # ▶ total_memory는 byte 단위 → 1024**3(=1GB)로 나눠서 GB로 환산
    # ▶ 이 값이 이후 모든 실습의 "제약 조건"이 됨 (예: 16GB VRAM)
else:
    print("GPU를 사용할 수 없습니다. CUDA 환경을 확인하세요.")
    # ▶ GPU가 없으면 이후 모델 로딩/추론 셀은 매우 느리거나 실행 불가
```

---

## Step 2. FP16 모델 로딩 (문제 체감)

### Cell 3 — FP16 모델 로딩

```python
# 사용할 모델 (경량 모델 선택 - Gated가 아닌 모델)
model_name = "Qwen/Qwen2.5-1.5B-Instruct"
# ▶ Gated 모델(예: Llama 계열)은 HuggingFace 접근 승인/토큰이 필요해 실습에 방해가 될 수 있어
#    별도 승인 없이 바로 받을 수 있는 1.5B(15억 파라미터)급 경량 모델을 사용

# FP16 모델 로딩
print("FP16 모델 로딩 중...")
torch.cuda.reset_peak_memory_stats()
# ▶ 지금까지 기록된 "GPU 최대 사용 메모리(peak)" 통계를 0으로 초기화
#    → 이후 max_memory_allocated() 호출 시 "이 시점 이후"의 순수한 최대치만 측정하기 위함

model_fp16 = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,   # ▶ 가중치를 16비트 부동소수점으로 로딩 (기본값은 FP32)
    device_map="auto",           # ▶ accelerate가 사용 가능한 GPU/CPU에 레이어를 자동 배치
)
tokenizer = AutoTokenizer.from_pretrained(model_name)
# ▶ 모델과 동일한 vocabulary/규칙을 쓰는 토크나이저 로딩 (문장을 토큰 ID 시퀀스로 변환)

# 모델 로딩 직후 메모리 측정 (가중치 메모리)
model_memory_fp16 = torch.cuda.memory_allocated() / 1024**3
# ▶ memory_allocated(): "현재 시점"에 GPU에 실제로 할당되어 있는 텐서 메모리(byte)
#    로딩 직후 호출하므로, 이 값은 사실상 "모델 가중치 자체의 메모리 크기"에 해당
print(f"모델 로딩 완료: {model_name}")
print(f"FP16 모델 메모리: {model_memory_fp16:.2f} GB")
```

### Cell 4 — 모델 파라미터 수 확인 및 이론적 메모리 계산

```python
# 모델 파라미터 수 확인
total_params = sum(p.numel() for p in model_fp16.parameters())
# ▶ model.parameters(): 모델 내부의 모든 가중치 텐서(p)를 순회하는 이터레이터
# ▶ p.numel(): 텐서 하나에 들어있는 원소(숫자) 개수
# ▶ 전체 합산 = 모델의 총 파라미터 개수 (예: 1.5B → 약 15억 개)

trainable_params = sum(p.numel() for p in model_fp16.parameters() if p.requires_grad)
# ▶ requires_grad=True인 파라미터만 필터링 → "학습(역전파) 대상"인 파라미터 수
#    (지금은 학습이 아니라 추론만 하므로 보통 총 파라미터 수와 같게 나옴)

print("=" * 50)
print("[모델 파라미터 분석]")
print("=" * 50)
print(f"총 파라미터 수: {total_params:,}")          # ▶ ':,' 포맷 → 천 단위 콤마 표시
print(f"학습 가능한 파라미터: {trainable_params:,}")

# 메모리 계산: 파라미터 수 × 바이트
memory_fp32 = total_params * 4 / 1024**3    # ▶ FP32 = 파라미터 1개당 4바이트(32비트)
memory_fp16 = total_params * 2 / 1024**3    # ▶ FP16 = 파라미터 1개당 2바이트(16비트)
memory_int4 = total_params * 0.5 / 1024**3  # ▶ INT4 = 파라미터 1개당 0.5바이트(4비트)
# ▶ 이 세 값은 "이론적" 계산치 — 실제 로딩 메모리는 오버헤드(버퍼, 메타데이터 등)로 조금 더 큼

print(f"\n[이론적 메모리 사용량 계산]")
print(f"FP32 (32-bit): {memory_fp32:.2f} GB")
print(f"FP16 (16-bit): {memory_fp16:.2f} GB")
print(f"INT4 (4-bit):  {memory_int4:.2f} GB")

print(f"\n[메모리 절감 효과]")
print(f"FP32 → FP16: {(1 - memory_fp16/memory_fp32)*100:.0f}% 절감")   # ▶ 정확히 50% 절감
print(f"FP16 → INT4: {(1 - memory_int4/memory_fp16)*100:.0f}% 절감")   # ▶ 정확히 75% 절감
print(f"FP32 → INT4: {(1 - memory_int4/memory_fp32)*100:.0f}% 절감")   # ▶ 정확히 87.5% 절감
```

### Cell 5 — FP32 vs FP16 숫자 표현 비교 (정밀도 손실 체험)

```python
print("=" * 50)
print("[FP32 vs FP16 숫자 표현 비교]")
print("=" * 50)

# 테스트할 값들
test_values = [
    3.141592653589793,   # 원주율 (정밀도 테스트) ▶ 유효숫자가 많은 무리수
    0.00001,             # 아주 작은 수           ▶ FP16의 표현 범위 하한 근처 테스트
    65504.0,             # FP16 최대값 근처        ▶ FP16이 표현 가능한 최대값(overflow 직전)
    0.123456789,         # 일반적인 소수           ▶ 평범한 실수에서도 오차가 생기는지 확인
]

for value in test_values:
    fp32 = torch.tensor(value, dtype=torch.float32)  # ▶ 같은 값을 32비트로 저장
    fp16 = torch.tensor(value, dtype=torch.float16)  # ▶ 같은 값을 16비트로 저장 (반올림 발생)

    print(f"\n원본값: {value}")
    print(f"FP32:   {fp32.item():.15f}")   # ▶ .item(): 텐서(스칼라) → 파이썬 float으로 추출
    print(f"FP16:   {fp16.item():.15f}")
    print(f"오차:   {abs(value - fp16.item()):.15f}")
    # ▶ 원본(파이썬 float, 사실상 FP64)과 FP16 변환값의 절대 오차
    #    → 비트 수가 적을수록 표현 가능한 "정밀도 격자"가 성겨서 오차가 커짐

print("\n" + "=" * 50)
print("💡 관찰: FP16은 정밀도가 낮아 작은 오차가 발생합니다.")
print("   이 오차가 모델 전체에 누적되면 품질 저하로 이어질 수 있습니다.")
# ▶ 이 셀의 목적: "비트 수를 줄이면 오차가 생긴다"는 양자화의 근본 원리를 숫자로 체감
```

### Cell 6 — 추론 함수 정의 및 FP16 추론 실행 (TODO 1)

```python
# TODO: FP16 모델로 추론 수행 및 latency/memory 측정

def measure_inference(model, tokenizer, prompt, max_new_tokens=128):
    """모델 추론을 수행하고 latency와 memory를 측정합니다."""
    # ▶ 이 함수는 이후 FP16/INT4/TTP 테스트에서 계속 재사용되는 "공통 측정 유틸"

    # 메모리 측정 (추론 전)
    torch.cuda.synchronize()
    # ▶ GPU는 비동기로 연산을 큐에 쌓아 실행하므로, synchronize()로 "지금까지의 GPU 연산이
    #    모두 끝날 때까지" CPU를 대기시켜야 정확한 시점의 메모리/시간을 측정할 수 있음
    memory_before = torch.cuda.memory_allocated() / 1024**3   # (측정만 하고 실제 사용 X, 참고용)

    # 입력 토큰화
    messages = [
        {"role": "user", "content": prompt}
    ]
    # ▶ HuggingFace 챗 모델은 {"role":..., "content":...} 형태의 대화 메시지 리스트를 입력받음
    inputs = tokenizer.apply_chat_template(
        messages,
        return_tensors="pt",        # ▶ PyTorch 텐서 형태로 반환
        return_dict=True,           # ▶ {"input_ids":..., "attention_mask":...} 딕셔너리로 반환
        add_generation_prompt=True  # ▶ 모델이 "이제 답변을 시작하라"는 신호 토큰을 마지막에 추가
    )
    input_ids = inputs["input_ids"].to(model.device)
    # ▶ 모델이 올라가 있는 장치(GPU)로 입력 텐서를 이동 (device 불일치 시 에러 방지)
    input_length = input_ids.shape[1]
    # ▶ 입력 프롬프트의 토큰 길이 저장 → 나중에 "생성된 부분만" 잘라내기 위해 필요

    # 재현성을 위한 seed 설정
    torch.manual_seed(42)
    # ▶ do_sample=True(확률적 샘플링)를 쓰면 실행할 때마다 답이 달라질 수 있음
    #    → seed 고정으로 FP16/INT4/TTP 비교 시 "같은 난수 조건"에서 비교 가능하게 함

    # 추론 시간 측정
    start_time = time.time()

    with torch.no_grad():
        # ▶ 추론(inference) 전용: 역전파를 위한 gradient 계산을 하지 않음 → 메모리/속도 이득
        outputs = model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,   # ▶ 새로 생성할 최대 토큰 수 (응답 길이 상한)
            do_sample=True,                  # ▶ 확률적 샘플링 사용 (False면 greedy/deterministic)
            temperature=0.7,                 # ▶ 낮을수록 결정적·보수적, 높을수록 다양·창의적
            top_p=0.95,                      # ▶ nucleus sampling: 누적확률 95% 안의 후보 토큰만 샘플링
            pad_token_id=tokenizer.eos_token_id,
            # ▶ 패딩 토큰이 별도로 없는 모델이 많아 EOS(문장 종료) 토큰을 패딩으로 재사용
        )

    torch.cuda.synchronize()   # ▶ generate()가 끝난 시점을 정확히 맞추기 위해 다시 동기화
    end_time = time.time()

    # 메모리 측정 (추론 후)
    memory_after = torch.cuda.max_memory_allocated() / 1024**3
    # ▶ max_memory_allocated(): reset_peak_memory_stats() 이후 "최대로 찍었던" 메모리(피크)
    #    → 가중치 + 활성화값 + KV캐시 등을 모두 포함한 실제 추론 부담을 보여줌

    # 결과 디코딩
    response = tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
    # ▶ outputs[0]에는 "입력 + 생성된 토큰"이 함께 들어있으므로 input_length 이후만 슬라이싱
    # ▶ skip_special_tokens=True: <eos> 같은 특수 토큰을 문자열에서 제거
    latency = end_time - start_time

    return response, latency, memory_after


# 테스트 프롬프트
test_prompt = "서울에서 부산까지 KTX로 얼마나 걸리나요?"

# FP16 추론 실행
response_fp16, latency_fp16, memory_fp16 = measure_inference(model_fp16, tokenizer, test_prompt)

print("=" * 50)
print("[FP16 모델 추론 결과]")
print("=" * 50)
print(f"입력: {test_prompt}")
print(f"응답: {response_fp16}")
print(f"\nLatency: {latency_fp16:.2f}초")
print(f"Memory: {memory_fp16:.2f} GB")
print("\n⚠️ 체감: 메모리를 많이 사용하네! 더 큰 모델은 16GB에 못 올리겠다.")
```

### Cell 7 — FP16 결과 저장 및 메모리 해제

```python
# FP16 결과 저장 (나중에 INT4와 비교용)
fp16_results = {
    "latency": latency_fp16,
    "memory": memory_fp16,
    "model_memory": model_memory_fp16,  # 모델 가중치 메모리
    "response": response_fp16
}
# ▶ Step 3에서 INT4 결과와 비교하기 위해 딕셔너리에 스냅샷 저장

print(f"FP16 모델 가중치 메모리: {model_memory_fp16:.2f} GB")
print(f"FP16 추론 피크 메모리: {memory_fp16:.2f} GB")
print(f"16GB VRAM의 {(memory_fp16/16)*100:.1f}% 사용 중")
# ▶ 실습 환경(16GB VRAM) 기준으로 몇 %를 차지하는지 계산해 "체감"을 숫자로 재확인

# FP16 모델 메모리 해제 (INT4 로딩을 위해)
del model_fp16
# ▶ 파이썬 변수 참조를 제거 → 더 이상 이 텐서를 참조하는 곳이 없어짐
torch.cuda.empty_cache()
# ▶ PyTorch가 내부적으로 들고 있던 미사용 GPU 메모리 캐시를 OS/CUDA에 반환
#    (del만으로는 GPU 메모리가 즉시 완전히 안 비워지는 경우가 많아 반드시 함께 사용)
print("\nFP16 모델 메모리 해제 완료")
```

---

## Step 3. INT4 양자화 적용 (해결)

### Cell 8 — 양자화 원리 시뮬레이션 (INT8 vs INT4)

```python
print("=" * 70)
print("[양자화 과정 단계별 체험: INT8 vs INT4 비교]")
print("=" * 70)

# 1. 원본 텐서 (FP16 가중치를 시뮬레이션)
original = torch.tensor([0.5, 1.2, -0.3, 2.1, -1.5], dtype=torch.float16)
# ▶ 실제 모델 가중치 대신, 손으로 계산 과정을 따라갈 수 있는 작은 샘플 텐서 사용
print(f"\n1️⃣ 원본 텐서 (FP16):")
print(f"   {original.tolist()}")

# 2. 양자화 파라미터 계산 (공통)
x_min, x_max = original.min().item(), original.max().item()
# ▶ 양자화 수식 Q(x) = round(x/scale) + zero_point 에서 scale/zero_point를 정하려면
#    먼저 데이터의 최솟값·최댓값(표현해야 할 범위)을 알아야 함
print(f"\n2️⃣ 데이터 범위 분석:")
print(f"   x_min: {x_min:.4f}, x_max: {x_max:.4f}")

# ============================================================
# INT8 양자화 (8비트 = 256 레벨)
# ============================================================
print("\n" + "=" * 70)
print("[INT8 양자화 (8-bit, 256 레벨)]")
print("=" * 70)

scale_int8 = (x_max - x_min) / 255  # 0~255 범위
# ▶ scale = "실수 범위 전체를 정수 격자 몇 칸에 나눠 담을지"의 단위 간격
#    8비트 부호없는 정수(uint8)는 0~255, 즉 256개 레벨을 표현 가능 → 255로 나눔
zero_point_int8 = round(-x_min / scale_int8)
# ▶ zero_point: 실수 0.0이 정수 격자에서 몇 번 칸에 대응하는지 (오프셋 보정값)

print(f"   scale: {scale_int8:.6f}")
print(f"   zero_point: {zero_point_int8}")

# INT8 양자화
quantized_int8 = torch.round(original / scale_int8 + zero_point_int8).to(torch.uint8)
# ▶ Q(x) = round(x/scale) + zero_point 를 그대로 코드로 옮긴 부분
#    실수를 scale로 나눠 정수 격자 단위로 변환 후 반올림, zero_point만큼 이동, uint8로 캐스팅
print(f"\n   양자화된 값 (INT8): {quantized_int8.tolist()}")

# INT8 역양자화
dequantized_int8 = (quantized_int8.float() - zero_point_int8) * scale_int8
# ▶ 양자화의 역과정: 정수값을 다시 실수 근사값으로 복원 (원본과 100% 같지는 않음)
print(f"   역양자화된 값:     {[round(x, 4) for x in dequantized_int8.tolist()]}")

# INT8 오차
error_int8 = (original.float() - dequantized_int8).abs()
# ▶ "원본 - 복원값"의 절대값 = 양자화로 인해 발생한 손실(정보 손실량)
print(f"\n   양자화 오차:       {[round(x, 6) for x in error_int8.tolist()]}")
print(f"   평균 오차: {error_int8.mean().item():.6f}")

# ============================================================
# INT4 양자화 (4비트 = 16 레벨)
# ============================================================
print("\n" + "=" * 70)
print("[INT4 양자화 (4-bit, 16 레벨)]")
print("=" * 70)

scale_int4 = (x_max - x_min) / 15  # 0~15 범위 (4비트)
# ▶ 4비트는 0~15, 즉 16개 레벨만 표현 가능 → 같은 실수 범위를 훨씬 "성긴" 격자에 담아야 함
zero_point_int4 = round(-x_min / scale_int4)

print(f"   scale: {scale_int4:.6f}")
print(f"   zero_point: {zero_point_int4}")

# INT4 양자화 (0~15 범위로 클램핑)
quantized_int4 = torch.round(original / scale_int4 + zero_point_int4).clamp(0, 15).to(torch.uint8)
# ▶ .clamp(0, 15): 반올림 과정에서 범위를 벗어날 수 있는 값을 0~15 사이로 강제로 잘라냄
#    (4비트 정수가 표현할 수 있는 값의 한계이므로 반드시 필요한 안전장치)
print(f"\n   양자화된 값 (INT4): {quantized_int4.tolist()}")

# INT4 역양자화
dequantized_int4 = (quantized_int4.float() - zero_point_int4) * scale_int4
print(f"   역양자화된 값:     {[round(x, 4) for x in dequantized_int4.tolist()]}")

# INT4 오차
error_int4 = (original.float() - dequantized_int4).abs()
print(f"\n   양자화 오차:       {[round(x, 6) for x in error_int4.tolist()]}")
print(f"   평균 오차: {error_int4.mean().item():.6f}")

# ============================================================
# INT8 vs INT4 비교 요약
# ============================================================
print("\n" + "=" * 70)
print("[INT8 vs INT4 비교 요약]")
print("=" * 70)
print(f"{'항목':<20} {'INT8 (8-bit)':>15} {'INT4 (4-bit)':>15}")
print("-" * 70)
print(f"{'표현 가능 레벨':<20} {'256':>15} {'16':>15}")
print(f"{'메모리 (1B 파라미터)':<20} {'1 GB':>15} {'0.5 GB':>15}")
print(f"{'평균 양자화 오차':<20} {error_int8.mean().item():>15.6f} {error_int4.mean().item():>15.6f}")
print(f"{'오차 증가율':<20} {'기준':>15} {f'{(error_int4.mean() / error_int8.mean()):.1f}x':>15}")
# ▶ 같은 데이터를 4비트로 담으면 8비트 대비 오차가 몇 배 커지는지 정량적으로 확인

print("\n" + "=" * 70)
print("💡 관찰:")
print("   - INT4는 INT8 대비 메모리 50% 추가 절감 (8bit → 4bit)")
print("   - 하지만 표현 가능한 레벨이 256 → 16으로 감소")
print(f"   - 양자화 오차가 약 {(error_int4.mean() / error_int8.mean()):.1f}배 증가")
print("   - 트레이드오프: 메모리 절감 ↑ vs 정밀도 손실 ↑")
print("=" * 70)
# ▶ 실제 bitsandbytes의 NF4는 이 단순 균등양자화보다 정교하지만(정규분포 기반 비균등 레벨),
#    "비트를 줄이면 오차가 커진다"는 근본 트레이드오프는 동일함
```

### Cell 9 — BitsAndBytesConfig로 INT4 모델 로딩 (TODO 2)

```python
# TODO: INT4 양자화 모델 로딩 및 FP16과 비교

# INT4 양자화 설정 (NF4 - Normal Float 4-bit)
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,                          # ▶ 4비트 양자화 로딩 활성화 (핵심 스위치)
    bnb_4bit_compute_dtype=torch.float16,       # ▶ 저장은 4bit지만, 실제 행렬곱 연산 시에는
                                                 #    FP16으로 복원해서 계산 (속도/정확도 균형)
    bnb_4bit_quant_type="nf4",                  # ▶ "nf4"(Normal Float 4, LLM 가중치의 정규분포
                                                 #    특성에 최적화) vs "fp4"(균등분포 가정) 중 선택
    bnb_4bit_use_double_quant=True,             # ▶ 이중 양자화: scale 상수 자체도 양자화하여
                                                 #    추가로 메모리 절감 (~0.4bit/param)
)
# ▶ 주의: 이 객체는 "설정값"만 담고 있을 뿐, 아직 아무 양자화도 수행하지 않음
#    실제 변환은 바로 아래 from_pretrained() 호출 시점에 발생

# INT4 모델 로딩
print("INT4 양자화 모델 로딩 중...")
torch.cuda.reset_peak_memory_stats()   # ▶ FP16 때와 마찬가지로 이번 측정을 위한 통계 초기화
model_int4 = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=quantization_config,   # ▶ 위에서 만든 설정을 전달 → 로딩과 동시에 양자화
    device_map="auto",
)

# 모델 로딩 직후 메모리 측정 (가중치 메모리)
model_memory_int4 = torch.cuda.memory_allocated() / 1024**3
print(f"INT4 모델 로딩 완료: {model_name}")
print(f"INT4 모델 메모리: {model_memory_int4:.2f} GB")
```

### Cell 10 — INT4 모델로 추론 실행

```python
# INT4 추론 실행
response_int4, latency_int4, memory_int4 = measure_inference(model_int4, tokenizer, test_prompt)
# ▶ Cell 6에서 정의한 동일한 measure_inference() 함수를 그대로 재사용
#    → FP16과 "같은 조건(같은 프롬프트, 같은 seed)"으로 비교해야 공정한 비교가 됨

print("=" * 50)
print("[INT4 모델 추론 결과]")
print("=" * 50)
print(f"입력: {test_prompt}")
print(f"응답: {response_int4}")
print(f"\nLatency: {latency_int4:.2f}초")
print(f"추론 피크 메모리: {memory_int4:.2f} GB")
```

### Cell 11 — FP16 vs INT4 비교표 출력

```python
# FP16 vs INT4 비교
print("\n" + "=" * 70)
print("[FP16 vs INT4 비교]")
print("=" * 70)
print(f"{'지표':<20} {'FP16':>15} {'INT4':>15} {'변화율':>15}")
print("-" * 70)

# 모델 가중치 메모리 비교 (핵심 지표)
model_memory_change = ((model_memory_int4 - fp16_results['model_memory']) / fp16_results['model_memory']) * 100
# ▶ (변경 후 - 변경 전) / 변경 전 × 100 = 증감률(%). 음수면 "감소"를 의미
print(f"{'모델 메모리 (GB)':<20} {fp16_results['model_memory']:>15.2f} {model_memory_int4:>15.2f} {model_memory_change:>14.1f}%")

# Latency 비교
latency_change = ((latency_int4 - fp16_results['latency']) / fp16_results['latency']) * 100
print(f"{'Latency (초)':<20} {fp16_results['latency']:>15.2f} {latency_int4:>15.2f} {latency_change:>14.1f}%")

# 추론 피크 메모리 비교
peak_memory_change = ((memory_int4 - fp16_results['memory']) / fp16_results['memory']) * 100
print(f"{'피크 메모리 (GB)':<20} {fp16_results['memory']:>15.2f} {memory_int4:>15.2f} {peak_memory_change:>14.1f}%")
# ▶ "모델 메모리"는 크게 줄어도 "피크 메모리"는 상대적으로 덜 줄어드는 경우가 많음
#    → 활성화값/KV캐시는 양자화 대상이 아니라 여전히 FP16으로 계산되기 때문 (Step3 개념 참고)

print("\n✅ 체감: INT4 양자화로 모델 메모리가 대폭 줄었다!")
print("   → 같은 GPU에서 더 큰 모델을 로딩할 수 있게 됨")
```

### Cell 12 — INT4 결과 저장 및 절감률 검증

```python
# INT4 결과 저장
int4_results = {
    "latency": latency_int4,
    "memory": memory_int4,
    "model_memory": model_memory_int4,
    "response": response_int4
}
# ▶ Step 5 마지막 전체 요약(Cell 20)에서 다시 사용하기 위해 저장

# 메모리 절감 확인 (모델 가중치 기준)
memory_saved = fp16_results['model_memory'] - model_memory_int4
memory_saved_percent = (memory_saved / fp16_results['model_memory']) * 100

print(f"모델 메모리 절감량: {memory_saved:.2f} GB ({memory_saved_percent:.1f}%)")

if memory_saved_percent >= 50:
    print("✅ INT4 양자화로 모델 메모리를 50% 이상 절감했습니다!")
    print("   이론적으로 FP16 → INT4는 75% 절감 (16bit → 4bit)")
    # ▶ 이론치(75%)보다 실제 절감률이 낮게 나올 수 있는데, 이는 이중 양자화 메타데이터,
    #    non-quantized 레이어(예: layernorm), 프레임워크 오버헤드 등이 존재하기 때문
else:
    print("⚠️ 메모리 절감 효과가 예상보다 적습니다.")
    print("   (이중 양자화 메타데이터 등의 오버헤드 존재)")
```

---

## Step 4. 환경 변화 입력 품질 저하 (새로운 문제 체감)

### Cell 13 — 테스트 샘플(오타/노이즈/모호함 등) 정의

```python
# 환경 변화 입력 샘플 정의
test_samples = [
    {
        "type": "정상",
        "prompt": "서울에서 부산까지 KTX로 얼마나 걸리나요?",
        "expected_quality": "높음"     # ▶ 학습 데이터에서 흔한 "깨끗한" 질문 형태
    },
    {
        "type": "오타",
        "prompt": "서울에셔 부산까지 KTX로 얼마나 걸리나요?",   # ▶ "에서"→"에셔" 오타 삽입
        "expected_quality": "중간"
    },
    {
        "type": "노이즈",
        "prompt": "서울에서 부산까지... 음... KTX로 얼마나 걸리나요? 대략?",
        "expected_quality": "중간"      # ▶ 불필요한 간투사·말줄임표로 문장을 어지럽힘
    },
    {
        "type": "모호함",
        "prompt": "그거 얼마나 걸려?",   # ▶ 맥락(주어/목적어)이 생략된 지시대명사형 질문
        "expected_quality": "낮음"
    },
    {
        "type": "조건변화",
        "prompt": "밤 11시에 출발하면 다음날 아침에 도착할 수 있나요?",
        "expected_quality": "중간"      # ▶ 시간 계산 + 조건 판단이 함께 필요한 복합 질문
    }
]
# ▶ expected_quality는 "이 입력이 얼마나 다루기 어려울지"에 대한 사전 예상치(참고용 라벨)

print(f"총 {len(test_samples)}개의 테스트 샘플 정의 완료")
```

### Cell 14 — INT4 모델에 환경 변화 입력 테스트

```python
# 환경 변화 입력 테스트
env_change_results = []

print("=" * 70)
print("[INT4 모델 - 환경 변화 입력 테스트]")
print("=" * 70)

for sample in test_samples:
    response, latency, _ = measure_inference(model_int4, tokenizer, sample["prompt"], max_new_tokens=100)
    # ▶ 세 번째 반환값(memory)은 여기서는 관심 대상이 아니라서 _ 로 버림(unpacking)

    env_change_results.append({
        "type": sample["type"],
        "prompt": sample["prompt"],
        "response": response,
        "latency": latency
    })
    # ▶ Step5(TTP)에서 "TTP 없음"일 때의 응답과 비교하기 위해 결과를 리스트에 누적 저장

    print(f"\n[{sample['type']}]")
    print(f"입력: {sample['prompt']}")
    print(f"응답: {response[:200]}..." if len(response) > 200 else f"응답: {response}")
    # ▶ 응답이 200자를 넘으면 잘라서(...) 출력, 짧으면 전체 출력 (출력 가독성 확보)
    print("-" * 70)
```

### Cell 15 — 품질 저하 관찰 요약 출력

```python
# 품질 저하 관찰
print("\n" + "=" * 50)
print("⚠️ 체감: 환경 변화 입력에서 품질이 저하되는 것 관찰")
print("=" * 50)
print("- 오타: 오타를 이해하지 못하거나 이상한 응답")
print("- 노이즈: 불필요한 표현에 혼란")
print("- 모호함: 맥락 부족으로 엉뚱한 응답")
print("- 조건변화: 복잡한 조건 처리 실패")
print("\n→ 이 문제를 해결하기 위해 TTP(Test-time Prompting) 전략을 적용해보자!")
# ▶ 이 셀은 별도 연산 없이, 위 Cell 14에서 실제로 관찰된 현상을 정리해 다음 Step으로 연결하는 역할
```

---

## Step 5. TTP(Test-time Prompting) 전략 적용 (해결)

### Cell 16 — TTP 템플릿 정의

```python
# TTP 템플릿 정의

# TTP-A: 출력 형식/제약 강화
TTP_A_TEMPLATE = """다음 질문에 답해주세요. 

**규칙:**
1. 오타나 불명확한 표현이 있어도 의도를 파악하세요.
2. 교통 관련 질문은 대략적인 소요 시간(시간 단위)으로 답하세요.
3. 맥락이 부족하면 일반적인 상황을 가정하여 답하세요.
4. 간결하게 핵심만 답하세요.

**질문:** {question}

**답변:**"""
# ▶ {question}은 str.format()에서 채워질 placeholder
# ▶ 전략: 모델에게 "지켜야 할 규칙"을 명시적으로 부여해 애매한 입력에서도 일관된 행동을 유도

# TTP-B: few-shot 예시 포함
TTP_B_TEMPLATE = """다음은 교통 관련 질문과 답변의 예시입니다.

**예시:**
Q: 서울역에서 대전역까지 KTX로 얼마나 걸려요?
A: 서울역에서 대전역까지 KTX로 약 50분~1시간 정도 소요됩니다.

이제 아래 질문에 동일한 형식으로 답해주세요.

**질문:** {question}

**답변:**"""
# ▶ 전략: 규칙을 "말로 설명"하는 대신, 원하는 Q&A 예시를 1개 "보여줘서" 형식을 모방하게 유도
#    (few-shot prompting)

print("TTP 템플릿 정의 완료:")
print("- TTP-A: 출력 형식/제약 강화")
print("- TTP-B: few-shot 예시 포함")
```

### Cell 17 — TTP 적용 함수 및 비교 테스트 (TODO 3)

```python
# TODO: TTP 템플릿 적용 후 품질 변화 비교

def apply_ttp(template, question):
    """TTP 템플릿을 적용하여 프롬프트를 생성합니다."""
    return template.format(question=question)
    # ▶ str.format(): 템플릿 문자열 안의 {question}을 실제 질문 텍스트로 치환
    #    모델 가중치는 전혀 건드리지 않고 "입력 프롬프트"만 가공하는 방식임에 주목

# TTP 적용 결과 저장
ttp_results = []

print("=" * 80)
print("[TTP 적용 테스트]")
print("=" * 80)

for sample in test_samples:
    original_prompt = sample["prompt"]

    # TTP-A 적용
    ttp_a_prompt = apply_ttp(TTP_A_TEMPLATE, original_prompt)
    response_a, _, _ = measure_inference(model_int4, tokenizer, ttp_a_prompt, max_new_tokens=100)
    # ▶ 같은 INT4 모델(model_int4)에 "가공된 프롬프트"만 다르게 넣어 응답을 비교

    # TTP-B 적용
    ttp_b_prompt = apply_ttp(TTP_B_TEMPLATE, original_prompt)
    response_b, _, _ = measure_inference(model_int4, tokenizer, ttp_b_prompt, max_new_tokens=100)

    ttp_results.append({
        "type": sample["type"],
        "original": original_prompt,
        "no_ttp": env_change_results[[r["type"] for r in env_change_results].index(sample["type"])]["response"],
        # ▶ Cell 14에서 저장해둔 env_change_results 리스트에서, 현재 sample과 같은 "type"을 가진
        #    항목의 인덱스를 찾아 그때의 "TTP 미적용 응답"을 함께 가져옴 (3자 비교를 위해)
        "ttp_a": response_a,
        "ttp_b": response_b
    })

    print(f"\n[{sample['type']}]")
    print(f"원본: {original_prompt}")
    print(f"TTP-A 응답: {response_a[:150]}..." if len(response_a) > 150 else f"TTP-A 응답: {response_a}")
    print(f"TTP-B 응답: {response_b[:150]}..." if len(response_b) > 150 else f"TTP-B 응답: {response_b}")
    print("-" * 80)
```

### Cell 18 — TTP 효과 요약 (수동 품질 점수표)

```python
# TTP 효과 요약
print("\n" + "=" * 60)
print("[TTP 효과 요약]")
print("=" * 60)
print(f"{'입력 유형':<12} {'TTP 없음':>12} {'TTP-A':>12} {'TTP-B':>12}")
print("-" * 60)

# 수동 품질 평가 (1-5점)
# 실제로는 모델 응답을 확인하고 평가해야 하지만, 여기서는 예시로 표시
quality_scores = {
    "정상": {"no_ttp": 5, "ttp_a": 5, "ttp_b": 5},
    "오타": {"no_ttp": 3, "ttp_a": 4, "ttp_b": 5},
    "노이즈": {"no_ttp": 2, "ttp_a": 4, "ttp_b": 4},
    "모호함": {"no_ttp": 1, "ttp_a": 3, "ttp_b": 4},
    "조건변화": {"no_ttp": 2, "ttp_a": 2, "ttp_b": 3}
}
# ▶ 실제 LLM 응답 품질을 자동으로 채점하는 로직은 없고, 교육 목적상 미리 정해둔 예시 점수표
#    (실무라면 사람 평가 또는 LLM-judge 방식으로 자동 채점 필요)

for input_type, scores in quality_scores.items():
    print(f"{input_type:<12} {scores['no_ttp']:>12}/5 {scores['ttp_a']:>12}/5 {scores['ttp_b']:>12}/5")

print("\n✅ 체감: TTP를 적용하니 품질이 회복됐네! 재학습 없이도 품질을 보정할 수 있구나!")
```

### Cell 19 — TTP 효과 검증 (평균 점수·개선율 계산)

```python
# TTP 효과 검증
avg_no_ttp = sum(s["no_ttp"] for s in quality_scores.values()) / len(quality_scores)
avg_ttp_a = sum(s["ttp_a"] for s in quality_scores.values()) / len(quality_scores)
avg_ttp_b = sum(s["ttp_b"] for s in quality_scores.values()) / len(quality_scores)
# ▶ 5개 입력 유형 각각의 점수를 합산 후 개수로 나눈 단순 평균

print("=" * 50)
print("[평균 품질 점수]")
print("=" * 50)
print(f"TTP 없음: {avg_no_ttp:.1f}/5")
print(f"TTP-A: {avg_ttp_a:.1f}/5 (형식 강화)")
print(f"TTP-B: {avg_ttp_b:.1f}/5 (few-shot)")

improvement_a = ((avg_ttp_a - avg_no_ttp) / avg_no_ttp) * 100
improvement_b = ((avg_ttp_b - avg_no_ttp) / avg_no_ttp) * 100
# ▶ TTP 적용 전 대비 개선율(%) = (적용 후 - 적용 전) / 적용 전 × 100

print(f"\nTTP-A 개선율: +{improvement_a:.1f}%")
print(f"TTP-B 개선율: +{improvement_b:.1f}%")

if avg_ttp_b > avg_no_ttp:
    print("\n✅ TTP 적용으로 품질이 개선되었습니다!")
```

### Cell 20 — 실습 전체 요약 출력

```python
# 실습 전체 요약
print("=" * 70)
print("[5-2 Quantization 실습 요약]")
print("=" * 70)

print("\n📊 FP16 vs INT4 비교:")
print(f"  - 모델 메모리: {fp16_results['model_memory']:.2f}GB → {int4_results['model_memory']:.2f}GB ({memory_saved_percent:.1f}% 절감)")
print(f"  - Latency: {fp16_results['latency']:.2f}초 → {int4_results['latency']:.2f}초")
# ▶ Step2~3에서 저장해둔 fp16_results / int4_results 딕셔너리를 다시 불러와 최종 리포트 작성

print("\n⚠️ 환경 변화 입력 품질 저하:")
print("  - 오타, 노이즈, 모호함, 조건변화 시 품질 저하 관찰")
print("  - INT4 양자화 후 환경 변화에 더 취약")

print("\n✅ TTP로 품질 회복:")
print(f"  - TTP-A (형식 강화): 평균 품질 {avg_no_ttp:.1f} → {avg_ttp_a:.1f}")
print(f"  - TTP-B (few-shot): 평균 품질 {avg_no_ttp:.1f} → {avg_ttp_b:.1f}")

print("\n🎯 핵심 교훈:")
print("  1. INT4 양자화로 모델 메모리 50~75% 절감 가능")
print("  2. 양자화 후 환경 변화 입력에서 품질 저하 주의")
print("  3. TTP로 재학습 없이 품질 보정 가능")
print("  4. 양자화의 주요 이점: 더 큰 모델을 같은 GPU에서 실행 가능")
# ▶ 노트북 전체 흐름(문제 체감 → 해결 → 새 문제 체감 → 해결)을 한 번에 정리하는 마무리 셀
```
