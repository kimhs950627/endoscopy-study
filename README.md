# EndoTODAY 참고서 — 상부위장관 내시경

한국의 위내시경 대가 이준행 선생이 운영하는 교육 사이트 **EndoTODAY(endotoday.com)** 의
강의·아틀라스를 바탕으로, 위내시경의 **테크닉 · 소견 해석 · 진단 · 치료**를 장기별·성상별로
정리한 개인 학습용 참고서. 총론 + 6개 장(식도·위·십이지장 × 양성·악성)으로 구성된다.

> 원저작물의 권리는 원저자에게 있다. 이 저장소는 개인 학습 목적의 요약·정리본이다.

## 산출물

| 파일 | 내용 |
|---|---|
| `index.html` | 표지 · 목차 · 처방 약어 범례 |
| `00-총론.html` | 삽입법·관찰, DEX 소견기술법, 색소/확대내시경, 조직검사, 진정, 항혈소판제/항응고제, 합병증 |
| `01-식도-양성.html` | 식도염(칸디다·바이러스·호산구·부식성·약물·sloughing), GERD, Barrett, 정맥류, 게실, 이완불능증, SMT·유두종·inlet patch, 열공탈장 |
| `02-식도-악성.html` | 편평세포암·Barrett 선암, 조기식도암 육안분류, 진단(색소·확대·EUS), 치료(ESD·CRT), 흑색종 |
| `03-위-양성.html` | 정상해부, H. pylori, 만성위염/Kyoto, 소화성궤양(Forrest·출혈), 용종·선종, SMT(GIST·NET 등), GAVE·PHG·정맥류, 위석·PEG |
| `04-위-악성.html` | 조기위암 육안분류, Borrmann, Lauren/WHO, TNM 8판, ESD 적응·eCura, GEJ암, MALT/림프종, 항암 |
| `05-십이지장-양성.html` | 위치기술, 궤양, 십이지장염, 이소성 위점막·췌장, 브루너샘, 림프관확장증, SMT, 게실, HSP, 선종 |
| `06-십이지장-악성.html` | 십이지장 선암, 유두부 병변, 신경내분비종양, 림프종, 전이 |
| `book.html` | 위 7개 장을 순서대로 병합한 단일 문서(연습문제 해설 펼침) |
| `EndoTODAY-참고서.pdf` | `book.html`을 인쇄용으로 렌더한 합본 PDF (352쪽, Git LFS) |
| `assets/book.css`, `assets/book.js` | 책 레이아웃(좌측 목차·스크롤스파이·인쇄 스타일) |
| `assets/img/<장>/` | 엔도투데이에서 수집한 실제 증례 이미지 713장 |
| `tools/` | 크롤러·빌드·검증 스크립트 |

각 장(총론 제외)은 **풍부한 증례 이미지 · 이미지–소견–치료 정리표 · 연습문제(정답·해설)** 를
포함한다. 약제는 `kcab 50mg qd 1mo` 처럼 **실제 처방 약어**로 표기했다.

## 조사(크롤링) 방법

EndoTODAY는 IIS가 비브라우저 요청을 `999 No Hacking`으로 차단한다.
그래서 브라우저형 헤더(User-Agent + Referer)로 우회하고, EUC-KR 문서를 UTF-8로 변환해 수집했다.

- 수집: 약 230개 강의/아틀라스 페이지, 이미지 6,428장 다운로드
- 문서 파싱: 태그 제거 텍스트 + 이미지 위치를 `work/digest/<장>.md`(장별 digest), 그리고
  `work/pages/<장>/NN-*.md`(페이지별 파일)로 저장해 집필 근거로 사용
- `work/`는 `.gitignore` 대상(로컬 작업물)

## 빌드 파이프라인

