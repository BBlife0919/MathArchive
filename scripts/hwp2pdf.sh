#!/bin/bash
set -e

INDIR="${1:-$HOME/Downloads}"
OUTDIR="${2:-$INDIR}"
PARALLEL="${PARALLEL:-6}"
BATCH="${BATCH:-30}"

PYTHON="/Users/youngwoolee/miniconda3/bin/python"
HWP5ODT="/Users/youngwoolee/miniconda3/bin/hwp5odt"
HWP2ODT_PY="/Users/youngwoolee/MathDB/scripts/hwp2odt_no_validate.py"
SOFFICE="/Applications/LibreOffice.app/Contents/MacOS/soffice"

shopt -s nullglob nocaseglob
FILES=( "$INDIR"/*.hwp )
shopt -u nocaseglob
COUNT=${#FILES[@]}

if [ "$COUNT" -eq 0 ]; then
  echo "No .hwp files in $INDIR"
  exit 0
fi

echo "Converting $COUNT .hwp files  (parallel=$PARALLEL, batch=$BATCH)"
echo "  in:  $INDIR"
echo "  out: $OUTDIR"
mkdir -p "$OUTDIR"

TMPDIR=$(mktemp -d -t hwp2pdf)
ODTDIR="$TMPDIR/odts"
mkdir -p "$ODTDIR"
trap 'rm -rf "$TMPDIR"' EXIT

pkill -9 -f soffice 2>/dev/null || true
sleep 1

convert_hwp_to_odt() {
  local f="$1"
  local base
  base=$(basename "$f")
  base="${base%.*}"
  local odt="$ODTDIR/$base.odt"
  if "$HWP5ODT" --output "$odt" "$f" >/dev/null 2>&1; then
    echo "ODT_OK $base"
  elif "$PYTHON" "$HWP2ODT_PY" "$f" "$odt" >/dev/null 2>&1; then
    echo "ODT_OK $base"
  else
    echo "ODT_FAIL $base"
  fi
}
export -f convert_hwp_to_odt
export HWP5ODT PYTHON HWP2ODT_PY ODTDIR

START=$(date +%s)

echo ""
echo "=== Phase 1: HWP -> ODT (parallel=$PARALLEL) ==="
PHASE1_LOG="$TMPDIR/phase1.log"
printf '%s\n' "${FILES[@]}" | xargs -I{} -P"$PARALLEL" bash -c 'convert_hwp_to_odt "$@"' _ {} > "$PHASE1_LOG" 2>&1
odt_ok=$(grep -c '^ODT_OK ' "$PHASE1_LOG" || true)
odt_fail=$(grep -c '^ODT_FAIL ' "$PHASE1_LOG" || true)
echo "ODT done: OK=$odt_ok FAIL=$odt_fail"
if [ "$odt_fail" -gt 0 ]; then
  echo "Failures:"; grep '^ODT_FAIL ' "$PHASE1_LOG" | head -5
fi

echo ""
echo "=== Phase 2: ODT -> PDF  (batch=$BATCH files per soffice invocation) ==="
shopt -s nullglob
ODTS=( "$ODTDIR"/*.odt )
shopt -u nullglob
ODT_TOTAL=${#ODTS[@]}
PROGRESS=0
BATCH_IDX=0
TMP_BATCH=()
for odt in "${ODTS[@]}"; do
  TMP_BATCH+=("$odt")
  if [ "${#TMP_BATCH[@]}" -ge "$BATCH" ]; then
    BATCH_IDX=$((BATCH_IDX+1))
    "$SOFFICE" --headless --convert-to pdf --outdir "$OUTDIR" "${TMP_BATCH[@]}" >/dev/null 2>&1 || true
    PROGRESS=$((PROGRESS + ${#TMP_BATCH[@]}))
    echo "  batch $BATCH_IDX done ($PROGRESS/$ODT_TOTAL)"
    TMP_BATCH=()
  fi
done
if [ "${#TMP_BATCH[@]}" -gt 0 ]; then
  BATCH_IDX=$((BATCH_IDX+1))
  "$SOFFICE" --headless --convert-to pdf --outdir "$OUTDIR" "${TMP_BATCH[@]}" >/dev/null 2>&1 || true
  PROGRESS=$((PROGRESS + ${#TMP_BATCH[@]}))
  echo "  batch $BATCH_IDX done ($PROGRESS/$ODT_TOTAL)"
fi

END=$(date +%s)

shopt -s nullglob
PDFS=( "$OUTDIR"/*.pdf )
shopt -u nullglob
echo ""
echo "Done in $((END-START))s. ODT_OK=$odt_ok ODT_FAIL=$odt_fail PDF_COUNT=${#PDFS[@]}"
echo "Output: $OUTDIR"
