# BeautifulSoup

## Install
```bash
pip install beautifulsoup4
```
- 예시 html
```html
<html>
 <head>
  <title>
   The Dormouse's story
  </title>
 </head>
 <p class="title">
  <b>
   The Dormouse's story
  </b>
 </p>
 <p class="story">
  Once upon a time there were three little sisters; and their names were
  <a class="sister" href="http://example.com/elsie" id="link1">
   Elsie
  </a>
  ,
  <a class="sister" href="http://example.com/lacie" id="link2">
   Lacie
  </a>
  and
  <a class="sister" href="http://example.com/tillie" id="link3">
   Tillie
  </a>
  ;
and they lived at the bottom of a well.
 </p>
 <p class="story">
  ...
 </p>
</html>
```

## BeautifulSoup 객체 생성

- `BeautifulSoup` 객체를 생성하면서, 문자열 또는 파일 핸들을 넘긴다.

```python
import requests
from bs4 import BeautifulSoup

soup = BeautifulSoup(open("index.html"))  # 파일

soup = BeautifulSoup("<html>data</html>") # 문자열

response = requests.get('http://www.naver.com')
soup = BeautifulSoup(response.text)
```

## HTML Tag 객체

- Tag 객체는 문서의 XML 태그 또는 HTML 태그에 해당

```python
soup = BeautifulSoup('<b class="boldest">Extremely bold</b>')
tag = soup.b
type(tag)
# <class 'bs4.element.Tag'>
```

#### 이름
- 태그는 이름을 가지며 `.name` 으로 접근
```python
tag.name
# u'b'
```

- 태그의 이름을 바꾸면, BeautifulSoup이 생성한 객체에 반영된다:

```python
tag.name = "blockquote"
tag
# <blockquote class="boldest">Extremely bold</blockquote>
```

#### 속성

- 태그는 속성을 여러개 가질 수 있다. 
- `<b class="boldest">` 태그는 속성으로 `class` 가 있는데 그 값은 `boldest` 이다. 

```python
tag['class']
# u'boldest'

tag.attrs
# {u'class': u'boldest'}

# 속성 추가 변경
tag['class'] = 'verybold'
tag['id'] = 1
tag
# <blockquote class="verybold" id="1">Extremely bold</blockquote>

del tag['class']
del tag['id']
tag
# <blockquote>Extremely bold</blockquote>
```

- 값이 여러개인 속성

```python
css_soup = BeautifulSoup('<p class="body strikeout"></p>')
css_soup.p['class']
# ["body", "strikeout"]

css_soup = BeautifulSoup('<p class="body"></p>')
css_soup.p['class']
# ["body"]
```

## Navigating the tree 

### 내려가기

- 태그에는 또다른 태그가 포함될 수 있으며, 태그의 자손(children)이라고 부른다. 
- 가장 단순하게 트리를 항해하는 방법은 태그의 이름을 지정한다. 
- `<head>` 태그를 원한다면, `soup.head` 라고 지정

```python
soup.head
# <head><title>The Dormouse's story</title></head>

soup.title
# <title>The Dormouse's story</title>

soup.body.b
# <b>The Dormouse's story</b>
```

- 태그 이름을 속성으로 사용하면 첫 번째 태그만 얻는다
```python
soup.a
# <a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>
```

- `<a>` 태그를 모두 얻거나, 특정이름으로 첫 번째 태그 말고 좀 더 복잡한 어떤 것을 얻고 싶다면, `find_all()` 과 같은 메소드 사용

```python
soup.find_all('a')
# [<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
#  <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>,
#  <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]
```

- 태그의 자손은 .contents라고 부르는 리스트로 얻을 수 있다:
```python
head_tag = soup.head
head_tag
# <head><title>The Dormouse's story</title></head>

head_tag.contents
[<title>The Dormouse's story</title>]

title_tag = head_tag.contents[0]
title_tag
# <title>The Dormouse's story</title>
title_tag.contents
# [u'The Dormouse's story']
```

