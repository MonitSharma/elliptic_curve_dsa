#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > endpoint-proposals.pid
trap 'rc=$?; echo "$rc" > "$root/endpoint-proposals.exit"' EXIT
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=2 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export CACHE_ATOM_CAP=1024 CACHE_PRODUCT_CAP=1000000 ANF_PAIR_CAP=64 CACHE_SPLIT=1 CACHE_RANK=density
ulimit -v 25165824
python3 /home/hclau/ecdsa_research/server-preflight.py > endpoint-proposals-preflight.json
python3 prepare_endpoint_proposals.py > endpoint-proposals-prepare.log 2>&1
out=endpoint-proposals-20261016
export CARGO_TARGET_DIR="$root/target-endpoint-census"
cargo test --manifest-path endpoint-proposals-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic global_tag_tests -- --test-threads=1 > "$out/tag-native-tests.log" 2>&1
cargo build --manifest-path endpoint-proposals-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic > "$out/build.log" 2>&1
python3 - <<'PY'
import hashlib,json,os,subprocess
from pathlib import Path
r=Path.cwd();d=r/'endpoint-proposals-20261016';p=json.loads((d/'DECLARATION.json').read_text());stream=r/p['stream'];sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();assert sha(stream)==p['stream_sha256']
with(d/'analysis.log').open('w')as log:rc=subprocess.run(['timeout','7200','/usr/bin/time','-v','taskset','-c',str(max(os.sched_getaffinity(0))),str(r/'target-endpoint-census/release/product_paired_diagnostic'),str(stream)],stdout=log,stderr=subprocess.STDOUT).returncode
(d/'analysis.exit').write_text(str(rc)+'\n');assert rc==0;assert sha(stream)==p['stream_sha256'];text=(d/'analysis.log').read_text();assert 'ENDPOINT_PROPOSAL_ONLY ' in text and 'ENDPOINT_WITHIN_PASS ' in text;assert not list(d.glob('*.bin'))
(d/'RESULTS.json').write_text(json.dumps(dict(status='SOURCE_ONLY_ENDPOINT_DONOR_FEASIBILITY_COMPLETE_NO_CANDIDATE',stream_sha256=p['stream_sha256'],analysis_log_sha256=sha(d/'analysis.log'),executable_sha256=sha(r/'target-endpoint-census/release/product_paired_diagnostic'),emits_stream=False,sampled_inputs=0,summary_lines=[x for x in text.splitlines() if x.startswith(('ENDPOINT_WITHIN_PASS ','LAZY_SUMMARY ','ENDPOINT_PROPOSAL_ONLY '))]),indent=2)+'\n')
PY
