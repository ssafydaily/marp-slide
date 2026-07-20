---
marp: true
theme: dark-plus-code
paginate: true
style: |
  
---

# 텍스트 출력하기

- 대/중/소 크기의 제목 출력하기
```python
import streamlit as st

st.title('대 제목')
st.header('중 제목')
st.subheader('소제목')
```
- 일반 텍스트, 마크다운 출력하기
```python
st.text("짧은 길이의 일반 텍스트.")
st.markdown("Markdown을 컴파일해서 출력")                         
st.write("텍스트 또는 다양한 Python 변수/객체 출력.")                             
st.caption("짧은 설명문 (캡션).")
```
---
# 텍스트 출력하기

- 코드 출력
```python
st.code("""
total = 0
for i in range(11):
    total += i
print(total)
""")
```
- latex 출력

```python
st.latex(r"Area = \pi r^2 와 같은 수식.") 
```

---
# 매직 커맨드

- `st.write()` 를 호출한 것과 같은 **매직 커맨드** 방법

```python
first = '변수에 저장한 텍스트'

"일반 텍스트입니다~!"
first
"첫번째 내용", first
```
- 다음 코드와 동일

```python
st.write("일반 텍스트입니다~!")
st.write(first)
st.write("첫번째 내용", first)
```
---

# 데이터 출력

- DataFrame, Json, metric 등 출력

```python

st.dataframe()
st.table()
st.json()
st.metric()
```

---

# 미디어 출력

- 이미지

```python
st.image()
```
- 오디오
```python
with open('sample.wav', 'rb') as f:
  audio_data = f.read()

st.audio(audio_data, format='auiod/wav')
```
- 비디오
```python
with open('video.mov', 'rb') as f:
    video_data = f.read()

st.video(video_data)
```

