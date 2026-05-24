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
    left: 50px;
    top: 50px;
  }
  h2 {
    font-size: 1.3rem;
  }
  h3 {
    font-size: 1rem;
  }

---

# Getting Started 

## Installation

### npm
```
npm install chart.js
```

### CDN 
- [CDNJS](https://cdnjs.com/libraries/Chart.js)
- [jsDeliver](https://www.jsdelivr.com/package/npm/chart.js?path=dist)


----------------

# 간단한 Bar Char 예제 

![](images/00_barchart.png)

-----------------

# Canvas 

- `반응성(responsiveness)` 을 위해서 *chart* 가 자신의 *container*를 가지도록 하는게 권장된다


```html
<div>
    <canvas id="myChart"></canvas>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

```
- `<canvas>`
- CDN 포함

----------------
- `<script> 추가하기`
```js
<script>
  const ctx = document.getElementById('myChart');

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
      datasets: [{
        label: '# of Votes',
        data: [12, 19, 3, 5, 2, 3],
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
</script>
```

--------------
## step-by-stop 가이드
> [charjs 가이드 문서 참고](https://www.chartjs.org/docs/latest/getting-started/usage.html
)

- 예시 
![bg right h:100%](images/00_chart01.png)

-----------------


## `package.json` 파일 작성
```json
{
  "name": "chartjs-example",
  "version": "1.0.0",
  "license": "MIT",
  "scripts": {
    "dev": "parcel src/index.html",
    "build": "parcel build src/index.html"
  },
  "devDependencies": {
    "parcel": "^2.6.2"
  },
  "dependencies": {
    "@cubejs-client/core": "^0.31.0",
    "chart.js": "^4.0.0"
  }
}
```
- 설정이 필요없는 간편한 빌드도구인 **Parcle** 선택
- 실제 데이터를 가져오기 위해서 **Cube**의 클라이언트 설치

------------------

- `npm install`, `yarn install`, 또는 `pnpm install` 실행해서 패키지 설치
- `src` 폴더 생성
- 폴더 내부에 `index.html` 작성
```html
<!doctype html>
<html lang="en">
  <head>
    <title>Chart.js example</title>
  </head>
  <body>
    <!-- <div style="width: 500px;"><canvas id="dimensions"></canvas></div><br/> -->
    <div style="width: 800px;">
      <canvas id="acquisitions"></canvas>
    </div>

    <!-- <script type="module" src="dimensions.js"></script> -->
    <script type="module" src="acquisitions.js"></script>
  </body>
</html>

```
----------------
- `src/acquisitions.js` 작성
```js
import Chart from 'chart.js/auto'

(async function() {
  const data = [
    { year: 2010, count: 10 },
    { year: 2011, count: 20 },
    { year: 2012, count: 15 },
    { year: 2013, count: 25 },
    { year: 2014, count: 22 },
    { year: 2015, count: 30 },
    { year: 2016, count: 28 },
  ];

  new Chart(
    document.getElementById('acquisitions'),
    {
      type: 'bar',
      data: {
        labels: data.map(row => row.year),
        datasets: [
          {
            label: 'Acquisitions by year',
            data: data.map(row => row.count)
          }
        ]
      }
    }
  );
})();

```
-------------

- 실행: `npm run dev`, `yarn dev`, `pnpm dev`
- 브라우저에서 `localhost:1234` 열기