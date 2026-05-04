`yield`는 파이썬에서 **제너레이터(generator)** 를 만들기 위해 사용하는 키워드입니다.  
처음 보면 `return`과 비슷해 보이지만, 실제로는 동작 방식이 꽤 다릅니다.

---

# 1. `yield`란 무엇인가?

일반 함수는 `return`을 만나면 **즉시 종료**되고 값을 하나 반환합니다.

반면 `yield`가 들어간 함수는 **제너레이터 함수**가 됩니다.  
이 함수를 호출하면 결과가 바로 실행되는 것이 아니라, **제너레이터 객체**가 만들어집니다.

그리고 이 제너레이터는:
- 값을 **하나씩 순서대로 생성**
- 값을 내보낸 뒤 **함수의 실행 상태를 기억**
- 다음 요청이 오면 **이전 지점부터 다시 실행**

합니다.

즉, `yield`는 데이터를 한꺼번에 다 만들어서 반환하지 않고,  
**필요할 때마다 하나씩 꺼내 쓸 수 있게 해주는 방식**입니다.

---

# 2. `return`과 `yield`의 차이

## `return`
- 함수 실행 종료
- 값을 한 번에 반환
- 이후 함수 상태는 사라짐

## `yield`
- 값을 잠깐 바깥으로 전달
- 함수는 종료되지 않고 **중단(pause)** 상태가 됨
- 다음 호출 때 이어서 실행

예를 들어:

```python
def normal_function():
    return 1
```

이 함수는 호출 시 `1`을 반환하고 끝납니다.

반면:

```python
def generator_function():
    yield 1
    yield 2
    yield 3
```

이 함수는 호출해도 바로 1, 2, 3을 반환하지 않고,  
**차례대로 값을 생성하는 제너레이터**를 반환합니다.

---

# 3. 기본 동작 예시

```python
def simple_generator():
    yield 1
    yield 2
    yield 3


gen = simple_generator()

print(next(gen))  # 1
print(next(gen))  # 2
print(next(gen))  # 3
```

## 설명
- `simple_generator()`를 호출하면 `gen`에는 제너레이터 객체가 들어갑니다.
- `next(gen)`을 호출할 때마다 함수가 다음 `yield`까지 실행됩니다.
- `yield 1`에서 1을 반환하고 잠시 멈춤
- 다시 `next(gen)`을 호출하면 `yield 2`부터 이어서 실행
- 마지막까지 가면 더 이상 줄 값이 없으므로 `StopIteration` 예외가 발생합니다.

즉, `yield`는 함수의 실행 위치를 기억했다가 이어서 실행할 수 있게 합니다.

---

# 4. 왜 `yield`를 쓰는가?

`yield`의 가장 큰 장점은 **메모리 효율성**입니다.

예를 들어 1부터 1억까지의 숫자를 모두 저장한 리스트를 만들면 메모리를 매우 많이 사용합니다.

```python
numbers = [i for i in range(100000000)]
```

하지만 제너레이터를 사용하면 값을 한 번에 다 저장하지 않고,  
필요한 순간에 하나씩 생성하므로 메모리를 훨씬 적게 씁니다.

```python
def number_generator():
    for i in range(100000000):
        yield i
```

이 방식은:
- 대용량 데이터 처리
- 파일 한 줄씩 읽기
- 네트워크 스트림 처리
- 무한 수열 생성

같은 상황에서 매우 유용합니다.

---

# 5. 예시 1: 리스트 반환과 제너레이터 반환 비교

```python
def get_squares_list(n):
    result = []
    for i in range(n):
        result.append(i * i)
    return result


def get_squares_generator(n):
    for i in range(n):
        yield i * i


print(get_squares_list(5))
print(list(get_squares_generator(5)))
```

## 실행 결과
```python
[0, 1, 4, 9, 16]
[0, 1, 4, 9, 16]
```

## 설명
두 함수 모두 겉으로 보기에는 같은 결과를 만듭니다.

하지만 내부 동작은 다릅니다.

### `get_squares_list`
- `0, 1, 4, 9, 16`을 전부 리스트에 저장
- 저장이 끝난 뒤 한 번에 반환

### `get_squares_generator`
- 호출 시 제너레이터 객체 반환
- 실제 값은 반복할 때 하나씩 생성

`list(get_squares_generator(5))`처럼 감싸면 결국 리스트로 바꾸므로 결과는 같아 보입니다.  
하지만 원래 제너레이터의 핵심은 **전부 저장하지 않고 필요할 때 생성**하는 데 있습니다.

---

# 6. 예시 2: 반복문에서 사용하는 가장 일반적인 형태

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1


