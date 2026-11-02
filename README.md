# Endoscopy Study — EGD · CFS 워크북

상부위장관내시경(EGD)과 대장내시경(CFS)을 각각 하나의 **워크북**으로 관리하는 개인 학습 저장소.
뼈대는 한국의 내시경 대가 이준행 선생이 운영하는 교육 사이트 **EndoTODAY(endotoday.com)** 의 강의·아틀라스,
살은 내가 학회에서 정리한 **OneNote 노트**다. 웹(GitHub Pages)은 읽고 검색하는 판, PDF는 들고 다니는 판이다.

> 원저작물의 권리는 원저자에게 있다. 이 저장소는 개인 학습 목적의 요약·정리본이다.
> 약제·용량·적응은 실제 처방 관례와 학회 노트를 따른 것으로, 임상 적용 시 최신 가이드라인과 환자 상태를
> 반드시 확인해야 한다.

## 사이트 구조

```
/                          허브 — EGD / CFS 배너
│  index.html
├─ egd/                    EGD(상부위장관) 워크북
│  ├─ index.html           워크북 표지 · 목차 · PDF 다운로드
│  ├─ 00-총론.html … 06-십이지장-악성.html    7개 장 (본문)
│  ├─ conference-notes.html                   학회노트 (OneNote 동기화분)
│  └─ book.html            7개 장 + 학회노트 합본 (PDF 원본)
├─ cfs/                    CFS(대장) 워크북 — 조립 중
│  ├─ index.html           현황 · 예정 목차
│  └─ surveillance.html    용종 추적 간격 표 (초안 공개)
├─ downloads/
│  └─ EGD-workbook.pdf     합본 PDF (Git LFS, 북마크 313개)
├─ notes/                  ★ 원고 SSOT — OneNote에서 동기화한 마크다운
│  ├─ pages.json           어떤 md를 어떤 페이지로 렌더할지 선언
│  ├─ egd-*.md, cfs-*.md
├─ assets/
│  ├─ site.css             허브·표지·노트 페이지 (테마 토큰)
│  ├─ book.css             장 본문 레이아웃 + 인쇄 스타일
│  └─ img/<장>/            EndoTODAY에서 수집한 증례 이미지 713장
└─ tools/                  빌드·검증·동기화 스크립트
```

경로 규칙: 허브는 `/index.html`, 워크북은 `egd/`·`cfs/` 아래. 장 파일은 `../assets/...`로 자산을 참조한다.

## 산출물

| 파일 | 내용 |
|---|---|
| `index.html` | 허브. EGD/CFS 배너, 파이프라인 설명, 바로 가기 |
| `egd/index.html` | EGD 워크북 표지 — 장별 목차, PDF 다운로드, 약어 범례 |
| `egd/00-총론.html` | 삽입법·관찰, DEX 소견기술법, 색소/확대내시경, 조직검사, 진정, 항혈소판제, 합병증 |
| `egd/01-식도-양성.html` | 식도염(칸디다·바이러스·호산구·부식성·약물·sloughing), GERD, Barrett, 정맥류, 게실, 이완불능증, SMT, 열공탈장 |
| `egd/02-식도-악성.html` | 편평세포암·Barrett 선암, 조기식도암 육안분류, EUS, ESD·CRT, 흑색종 |
| `egd/03-위-양성.html` | 정상해부, H. pylori, 만성위염/Kyoto, 소화성궤양(Forrest), 용종·선종, SMT, GAVE·PHG·정맥류, 위석·PEG |
| `egd/04-위-악성.html` | 조기위암 육안분류, Borrmann, Lauren/WHO, TNM 8판, ESD 적응·eCura, GEJ암, MALT |
| `egd/05-십이지장-양성.html` | 위치기술, 궤양, 십이지장염, 이소성 위점막·췌장, 림프관확장증, SMT, 게실, HSP, 선종 |
| `egd/06-십이지장-악성.html` | 십이지장 선암, 유두부 병변, NET, 림프종, 전이 |
| `egd/conference-notes.html` | **학회노트** — GERD/LA, Barrett, 궤양 vs 위암, 조기위암 ESD 적응·추적 |
| `egd/book.html` | 위 7개 장 + 학회노트를 병합한 단일 문서 (PDF 인쇄 원본) |
| `downloads/EGD-workbook.pdf` | 합본 PDF 349쪽, 북마크 313개 (Git LFS) |
| `cfs/index.html` | CFS 워크북 현황·예정 목차 |
| `cfs/surveillance.html` | 용종 소견별 추적 대장내시경 간격 (학회 정리 초안) |

## OneNote 동기화 — 이 저장소의 핵심 루프

학회 정리는 **OneNote `Books_for_Meds`** 에 쌓고, 그 내용이 워크북으로 흘러 들어온다.
**상세 절차는 [`tools/sync-onenote.md`](tools/sync-onenote.md)** — Kimaki(MCP 직접)와 데스크톱(HTML 내보내기)
양쪽 경로를 모두 적어 두었다.

