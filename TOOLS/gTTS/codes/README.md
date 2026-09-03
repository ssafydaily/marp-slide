---
marp: true
theme: dark-plus-code
paginate: true
style: |
  

---

# gTTS
- gTTS는 파이썬 라이브러리로 텍스트를 음성으로 변환할 수 있는 기능을 제공
- gTTS는 Google의 비공식 API에 접근하므로, 반드시 인터넷 연결이 필요

## 설치
```
pip install gTTS
```

------------------

## gtts-cli
```
gtts-cli [options] text
```
- 텍스트를 음성으로 변환하여 출력

<div class="callout info">
<div class="callout-title">

  Options:

</div>

  `-f`, `--file <file>` : <text> 대신에 <file> 에서 읽기
  `-o`, `--output <file>` : 표준 출력(stdout) 대신에 <file> 에 출력
  `-l`, `--lang <lang>` : IETF 언어 태그 지정 기본값은 en
  `--all` : IETF 언어 태그들을 모두 출력
  `--version` : 버전 정보
  `-s`, `--slow` : 느리게 읽음

</div>

--------------------

## 예시

- 한국어 언어 태그

```
# print language tags 
gtts-cli --all
```

- 한국어 태그 보기
```
gtts-cli --all | grep -i korea

# ko: Korean
```


- 텍스트를 음성으로 변환
```
gtts-cli "안녕하세요" --lang ko --output output.mp3
```

--------------------

# 전처리 및 토큰화
- **Pre-processing** 과 **Tokenizing** 은 자연어 처리(NLP)에서 텍스트 데이터를 모델이 이해할 수 있는 형태로 변환하기 위한 기초적인 단계

- 이를 통해 원시 텍스트(raw text)를 정제하고 구조화하여, 분석이나 모델 학습에 적합한 형태로 변환

- gTTS는 내부적으로 텍스트를 음성으로 바꾸기 전에 구글의 TTS 엔진에 적합한 형태로 텍스트를 정제

- 이 과정은 대부분 자동으로 처리되며, 사용자가 직접 제어할 수 있는 범위는 제한적

- gTTS는 사용자가 명시적으로 토큰화를 수행할 필요가 없고, Google TTS API가 문장 단위로 자동 토큰화 및 음소 처리를 수행

---------------------

## `gtts.gTTS`

- gtts 모듈의 핵심 클래스이며, 텍스트를 음성 데이터로 변환할 때 사용

**생성자(__init__) 파라미터**

- `text` : 변환할 텍스트
- `lang` : 언어 코드 (ko, en, ja, fr, 등)
- `slow` : True로 설정하면 느리게 읽음 (기본값: False)
- `tld` : 도메인 (지역별 억양 조정), com, co.kr, co.uk 등

------------------
- 간단한 생성 예제

```python
from gtts import gTTS

tts = gTTS("천천히 읽어볼게요", lang="ko", slow=True)
```

<div class="callout info">
<div class="callout-title">
  INFO
</div>

  - **tld(top-level domain)** 는 발음 억양이나 지역 방언을 조정할 때 사용
  - 예> `en + com`은 미국식 영어, `en + co.uk`은 영국식 영어

</div>

------------------

**메소드**
```python
save(filename: str)
```
- 음성 데이터를 파일로 저장
- 파일 확장자는 자동으로 결정되며, 파일 확장자가 없으면 .mp3로 저장

```python
from gtts import gTTS
tts = gTTS('hello', lang='en')
tts.save('hello.mp3')
write_to_fp(fp: IOBase)
```

------------------

- 음성 데이터를 파일 객체에 쓰기
```python
from gtts import gTTS
tts_en = gTTS('hello', lang='en')
tts_fr = gTTS('bonjour', lang='fr')

with open('hello_bonjour.mp3', 'wb') as f:
    tts_en.write_to_fp(f)
    tts_fr.write_to_fp(f)
```




