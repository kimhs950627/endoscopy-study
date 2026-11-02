# OneNote → 워크북 동기화 절차

OneNote가 원본(SSOT)이고, `notes/*.md`는 그 사본, HTML/PDF는 매번 다시 굽는 산출물이다.
이 문서는 **Kimaki 세션(매일 03:00 루틴)과 데스크톱(Claude Code / OpenCode / VS Code) 양쪽에서 같은 순서로**
돌리기 위한 절차다.

## 0. 원본 위치 (2026-11-03 기준)

| 항목 | 값 |
|---|---|
| 노트북 | `Books_for_Meds` — `0-7B7300AE98D01EB7!22475` |
| 섹션 1 | `검진 protocol, DDx` — `0-7B7300AE98D01EB7!s1a079557ab70471481fdbff49fec8d91` |
| 섹션 2 | `위내시경 공부` — `0-7B7300AE98D01EB7!s75437d7d6d7f4020a097971997d659be` |
| 섹션 3 | `외래진료 공부, 학회내용 정리...` — `0-7B7300AE98D01EB7!s6fe88e7efc9849e18fd8ebdaf4af4dfd` |

페이지는 계속 늘어나므로 **매번 `listPages`로 확인**한다.

## 1. 노트 → 위치 매핑

학회노트는 별도 장이 아니라 **원본 워크북의 해당 질환 절 안에** 들어간다 (`notes/notes.map.json`).

| 노트 파일 | 삽입 위치(장) | 삽입 기준 h2 | 화면 표시 |
|---|---|---|---|
| `notes/egd-gerd.md` | `egd/01-식도-양성.html` | 위식도역류질환의 내시경 소견 | GERD · LA 분류 · 치료 |
| `notes/egd-barrett.md` | `egd/01-식도-양성.html` | 바렛식도 | Barrett · expert positioning |
| `notes/egd-gu-cancer.md` | `egd/03-위-양성.html` | 위궤양 | 궤양 vs 위암 · 조직검사 |
| `notes/egd-egc-observe.md` | `egd/04-위-악성.html` | 위암을 놓치지 않는 내시경 | 관찰 술기 |
| `notes/egd-egc-esd.md` | `egd/04-위-악성.html` | ESD 적응 기준 | 조기위암 ESD 적응과 추적 |
| `notes/cfs-surveillance.md` | `cfs/surveillance.html` | (페이지 전체) | 용종 추적 간격 |

| OneNote 페이지 | 섹션 | 흘러가는 곳 |
|---|---|---|
| 위내시경 질환 Study | 검진 protocol, DDx | `egd-gerd / egd-barrett / egd-gu-cancer / egd-egc-*` |
| CFS f/u schedule | 위내시경 공부 | `cfs-surveillance.md` |
| GI 학회 정리 | 외래진료·학회 | 간 내용이라 EGD 범위 밖 — 보류 |
| EGD, CFS atlas | 위내시경 공부 | 이미지 소스 (텍스트 없음) |
| EndoToday guide 1~4 | 위내시경 공부 | 본문 비어 있음 — 채워지면 매핑 추가 |

새 주제가 생기면 **① `notes/egd-<주제>.md` 작성 → ② `notes/notes.map.json`에 한 줄 추가**가 전부다.
그 다음 빌드가 알아서 표·서브탭·PDF까지 맞춘다.

## 2. Kimaki 세션에서 (MCP 직접)

```
1) tools.onenote.listPages(sectionId=…)                    # 페이지 목록·수정일 확인
2) tools.onenote.getPageContent(pageId=…, format="html")   # HTML로 받는다(text는 중복이 심함)
3) 실행 런타임에서 HTML → 마크다운으로 정리해 notes/*.md 로 저장
4) bash tools/build_pdf.sh egd                             # 노트삽입→서브탭→합본→PDF→북마크
5) git add -A && git commit && git push
```

HTML을 파일로 떨구지 않고 런타임에서 마크다운으로 바꾸면 컨텍스트를 아낀다.
파일로 저장했다면 데스크톱과 같은 경로를 쓴다:

```bash
python3 tools/onenote_to_md.py raw/gi.html \
  --out notes/egd-gerd.md \
  --title "GERD — 개념 · LA 분류 · 치료" \
  --source "OneNote / Books_for_Meds / 검진 protocol, DDx / 위내시경 질환 Study"
```

## 3. 데스크톱에서 (MCP 없이)

OneNote 데스크톱 앱에서 해당 페이지를 **HTML로 내보내기**(파일 → 내보내기 → HTML) 후 같은 명령.

```bash
python3 tools/onenote_to_md.py ~/Downloads/GI.html --out notes/egd-gerd.md --title "…"
bash tools/build_pdf.sh egd
```

## 4. build_pdf.sh 가 하는 일

```
tools/build_notes.py    notes/*.md → cfs/surveillance.html 같은 독립 페이지
tools/apply_notes.py    notes/notes.map.json 대로 각 장의 해당 절 뒤에 인라인 삽입
                        (기존 블록은 지우고 다시 넣는다 → 중복 없음)
tools/build_nav.py      <h2>마다 id 부여 + 질환 서브탭 JSON 재생성
tools/build_book.py     장들을 합본 book.html 로 병합, 표지 갱신일 스탬프
Chrome --print-to-pdf   → downloads/EGD-workbook.pdf
tools/add_outline.py    장·절 북마크 주입
```

## 5. 걸러내는 것 (자동)

`tools/onenote_to_md.py`가 아래를 버린다. 걸러진 뒤에도 이상하면 손으로 지우고 **패턴을
`DROP_PATTERNS`에 추가**한다.

- 개인 금융: `실손`, `보험`, `연금`, `계좌`, `대출`, `카드값`
- 식별자: `주민등록`, `휴대폰`, `비밀번호`
- 금액 표기: `59,790원` 처럼 숫자+원
- OneNote 중첩 목록이 평탄화되며 생기는 **중복 줄**(정규화 후 첫 등장만 유지)

## 6. 편집 원칙

- **사실은 바꾸지 않는다.** 숫자·용량·분류 기준은 원문 그대로 옮긴다.
- **구조만 바꾼다.** 평탄한 목록을 `##` 섹션 + 표로 재편집해 판단에 바로 쓰이게 한다.
- 원문에 없는 내용을 채워 넣지 않는다. 빈 곳은 "확인 필요"로 남긴다.
- 끝에 "최신 가이드라인 확인" 문구를 유지한다.

## 7. 매일 03:00 자동 실행

Kimaki 루틴이 이 문서를 읽고 같은 절차를 돈다 (파일: `routines/onenote-sync.md`).

```bash
kimaki routine list          # 등록 확인
kimaki routine run <id>      # 수동 즉시 실행
```

루틴은 **바뀐 것이 없으면 아무것도 커밋하지 않고 조용히 종료**한다.

## 8. 검증

```bash
python3 tools/check.py                                   # 장별 이미지·표·퀴즈 무결성
S=~/.config/opencode/skills/design-craft/scripts
$S/page-check.sh egd/01-식도-양성.html --width 1440       # 0 HIGH (칩 가로스크롤 MED는 의도)
python3 -c "import pymupdf;d=pymupdf.open('downloads/EGD-workbook.pdf');print(d.page_count,len(d.get_toc()))"
```
