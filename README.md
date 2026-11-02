# Endoscopy Study — EGD · CFS 워크북

상부위장관내시경(EGD)과 대장내시경(CFS)을 각각 하나의 **워크북**으로 관리하는 개인 학습 저장소.

> **원저와 존중** — 이 워크북은 **이준행 교수님이 운영하는 EndoTODAY(endotoday.com)** 의 강의·아틀라스를
> 바탕으로 만든 **개인 학습용 2차 정리물**입니다. 원저작물과 증례 이미지의 저작권은 이준행 교수님께 있으며,
> 이 저장소는 상업적 이용·재배포를 하지 않습니다. 내용의 오류와 해석은 정리한 사람의 것입니다.
> ('학회노트' 표시가 붙은 부분은 본인의 OneNote 학회 정리를 옮긴 것입니다.)

- 사이트: **https://kimhs950627.github.io/endoscopy-study/**
- 약제·용량·적응은 실제 처방 관례와 학회 노트를 따른 것으로, 임상 적용 시 최신 가이드라인과 환자 상태를
  반드시 확인해야 합니다.

## 사이트 구조

```
/                          허브 — EGD / CFS 배너
│  index.html
├─ egd/                    EGD(상부위장관) 워크북
│  ├─ index.html           워크북 표지 · 목차 · PDF 다운로드
│  ├─ 00-총론.html
│  ├─ 01-식도-양성.html 02-식도-악성.html
│  ├─ 03-위-양성.html   04-위-악성.html
│  ├─ 05-십이지장-양성.html 06-십이지장-악성.html
│  ├─ 07-감별증례.html      감별 증례 100 (생성물)
│  └─ book.html            합본 (PDF 인쇄 원본)
├─ cfs/                    CFS(대장) 워크북 — 조립 중
│  ├─ index.html           현황 · 예정 목차
│  └─ surveillance.html    용종 추적 간격 표
├─ downloads/EGD-workbook.pdf   합본 PDF (Git LFS, 347쪽 · 북마크 312개)
├─ notes/                  ★ 학회노트 원고 (OneNote에서 동기화)
│  ├─ notes.map.json       어떤 노트를 어느 장의 어느 절에 넣을지 선언
│  ├─ pages.json           독립 페이지로 렌더할 노트 (cfs 등)
│  └─ egd-*.md, cfs-*.md
├─ data/structure.json     기관(식도·위·십이지장) × 양성/악성 장 매핑
├─ data/cases.json         감별 증례 100 (PDF에서 재추출, tools/import_cases.py 산출)
├─ routines/onenote-sync.md  매일 03:00 자동 동기화 지시서
├─ assets/
│  ├─ site.css             허브·표지 테마 토큰
│  ├─ book.css             장 레이아웃 + 질환 서브탭 + 인쇄 스타일
│  ├─ dx.js                질환 서브탭 렌더러
│  └─ img/<장>/            EndoTODAY에서 수집한 증례 이미지 713장
└─ tools/                  빌드·검증·동기화 스크립트
```

## 질환 서브탭 (핵심 UI)

장을 열면 상단에 3단 탭이 붙는다.

```
[총론] [식도] [위] [십이지장]  ›  [양성] [악성]        목차
─────────────────────────────────────────────────────────
[1. 감염성 식도염] [2. 호산구 식도염] [3. 부식성 …]  ← 가로 스크롤
```

- 1단 기관 탭 → 해당 기관의 양성/악성 장으로 이동
- 2단 성상 탭 → 같은 기관의 양성 ↔ 악성 전환
- 3단 질환 칩 → 그 장의 `<h2>` 절로 바로 이동, 스크롤하면 활성 칩이 자동 추적
- **◆ 표시가 붙은 칩 = 학회노트가 들어 있는 질환** (예: GERD, Barrett, 위궤양, ESD 적응)
- 마지막 탭 **증례** → 「감별 증례 100」 (위 80 · 식도 20)

생성은 `tools/build_nav.py`가 한다. 장에 `<h2>`를 추가하면 다음 빌드에서 칩이 자동으로 늘어난다.

## 학회노트 — 별도 장이 아니라 해당 질환 안에

