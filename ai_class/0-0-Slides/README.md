# NumPy · pandas · Matplotlib 교육자료 (Marp)

머신러닝/딥러닝을 위한 데이터 수집·전처리·분석 교육과정 — 총 6시간+

| 파일 | 주제 | 소요 시간 |
|---|---|---|
| `numpy.md` | 수치 배열 연산 | ~2h |
| `pandas.md` | 표 데이터 수집·전처리 | ~2.5h |
| `matplotlib.md` | 시각화 | ~1.5-2h |

## 빌드 방법

```bash
npm install -g @marp-team/marp-cli

marp numpy.md -o numpy.html        # HTML
marp numpy.md --pdf                # PDF
marp numpy.md --pptx               # PowerPoint
```

VS Code에서는 **Marp for VS Code** 확장 설치 후 미리보기/내보내기 가능.

- 테마: gaia / 언어: 한국어 + 영어 용어 병기
- 각 챕터에 ML 활용 맥락 + 따라하기 실습 포함
- 데이터: Titanic(공개) + np.random 가상 데이터 혼합
