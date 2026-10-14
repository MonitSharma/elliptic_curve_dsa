#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/column-pair-attested.exit' EXIT
ulimit -v 8388608
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/column-pair-attested-preflight.json
base_binary=column-base-v3/target/release/qubit_column_probe_column_base_v3
compact_binary=column-compact-v3/target/release/qubit_column_probe_column_compact_v3
test -x "$base_binary"
test -x "$compact_binary"
sha256sum "$base_binary" "$compact_binary" column-base-v3/src/main.rs column-compact-v3/src/main.rs
/usr/bin/time -v "$base_binary" 0xe1a14a46e6340fd02bde43002b9b85d32649195df078b8aa7efe88ce0964f802 36 35 evidence/column-base-attested-states > evidence/column-base-attested.log 2>&1
/usr/bin/time -v "$compact_binary" 0xe1a14a46e6340fd02bde43002b9b85d32649195df078b8aa7efe88ce0964f802 36 35 evidence/column-compact-attested-states > evidence/column-compact-attested.log 2>&1
python3 - <<'PY'
from pathlib import Path
import hashlib,json
root=Path('evidence')
attestations={}
for variant in ['base','compact']:
    lines=root.joinpath(f'column-{variant}-attested.log').read_text().splitlines()
    attestations[variant]=json.loads(next(s.removeprefix('PROBE_ATTESTATION ') for s in lines if s.startswith('PROBE_ATTESTATION ')))
    assert attestations[variant]['source_variant']==variant
    for f,sha in attestations[variant]['source_sha256'].items():
        assert hashlib.sha256(Path(variant,f).read_bytes()).hexdigest()==sha
stages=[]
for p in sorted(root.joinpath('column-base-attested-states').glob('stage-*.txt'),key=lambda p:int(p.stem.split('-')[1])):
    compact=root/'column-compact-attested-states'/p.name
    a,b=p.read_text().splitlines(),compact.read_text().splitlines()
    assert len(a)==len(b)==693
    stages.append({'stage':int(p.stem.split('-')[1]),'differing_qubit_ids':[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]})
report={'scope':'Attested single native HR column, no payload; no official score','attestations':attestations,'stages':stages}
root.joinpath('column-state-comparison-attested.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
PY
date -u