- `.contents` 와 `.children` 속성은 오직 한 태그의 **직계(direct) 자손** 만 고려한다. 
```python
head_tag.contents
# [<title>The Dormouse's story</title>]

for child in head_tag.descendants:
    print(child)
# <title>The Dormouse's story</title>
# The Dormouse's story
```
- `<head>` 태그는 오직 자손이 하나이지만, 후손은 둘이다: `<title>` 태그와 `<title>` 태그의 자손이 그것이다. `BeautifulSoup` 객체는 오직 하나의 직계 자손(`<html>` 태그)만 있지만, 수 많은 후손을 가진다:

```python
len(list(soup.children))
# 1
len(list(soup.descendants))
# 25
```

### 올라가기
- 태그마다 그리고 문자열마다 **부모(parent)** 가 있다
- 한 요소의 부모는 `.parent` 속성으로 접근한다. 

```python
title_tag = soup.title
title_tag
# <title>The Dormouse's story</title>

title_tag.parent
# <head><title>The Dormouse's story</title></head>
# title 문자열 자체로 부모가 있다: 그 문자열을 담고 있는 <title> 태그가 그것이다

title_tag.string.parent
# <title>The Dormouse's story</title>
# <html> 태그와 같은 최상위 태그의 부모는 BeautifulSoup 객체 자신이다

html_tag = soup.html
type(html_tag.parent)
# <class 'bs4.BeautifulSoup'>
# BeautifulSoup 객체의 .parent는 None으로 정의된다

print(soup.parent)
# None
```

- `.parents` 로 한 요소의 부모들을 모두 다 반복할 수 있다. 

```python
link = soup.a
link
# <a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>
for parent in link.parents:
    if parent is None:
        print(parent)
    else:
        print(parent.name)
# p
# body
# html
# [document]
# None
```

### 옆으로 가기

-간단한 예시 문서
```python
sibling_soup = BeautifulSoup("<a><b>text1</b><c>text2</c></b></a>")
print(sibling_soup.prettify())
# <html>
#  <body>
#   <a>
#    <b>
#     text1
#    </b>
#    <c>
#     text2
#    </c>
#   </a>
#  </body>
# </html>
```

- <b> 태그와 <c> 태그는 같은 태그의 직계 자손이다. 
- 이를 **형제들(siblings)**이라고 부른다. 
- 문서가 **pretty-printed**로 출력되면, 형제들은 같은 들여쓰기 수준에서 나타난다. 

- `.next_sibling` 과 `.previous_sibling` 를 사용하면 해석 트리에서 같은 수준에 있는 페이지 요소들 사이를 항해할 수 있다:

```python
sibling_soup.b.next_sibling
# <c>text2</c>

sibling_soup.c.previous_sibling
# <b>text1</b>
```

- 문자열이나 태그의 `.next_element` 속성은 바로 다음에 해석된 것을 가리킨다. `.next_sibling` 과 같을 것 같지만, 완전히 다르다.
- 다음은 “three sisters”문서에서 마지막 `<a>` 태그이다. `.next_sibling`은 문자열이다: 

```python
last_a_tag = soup.find("a", id="link3")
last_a_tag
# <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>

last_a_tag.next_sibling
# '; and they lived at the bottom of a well.'

last_a_tag.next_element
# u'Tillie'
```
- `.previous_element` 속성은 `.next_element` 와 정반대이다. 바로 앞에 해석된 요소를 가리킨다


## 트리 탐색하기

- "three sisters" 문서를 예제로 사용

```python
from bs4 import BeautifulSoup
html_doc = """ 
  예시 문서
"""

soup = BeautifulSoup(html_doc)
```

- `find_all()` 인자에 **filter** 를 설정하면 문서에서 원하는 부분을 추출할 수 있다.

### filter 종류

- 필터들은 탐색 API 전체에서 활용된다. 태그의 이름, 속성, 문자열 텍스트, 또는 이런 것들을 조합하여 사용한다.

