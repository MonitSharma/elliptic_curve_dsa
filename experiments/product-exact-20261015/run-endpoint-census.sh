#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=endpoint-source-census-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=2 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export CACHE_ATOM_CAP=1024 CACHE_PRODUCT_CAP=1000000 ANF_PAIR_CAP=64
ulimit -v 25165824
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/build-preflight.json"
python3 prepare_endpoint_census.py > "$out/prepare.log" 2>&1
export CARGO_TARGET_DIR="$root/target-endpoint-census"
cargo test --manifest-path endpoint-census-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic endpoint_census -- --test-threads=1 > "$out/endpoint-native-tests.log" 2>&1
cargo test --manifest-path endpoint-census-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic interned_anf_retained -- --test-threads=1 > "$out/kernel-native-tests.log" 2>&1
cargo build --manifest-path endpoint-census-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic > "$out/build.log" 2>&1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/run-preflight.json"
python3 - <<'PY'
import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();d=r/'endpoint-source-census-20261016';p=json.loads((d/'DECLARATION.json').read_text());stream=r/p['stream']
assert hashlib.sha256(stream.read_bytes()).hexdigest()==p['stream_sha256']
cpu=subprocess.check_output(['python3','-c','import os; print(max(os.sched_getaffinity(0)))'],text=True).strip()
with (d/'analysis.log').open('w') as log:
 rc=subprocess.run(['timeout','7200','/usr/bin/time','-v','taskset','-c',cpu,str(r/'target-endpoint-census/release/product_paired_diagnostic'),str(stream)],stdout=log,stderr=subprocess.STDOUT).returncode
(d/'analysis.exit').write_text(str(rc)+'\n');assert rc==0
assert hashlib.sha256(stream.read_bytes()).hexdigest()==p['stream_sha256']
text=(d/'analysis.log').read_text();assert 'SOURCE_ENDPOINT_CENSUS_COMPLETE' in text
assert not list(d.glob('*.bin'))
(d/'RESULTS.json').write_text(json.dumps(dict(status='COMPLETE_SOURCE_ONLY_CENSUS_NO_CANDIDATE',stream_sha256=p['stream_sha256'],analysis_log_sha256=hashlib.sha256((d/'analysis.log').read_bytes()).hexdigest(),executable_sha256=hashlib.sha256((r/'target-endpoint-census/release/product_paired_diagnostic').read_bytes()).hexdigest(),emits_stream=False,sampled_inputs=0,scope='Recovered endpoints are source proof leads only; no donor allocation, rewritten circuit, numerical Toffoli mean, failure gate or record is claimed. Existing simplifier counts include unreachable guards and are structural only.'),indent=2)+'\n')
PY
