# 챕터 HTML 작성 규칙 (EndoTODAY 참고서)

이 문서는 각 챕터 HTML을 **동일한 서식**으로 만들기 위한 규칙이다. 기준 원본은
`05-십이지장-양성.html` (exemplar) 이다. 반드시 그 파일을 먼저 읽고 형태를 맞춰라.

## 1. 파일/링크 규칙
- 파일명은 `NN-챕터명.html` (이미 정해져 있음). 챕터는 00~06.
- 공용 자산: `assets/book.css`, `assets/book.js` — 절대 수정하지 말 것.
- 이미지 경로는 digest에 나온 `assets/img/<챕터폴더>/<파일명>` 문자열을 **그대로** 복사한다.
  임의로 파일명을 바꾸거나 새 이미지를 상상해서 넣지 말 것. 없는 파일을 참조하면 안 된다.
- 상단바의 이전/다음 링크는 이웃 챕터 파일명으로 연결한다.

## 2. 스켈레톤 (그대로 사용)
```html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CHAPTER NN · 챕터 제목 — EndoTODAY 참고서</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/book.css">
</head>
<body>
<header class="topbar">
  <a class="brand" href="index.html">EndoTODAY 참고서</a>
  <span class="chap">CHAPTER NN · 챕터 제목</span>
  <span class="nav"><a href="이전.html">◀ 이전</a><a href="index.html">목차</a><a href="다음.html">다음 ▶</a></span>
</header>
<div class="layout">
  <nav class="toc"><div class="ttl">목차</div><div id="toc"></div></nav>
  <main>
    <div class="chapter-head">
      <div class="no">CHAPTER NN</div>
      <h1>챕터 제목</h1>
      <p class="lead">한두 문장 요약 (이 챕터에서 다루는 범위).</p>
    </div>
    <!-- 본문 -->
    <a class="back" href="index.html">← 목차로</a>
    <footer>출처: EndoTODAY (endotoday.com, 이준행) 기반 개인 학습용 정리. 약제·용량은 실제 처방 관례에 따름.</footer>
  </main>
</div>
<button id="totop" title="맨 위로">↑</button>
<script src="assets/book.js"></script>
</body>
</html>
```

## 3. 본문 구조 (필수)
각 챕터는 아래 순서로 구성한다.

1. **도입** — 챕터 개요 문단 2~3개.
2. **질환별 섹션** — `<h2>`로 대질환, 필요시 `<h3>`로 세분. 각 섹션마다:
   - 정의·빈도·임상의의 (문단)
   - **내시경 소견** 서술 (문단/불릿)
   - **이미지 2~4장** (`figure` 1장 또는 `figgrid` 묶음)
   - 감별·진단 포인트 (`<h4>` + 불릿, 또는 `.pearl`/`.pf` 박스)
   - 치료·처방 (`.rx` 박스, 아래 §5 형식)
3. **이미지–소견–치료 정리표** — 챕터 맨 뒤. 대표 질환 전체를 한 표로. (아래 §4)
4. **연습문제** — 챕터 맨 끝 `.quiz`. 10~15문항. (아래 §6)

## 4. 이미지–소견–치료 정리표 (필수, 총론 제외)
`.tblwrap` 안에 `<table>`. `caption`에 표 제목. 컬럼:
`질환 | 대표 이미지 | 내시경 소견 | 감별·진단 포인트 | 치료·처방`
- "대표 이미지" 칸에는 `<img src="assets/img/<챕터>/<파일>" alt="질환">` 를 넣는다(1장).
- 치료 칸에는 약어 처방을 `<code>`로 넣고, 처치/내시경치료는 텍스트로.
- 챕터의 모든 주요 질환을 최소 1행씩 포함.

## 5. 처방 표기 규칙 (매우 중요)
실제 의사 처방 약어를 사용한다. `<div class="rx"><div class="t">치료·처방</div><ul>…</ul></div>`.
- 빈도: `qd`(1일1회) `bid` `tid` `qid` `qod` `hs`(취침시) `prn`
- 기간: `1mo`(1개월) `2wk` `8wk` `14d` `3d`
- 용법: `po`(경구) `IV` `IM` `pc`(식후) `ac`(식전)
- 예시:
  - GERD/역류식도염: `<code>esomeprazole 40mg qd pc 4-8wk</code>` 또는 `<code>kcab(tegoprazan) 50mg qd 1mo</code>`
  - H. pylori 제균(14d): `<code>amox 1g bid pc + clarithro 500mg bid pc + PPI bid pc 14d</code>`
  - 위궤양: `<code>kcab 50mg qd ac-30min 8wk</code>`
  - 출혈성궤양 지혈 후: `<code>esomeprazole 40mg IV q12h 72h → po 40mg qd</code>`
  - 십이지장궤양: `<code>PPI qd 4-6wk</code>` (Hp 양성이면 제균 우선)
  - P-CAB 성분명: tegoprazan = 국내 브랜드 K-CAB. 저자는 `kcab` 약어를 즐겨 씀.
