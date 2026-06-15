---
marp: true
theme: default
paginate: true
style: |
  @import "../../custom-theme.css"
---

# Vue-chartjs
> [참고](https://vue-chartjs.org/)
-  **Vue** 에서 *Chart.js* 를 사용할 수 있도록 래핑한 라이브러리
- 재사용 가능한 차트 컴포넌트를 쉽게 만들 수 있습니다.

## 설치
```bash
pnpm add vue-chartjs chart.js
# or
yarn add vue-chartjs chart.js
# or
npm i vue-chartjs chart.js
```

------------------------------------

# Chart 생성
- 기본 차트 `import` 하기
```js
import { Bar } from 'vue-chartjs'
```

<div class="callout info">
<div class="callout-title">

[Chart.js docs](https://www.chartjs.org/docs/latest/#creating-a-chart) 에서 객체 구조를 확인하시오.

</div>
</div>


------------
# 컴포넌트 작성

```js
<template>
  <div class="chart-container">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
// 1. 사용할 컴포넌트와 Chart.js 필수 요소들을 import 합니다.
import { Bar } from 'vue-chartjs'
import { 
  Chart as ChartJS, 
  Title, 
  Tooltip, 
  Legend, 
  BarElement, 
  CategoryScale, 
  LinearScale 
} from 'chart.js'
```
-----------------

```js
// 2. Chart.js에 사용할 모듈들을 등록(Register)합니다. (이 과정이 누락되면 차트가 뜨지 않습니다)
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

// 3. 차트에 들어갈 데이터 정의 (computed를 사용하면 데이터가 변경될 때 차트가 알아서 업데이트됩니다)
const monthlySales = ref([40, 20, 12, 39, 10, 40, 39])

const chartData = computed(() => ({
  labels: ['1월', '2월', '3월', '4월', '5월', '6월', '7월'],
  datasets: [
    {
      label: '2026년 월별 매출 (백만 원)',
      backgroundColor: '#f87979',
      data: monthlySales.value
    }
  ]
}))
```
------------

```js
// 4. 차트 옵션 설정
const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
    },
    title: {
      display: true,
      text: '상반기 실적 그래프'
    }
  }
})
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  height: 400px;
}
</style>
```

--------------

# Composition API 구현 핵심
- **Tree Shaking 지원**: *Chart.js* v4부터는 용량을 줄이기 위해 필요한 기능만 선별해 등록하는 구조입니다. `ChartJS.register(...)`부분을 빼먹으면 에러가 발생하므로, 차트 종류(Bar, Line 등)에 맞는 Element를 꼭 등록한다.

- **반응형(Reactivity)**: API 호출 등으로 데이터가 나중에 로드되거나 변경되는 경우, 예제 1처럼 computed 내부에 ref 변수를 녹여내어 사용하면 자동으로 차트가 리렌더링된다.

- **스타일 팁**: 차트 컴포넌트를 감싸는 외부 `<div>`에 `position: relative`와 `height` 값을 지정해 두어야 차트가 깨지지 않고 부모 크기에 맞게 반응형(`responsive: true`)으로 작동한다.

---------------

# 트리 쉐이킹 비활성화 방법 (auto)
- 매번 필요한 기능을 import 하고 등록하는 과정이 번거롭거나, 내부 어드민 페이지라서 용량 최적화가 크게 중요하지 않은 경우 
- 모든 기능을 한 번에 등록하는 헬퍼 패키지를 사용

```js
// 모든 구성 요소가 포함된 오토(auto) 모듈을 가져옵니다.
import Chart from 'chart.js/auto';

// 이렇게 하면 내부적으로 모든 요소가 자동 등록(register)되므로
// 예전 v2처럼 아무런 등록 절차 없이 모든 차트를 바로 쓸 수 있습니다.
```

<div class="callout tip">
<div class="callout-title">

*트리 쉐이킹* 은 나무를 흔들어(Shake) 죽은 잎사귀를 떨어뜨리듯, 방대한 라이브러리 코드 중 실제로 프로젝트에서 '사용하지 않는 코드'를 빌드 시스템(Webpack, Vite, Rollup 등)이 자동으로 감지해 최종 번들 파일에서 제외하는 기술

</div>
</div>

--------------