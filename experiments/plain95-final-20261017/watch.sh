#!/usr/bin/env bash
# Wait for the PRODUCT95 search to end; on a pass, audit every lower nonce and finalize.
# Lightweight: one check every 10 minutes. Queue mode: never submits.
set -uo pipefail
r=/home/hclau/ecdsa_research/plain95-final-20261017
s=/home/hclau/ecdsa_research/plain95-operational-20261017
cd "$r"; echo $$ > watch.pid
log() { echo "$(date -Is) $*" >> "$r/watch.log"; }
log "watching $s"
while [ ! -e "$s/run-record.json" ]; do sleep 60; done
python3 - "$s" "$r" <<'PY'
import json,sys
from pathlib import Path
s,r=Path(sys.argv[1]),Path(sys.argv[2])
run=json.loads((s/'run-record.json').read_text())
b=r/'BINDING.json'
if not b.exists():b.write_text(json.dumps({'acceptance_sha256':run['acceptance_sha256'],'executable_sha256':run['executable_sha256'],'candidate_sha256':run['candidate_sha256'],'started_utc':run['started_utc'],'source':'run-record.json at search launch'},indent=2)+chr(10))
PY
log "search launched; binding written"
while [ ! -e "$s/search.exit" ]; do sleep 600; done
log "search.exit=$(cat "$s/search.exit")"
status=$(python3 -c "import json;print(json.load(open('$s/RESULT.json'))['status'])" 2>/dev/null || echo MISSING_RESULT)
log "search status $status"
if [ "$status" != "PASS_AWAITS_COMPLETE_LOG_AUDIT_AND_UNCHANGED_BENCHMARK" ]; then
  echo "{\"status\":\"NO_FINALIZATION\",\"search_status\":\"$status\"}" > "$r/WATCH_RESULT.json"; log done; exit 0
fi
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > terminal-audit-preflight.json
if ! python3 "$r/audit-terminal.py" "$s" "$r/ROOT_TERMINAL_AUDIT.json" > "$r/terminal-audit.log" 2>&1; then
  echo '{"status":"TERMINAL_AUDIT_FAILED"}' > "$r/WATCH_RESULT.json"; log "audit failed"; exit 1
fi
log "audit passed; finalizing"
bash "$r/run-final.sh"; code=$?
log "run-final exit $code"
python3 - "$r" "$code" <<'EOF'
import json, sys
from pathlib import Path
r, code = Path(sys.argv[1]), int(sys.argv[2])
b = r / "BENCHMARK_RESULT.json"
res = json.loads(b.read_text()) if b.exists() else None
(r / "WATCH_RESULT.json").write_text(json.dumps({
    "status": "READY_FOR_USER_REVIEW" if code == 0 and res and res.get("beats_public_product_record") else "FINALIZATION_INCOMPLETE_OR_NOT_A_RECORD",
    "run_final_exit": code, "benchmark": res, "submission_mode": "queue"}, indent=2) + "\n")
EOF
log done
