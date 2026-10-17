#!/usr/bin/env bash
# WIDE95: ascending exact nonce screen from 1 (lowest pass), set TAIL_NONCE, unchanged benchmark.
# Runs only if the declared gate verdict against the official Toffoli record is PASS. Queue only.
set -euo pipefail
root=/home/hclau/ecdsa_research/wide95-native-20261017
cd "$root"
echo $$ > search.pid
trap 'rc=$?; echo "$rc" > "$root/search.exit"' EXIT
python3 - <<'PY'
import json
g=json.load(open('/home/hclau/ecdsa_research/wide95-native-20261017/GATE.json'))
v=g['verdicts']['official_toffoli_record_1d8c05ee']
assert v['status']=='FAILURE_GATE_PASS' and all(v['rules'].values()), v['status']
PY
echo "7c0ac9588dbf3aa90967315923778c9b3ccb954aae34bb71fc6c7bb970523109  candidate/ops.bin" | sha256sum -c
mkdir -p evidence
cp candidate/ops.bin evidence/frozen-ops.bin
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/screen-preflight.json
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 50331648
/usr/bin/time -v /home/hclau/ecdsa_research/nonce-screen-20261015/screen/target/release/nonce_screen evidence/frozen-ops.bin 1 20000 16 evidence/screen.jsonl > evidence/screen.out 2> evidence/screen.err
python3 select.py > evidence/select.log 2>&1
cd candidate
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/evidence/benchmark-preflight.json"
set +e
/usr/bin/time -v ./benchmark.sh > "$root/evidence/benchmark.log" 2>&1
rc=$?
set -e
echo "$rc" > "$root/evidence/benchmark.exit"
if test -f results.tsv; then cp results.tsv "$root/evidence/benchmark-results.tsv"; fi
git restore --source=HEAD -- results.tsv
test "$rc" = 0
cp score.json "$root/evidence/score.json"
cd "$root"
python3 verify-final.py > evidence/verify-final.log 2>&1