OneNote 학회 정리는 **원본 워크북의 해당 질환 절 끝에 인라인 블록**으로 들어간다
(`tools/apply_notes.py`, 매핑은 `notes/notes.map.json`).

| 노트 | 들어가는 곳 |
|---|---|
| `notes/egd-gerd.md` | 01 식도 양성 · 위식도역류질환 절 |
| `notes/egd-barrett.md` | 01 식도 양성 · 바렛식도 절 |
| `notes/egd-gu-cancer.md` | 03 위 양성 · 위궤양 절 |
| `notes/egd-egc-observe.md` | 04 위 악성 · 위암을 놓치지 않는 내시경 절 |
| `notes/egd-egc-esd.md` | 04 위 악성 · ESD 적응 기준 절 |
| `notes/cfs-surveillance.md` | `cfs/surveillance.html` (독립 페이지) |

삽입 블록은 `<!-- note:<slug>:start --> … <!-- note:<slug>:end -->` 마커로 감싸므로 **다시 돌려도
중복되지 않고 교체**된다. 새 주제는 ① md 작성 ② `notes.map.json`에 `{file, chapter, h2, label}` 한 줄 —
그 다음 빌드가 서브탭·합본·PDF까지 알아서 맞춘다.

## 감별 증례 100 (CHAPTER 07)

`D:/pdf_to_cards`의 증례 카드(`100증례 조기위암, 식도암 감별`)를 워크북에 합쳤다.

```
PDF(스캔) + cards.json(page·image 매핑)
        │  tools/import_cases.py — 텍스트는 PDF에서 읽기순서로 재추출,
        │                          이미지는 820px/JPEG82로 축소(38MB)
        ▼
   data/cases.json   {case, pages, imgs, age_sex, history, summary, body, pathology, tags, organ}
   assets/img/cases/ 587장
        │  tools/build_cases.py
        ▼
   egd/07-감별증례.html — 위 80 / 식도 20 그룹, 필터·검색·정답 펼치기
        ▼  build_book → build_pdf
   PDF: 증례당 반 페이지, 정답·해설 항상 펼친 상태
```

- 자체 제작한 `cards.json`의 텍스트는 문장 순서가 뒤섞여 있어 **버리고**, 같은 PDF에서
  PyMuPDF로 다시 뽑았다(그림라벨·페이지번호·`그 밖의 해답` 제거, 줄바꿈은 문장부호 기준으로 병합).
- 부위 분류는 본문의 해부 키워드(`식도·EGJ·편평상피·이완불능`)로 판정 → 정확히 81~100이 식도.
- 사진만 먼저 보고 판독하는 자습용: 해설은 `<details>`로 접혀 있고, 인쇄(PDF)에서는 항상 펼쳐진다.
- 원본 PDF는 저장소에 넣지 않는다(로컬 `D:/pdf_to_cards`에만 존재). 재생성이 필요하면 그 경로에서 실행.

## 매일 03:00 동기화

`routines/onenote-sync.md` 지시서를 Kimaki 루틴이 매일 03:00 KST에 실행한다.

```
OneNote Books_for_Meds
  검진 protocol, DDx ─ 위내시경 질환 Study ─┐
  위내시경 공부 ─ CFS f/u schedule ─────────┤
  외래진료·학회 ─ GI 학회 정리 ──────────────┤
                                            ▼
                        (MCP getPageContent → HTML)
                                            ▼
                       tools/onenote_to_md.py  ← 잡음·중복 제거
                                            ▼
                                  notes/*.md  (SSOT)
                                            ▼
   tools/apply_notes.py  → 각 장의 해당 질환 절에 인라인 삽입
   tools/build_nav.py    → 질환 서브탭 재생성
   tools/build_book.py   → egd/book.html
   tools/build_pdf.sh    → downloads/EGD-workbook.pdf (+북마크)
                                            ▼
                        git push → GitHub Actions → Pages
```

- **바뀐 것이 없으면 커밋하지 않는다** (루틴 규칙).
- 수동 실행: `kimaki routine run <id>` / 데스크톱은 `tools/sync-onenote.md` §3.
- 상세 절차·매핑·필터 규칙: [`tools/sync-onenote.md`](tools/sync-onenote.md)

## 빌드

