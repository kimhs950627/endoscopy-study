#!/usr/bin/env bash
# Rebuild everything that must stay in sync with the notes:
#   notes/*.md  →  egd|confs html  →  egd/book.html  →  downloads/*.pdf (with bookmarks)
#
# Usage: bash tools/build_pdf.sh [egd|cfs|all]
set -euo pipefail
cd "$(dirname "$0")/.."

TARGET="${1:-all}"

echo "→ notes → 페이지 (cfs 추적 간격 등)"
python3 tools/build_notes.py

echo "→ 학회노트를 각 질환 절 안에 삽입"
( cd tools && python3 apply_notes.py )

echo "→ 증례 장 재생성"
python3 tools/build_cases.py

echo "→ 질환 서브탭 재생성"
python3 tools/build_nav.py

echo "→ chapters → book.html"
python3 tools/build_book.py

render() {  # $1 = html path (relative), $2 = pdf output (relative)
  local html="$1" pdf="$2"
  local chrome="${CHROME:-}"
  if [ -z "$chrome" ]; then
    if [ -x "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" ]; then
      chrome="/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
    else
      chrome="$(command -v google-chrome || command -v chromium || command -v chromium-browser || true)"
    fi
  fi
  [ -n "$chrome" ] || { echo "no chrome found; set CHROME=/path/to/chrome" >&2; return 1; }

  rm -f "$pdf"
  if [[ "$chrome" == *.exe ]]; then
    local win_html win_pdf
    win_html="$(wslpath -w "$PWD/$html")"
    win_pdf="$(wslpath -w "$PWD/$pdf")"
    "$chrome" --headless=new --disable-gpu --no-pdf-header-footer \
      --virtual-time-budget=20000 --print-to-pdf="$win_pdf" "file:///${win_html//\\//}" >/dev/null 2>&1
  else
    "$chrome" --headless=new --disable-gpu --no-pdf-header-footer \
      --virtual-time-budget=20000 --print-to-pdf="$PWD/$pdf" "file://$PWD/$html" >/dev/null 2>&1
  fi
  [ -f "$pdf" ] || { echo "PDF was not produced: $pdf" >&2; return 1; }
  echo "  printed $(du -h "$pdf" | cut -f1) → $pdf"
}

case "$TARGET" in
  egd|all)
    echo "→ egd/book.html → downloads/EGD-workbook.pdf"
    render egd/book.html downloads/EGD-workbook.pdf
    echo "→ bookmarks"
    python3 tools/add_outline.py downloads/EGD-workbook.pdf egd/book.html /tmp/opencode/EGD-outline.pdf
    mv /tmp/opencode/EGD-outline.pdf downloads/EGD-workbook.pdf
    ;;
esac

case "$TARGET" in
  cfs)
    echo "CFS 워크북은 아직 조립 전이라 PDF가 없다 (cfs/index.html 참고)." ;;
esac

echo "done."
