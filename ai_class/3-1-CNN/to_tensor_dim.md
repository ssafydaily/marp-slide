좋은 질문입니다. 네, `transforms.ToTensor()`는 내부적으로 차원 순서를 바꿉니다. 이걸 "어떻게 아는지"까지 포함해서 정리해드릴게요.

## 무엇이 바뀌는가

```python
PIL.Image (H, W, C)  →  ToTensor()  →  torch.Tensor (C, H, W)
```

CIFAR-10 예시로 보면:
- 입력: PIL 이미지, 크기 `(32, 32)`, 채널 3개 → 내부적으로는 `(H=32, W=32, C=3)` 순서의 배열
- 출력: `torch.Tensor`, shape `[3, 32, 32]` → `(C=3, H=32, W=32)` 순서

즉 **채널(C) 차원이 맨 뒤에서 맨 앞으로 이동**합니다. 동시에 픽셀 값도 `uint8 (0~255)` → `float32 (0.0~1.0)`로 스케일이 바뀝니다(이건 차원과 별개의 변환).

## 왜 이렇게 바뀌는가

이미지 라이브러리(PIL, OpenCV, matplotlib 등)는 관례적으로 **HWC(Height-Width-Channel)** 순서를 씁니다. 사람이 이해하기에 "가로×세로 격자 안에 RGB 3개 값이 들어있다"는 구조가 직관적이기 때문입니다.

반면 PyTorch(그리고 대부분의 딥러닝 프레임워크)는 **CHW(Channel-Height-Width)** 순서를 텐서 표준으로 씁니다. 그 이유는:
- 합성곱(Convolution) 연산이 채널 축을 기준으로 필터를 적용하는데, 채널을 앞쪽 차원에 두면 메모리 접근 패턴이 더 효율적입니다.
- 배치 차원까지 포함하면 PyTorch의 표준은 `(N, C, H, W)`(NCHW)입니다. `ToTensor()`는 이 중 `(C, H, W)`까지 만들어주고, `DataLoader`가 배치로 묶을 때 앞에 `N` 차원을 자동으로 붙여줍니다.

그래서 `ToTensor()`는 "이미지 라이브러리 세계(HWC)"에서 "PyTorch 신경망 세계(CHW)"로 넘어가는 다리 역할을 하는 겁니다.

## 어떻게 알 수 있는가 (알아내는 방법)

이건 추측하는 게 아니라 **공식 문서에 명시**되어 있습니다.공식 문서와 소스코드로 정확히 확인됩니다.

## 문서에 명시된 사실

torchvision 공식 문서에는 `ToTensor()`의 동작이 이렇게 정의돼 있습니다.

> PIL Image 또는 ndarray(H x W x C, 0~255 범위)를 (C x H x W), 0.0~1.0 범위의 torch.FloatTensor로 변환한다

즉 **"HWC → CHW"라는 변환 규칙은 문서 한 줄에 이미 공식적으로 적혀 있습니다.** 추측이 아니라 API 스펙입니다.

## 소스코드 레벨에서 보면 (실제로 일어나는 일)

torchvision 내부 구현을 보면 PIL 이미지를 numpy 배열로 바꾼 뒤 `(height, width, channel)` 형태로 view하고, "HWC에서 CHW 포맷으로 바꾸기 위해" `permute((2, 0, 1))`을 호출합니다.

`permute((2, 0, 1))`이 핵심입니다:
```python
# 변환 전 axis 순서:  (0=H, 1=W, 2=C)
# permute(2, 0, 1) → 새 axis 순서: (C, H, W)
img = img.view(H, W, C)          # (32, 32, 3)
img = img.permute(2, 0, 1)       # (3, 32, 32)  ← 축 순서만 재배치
```
숫자를 옮기는 게 아니라 **"어느 축을 몇 번째로 볼지"만 바꾸는 연산**이라 계산 비용이 거의 없습니다.

## 어떻게 "알고" 이걸 쓰는가 — 실전 팁

1. **공식 문서를 1차 소스로 삼는다.** `help(transforms.ToTensor)` 또는 `torchvision.transforms.ToTensor` 문서 페이지에 입출력 shape·범위가 항상 명시돼 있습니다. 처음 보는 함수는 소스를 뜯기보다 docstring부터 확인하는 게 표준적인 방법입니다.
2. **직접 shape을 찍어본다.** 가장 확실한 방법입니다.
   ```python
   img = trainset[0][0]        # PIL Image, .size = (32, 32)
   tensor = transforms.ToTensor()(img)
   print(tensor.shape)         # torch.Size([3, 32, 32]) ← 바로 확인됨
   ```
3. **프레임워크의 "약속(convention)"을 알고 있으면 예측 가능**해집니다. PyTorch 계열(nn.Conv2d 등)은 항상 `(N, C, H, W)`을 기대한다는 걸 알고 있으면, "PIL은 HWC니까 PyTorch에 넣으려면 어차피 CHW로 바뀌어야겠구나"라고 미리 짐작할 수 있습니다. 반대로 TensorFlow/Keras는 기본이 `(N, H, W, C)`(NHWC)라서, 이런 프레임워크 간 관례 차이를 아는 것 자체가 "채널 축이 어디 있는지"를 판단하는 실질적인 근거가 됩니다.

**요약**: ToTensor()는 HWC→CHW로 축을 `permute`하고 값도 0~255→0~1로 스케일링합니다. 이건 문서에 명시된 공식 동작이며, 확신이 안 설 땐 `.shape`을 직접 찍어보는 게 가장 빠르고 정확한 확인 방법입니다.