```bash
bash tools/build_pdf.sh egd      # 노트삽입 → 서브탭 → 합본 → PDF → 북마크 (한 번에)

python3 tools/build_notes.py     # notes/pages.json 이 선언한 독립 페이지
(cd tools && python3 apply_notes.py)   # 학회노트를 각 질환 절에 인라인 삽입
python3 tools/build_nav.py       # <h2> id 부여 + 질환 서브탭 JSON
python3 tools/build_book.py      # 장들 → egd/book.html, 표지 갱신일 스탬프
python3 tools/check.py           # 장별 이미지·표·퀴즈 무결성
```

필요 패키지: `pip install pymupdf`, `git lfs install`. PDF 인쇄는 Chrome(Windows `chrome.exe` 또는
리눅스 chromium)을 헤드리스로 쓴다.

### 편집 규칙

- 장 본문은 `egd/*.html`을 직접 고친다. 학회노트는 **`notes/*.md`만** 고친다(HTML은 다음 빌드에서 덮어씀).
- 장에 `<h2>`를 추가하면 서브탭 칩이 자동 생성된다. `<h2>` 번호(`12.`)는 유지한다.
- 인쇄 스타일은 `assets/book.css`의 `@media print`. 긴 박스는 페이지를 넘어가도 잘리지 않게
  `break-inside:auto` + `box-decoration-break:clone`, 표는 `thead` 반복·행 분할 금지.
- 한국어 줄바꿈은 `word-break:keep-all` 유지(`break-all` 금지 — '독일'이 '독/일'로 쪼개진다).

## GitHub Pages

- 저장소는 **public** — GitHub Pages는 무료 플랜에서 private 저장소를 지원하지 않는다.
- 배포: master push → Pages **legacy branch build**(branch `master`, path `/`). `.nojekyll`이 있어
  정적 파일이 그대로 올라간다. HTML/PDF는 **로컬에서 구운 뒤 커밋**한다.
- **PDF는 Git LFS**라 Pages가 포인터(134B)를 서빙한다. 그래서 다운로드 버튼은 LFS 미디어 URL을 쓴다:
  `https://media.githubusercontent.com/media/kimhs950627/endoscopy-study/master/downloads/EGD-workbook.pdf`
- 저장소 public 전환 근거: 무료 플랜에서 private 저장소는 Pages를 지원하지 않는다.
- 주소: https://kimhs950627.github.io/endoscopy-study/

## CFS(대장내시경) 워크북 계획

EGD와 같은 파이프라인을 쓴다. 예정 목차는 `cfs/index.html`, 지금은 `notes/cfs-surveillance.md`만 공개.

1. EndoTODAY 대장 파트를 `tools/crawl.py`로 추가 수집 (`assets/img/cfs-*`)
2. OneNote `대장내시경 질환 study`·`대장내시경 Protocol`이 채워지는 대로 `notes/cfs-*.md` 동기화
3. 장 집필 → `cfs/0*.html` → `data/structure.json`에 CFS 기관 추가 → 서브탭 자동 생성
4. `cfs/book.html` → `downloads/CFS-workbook.pdf` (`build_pdf.sh`의 case에 cfs 분기 추가)

## 조사(크롤링) 방법

EndoTODAY는 IIS가 비브라우저 요청을 `999 No Hacking`으로 차단한다. 그래서 브라우저형 헤더
(User-Agent + Referer)로 우회하고, EUC-KR 문서를 UTF-8로 변환해 수집했다.

- 수집: 약 230개 강의/아틀라스 페이지, 이미지 6,428장 다운로드
- 문서 파싱: 태그 제거 텍스트 + 이미지 위치를 `work/digest/<장>.md`, `work/pages/<장>/NN-*.md`로 저장
- `work/`는 `.gitignore` 대상(로컬 작업물)

## 도구

