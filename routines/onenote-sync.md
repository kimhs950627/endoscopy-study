---
title: OneNote 학회노트 매일 동기화
description: >
  Managed by a kimaki routine. Do not move or delete this file
  without also updating the routine (kimaki routine list / kimaki routine edit).
---

매일 03:00 KST. `tools/sync-onenote.md` 절차대로 OneNote 학회노트를 워크북에 반영한다.

## 할 일

1. `tools/sync-onenote.md`를 읽고 §0·§1 매핑을 확인한다.
2. OneNote MCP로 아래 섹션의 페이지 목록과 수정일을 확인한다.
   - `검진 protocol, DDx` — `위내시경 질환 Study` (핵심)
   - `위내시경 공부` — `CFS f/u schedule`, `EndoToday guide 1~4`
   - `외래진료 공부, 학회내용 정리...` — `GI 학회 정리` (간 내용은 EGD 범위 밖이라 보류)
3. **마지막 동기화 이후 수정된 페이지만** `getPageContent(format="html")`로 읽는다.
   `notes/*.md`의 front-matter `updated:`와 페이지 Modified를 비교한다.
4. 바뀐 내용이 있으면 해당 `notes/egd-*.md`를 갱신한다. 사실은 그대로, 구조만 재편집.
   개인 금융·식별자·금액은 넣지 않는다.
5. `bash tools/build_pdf.sh egd` 실행 (노트 삽입 → 서브탭 → 합본 → PDF → 북마크).
6. `python3 tools/check.py` 로 무결성 확인.
7. 변경이 있으면 커밋·푸시. 커밋 메시지 끝에 이 스레드 링크를 붙인다.

## 규칙

- **바뀐 것이 없으면 아무 것도 커밋하지 않는다.** 그 경우 한 줄 요약만 남기고 종료.
- 새 주제가 생기면 `notes/notes.map.json`에 삽입 위치(h2)를 반드시 함께 추가한다.
- 원문에 없는 내용은 쓰지 않는다. 불확실하면 "확인 필요"로 남긴다.
- 빌드가 실패하면(크롬 없음, PDF 미생성) 실패 사실과 로그 마지막 10줄을 보고하고 멈춘다.
- 사용자에게 알릴 만한 새 사실(새 가이드라인, 처방 변경)이 있으면 완료 후 멘션한다.
