

------------------

## 핵심 개념: Decorator란?

Decorator는 **함수나 클래스를 인자로 받아 새로운 함수를 반환하는 고차함수(Higher-order function)**입니다. 기존 코드를 수정하지 않고 기능을 추가하거나 변형할 수 있습니다.

`@` 기호는 단순히 문법적 설탕(syntactic sugar)입니다:

```python
@my_decorator
def hello(): ...

# 위 코드는 아래와 완전히 동일합니다
def hello(): ...
hello = my_decorator(hello)
```


#### Decorator의 기본 구조
```
- Decorator는 함수를 감싸는 wrapper 함수를 반환합니다. 핵심 패턴은 클로저(closure)입니다.
- 원본 함수 → decorator(fn) → wrapper 함수 반환 → 원본 이름에 재할당
```

```python
def my_decorator(func):
    def wrapper():
        print("함수 실행 전")
        func()               # 원본 함수 호출
        print("함수 실행 후")
    return wrapper       # wrapper를 반환 (호출 X)

# @my_decorator 는 아래와 동일
def say_hello():
    print("Hello!")

say_hello = my_decorator(say_hello)   # 직접 호출 방식

# @syntax 사용 (위와 완전히 동일)
@my_decorator
def say_hi():
    print("Hi!")

say_hi()
```


------------------

아래 인터랙티브 가이드로 각 개념을 단계별로 살펴보세요:---

## 정리: 단계별 핵심 포인트

**① 기본 구조** — decorator는 함수를 받아 함수를 반환합니다. `return wrapper`는 호출하지 않고 함수 객체 자체를 반환합니다.

**② `@functools.wraps`** — 실무에서는 항상 붙이세요. `__name__`, `__doc__` 등 원본 메타데이터를 보존합니다.

**③ `*args, **kwargs`** — 어떤 함수에도 적용 가능한 범용 decorator의 핵심입니다. 반환값도 반드시 `return result`로 전달해야 합니다.

**④ 매개변수 decorator** — 3중 중첩 구조입니다. `@retry(n=3)` 형태로 decorator에 인자를 전달할 수 있습니다.

**⑤ 클래스 decorator** — `__call__`을 구현해 상태를 유지할 때 사용합니다. `functools.lru_cache`가 이 방식입니다.

**⑥ 중첩 & 실전** — 여러 decorator는 아래에서 위 순서로 적용됩니다. 인증, 로깅, 타이머 등 횡단 관심사(cross-cutting concerns)를 분리하는 데 이상적입니다.

궁금한 부분이 있으면 말씀해 주세요!


------------------