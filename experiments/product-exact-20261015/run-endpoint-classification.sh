#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > endpoint-classification.pid
trap 'rc=$?; echo "$rc" > "$root/endpoint-classification.exit"' EXIT
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=2 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export CACHE_ATOM_CAP=1024 CACHE_PRODUCT_CAP=1000000 ANF_PAIR_CAP=64
ulimit -v 25165824
python3 /home/hclau/ecdsa_research/server-preflight.py > endpoint-classification-preflight.json
python3 prepare_endpoint_classification.py > endpoint-classification-prepare.log 2>&1
out=endpoint-classification-20261016
export CARGO_TARGET_DIR="$root/target-endpoint-census"
cargo test --manifest-path endpoint-classification-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic endpoint_census -- --test-threads=1 > "$out/native-tests.log" 2>&1
cargo build --manifest-path endpoint-classification-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic > "$out/build.log" 2>&1
python3 - <<'PY'
import hashlib,json,os,subprocess
from pathlib import Path
r=Path.cwd();d=r/'endpoint-classification-20261016';p=json.loads((d/'DECLARATION.json').read_text());stream=r/p['stream'];sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();assert sha(stream)==p['stream_sha256']
with(d/'analysis.log').open('w')as log:rc=subprocess.run(['timeout','7200','/usr/bin/time','-v','taskset','-c',str(max(os.sched_getaffinity(0))),str(r/'target-endpoint-census/release/product_paired_diagnostic'),str(stream)],stdout=log,stderr=subprocess.STDOUT).returncode
(d/'analysis.exit').write_text(str(rc)+'\n');assert rc==0;assert sha(stream)==p['stream_sha256'];text=(d/'analysis.log').read_text();assert 'ENDPOINT_CLASSIFICATION ' in text and 'SOURCE_ENDPOINT_CENSUS_COMPLETE' in text;assert not list(d.glob('*.bin'))
(d/'RESULTS.json').write_text(json.dumps(dict(status='READ_ONLY_ENDPOINT_CLASSIFICATION_COMPLETE_NO_CANDIDATE',stream_sha256=p['stream_sha256'],analysis_log_sha256=sha(d/'analysis.log'),executable_sha256=sha(r/'target-endpoint-census/release/product_paired_diagnostic'),emits_stream=False,sampled_inputs=0,summary_lines=[x for x in text.splitlines() if x.startswith(('ENDPOINT_CLASSIFICATION ','SOURCE_ENDPOINT_CENSUS_COMPLETE'))]),indent=2)+'\n')
PY