| 파일 | 역할 |
|---|---|
| `tools/crawl.py` | 엔도투데이 페이지·이미지 수집 → `work/digest`, `assets/img` |
| `tools/split.py` | digest를 페이지별 파일로 분할 → `work/pages` |
| `tools/index_links.py` | 아틀라스 index에서 섹션별 링크 추출 |
| `tools/TEMPLATE.md` | 챕터 HTML 작성 규칙 |
| `tools/assemble.py` | 01·03·04장 조각 조립 (레거시) |
| `tools/renumber.py` | 챕터 내 `<h2>` 번호 재부여 |
| `tools/check.py` | HTML 검증: 이미지 존재·figure/표/퀴즈 개수 |
| `tools/prune.py` | 참조되지 않는 이미지 삭제 |
| `tools/onenote_to_md.py` | OneNote HTML → 마크다운 (잡음·중복 제거, 표 변환) |
| `tools/build_notes.py` | `notes/*.md` → 독립 페이지 |
| `tools/apply_notes.py` | 학회노트를 각 장의 해당 절에 인라인 삽입 |
| `tools/build_nav.py` | 질환 서브탭(기관 → 양성/악성 → 질환 칩) 생성 |
| `tools/import_cases.py` | 증례 PDF → `data/cases.json` + `assets/img/cases` (텍스트 재추출·이미지 축소) |
| `tools/build_cases.py` | `data/cases.json` → `egd/07-감별증례.html` |
| `tools/build_book.py` | 장들 → `egd/book.html`, 표지 갱신일 스탬프 |
| `tools/build_pdf.sh` | 위 단계 + Chrome 인쇄 + 북마크를 한 번에 |
| `tools/add_outline.py` | PDF 장·절 북마크 주입 (PyMuPDF, 한글 안전) |
| `tools/sync-onenote.md` | 동기화 절차서 (Kimaki MCP / 데스크톱 공통) |

## 통계

| 항목 | 값 |
|---|---|
| EGD 장 수 | 8 (총론 + 3기관 × 양성/악성 + 감별증례) |
| 질환 서브탭 | 185개 절 |
| 이미지(figure) | 장별 25~217, 합계 695 |
| 연습문제 | 장별 12~15, 합계 95 |
| 인라인 학회노트 | 5개 블록 (01·03·04장) |
| 수집 이미지 | 6,428장 → 사용 713장(107MB) |
| 감별 증례 | 100례 (위 80 · 식도 20), 사진 587장 |
| 합본 PDF | 426쪽, 약 153MB, 북마크 315개 |

## 개발 이력

- **2026-11-03 · 감별 증례 100 통합**: `D:/pdf_to_cards`의 증례 카드를 CHAPTER 07로 편입.
  텍스트를 PDF에서 읽기순서로 재추출(원본 카드 텍스트는 문장이 뒤섞여 있었음), 이미지 820px로 축소(61→38MB),
  위 80/식도 20 그룹 + 필터·검색 + 정답 접기(인쇄 시 펼침). PDF 426쪽 / 153MB.
- **2026-11-03 · 질환 서브탭 + 인라인 학회노트**: 기관→양성/악성→질환 3단 탭 도입(`build_nav.py`+`dx.js`).
  학회노트를 별도 장에서 각 질환 절 안으로 이동(`apply_notes.py`, 마커 기반 교체). 매일 03:00 동기화 루틴.
  저장소 public 전환 + EndoTODAY·이준행 교수 원저 명시.
- **2026-11-02 · 사이트 재편**: 허브 + `egd/` + `cfs/` 구조, GitHub Pages 워크플로, OneNote 동기화 파이프라인,
  디자인 테마 통일(Gowun Batang + IBM Plex Sans KR, EGD 옥색 / CFS 테라코타).
- **PDF 잘림 방지**: 긴 컬러박스 `break-inside:auto` + `box-decoration-break:clone`, 표 `thead` 반복·행 분할 금지,
  `orphans/widows`. 347쪽 전체에서 페이지 밖으로 나간 텍스트 블록 0.
- **북마크**: Python(PyMuPDF)으로 이전 — 한글 제목을 그대로 넣고 본문 텍스트를 순차 검색해 페이지 매핑.
- **크롤링 차단 우회**: IIS 999 → 브라우저 헤더 + EUC-KR→UTF-8.
- **이미지 용량**: 참조된 이미지만 남겨 `1,021MB → 107MB`(713장).

## 참고

- GitHub 단일 파일 100MB 제한 때문에 PDF는 **Git LFS**로 추적한다(`.gitattributes`).
  클론 후 `git lfs install`이 필요하다.
- Discord/Kimaki에서 표는 렌더링되지 않으므로 README를 붙여넣을 때는 `md-view` 링크를 쓴다.
