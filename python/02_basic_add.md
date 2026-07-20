---
marp: true
theme: dark-plus-code
paginate: true
size: 16:9
style: |
  
---

<!-- _class: lead -->

# Python 핵심 개념 정리

## 형변환 · `==` vs `is` · 논리연산자와 단축평가

---

# 목차

1. **형변환 (Type Conversion)**
   - 암시적 형변환 (Implicit)
   - 명시적 형변환 (Explicit)

2. **동등연산자 `==` vs `is`**
   - 값 비교와 정체성 비교

3. **논리연산자와 Short Circuit (단축평가)**
   - `and`, `or`, `not`의 동작 원리

---

<!-- _class: lead -->

# 1. 형변환
## Type Conversion

---

# 형변환의 두 종류

| 구분 | 암시적 (Implicit) | 명시적 (Explicit) |
|---|---|---|
| 주체 | 파이썬이 자동 수행 | 개발자가 직접 호출 |
| 범위 | **숫자 타입만** | 거의 모든 타입 |
| 방법 | 연산 시 자동 승격 | `int()`, `str()` 등 생성자 |
| 예시 | `1 + 0.5 → 1.5` | `int("42") → 42` |

> 핵심 원리: 파이썬은 **강타입 언어** — 숫자 계열 외에는 절대 자동 변환하지 않음

---

# 암시적 형변환 — 승격 방향

```
bool  →  int  →  float  →  complex
(좁은 타입)              (넓은 타입)
```

- 정보 손실이 **없는 방향**으로만 자동 승격
- 역방향(float → int)은 절대 자동으로 일어나지 않음

```python
True + 1        # 2         (bool → int)
3 + 0.5         # 3.5       (int → float)
1.5 + 2j        # (1.5+2j)  (float → complex)
```

---

# 암시적 형변환이 발생하는 상황

```python
# ① 혼합 산술 연산 — 넓은 타입으로 승격
7.0 // 2        # 3.0  (float가 섞이면 결과도 float)

# ② bool의 산술 참여 (True=1, False=0)
sum(x > 2 for x in [1, 3, 5])   # 2

# ③ / 나눗셈 — 항상 float
10 / 2          # 5.0  (5가 아님!)

# ④ 음수 지수
2 ** -1         # 0.5  (int ** int인데 float)

# ⑤ 복합 대입 — 변수 타입이 바뀜
x = 10; x += 0.5   # x는 10.5 (float)
```

---

# 명시적 형변환 — 주요 함수

```python
int(3.9)        # 3       소수부 버림 (반올림 아님)
int("3.5")      # ValueError! → int(float("3.5"))
float("3.14")   # 3.14
str(42)         # '42'    거의 항상 성공
bool("False")   # True!   비어있지 않은 문자열 (흔한 실수)
```

**컬렉션 간 변환** — iterable이면 자유롭게 변환

```python
list("abc")            # ['a', 'b', 'c']
set([1, 2, 2, 3])      # {1, 2, 3}  중복 제거
dict(zip(["a"], [1]))  # {'a': 1}
```

---

# 자바스크립트와의 비교

```python
# Python — 강타입: 애매하면 에러
"나이: " + 25        # TypeError!
"나이: " + str(25)   # '나이: 25'  명시적 변환 필수
```

```javascript
// JavaScript — 암시적 변환 허용
"나이: " + 25        // "나이: 25"  자동 변환
```

> **"명시적인 것이 암시적인 것보다 낫다"**
> — The Zen of Python

---

<!-- _class: lead -->

# 2. 동등연산자
## `==` vs `is`

---

# 핵심 차이

| | `==` (동등성) | `is` (정체성) |
|---|---|---|
| 비교 대상 | **값** (value) | **객체 자체** (identity) |
| 내부 동작 | `__eq__` 메서드 호출 | `id()` 메모리 주소 비교 |
| 재정의 | 가능 (커스텀 클래스) | 불가능 |
| 질문 | "값이 같은가?" | "**같은 객체**인가?" |

```python
a = [1, 2, 3]
b = [1, 2, 3]
a == b    # True   값이 같음
a is b    # False  서로 다른 객체 (다른 메모리)

c = a
c is a    # True   같은 객체를 가리킴
```

---

# `==`의 동작 — 리치 비교 프로토콜

```python
1 == 1.0     # True — float.__eq__가 int를 받아 값 비교
True == 1    # True — bool은 int의 서브클래스 (변환 없음!)
1 == 1+0j    # True — complex가 실수부/허수부 비교
```

**단순 타입 승격이 아닌 정확한 값 비교:**

```python
n = 2**53 + 1
float(n) == 2.0**53   # True   (float 변환 시 정밀도 손실)
n == 2.0**53          # False  (파이썬은 정확하게 판정!)
```

> 해시 일관성: `hash(1) == hash(1.0) == hash(True)`
> → `{1: 'a', 1.0: 'b', True: 'c'}` 는 `{1: 'c'}`

