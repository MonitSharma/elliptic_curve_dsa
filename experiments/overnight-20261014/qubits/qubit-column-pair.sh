#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
mkdir -p evidence
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/column-pair.exit' EXIT
ulimit -v 8388608
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/column-pair-preflight.json
python3 qubit-create-column-probe.py base base column-base-v2
python3 qubit-create-column-probe.py compact base column-compact-v2
sha256sum evidence/compact-packet.tsv base/src/point_add/midg.rs compact/src/point_add/midg.rs column-base-v2/src/main.rs column-compact-v2/src/main.rs
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/qubits/column-base/target
cargo +1.93.0 build --release --offline --manifest-path column-base-v2/Cargo.toml
sha256sum column-base/target/release/qubit_column_probe_column_base_v2
/usr/bin/time -v column-base/target/release/qubit_column_probe_column_base_v2 0xe1a14a46e6340fd02bde43002b9b85d32649195df078b8aa7efe88ce0964f802 36 35 evidence/column-base-v2-states > evidence/column-base-v2.log 2>&1
cargo +1.93.0 build --release --offline --manifest-path column-compact-v2/Cargo.toml
sha256sum column-base/target/release/qubit_column_probe_column_compact_v2
/usr/bin/time -v column-base/target/release/qubit_column_probe_column_compact_v2 0xe1a14a46e6340fd02bde43002b9b85d32649195df078b8aa7efe88ce0964f802 36 35 evidence/column-compact-v2-states > evidence/column-compact-v2.log 2>&1
python3 - <<'PY'
from pathlib import Path
import json
root=Path('evidence')
stages=[]
for p in sorted(root.joinpath('column-base-v2-states').glob('stage-*.txt'),key=lambda p:int(p.stem.split('-')[1])):
    compact=root/'column-compact-v2-states'/p.name
    a,b=p.read_text().splitlines(),compact.read_text().splitlines()
    stages.append({'stage':int(p.stem.split('-')[1]),'differing_qubit_ids':[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]})
report={'scope':'One native HR column, no payload; no official score','stages':stages}
root.joinpath('column-state-comparison-v2.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
PY
date -u
