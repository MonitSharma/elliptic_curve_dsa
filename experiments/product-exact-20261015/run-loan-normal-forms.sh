#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > loan-normal-forms.pid
trap 'rc=$?; echo "$rc" > "$root/loan-normal-forms.exit"' EXIT
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 25165824
python3 /home/hclau/ecdsa_research/server-preflight.py > loan-normal-forms-preflight.json
python3 prepare_loan_normal_forms.py > loan-normal-forms-prepare.log 2>&1
export CARGO_TARGET_DIR="$root/target-endpoint-census"
cargo test --manifest-path loan-normal-forms-tool/Cargo.toml --release --locked --offline --bin value_prefilter dirty_rhs_tests -- --test-threads=1 > loan-normal-forms-20261016/native-tests.log 2>&1
cargo build --manifest-path loan-normal-forms-tool/Cargo.toml --release --locked --offline --bin value_prefilter > loan-normal-forms-20261016/build.log 2>&1
python3 - <<'PY'
import hashlib,json,os,subprocess
from pathlib import Path
r=Path.cwd();d=r/'loan-normal-forms-20261016';p=json.loads((d/'DECLARATION.json').read_text());s=r/p['stream'];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();assert sha(s)==p['stream_sha256']
with(d/'analysis.log').open('w')as out:rc=subprocess.run(['timeout','1800','/usr/bin/time','-v','taskset','-c',str(max(os.sched_getaffinity(0))),str(r/'target-endpoint-census/release/value_prefilter'),str(s),str(d/'n2-loan-family.json')],stdout=out,stderr=subprocess.STDOUT).returncode
(d/'analysis.exit').write_text(str(rc)+'\n');assert rc==0 and sha(s)==p['stream_sha256'];rows=[json.loads(x)for x in(d/'analysis.log').read_text().splitlines()if x.startswith('{')];assert len(rows)==2 and all(len(x['result']['query_rows'])==8 for x in rows)
(d/'RESULTS.json').write_text(json.dumps(dict(status='COMPLETE_SOURCE_ONLY_DIRTY_RHS_QUERIES_NO_CANDIDATE',rows=rows,stream_sha256=p['stream_sha256'],executable_sha256=sha(r/'target-endpoint-census/release/value_prefilter'),sampled_inputs=0,emits_stream=False),indent=2)+'\n')
PY