---

# `is`의 함정 — 작은 정수 캐싱

```python
a = 256; b = 256
a is b        # True   (-5 ~ 256은 캐싱된 같은 객체)

a = 257; b = 257
a is b        # False! (범위 밖은 별도 객체) ※ 실행 환경에 따라 다름

s1 = "hello"; s2 = "hello"
s1 is s2      # True (문자열 인터닝 — 구현 세부사항, 믿지 말 것)
```

> CPython의 **최적화 세부사항**일 뿐 — 절대 의존하면 안 됨!

---

# 올바른 사용 규칙

```python
# ✅ is는 싱글턴(None, True, False) 비교에만
if x is None:          # 권장 (PEP 8)
if x is not None:

# ❌ 값 비교에 is 사용 금지
if x is 257:           # SyntaxWarning + 버그 위험

# ✅ 값 비교는 항상 ==
if score == 100:
if name == "python":
```

**한 줄 요약**
- `==` : 내용물이 같은가 → **일상적인 비교**
- `is` : 같은 메모리의 같은 객체인가 → **`None` 체크 전용**

---

<!-- _class: lead -->

# 3. 논리연산자와
## Short Circuit (단축평가)

---

# 논리연산자의 핵심 성질

**파이썬의 `and`/`or`는 `True`/`False`가 아니라 피연산자 객체를 그대로 반환!**

| 표현식 | 규칙 | 결과 |
|---|---|---|
| `A and B` | A가 거짓 → **A 반환** (B 평가 안 함) | 거짓인 쪽 |
| | A가 참 → **B 반환** | 마지막 값 |
| `A or B` | A가 참 → **A 반환** (B 평가 안 함) | 참인 쪽 |
| | A가 거짓 → **B 반환** | 마지막 값 |
| `not A` | 진리값 반전 | 항상 `True`/`False` |

```python
0 and 3.14    # 0     (False 아님!)
2 and 3.14    # 3.14
0 or 3.14     # 3.14
2 or 3.14     # 2
```

---

# 실행 과정: `0 and 3.14`

```python
0 and 3.14      # → 0 (int)
```

**① 왼쪽 `0` 평가** — `and`는 항상 왼쪽부터

**② 진리값 판정** — `0`은 falsy
   (`False`로 변환되는 게 아니라 **판정만** 함)

**③ 단축평가 발동** — 왼쪽이 거짓이면 전체가 거짓 확정
   → 오른쪽 `3.14`는 **평가조차 하지 않음**

**④ `0`을 그대로 반환** — `type(결과)`는 `int`

---

# 진리값 판정 (Truthiness)

불리언 문맥에서 모든 객체는 참/거짓으로 판정됨

**Falsy (거짓)** — "0이거나 비어 있는 것"

```python
False, None, 0, 0.0, 0j, '', [], (), {}, set(), range(0)
```

**Truthy (참)** — 나머지 전부

```python
bool(-1)        # True   0이 아니면 참
bool("False")   # True!  비어있지 않은 문자열
bool([0])       # True   요소가 있는 리스트
```

---

# 단축평가 증명 — 오른쪽은 실행되지 않는다

```python
def f():
    print("f 실행됨!")
    return 3.14

0 and f()    # (출력 없음) → 0      f는 호출 안 됨!
1 and f()    # "f 실행됨!" → 3.14
1 or f()     # (출력 없음) → 1      f는 호출 안 됨!
0 or f()     # "f 실행됨!" → 3.14
```

> 오른쪽에 함수 호출·부수 효과가 있어도
> 결과가 확정되면 **실행 자체를 건너뜀**

---

# 단축평가의 실무 활용

```python
# ① 가드 패턴 — 에러 방지
x = None
x and x.upper()        # None (AttributeError 안 남)
lst and lst[0]         # 빈 리스트여도 IndexError 안 남

# ② 기본값 지정
name = user_input or "기본값"

# ③ 조건부 실행 (division by zero 방지)
b != 0 and a / b

# ④ 여러 조건 연결 — 앞에서 확정되면 뒤는 평가 안 함
if user is not None and user.is_active and user.age > 18:
    ...   # user가 None이면 뒤의 속성 접근을 시도조차 안 함
```

---

# 전체 요약

**형변환**
- 암시적: 숫자 계열만, `bool → int → float → complex` 방향으로만
- 명시적: `int()`, `str()` 등 — 새 객체 생성, 원본 불변

**`==` vs `is`**
- `==` 값 비교 (`__eq__`), `is` 객체 정체성 비교 (`id`)
- `is`는 `None` 체크 전용, 값 비교는 항상 `==`

**논리연산자와 단축평가**
- `and`/`or`는 피연산자를 그대로 반환 (bool 아님)
- 결과 확정 시 오른쪽은 평가하지 않음 → 가드/기본값 패턴

---

<!-- _class: lead -->

# 감사합니다

### Python: 명시적인 것이 암시적인 것보다 낫다