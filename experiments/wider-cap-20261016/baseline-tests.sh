#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/wider-cap-20261016
cd "$root"
echo $$ > baseline-tests.pid
trap 'rc=$?; echo "$rc" > "$root/baseline-tests.exit"' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > baseline-tests-preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
export CARGO_TARGET_DIR="$root/target"
git -C /home/hclau/ecdsa_research/toffoli worktree add --detach "$root/parent-tests" 5a7c390233c72133df9b591c92e43422c5892142 > baseline-worktree.log 2>&1
cd parent-tests
set +e
cargo test --release --locked --offline --bin build_circuit -- --test-threads=1 > "$root/parent-all-tests.log" 2>&1
rc=$?
set -e
echo "$rc" > "$root/parent-all-tests.exit"
python3 - "$root" <<'PY'
import json,re,sys
from pathlib import Path
r=Path(sys.argv[1]);sets=[]
for name in ['parent-all-tests.log','cap1792-tests.log']:
 s=(r/name).read_text();m=re.search(r'^failures:\n(.*?)\n\ntest result:',s,re.M|re.S)
 assert m,name
 sets.append(sorted(x.strip() for x in m[1].splitlines() if x.strip()))
d={'parent_failed_tests':sets[0],'cap1792_failed_tests':sets[1],'same_failed_test_names':sets[0]==sets[1],'status':'DIAGNOSTIC_NATIVE_FAILURE_COMPARISON_NOT_A_SCORE'}
(r/'native-baseline-comparison.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
PY