- 실제 시판명/성분명을 혼용해도 좋다. 단, 기간·용량은 상식적인 범위로.

## 6. 연습문제 (필수)
`.quiz` 안에 `<h3>연습문제</h3>` + 10~15개의 `.q`.
```html
<div class="q">
  <p class="stem"><span class="n">1.</span> 문제 지문</p>
  <ol class="opts"><li>보기1</li><li>보기2</li><li>보기3</li><li>보기4</li></ol>
  <details><summary></summary><div class="ans"><b>정답: ②</b> — 해설.</div></details>
</div>
```
- 5문항은 4지선다, 나머지는 O/X 또는 단답/사진판독형으로 섞어도 좋다.
- 반드시 **정답과 근거 해설**을 포함.

## 7. 실제 HTML — 전체 예시 (그대로 복사 후 내용 교체)
```html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CHAPTER 05 · 십이지장 양성 질환 — EndoTODAY 참고서</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/book.css">
</head>
<body>
<header class="topbar">
  <a class="brand" href="index.html">EndoTODAY 참고서</a>
  <span class="chap">CHAPTER 05 · 십이지장 양성 질환</span>
  <span class="nav"><a href="04-위-악성.html">◀ 이전</a><a href="index.html">목차</a><a href="06-십이지장-악성.html">다음 ▶</a></span>
</header>
<div class="layout">
  <nav class="toc"><div class="ttl">목차</div><div id="toc"></div></nav>
  <main>
    <div class="chapter-head">
      <div class="no">CHAPTER 05</div>
      <h1>십이지장 양성 질환</h1>
      <p class="lead">…</p>
    </div>

    <h2>1. 십이지장 관찰과 위치 기술</h2>
    <p>…</p>
    <div class="figgrid">
      <figure><img src="assets/img/05-십이지장-양성/20110519_1.png" alt="SDA"><figcaption><b>SDA</b> …</figcaption></figure>
      <figure><img src="assets/img/05-십이지장-양성/20110519_2.png" alt="bulb"><figcaption>…</figcaption></figure>
    </div>

    <div class="rx"><div class="t">치료·처방</div>
      <ul><li>… <code>kcab 50mg qd 4wk</code></li></ul>
    </div>

    <div class="tblwrap">
      <table>
        <caption>표. 십이지장 양성 병변 — 이미지·소견·치료 정리</caption>
        <thead><tr><th>질환</th><th>대표 이미지</th><th>내시경 소견</th><th>감별·진단 포인트</th><th>치료·처방</th></tr></thead>
        <tbody>
          <tr><td>이소성 위점막</td><td><img src="assets/img/05-십이지장-양성/20250207_02.jpg" alt=""></td><td>…</td><td>…</td><td>…</td></tr>
        </tbody>
      </table>
    </div>

    <div class="quiz">
      <h3>연습문제</h3>
      <div class="q"><p class="stem"><span class="n">1.</span> …</p>
        <ol class="opts"><li>…</li><li>…</li><li>…</li><li>…</li></ol>
        <details><summary></summary><div class="ans"><b>정답: ③</b> — …</div></details>
      </div>
    </div>

    <a class="back" href="index.html">← 목차로</a>
    <footer>출처: EndoTODAY (endotoday.com, 이준행) 기반 개인 학습용 정리.</footer>
  </main>
</div>
<button id="totop" title="맨 위로">↑</button>
<script src="assets/book.js"></script>
</body>
</html>
```

## 8. 품질 규칙
- digest(`work/digest/<챕터>.md`)의 사실·수치·문헌만 인용한다. 없는 논문/수치를 지어내지 말 것.
- 일반 의학 상식 보충은 허용하되, 단정적 수치 날조는 금지.
- 한국어 표준 임상용어를 쓴다. 이준행의 실전적 어투를 살린다.
- 이미지 캡션은 병변명 + 핵심 소견 한 줄.
- 목차(TOC)는 `book.js`가 자동 생성하므로 직접 만들지 않는다 (id만 신경쓰지 말 것).