#### 문자열
- 문자열과 일치하는 태그를 탐색한다. 

```python
soup.find_all('b')
# [<b>The Dormouse's story</b>]
```

#### 정규 표현식
- 정규 표현식 객체를 건네면, match() 메소드를 사용하여 정규 표현식에 맞는 태그를 찾는다. 
- 다음 코드는 이름이 `b` 로 시작하는 태그를 모두 찾는다
- `<body>` 태그와 `<b>` 태그를 찾을 것이다

```python
import re
for tag in soup.find_all(re.compile("^b")):
    print(tag.name)
# body
# b
```

- 다음 코드는 이름에 `t`가 포함된 태그를 모두 찾는다:

```python
for tag in soup.find_all(re.compile("t")):
    print(tag.name)
# html
# title
```

### 리스트
- 리스트에 담긴 항목마다 문자열에 부합하는 태그를 찾는다

```python
soup.find_all(["a", "b"])
# [<b>The Dormouse's story</b>,
#  <a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
#  <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>,
#  <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]
```

### True

- True 값은 참이면 모두 부합시킨다. 다음 코드는 문서에서 태그를 모두 찾지만, 텍스트 문자열은 전혀 찾지 않는다:
```python
for tag in soup.find_all(True):
    print(tag.name)
# html
# head
# title
# body
# p
# b
# p
# a
# a
# a
# p
```

### 함수
- 원하는 태그에 대한 조건을 체크해서 `True` 를 반환하는 함수 작성

```python
def has_class_but_no_id(tag):
    return tag.has_key('class') and not tag.has_key('id')

soup.find_all(has_class_but_no_id)
# [<p class="title"><b>The Dormouse's story</b></p>,
#  <p class="story">Once upon a time there were...</p>,
#  <p class="story">...</p>]
```

- 이 함수는 `<p>` 태그만 얻는다. 
- `<a>` 태그는 획득하지 않는데, `class`와 `id`가 모두 정의되어 있기 때문이다. 
- `<html>` 과 `<title>` 도 얻지 않는데, 왜냐하면 `class`가 정의되어 있지 않기 때문이다.


### find_all()

- `find_all(name, attrs, recursive, text, limit, **kwargs)`

  - 필터에 부합하는 후손들을 찾아서 모두 추출 

```python
soup.find_all("title")
# [<title>The Dormouse's story</title>]

soup.find_all("p", "title")
# [<p class="title"><b>The Dormouse's story</b></p>]

soup.find_all("a")
# [<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
#  <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>,
#  <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]

soup.find_all(id="link2")
# [<a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>]

import re
soup.find(text=re.compile("sisters"))
# u'Once upon a time there were three little sisters; and their names were\n'
```
#### `name` : 특정 이름을 가진 태그에만 관심을 가진다. 
#### `키워드 인자` : 태그의 속성중 하나에 대한 필터로 변환된다. `id` 라는 인자에 값을 하나 건네면, 각 태그의 `id`속성에 대하여 걸러낸다

```python
soup.find_all(id='link2')
# [<a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>]

soup.find_all(href=re.compile("elsie"))
# [<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>]

soup.find_all(id=True)
# [<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
#  <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>,
#  <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]

soup.find_all(href=re.compile("elsie"), id='link1')
# [<a class="sister" href="http://example.com/elsie" id="link1">three</a>]
```

#### CSS 클래스로 탐색하기
- CSS 속성의 이름인 `class`는 파이썬에서 예약어이다. 키워드 인자로 class를 사용하면 구문 에러를 만나게 된다. 
- 뷰티플 4.1.2 부터, CSS 클래스로 검색할 수 있는데 `class_` 키워드 인자를 사용한다.

