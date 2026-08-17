정확한 지점을 짚어주는 좋은 질문입니다. 결론부터 말하면 **"배치 단위"가 아니라 "샘플 하나씩" 실행됩니다.** DataLoader가 배치로 묶는 건 그 다음 단계입니다.

## 실제 동작 순서

```
for xb, yb in trainloader:   # ← 이 순간 실행이 시작됨
    ...
```

이 한 줄이 내부적으로 하는 일:

1. `trainloader`가 이번 배치에 쓸 인덱스 256개를 무작위로 뽑음 (`shuffle=True`)
2. **각 인덱스마다 개별적으로** `trainset[idx]` 호출 → 이게 `CIFAR10.__getitem__(idx)`를 실행
3. `__getitem__` 내부에서 `self.transform(img)`가 호출됨 → **여기서 실제로 Resize/ToTensor/Normalize/RandomCrop이 이미지 1장에 대해 실행**
4. 256개의 `(image_tensor, label)`이 다 만들어지면, `collate_fn`(기본값)이 이걸 `torch.stack`으로 묶어서 `[256, 3, 224, 224]` 배치 텐서 하나로 합침
5. 이 합쳐진 배치가 `xb`로 반환됨

torchvision `CIFAR10` 소스코드를 보면 이 구조가 그대로 드러납니다.확인됐습니다. 공식 문서 기준으로 모든 데이터셋 클래스는 `torch.utils.data.Dataset`의 서브클래스이며 `__getitem__`과 `__len__` 메서드를 구현하고 있고, 이 덕분에 `torch.utils.data.DataLoader`에 전달되어 `torch.multiprocessing` 워커를 이용해 여러 샘플을 병렬로 로드할 수 있습니다. 그리고 `CIFAR10`의 `transform` 파라미터는 "PIL 이미지를 받아서 변환된 버전을 반환하는 함수/변환"으로 정의되어 있고, `__getitem__(index)`가 `(image, target)`을 반환합니다.

핵심은 여기 있습니다: **`transform`이 실행되는 단위는 `__getitem__` 한 번 = 이미지 1장**입니다. 배치가 아닙니다.

## 정리하면

**실행 시점**: `Compose([...])`를 만들 때(=코드에서 `train_transform = transforms.Compose([...])` 줄)는 함수 객체만 만들어질 뿐, **아무 이미지도 처리되지 않습니다.** 실제 실행은 `for xb, yb in trainloader:` 루프가 돌면서 각 인덱스를 요청할 때 일어납니다(lazy execution).

**실행 단위**: 배치 256장을 한꺼번에 텐서로 변환하는 게 아니라, `trainset[0]`, `trainset[1]`, ... 이런 식으로 **인덱스 하나당 한 번씩** `__getitem__` → `self.transform(img)` 호출이 일어나고, 그 결과들을 DataLoader가 나중에 `torch.stack`으로 묶어서 배치를 만듭니다.

```python
# torchvision CIFAR10.__getitem__ 개념적으로 이렇게 동작
def __getitem__(self, index):
    img, target = self.data[index], self.targets[index]
    img = Image.fromarray(img)          # numpy → PIL
    if self.transform is not None:
        img = self.transform(img)       # ← 여기서 실제 실행! (이미지 1장 단위)
    return img, target
```

## num_workers와의 관계

`num_workers=8`로 설정하면, 위 `__getitem__` 호출이 **8개의 별도 프로세스에서 병렬로** 일어납니다. 즉 워커 1이 인덱스 3번 이미지에 transform을 적용하는 동안, 워커 2는 인덱스 47번 이미지에 transform을 적용하는 식으로 동시에 진행되고, 메인 프로세스는 이 결과들이 8개(또는 배치 크기만큼) 모이길 기다렸다가 하나의 배치 텐서로 묶습니다. GPU가 이전 배치로 연산하는 동안 다음 배치를 미리 준비해둘 수 있어서 학습 속도가 빨라지는 원리입니다.

## 왜 이게 중요한가 (특히 증강에서)

이 구조 덕분에 `RandomCrop`, `RandomHorizontalFlip` 같은 **무작위 증강이 "샘플 단위·에포크마다 새로" 적용**됩니다.

- 데이터셋은 미리 변환해서 저장해두는 게 아니라, 매번 접근할 때마다 새로 계산합니다.
- 그래서 같은 이미지(index=0)라도 epoch 1에서 뽑히는 랜덤 크롭 위치와 epoch 2에서 뽑히는 위치가 다릅니다.
- 만약 transform이 배치 단위로 딱 한 번만 실행되고 캐싱된다면, 모델은 매 epoch 똑같은 증강 결과만 보게 되어 증강의 "다양성 확보" 효과가 사라집니다.

**주의할 점**: 이 lazy·per-sample 방식 때문에 무거운 transform(특히 Resize처럼 이미지를 키우는 연산)이 매 epoch·매 배치마다 반복 계산됩니다. `num_workers`를 늘리거나, 자주 재사용되는 무거운 전처리는 미리 디스크에 저장해두는 식으로 최적화하기도 합니다. 이 실습에서는 데이터가 크지 않아 문제되지 않지만, 실무에서 학습 속도가 데이터 로딩 병목에 걸릴 때 확인해봐야 할 지점입니다.