for number in countdown(5):
    print(number)
```

## 실행 결과
```python
5
4
3
2
1
```

## 설명
이 코드는 `5`부터 `1`까지 하나씩 생성합니다.

동작 순서는 다음과 같습니다.

1. `countdown(5)` 호출 → 제너레이터 객체 생성
2. `for`문이 첫 번째 값을 요청
3. 함수가 `yield n`까지 실행되어 `5`를 반환
4. 다음 반복에서 함수는 멈췄던 지점 다음 줄인 `n -= 1`부터 다시 실행
5. 다시 `yield n`에서 `4` 반환
6. 이를 반복하다가 `n == 0`이 되면 종료

`for`문은 내부적으로 `next()`를 반복 호출한다고 생각하면 이해하기 쉽습니다.

---

# 7. 예시 3: 함수 실행 상태가 유지된다는 점 보여주기

```python
def test_generator():
    print("함수 시작")
    yield 1
    print("첫 번째 yield 이후")
    yield 2
    print("두 번째 yield 이후")
    yield 3
    print("함수 종료")


gen = test_generator()

print(next(gen))
print(next(gen))
print(next(gen))
```

## 실행 결과
```python
함수 시작
1
첫 번째 yield 이후
2
두 번째 yield 이후
3
```

## 설명
이 예제는 `yield`가 함수의 상태를 저장한다는 점을 잘 보여줍니다.

### 첫 번째 `next(gen)`
- `"함수 시작"` 출력
- `yield 1`에서 멈춤
- `1` 반환

### 두 번째 `next(gen)`
- 이전에 멈춘 지점 다음부터 실행
- `"첫 번째 yield 이후"` 출력
- `yield 2`에서 멈춤
- `2` 반환

### 세 번째 `next(gen)`
- `"두 번째 yield 이후"` 출력
- `yield 3`에서 멈춤
- `3` 반환

만약 한 번 더 `next(gen)`을 호출하면 `"함수 종료"`가 출력된 뒤 `StopIteration`이 발생합니다.

---

# 8. 예시 4: 큰 파일을 한 줄씩 처리하는 개념

```python
def read_lines(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            yield line.strip()
```

사용 예:

```python
for line in read_lines("sample.txt"):
    print(line)
```

## 설명
이 함수는 파일 전체를 메모리에 한 번에 올리지 않고,  
**한 줄씩 읽어서 반환**합니다.

이런 방식은 파일이 매우 클 때 특히 유리합니다.

### 장점
- 메모리 절약
- 처리 시작이 빠름
- 스트리밍 방식 처리 가능

---

# 9. 예시 5: 무한 제너레이터

```python
def infinite_numbers():
    num = 1
    while True:
        yield num
        num += 1


gen = infinite_numbers()

for _ in range(5):
    print(next(gen))
```

## 실행 결과
```python
1
2
3
4
5
```

## 설명
일반 리스트로는 무한한 값을 만들 수 없습니다.  
하지만 `yield`를 사용하면 **필요할 때마다 다음 값만 생성**하면 되므로 무한 시퀀스도 표현할 수 있습니다.

이 예제는:
- 처음에 1 반환
- 다음 요청 시 2 반환
- 계속 반복

하는 구조입니다.

---

# 10. `yield from`

파이썬에는 `yield from`이라는 문법도 있습니다.  
이것은 다른 반복 가능한 객체(iterable) 또는 다른 제너레이터의 값을 **대신 전달**할 때 사용합니다.

```python
def generator1():
    yield 1
    yield 2


def generator2():
    yield 0
    yield from generator1()
    yield 3


for x in generator2():
    print(x)
```

## 실행 결과
```python
0
1
2
3
```

## 설명
`yield from generator1()`은 아래와 거의 비슷합니다.

```python
for x in generator1():
    yield x
```

즉, 다른 제너레이터가 생산하는 값을 그대로 이어받아 내보낼 수 있습니다.

---

# 11. `yield`와 `return`을 함께 사용할 수 있는가?

가능합니다.  
다만 제너레이터 함수에서 `return`은 **함수 종료**의 의미를 가집니다.

```python
def gen():
    yield 1
    yield 2
    return
```

이 경우:
- 1 반환
- 2 반환
- 종료

파이썬 3에서는 제너레이터 안의 `return 값`도 가능하지만,  
일반적인 `for`문 사용에서는 그 값이 직접 보이지 않습니다.  
보통은 특별한 경우가 아니면 단순 종료 용도로만 생각하면 됩니다.

---

# 12. 제너레이터 표현식

리스트 컴프리헨션과 비슷하게 제너레이터 표현식도 있습니다.

## 리스트 컴프리헨션
```python
squares_list = [x * x for x in range(5)]
```

## 제너레이터 표현식
```python
squares_gen = (x * x for x in range(5))
```

차이점:
- 리스트 컴프리헨션: 결과를 즉시 모두 메모리에 저장
- 제너레이터 표현식: 필요할 때마다 값 생성

예:

```python
squares_gen = (x * x for x in range(5))

for value in squares_gen:
    print(value)
```

---

# 13. `yield` 사용 시 주의점

## 1) 한 번 소비하면 다시 못 쓴다
제너레이터는 한 번 순회가 끝나면 다시 처음부터 사용할 수 없습니다.

```python
def gen():
    yield 1
    yield 2

g = gen()

print(list(g))  # [1, 2]
print(list(g))  # []
```

이미 다 꺼내 썼기 때문입니다.

---

## 2) 인덱싱이 안 된다
리스트처럼 `g[0]` 형태로 접근할 수 없습니다.

```python
g = (x for x in range(5))
```

이 객체는 순차적으로만 꺼낼 수 있습니다.

---

## 3) 필요하면 리스트로 변환해야 한다
여러 번 재사용하거나 랜덤 접근이 필요하면 리스트가 더 적절할 수 있습니다.

```python
g = (x for x in range(5))
numbers = list(g)
```

---

# 14. 실무적으로 언제 유용한가?

`yield`는 다음과 같은 상황에서 매우 자주 유용합니다.

- 큰 데이터셋 순차 처리
- 로그 파일 분석
- CSV/JSONL 스트리밍 처리
- 페이지네이션 API 결과 순회
- 무한 스트림 생성
- 파이프라인 처리

예를 들어 대용량 로그 파일에서 에러가 있는 줄만 찾는 경우:

```python
def read_errors(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            if "ERROR" in line:
                yield line.strip()
```

이렇게 하면 전체 파일을 메모리에 다 올릴 필요 없이 에러 줄만 하나씩 처리할 수 있습니다.

---

# 15. 핵심 정리

`yield`를 한 문장으로 정리하면:

> **함수의 실행 상태를 유지하면서, 값을 하나씩 순차적으로 반환하게 해주는 키워드**

핵심 특징은 다음과 같습니다.

- `yield`가 있는 함수는 제너레이터 함수가 된다.
- 호출 시 바로 실행되지 않고 제너레이터 객체를 반환한다.
- `next()` 또는 `for`문으로 값을 하나씩 꺼낸다.
- 값을 반환한 뒤 함수 상태가 유지된다.
- 메모리 효율이 좋다.
- 큰 데이터나 무한 시퀀스 처리에 적합하다.

---

# 16. 이해를 돕는 종합 예시

```python
def even_numbers(limit):
    print("제너레이터 시작")
    for number in range(limit + 1):
        if number % 2 == 0:
            print(f"{number} 생성")
            yield number
    print("제너레이터 종료")


gen = even_numbers(10)

for value in gen:
    print(f"사용: {value}")
```

## 예상 실행 결과
```python
제너레이터 시작
0 생성
사용: 0
2 생성
사용: 2
4 생성
사용: 4
6 생성
사용: 6
8 생성
사용: 8
10 생성
사용: 10
제너레이터 종료
```

## 설명
이 코드는 0부터 10까지의 짝수만 하나씩 생성합니다.

동작 흐름은 다음과 같습니다.

1. `even_numbers(10)` 호출 → 제너레이터 객체 생성
2. `for`문이 첫 값을 요청
3. 함수가 실행되면서 `"제너레이터 시작"` 출력
4. 짝수를 만나면 `"0 생성"` 출력 후 `yield 0`
5. 바깥의 `for`문이 `0`을 받아 `"사용: 0"` 출력
6. 다음 반복에서 다시 함수 내부로 돌아가 이어서 실행
7. 같은 방식으로 2, 4, 6, 8, 10 생성
8. 반복이 끝나면 `"제너레이터 종료"` 출력

이 예제의 핵심은:
- **값 생성 시점**과
- **값 소비 시점**이
서로 맞물려 진행된다는 것입니다.

즉, 값을 미리 전부 만들어 두는 것이 아니라,  
필요할 때마다 생성해서 즉시 사용하는 구조입니다.

---

원하시면 다음 단계로 이어서  
1. `yield`와 `return`의 내부 동작 비교  
2. `send()`, `throw()`, `close()`를 포함한 고급 제너레이터  
3. 코루틴과의 관계  
4. 실무형 예제(파일 처리, API 페이지네이션, 데이터 파이프라인)  
까지 확장해서 설명드릴 수 있습니다.