```python
soup.find_all("a", class_="sister")
# [<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
#  <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>,
#  <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]

soup.find_all(class_=re.compile("itl"))
# [<p class="title"><b>The Dormouse's story</b></p>]

def has_six_characters(css_class):
    return css_class is not None and len(css_class) == 6

soup.find_all(class_=has_six_characters)
# [<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
#  <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>,
#  <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]

css_soup = BeautifulSoup('<p class="body strikeout"></p>')
css_soup.find_all("p", class_="strikeout")
# [<p class="body strikeout"></p>]

css_soup.find_all("p", class_="body")
# [<p class="body strikeout"></p>]

css_soup.find_all("p", class_="body strikeout")
# [<p class="body strikeout"></p>]

css_soup.find_all("p", class_="strikeout body")
# []

soup.find_all("a", "sister")
# [<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
#  <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>,
#  <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]
```

#### text
- 태그 대신 문자열을 탐색할 수 있다. name과 키워드 인자에서처럼, 문자열, 정규 표현식, 리스트, 함수, 또는 True 값을 건넬 수 있다.

```python
soup.find_all(text="Elsie")
# [u'Elsie']

soup.find_all(text=["Tillie", "Elsie", "Lacie"])
# [u'Elsie', u'Lacie', u'Tillie']

soup.find_all(text=re.compile("Dormouse"))
[u"The Dormouse's story", u"The Dormouse's story"]

def is_the_only_string_within_a_tag(s):
    """Return True if this string is the only child of its parent tag."""
    return (s == s.parent.string)

soup.find_all(text=is_the_only_string_within_a_tag)
# [u"The Dormouse's story", u"The Dormouse's story", u'Elsie', u'Lacie', u'Tillie', u'...']

soup.find_all("a", text="Elsie")
# [<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>]
```

#### limit 

- 문서가 방대하면 시간이 좀 걸릴 수 있다. 
- 결과가 모조리 필요한 것은 아니라면, limit에 숫자를 설정 
- SQL에서의 LIMIT 키워드와 동일하게 작동

```python
soup.find_all("a", limit=2)
# [<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
#  <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>]
```

#### recursive 
- `mytag.find_all()`를 호출하면, 뷰티플수프는 mytag의 후손을 모두 조사한다
- 직계 자손만 조사하고 싶다면, `recursive=False` 를 건네면 된다.


## find()

- `find(name, attrs, recursive, text, **kwargs)`

- `find_all()` 메소드는 전체 문서에서 결과를 찾지만, 어떤 경우는 하나의 결과만 필요할 수 있다. 
- <body> 태그가 하나 뿐임을 안다면, 전체 문서를 훓어 가면서 찾는 것은 시간 낭비
- find_all 메쏘드를 호출할 때마다, **limit=1** 을 건네기 보다는 `find()` 를 사용

```python
soup.find_all('title', limit=1)
# [<title>The Dormouse's story</title>]

soup.find('title')
# <title>The Dormouse's story</title>
```
- 유일한 차이점은 `find_all()`는 단 한개의 결과만 담고 있는 리스트를 돌려주고, `find()`는 그 결과를 돌려준다는 점이다.
- 결과가 없다면 `find_all()`은 빈 리스트, `find()`는 `None`

```python
print(soup.find("nosuchtag"))
# None
```

## CSS 선택자

- **BeautifulSoup** 은 CSS 선택자 표준의 부분집합을 지원한다. 
- 문자열로 선택자를 구성하고 그것을 **Tag**의 `.select()` 메쏘드 또는 BeautifulSoup 객체 자체에 전달

```python
soup.select("title")
# [<title>The Dormouse's story</title>]

soup.select("body a")
# [<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
#  <a class="sister" href="http://example.com/lacie"  id="link2">Lacie</a>,
#  <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]

soup.select("html head title")
# [<title>The Dormouse's story</title>]

soup.select("head > title")
# [<title>The Dormouse's story</title>]

soup.select("p > a")
# [<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
#  <a class="sister" href="http://example.com/lacie"  id="link2">Lacie</a>,
#  <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]

soup.select("body > a")
# []

soup.select(".sister")
# [<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
#  <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>,
#  <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]

soup.select("[class~=sister]")
# [<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
#  <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>,
#  <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]
```

