---
marp: true
theme: default
paginate: true
style: |
  section {
    padding: 1.5rem; /* 원하는 여백 값으로 조절 */
  }
  h1 {
    position: absolute;
    left: 50px;
    top: 50px;
  }
---

# 문자열 길이

- 문자열은 `iterable`
- `for`로 문자열을 순회하면서 카운팅

```python

def str_len(words):
  count = 0
  for ch in words:
    count += 1
  return count

print(str_len('파이썬으로 코딩하기'))

```

-------------------------------------------

# 특정 문자의 개수 계산

- `str.count()` 

```python
words = 'Hello, World!''
print(words.count('o'))
```

- `for` 루프로 직접 구현

```python

def count_character(words, target):
  count = 0
  for char in words:
    if target == char:
      count += 1
  return count

print(count_character('Hello, World!', 'o'))
```

-------------------------------------------

# 최대/최소 값


-------------------------------------------

# 최대/최소 인덱스


-------------------------------------------

# 리스트 순회하기


-------------------------------------------

# 문자열 비교


-------------------------------------------