```
OneNote Books_for_Meds
  검진 protocol, DDx ─ 위내시경 질환 Study ─┐
  위내시경 공부 ─ CFS f/u schedule ─────────┤
  외래진료·학회 ─ GI 학회 정리 ──────────────┤
                                            ▼
                        (MCP getPageContent → HTML)
                                            ▼
                       tools/onenote_to_md.py  ← 잡음 제거·중복 제거
                                            ▼
                                  notes/*.md  (SSOT)
                                            ▼
        tools/build_notes.py → egd/conference-notes.html · cfs/surveillance.html
                                            ▼
        tools/build_book.py  → egd/book.html
                                            ▼
        tools/build_pdf.sh   → downloads/EGD-workbook.pdf (+ 북마크)
                                            ▼
                            git push → GitHub Actions → Pages
```

**매일/주기 실행**은 Kimaki 루틴으로 돌린다. 루틴 프롬프트 예:

```
tools/sync-onenote.md 절차를 따라 OneNote에서 위내시경·대장내시경 학회노트를 읽어
notes/*.md 를 갱신하고, bash tools/build_pdf.sh egd 로 PDF까지 다시 만든 뒤
변경 사항을 커밋·푸시해줘. 새로 추가된 사실이 없으면 아무 것도 바꾸지 말고 그대로 보고해줘.
```

동기화에서 지키는 것:

- **사실은 그대로, 구조만 재편집.** 숫자·용량·분류 기준은 원문 그대로 옮기고, 평탄한 목록을
  `##` 섹션과 표로 바꿔 내시경 판단에 바로 쓰이게 한다.
- **원문에 없는 내용은 채우지 않는다.** 비어 있으면 "확인 필요"로 남긴다.
- **자동으로 버리는 것** — 개인 금융(실손·보험·연금·계좌), 식별자, 금액 표기, OneNote 평탄화 중복 줄.
  목록은 `tools/onenote_to_md.py`의 `DROP_PATTERNS`.
- 새 페이지가 생기면 `tools/sync-onenote.md`의 매핑 표에 한 줄, `notes/pages.json`의 `files`에 파일 하나를 더한다.

## 빌드

```bash
# 1) 노트 → HTML → 합본 → PDF (한 번에)
bash tools/build_pdf.sh egd

# 개별 단계
python3 tools/build_notes.py     # notes/*.md → notes/pages.json 이 선언한 페이지
python3 tools/build_book.py      # egd/0*.html + 학회노트 → egd/book.html, 표지 날짜 스탬프
python3 tools/add_outline.py downloads/EGD-workbook.pdf egd/book.html /tmp/out.pdf
python3 tools/check.py           # 장별 이미지·표·퀴즈 무결성 검증
```

`build_pdf.sh`는 Chrome(Windows `chrome.exe` 또는 리눅스 chromium)을 찾아 헤드리스 인쇄하고,
`add_outline.py`(PyMuPDF)가 장·절 제목을 PDF 본문에서 순차 검색해 북마크를 심는다.
필요 패키지: `pip install pymupdf`, `git lfs install`.

### 원고 편집 규칙

- 장 본문은 `egd/*.html`을 직접 고친다. 조각 조립(`assemble.py`)은 01·03·04장에만 쓰는 레거시 경로다.
- **학회노트는 `notes/*.md`를 고친다.** HTML을 직접 고치면 다음 동기화에서 덮어쓴다.
- 인쇄 스타일은 `assets/book.css`의 `@media print`에 모여 있다(표 잘림·박스 분할·해설 펼침).
- 한국어 줄바꿈은 `word-break:keep-all`을 유지한다(`break-all` 금지 — '독일'이 '독/일'로 쪼개진다).

## GitHub Pages 배포

- `.github/workflows/pages.yml` — `master` push 시 저장소 루트를 그대로 Pages로 올린다(LFS 포함).
  빌드 단계가 없는 정적 사이트라 HTML/PDF는 **로컬에서 구운 뒤 커밋**한다.
- 공개 주소(활성화 후): `https://kimhs950627.github.io/endoscopy-study/`
- ⚠️ **GitHub Pages는 private 저장소에서 무료 플랜으로 쓸 수 없다.** 저장소를 public으로 전환하거나
  Pro/Team 플랜이 필요하다. public 전환 시 EndoTODAY 유래 자료가 공개된다는 점을 감안할 것.

## CFS(대장내시경) 워크북 계획

EGD와 같은 파이프라인으로 만든다. 예정 목차는 `cfs/index.html`에 있고, 지금은
`notes/cfs-surveillance.md`(용종 추적 간격)만 공개 상태다.

1. EndoTODAY 대장 파트를 `tools/crawl.py`로 추가 수집 (`assets/img/cfs-*`)
2. OneNote `대장내시경 질환 study`·`대장내시경 Protocol` 페이지가 채워지는 대로 `notes/cfs-*.md`로 동기화
3. 장 집필 → `cfs/0*.html` → `cfs/book.html` → `downloads/CFS-workbook.pdf`
4. `tools/build_pdf.sh`의 `case` 문에 cfs 분기 추가

