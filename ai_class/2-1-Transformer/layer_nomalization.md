GPT (Generative Pre-trained Transformer)

Transformer의 디코더 구조만을 사용하는 언어 모델
Auto-regressive 방식으로 다음 토큰을 예측하여 텍스트를 생성
주요 구성 요소

간단한 GPT를 직접 구현해보면서 모델 아키텍쳐를 이해해보겠습니다. 최근에 나오는 OpenAI의 GPT, Google의 Gemini, Meta의 Llama 등은 모두 이러한 GPT의 아키텍쳐를 기반으로 다양하게 변형하거나 학습들 다양하게 한 모델들입니다. 모델에 대한 아키텍쳐를 어느정도 이해한 다음, 모델의 특성을 파악한다면 더더욱 이해도가 높아질 것입니다. 다음 4가지가 GPT를 구현하는데 있어 주요한 구성 요소입니디ㅏ.

Attention 메커니즘
Query, Key, Value 행렬을 통해 입력 토큰 간의 관계 학습
Self-Attention: 같은 시퀀스 내에서 각 토큰이 다른 토큰과의 연관성을 계산
Layer Normalization
각 레이어의 출력을 정규화하여 학습 안정성 향상
Batch Normalization과 달리 시퀀스 길이에 독립적
MLP (Multi-Layer Perceptron)
Feed-Forward 네트워크로, Attention 이후 비선형 변환 수행
보통 2개의 선형 레이어 + 활성화 함수로 구성
Decoder Block
Masked Self-Attention + Layer Norm + MLP + Layer Norm
Residual Connection (잔차 연결)로 그래디언트 소실 방지