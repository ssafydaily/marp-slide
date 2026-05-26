---
marp: true
theme: default
paginate: true
style: |
  section {
    padding: 1.5rem; /* 원하는 여백 값으로 조절 */
  }
  h1 {
    font-size: 1.5rem;
    position: absolute;
    left: 40px;
    top: 30px;
  }
  h2 {
    font-size: 1.3rem;
  }
  h3 {
    font-size: 1rem;
  }
---

# TypeScript 설치하기
- 프로젝트에서 TypeScript를 사용할 수 있는 두 가지 주요 방법:

  - npm 사용하기(Node.js 패키지 매니저)
  - Visual Studio TypeScript 플러그인 설치하기

## npm 사용자
```bash
npm install -g typescript
```

---------------

# Typescript 파일 생성하기

- 다음 내용을 `greeter.ts` 에 작성

```ts
function greeter(person) {
  return "Hello, " + person;
}
 
let user = "Jane User";
 
document.body.textContent = greeter(user);
```

- `.ts` 확장자를 사용했지만, 이 코드는 *JavaScript* 입니다. 뿐입니다. 

-----------------

# 코드 컴파일 하기

- 명령 줄에서, TypeScript 컴파일러를 실행:
- 작성한 코드와 동일한 JavaScript 파일, `greeter.js` 생성

```bash
tsc greeter.ts
```

- 함수 인수인 `person`에 `: string` 타입 표기를 추가한다.
```ts
function greeter(person: string) {
  return "Hello, " + person;
}
 
let user = "Jane User";
 
document.body.textContent = greeter(user);
```
-----------------
# 타입 표기

```ts
unction greeter(person: string) {
  return "Hello, " + person;
}
 
let user = [0, 1, 2];
 
document.body.textContent = greeter(user);

// Argument of type 'number[]' is not assignable to parameter of type 'string'.
```
- 컴파일 하면 오류 발생
```
error TS2345: Argument of type 'number[]' is not assignable to parameter of type 'string'.
```
-------------------
# 인터페이스
- typeScript에서는, 내부 구조가 호환되는 경우 두 개의 타입이 호환됩니다

```ts
interface Person {
  firstName: string;
  lastName: string;
}
 
function greeter(person: Person) {
  return "Hello, " + person.firstName + " " + person.lastName;
}
 
let user = { firstName: "Jane", lastName: "User" };
 
document.body.textContent = greeter(user);
```

-------------------
## 클래스
- 몇 가지 퍼블릭 필드와 생성자를 포함한 Student 클래스를 생성
```ts
class Student {
  fullName: string;
  constructor(
    public firstName: string,
    public middleInitial: string,
    public lastName: string
  ) {
    this.fullName = firstName + " " + middleInitial + " " + lastName;
  }
}
```
-------------------

```ts
interface Person {
  firstName: string;
  lastName: string;
}
 
function greeter(person: Person) {
  return "Hello, " + person.firstName + " " + person.lastName;
}
 
let user = new Student("Jane", "M.", "User"); 
document.body.textContent = greeter(user);
```

----------------
# 웹앱 실행하기

- `greeter.html` 작성

```html
<!DOCTYPE html>
<html>
  <head>
    <title>TypeScript Greeter</title>
  </head>
  <body>
    <script src="greeter.js"></script>
  </body>
</html>
```