## 조사(크롤링) 방법

EndoTODAY는 IIS가 비브라우저 요청을 `999 No Hacking`으로 차단한다.
그래서 브라우저형 헤더(User-Agent + Referer)로 우회하고, EUC-KR 문서를 UTF-8로 변환해 수집했다.

- 수집: 약 230개 강의/아틀라스 페이지, 이미지 6,428장 다운로드
- 문서 파싱: 태그 제거 텍스트 + 이미지 위치를 `work/digest/<장>.md`(장별 digest),
  `work/pages/<장>/NN-*.md`(페이지별 파일)로 저장해 집필 근거로 사용
- `work/`는 `.gitignore` 대상(로컬 작업물)

## 도구

| 파일 | 역할 |
|---|---|
| `tools/crawl.py` | 엔도투데이 페이지·이미지 수집 → `work/digest`, `assets/img` |
| `tools/split.py` | digest를 페이지별 파일로 분할 → `work/pages` |
| `tools/index_links.py` | 아틀라스 index에서 섹션별 링크 추출 |
| `tools/TEMPLATE.md` | 챕터 HTML 작성 규칙(스켈레톤·클래스·처방 약어) |
| `tools/assemble.py` | 01·03·04장: 조각(`work/frag/*.html`)을 스켈레톤에 조립 (레거시) |
| `tools/renumber.py` | 챕터 내 `<h2>` 번호를 순차 재부여 |
| `tools/check.py` | HTML 검증: 이미지 존재 여부·figure/표/퀴즈 개수 |
| `tools/prune.py` | 참조되지 않는 이미지 삭제 |
| `tools/onenote_to_md.py` | OneNote HTML → 마크다운 (잡음·중복 제거, 표 변환) |
| `tools/build_notes.py` | `notes/*.md` → `notes/pages.json`이 선언한 HTML 페이지 |
| `tools/build_book.py` | EGD 7장 + 학회노트 → `egd/book.html`, 표지 갱신일 스탬프 |
| `tools/build_pdf.sh` | 노트→HTML→합본→PDF→북마크를 한 번에 |
| `tools/add_outline.py` | PDF 장·절 북마크 주입 (PyMuPDF, 한글 UTF-8 안전) |
| `tools/sync-onenote.md` | OneNote 동기화 절차서 (Kimaki MCP / 데스크톱 공통) |

## 통계

| 항목 | 값 |
|---|---|
| EGD 장 수 | 7 (총론 + 6) + 학회노트 |
| 이미지(figure) | 장별 25~217, 합계 695 |
| 연습문제 | 장별 12~15, 합계 95 |
| 수집 이미지 | 6,428장 → 사용 713장(107MB) |
| 합본 PDF | 349쪽, 약 115MB, 북마크 313개 |

## 개발 이력

- **2026-11-02 · 사이트 재편**: 단일 책에서 `허브 + egd/ + cfs/` 구조로 분리. GitHub Pages 워크플로 추가.
  OneNote 동기화 파이프라인(`notes/*.md` SSOT → HTML → PDF) 구축, 학회노트 장 신설.
  디자인 테마를 "차트 위의 옥색" 계열로 통일(서체 Gowun Batang + IBM Plex Sans KR, EGD 옥색 / CFS 테라코타).
- **크롤링 차단 우회**: IIS 999 → 브라우저 헤더 + EUC-KR→UTF-8.
- **집필 스케일 관리**: 장별 digest를 페이지 단위로 쪼개(`work/pages`) 근거 기반으로 집필.
- **이미지 용량**: 참조된 이미지만 남겨 `1,021MB → 107MB`(713장)로 정리.
- **PDF 표 잘림**: 인쇄 CSS에서 `.tblwrap{overflow:visible}`, `table{min-width:0}`,
  `th{white-space:normal}`, 셀 `overflow-wrap:anywhere`, `thead` 반복, `tr` 분할 방지로 해결.
- **연습문제 닫힘**: 합본 로드 시 모든 `details`를 열고, 인쇄에서 `summary` 숨김 + `.ans` 표시.
- **북마크 한글 깨짐/객체 오류**: Python(PyMuPDF)으로 이전 — 제목 문자열을 그대로 넣고
  본문 텍스트를 순차 검색해 페이지를 매핑한다(중복 단어로 뒤로 점프하지 않게 커서 유지).

## 참고

- GitHub 단일 파일 100MB 제한 때문에 PDF는 **Git LFS**로 추적한다(`.gitattributes`).
  클론 후 `git lfs install`이 필요하며, 없으면 PDF는 포인터 텍스트로 받아진다.
- Discord/Kimaki에서 표는 렌더링되지 않으므로 README를 붙여넣을 때는 `md-view` 링크를 쓴다.
