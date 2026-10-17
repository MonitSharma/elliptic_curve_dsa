#!/bin/bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product179-native-20261017
cd "$root"
echo $$ > run.pid
trap 'echo $? > /home/hclau/ecdsa_research/product179-native-20261017/run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 prepare.py > prepare.log 2>&1
cd candidate
cargo test --release --locked --offline --bin build_circuit frozen_cache_product179::tests -- --test-threads=1 > ../native-tests.log 2>&1
cargo build --release --locked --offline --bin build_circuit > ../build.log 2>&1
/usr/bin/time -v ./target/release/build_circuit > ../generate.log 2>&1
sha256sum ops.bin > ../ops.sha256
cd "$root"
python3 - <<'PY'
import hashlib,json
from pathlib import Path
d=json.loads(Path('DECLARATION.json').read_text())
got=Path('ops.sha256').read_text().split()[0]
ok=got==d['expected_normal_generated_stream_sha256']
Path('NATIVE_IDENTITY.json').write_text(json.dumps({'status':'NATIVE_BYTE_IDENTITY_PASS' if ok else 'NATIVE_BYTE_IDENTITY_FAIL','generated':got,'expected':d['expected_normal_generated_stream_sha256']},indent=2)+'\n')
print('OK' if ok else 'FAIL')
PY
