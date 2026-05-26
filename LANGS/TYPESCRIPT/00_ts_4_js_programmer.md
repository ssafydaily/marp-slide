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

# Typescript?

- *TypeScript* 은 *JavaScript* 기능들을 제공하면서 그 위에 자체 레이어를 추가
- 이 레이어가 TypeScript **타입 시스템** 입니다.

- *JavaScript* 는 `string`, `number`, `object`, `undefined` 같은 원시 타입을 가지고 있지만, 전체 코드베이스에 일관되게 할당되었는지는 미리 확인하지 않는다.

- *TypeScript* 의 타입 검사기는 사용자가 생각한 일과 JavaScript가 실제로 하는 일 사이의 불일치를 강조



----------------------
# 타입 추론(Types by inference)

```js
let helloWorld = "Hello World";
```

- javascript는 변수를 생성하면서 할당하는 값으로 타입을 결정
- JavaScript의 동작 방식을 이해함으로써 TypeScript는 JavaScript 코드를 받아들이면서 타입을 가지는 타입 시스템을 구축

----------------------

# 타입 정의(Defining Types)

 - `name: string`과 `id: number`을 포함하는 추론 타입을 가진 객체를 생성하는 예제
```js
const user = {
  name: "Hayes",
  id: 0,
};
```
- 객체의 형태를 명시적으로 나타내기 위해서는 `interface` 로 선언

```ts
interface User {
  name: string;
  id: number;
}
```

------------

- 변수 선언 뒤에 `: TypeName`의 구문을 사용해 JavaScript 객체가 새로운 interface의 형태를 따르고 있음을 선언
```ts
const user: User = {
  name: "Hayes",
  id: 0,
};
```

- 해당 인터페이스에 맞지 않는 객체를 생성하면 TypeScript는 경고를 줍니다.
```ts
// @errors: 2322
interface User {
  name: string;
  id: number;
}
const user: User = {
  username: "Hayes",
  id: 0,
};
```

------------------------

- JavaScript는 클래스와 객체 지향 프로그래밍을 지원하므로, TypeScript 또한 동일하다. 
- 인터페이스는 클래스로도 선언할 수 있다.

```ts
interface User {
  name: string;
  id: number;
}
class UserAccount {
  name: string;
  id: number;
  constructor(name: string, id: number) {
    this.name = name;
    this.id = id;
  }
}
const user: User = new UserAccount("Murphy", 1);
```

---------
- 인터페이스는 함수에서 매개변수와 리턴 값을 명시하는데 사용되기도 합니다.

```ts
// @noErrors
interface User {
  name: string;
  id: number;
}
// ---cut---
function getAdminUser(): User {
  //...
}
function deleteUser(user: User) {
  // ...
}
```
----------------

# 타입 구성 (Composing Types)
- 여러가지 타입을 이용하여 새 타입을 작성하기

## 유니언 (Unions)
- 유니언은 타입이 여러 타입 중 하나일 수 있음을 선언하는 방법

```ts
// boolean 타입을 true 또는 false로 설명

type MyBool = true | false;
```

> 참고: `MyBool` 위에 마우스를 올리면, `boolean`으로 분류된 것을 볼 수 있다 
> - 구조적 타입 시스템의 프로퍼티

--------

- 유니언 타입이 가장 많이 사용된 사례 중 하나
- 값이 `string` 또는 `number`의 **리터럴 집합**을 설명하는 것

```ts
type WindowStates = "open" | "closed" | "minimized";
type LockStates = "locked" | "unlocked";
type OddNumbersUnderTen = 1 | 3 | 5 | 7 | 9;
```
- 다양한 타입을 처리하는 방법을 제공하는데, 예를 들어 `array` 또는 `string`을 받는 함수가 있을 수 있다.

```ts
function getLength(obj: string | string[]) {
  return obj.length;
}
```

---------------

- TypeScript는 코드가 시간에 따라 변수가 변경되는 방식을 이해하며, 이러한 검사를 사용해 타입을 골라낼 수 있다.

| Type |	Predicate |
|------|-------------|
| string |	typeof s === "string" |
| number |	typeof n === "number" |
| boolean |	typeof b === "boolean" |
| undefined |	typeof undefined === "undefined" |
| function |	typeof f === "function" |
| array |	Array.isArray(a) |

----------

- `typeof obj === "string"` 을 이용하여 `string`과 `array`를 구분

```ts
function wrapInArray(obj: string | string[]) {
  if (typeof obj === "string") {
    return [obj];
//          ^?
  } else {
    return obj;
  }
}
```

-----------------

## 제네릭 (Generics)

- 제네릭은 타입에 변수를 제공하는 방법입니다.
- 배열이 일반적인 예시이며, 제네릭이 없는 배열은 어떤 것이든 포함할 수 있지만, 
- 제네릭이 있는 배열은 배열 안의 값을 설명할 수 있다.

```ts
type StringArray = Array<string>;
type NumberArray = Array<number>;
type ObjectWithNameArray = Array<{ name: string }>;
```

-----------

- 제네릭을 사용하는 고유 타입을 선언할 수 있다:

```ts
// @errors: 2345
interface Backpack<Type> {
  add: (obj: Type) => void;
  get: () => Type;
}

// 이 줄은 TypeScript에 `backpack`이라는 상수를 선언
declare const backpack: Backpack<string>;

// 위에서 Backpack의 변수 부분으로 선언해서, object는 string
const object = backpack.get();

// backpack 변수가 string이므로, add 함수에 number를 전달할 수 없다.
backpack.add(23);
```
---------------------

# 구조적 타입 시스템(Structural type system)
<br>

- TypeScript의 핵심 원칙 중 하나는 타입 검사가 값이 있는 형태에 집중한다는 것이다. 
- 이는 때때로 “덕 타이핑(duck typing)” 또는 “구조적 타이핑” 이라고 부른다.
- 구조적 타입 시스템에서 두 객체가 같은 형태를 가지면 같은 것으로 간주됩니다.

```ts
interface Point {
  x: number;
  y: number;
}
function printPoint(p: Point) {
  console.log(`${p.x}, ${p.y}`);
}
// "12, 26"를 출력합니다
const point = { x: 12, y: 26 };
printPoint(point);
```
- `point`변수는 `Point`타입으로 선언된 적이 없지만, 타입 검사에서 point의 형태와 Point의 형태를 비교.(같은 형태이기 때문에, 통과)

---------------------