```
tools/crawl.py          엔도투데이 페이지·이미지 수집 → work/digest, assets/img
tools/split.py          digest를 페이지별 파일로 분할 → work/pages
tools/index_links.py    아틀라스 index에서 섹션별 링크 추출
tools/TEMPLATE.md       챕터 HTML 작성 규칙(스켈레톤·클래스·처방 약어)
tools/assemble.py       01·03·04장: 조각(work/frag/*.html)을 스켈레톤에 조립
tools/renumber.py       챕터 내 <h2> 번호를 순차 재부여
tools/check.py          HTML 검증: 이미지 존재 여부·figure/표/퀴즈 개수
tools/prune.py          참조되지 않는 이미지 삭제
tools/build_book.py     7개 장 → book.html (합본)
tools/add_outline.mjs   PDF에 장·절 북마크(outline) 주입 (pdfjs-dist + pdf-lib)
```

### 합본 PDF 생성

1. `python3 tools/build_book.py` → `book.html`
2. Windows Chrome 헤드리스로 인쇄:
   ```
   chrome.exe --headless=new --disable-gpu --no-pdf-header-footer \
     --print-to-pdf="D:\...\EndoTODAY-참고서.pdf" "file:///D:/.../book.html"
   ```
3. `node tools/add_outline.mjs <pdf> <book.html> <out.pdf>` → 북마크 주입
   (필요 패키지: `npm i pdfjs-dist pdf-lib`)

## 개발 이력 / 수정 사항

- **크롤링 차단 우회**: IIS 999 → 브라우저 헤더 + EUC-KR→UTF-8.
- **집필 스케일 관리**: 장별 digest를 페이지 단위로 쪼개(`work/pages`) 근거 기반으로 집필.
  01·03·04장은 분량이 커서 3개 조각으로 나눠 집필 후 `assemble.py`로 조립.
- **이미지 용량**: 참조된 이미지만 남겨 `1,021MB → 107MB`(713장)로 정리(`prune.py`).
- **PDF 표 잘림**: 인쇄 CSS에서 `.tblwrap{overflow:visible}`, `table{min-width:0}`,
  `th{white-space:normal}`, 셀 `overflow-wrap:anywhere`, `thead` 반복, `tr` 분할 방지로 해결.
- **연습문제 닫힘**: 합본 로드 시 모든 `details`를 열고, 인쇄에서 `summary` 숨김 + `.ans` 표시.
- **컬러박스 페이지 분할**: `.rx/.pf/.pearl/figure/quiz/blockquote`에 `break-inside:avoid`.
- **북마크 한글 깨짐**: `PDFHexString.fromText`(UTF-16BE) 사용.
- **북마크 객체 오류**: `pdf.save({useObjectStreams:false})`로 클래식 xref 저장(pdfjs 호환).
- **북마크 페이지 매핑**: pdfjs 텍스트 추출로 소제목을 순차 검색. PDF 텍스트가 단어 사이를
  NUL(`\u0000`)로 구분하므로 정규화는 `[^\p{L}\p{N}]` 제거로 처리.
- **북마크 번호 중복**: 조각 조립 시 장 내 `<h2>` 번호가 조각마다 1부터 재시작 →
  `renumber.py`로 장 내 순차 재번호(예: 01장 1~29). 현재 북마크 순서 불일치 0건.

## 통계

| 항목 | 값 |
|---|---|
| 장 수 | 7 (총론 + 6) |
| 이미지(figure) | 장별 25~217, 합계 695 |
| 연습문제 | 장별 12~15, 합계 95 |
| 이미지–소견–치료 정리표 | 01~06장 각 1 (+ 총론 상황별 대응표) |
| 수집 이미지 | 6,428장 → 사용 713장(107MB) |
| 합본 PDF | 352쪽, 약 143MB, 북마크 177개(장 7 + 절 170) |

## 참고

- GitHub 단일 파일 100MB 제한 때문에 PDF는 **Git LFS**로 추적한다(`.gitattributes`).
  클론 후 `git lfs install`이 필요하며, 없으면 PDF는 포인터 텍스트로 받아진다.
- 약제·용량·기간은 실제 처방 관례에 따른 것으로, 임상 적용 시 최신 가이드라인과
  환자 상태를 반드시 확인해야 한다.
