---
marp: true
theme: dark-plus-code
paginate: true
style: |
  
  section, pre {
    font-size: 28px;
  }
---

<!-- class:_lead -->


# Basic Syntax


----------------------

**Q1.** 다음 코드의 출력 결과는?

```python
lst = [3, 6, 9, 12, 15, 18, 21]
result = lst[1:6:2]
print(result)
```

-----------------------
**Q1.** 다음 코드의 출력 결과는?

```python
lst = [3, 6, 9, 12, 15, 18, 21]
result = lst[1:6:2]
print(result)
```
## [6, 12, 18]

-----------------------

**Q2.** 다음 코드의 출력 결과는?

```python
print(-3 ** 2)
```

-----------------------

**Q2.** 다음 코드의 출력 결과는?

```python
print(-3 ** 2)
```

## -9

------------------------

**Q3.** 다음 코드의 실행 결과 타입은?

```python
data = "7"
result = int(data) + float(data)
print(type(result))
```

------------------------
**Q3.** 다음 코드의 실행 결과 타입은?

```python
data = "7"
result = int(data) + float(data)
print(type(result))
```

## float

------------------------

<!-- class:_lead -->

# Function

-----------------------

**Q1.** 재귀를 이용하여 정수 리스트의 합을 구하는 함수를 완성하려 한다. 빈칸에 들어갈 종료 조건으로 알맞은 것은?

```python
def list_sum(nums):
    if len(nums) == 0:
        return _________
    return nums[0] + list_sum(nums[1:])
```

----------------

**Q2.** 다음 코드의 실행 결과는?

```python
def change():
    global x
    x = 'B'
    return 'C'

x = 'A'
x = change()
print(x)
```

① A ② B ③ C ④ 오류 발생

----------------

**Q3.** 다음 코드의 출력 결과는?

```python
a = [1, 2, 3]
b = [10, 20, 30]
print(list(zip(a, b)))
```

----------------

