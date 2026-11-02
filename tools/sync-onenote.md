# OneNote → 워크북 동기화 절차

OneNote가 원본(SSOT)이고, `notes/*.md`는 그 사본, HTML/PDF는 매번 다시 굽는 산출물이다.
이 문서는 **Kimaki 세션과 데스크톱(Claude Code / OpenCode / VS Code) 양쪽에서 같은 순서로** 돌리기 위한 절차다.

## 0. 원본 위치 (2026-11-02 기준)

| 항목 | 값 |
|---|---|
| 노트북 | `Books_for_Meds` — `0-7B7300AE98D01EB7!22475` |
| 섹션 1 | `검진 protocol, DDx` — `0-7B7300AE98D01EB7!s1a079557ab70471481fdbff49fec8d91` |
| 섹션 2 | `위내시경 공부` — `0-7B7300AE98D01EB7!s75437d7d6d7f4020a097971997d659be` |
| 섹션 3 | `외래진료 공부, 학회내용 정리...` — `0-7B7300AE98D01EB7!s6fe88e7efc9849e18fd8ebdaf4af4dfd` |

인덱스는 ID가 바뀌지 않지만, 페이지는 새로 만들어질 수 있으므로 **매번 `listPages`로 확인**한다.

## 1. 페이지 → 파일 매핑

| OneNote 페이지 | 섹션 | 대상 파일 | 워크북 |
|---|---|---|---|
| 위내시경 질환 Study | 검진 protocol, DDx | `notes/egd-gerd-barrett.md`, `notes/egd-ugc-cancer.md`, `notes/egd-egc-esd.md` | EGD |
| CFS f/u schedule | 위내시경 공부 | `notes/cfs-surveillance.md` | CFS |
| GI 학회 정리 | 외래진료·학회 | (간내용은 EGD 범위 밖 — 보류) | — |
| EGD, CFS atlas | 위내시경 공부 | 이미지 소스 (텍스트 없음) | EGD/CFS |
| EndoToday guide 1~4 | 위내시경 공부 | 본문 비어 있음 — 채워지면 매핑 추가 | EGD |

새 페이지가 생기면 이 표에 한 줄 추가하고 `notes/pages.json`의 `files` 배열에 파일을 넣는다.

## 2. Kimaki 세션에서 (MCP 직접 사용)

```
1) tools.onenote.listPages(sectionId=…)                    # 페이지 목록·수정일 확인
2) tools.onenote.getPageContent(pageId=…, format="html")   # HTML로 받는다(text는 중복이 심함)
3) 실행 런타임에서 HTML → 마크다운으로 정리해 notes/*.md 로 저장
4) python3 tools/build_notes.py                            # md → egd/conference-notes.html
5) bash tools/build_pdf.sh egd                             # book.html → PDF + 북마크
6) git add -A && git commit && git push
```

HTML을 파일로 떨구지 않고 런타임에서 바로 마크다운으로 바꾸면 컨텍스트를 아낄 수 있다.
파일로 저장했다면 데스크톱과 같은 경로를 쓴다:

```bash
python3 tools/onenote_to_md.py raw/gi.html \
  --out notes/egd-gerd-barrett.md \
  --title "GERD · Reflux Esophagitis · Barrett" \
  --source "OneNote / Books_for_Meds / 검진 protocol, DDx / 위내시경 질환 Study"
```

## 3. 데스크톱에서 (MCP 없이)

OneNote 데스크톱 앱에서 해당 페이지를 **HTML로 내보내기**(파일 → 내보내기 → HTML) 한 뒤 같은 명령을 쓴다.

```bash
python3 tools/onenote_to_md.py ~/Downloads/GI.html --out notes/egd-gerd-barrett.md --title "…"
python3 tools/build_notes.py
bash tools/build_pdf.sh egd
```

## 4. 걸러내는 것 (자동)

`tools/onenote_to_md.py`가 아래를 버린다. 걸러진 뒤에도 이상하면 손으로 지우고 **걸러야 할 패턴을
`DROP_PATTERNS`에 추가**한다.

- 개인 금융: `실손`, `보험`, `연금`, `계좌`, `대출`, `카드값`
- 식별자: `주민등록`, `휴대폰`, `비밀번호`
- 금액 표기: `59,790원` 처럼 숫자+원
- OneNote 중첩 목록이 평탄화되며 생기는 **중복 줄**(정규화 후 첫 등장만 유지)

## 5. 편집 원칙

- **사실은 바꾸지 않는다.** 숫자·용량·분류 기준은 원문 그대로 옮긴다.
- **구조만 바꾼다.** 원문은 평탄한 목록이므로 `##` 섹션 + 표로 재편집해 내시경 판단에 바로 쓰이게 한다.
- 원문에 없는 내용을 채워 넣지 않는다. 빈 곳은 "확인 필요"로 남긴다.
- 약제·적응은 마지막에 최신 가이드라인 확인 문구를 유지한다.

## 6. 검증

```bash
python3 tools/check.py                                   # 장별 이미지·표·퀴즈 무결성
python3 tools/build_notes.py && python3 tools/build_book.py
S=~/.config/opencode/skills/design-craft/scripts
$S/page-check.sh egd/conference-notes.html --width 1440   # 0 HIGH 확인
```

PDF는 `python3 -c "import pymupdf;print(pymupdf.open('downloads/EGD-workbook.pdf').get_toc()[:3])"`로
북마크가 살아 있는지 확인한다.
