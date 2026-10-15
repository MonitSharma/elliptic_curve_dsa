#!/usr/bin/env bash
# Unchanged official benchmark, normal Vec build, protected promoted-base files.
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
PACKAGE="$ROOT/clean-replay-v6-binary"
cd "$ROOT"
echo "$$" > "$ROOT/normal-benchmark-v6.pid"
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/q692_readiness_20261015/normal-benchmark-v6.exit' EXIT
exec 9> /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/sole-large-evaluator.lock
flock -n 9
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL FROGDROP_CK F1_PROFILE CARGO_TARGET_DIR ZSTD_LEVEL
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > "$ROOT/normal-benchmark-v6-preflight.json"
python3 - <<'PY'
from pathlib import Path
import hashlib,json,re,subprocess
r=Path('/home/hclau/ecdsa_research/q692_readiness_20261015');p=r/'clean-replay-v6-binary'
log=(r/'counter-control-fold-v6.log').read_text(encoding='utf8')
q,t,n,width=map(int,re.findall(r'LOWQ_EXACT_STREAM Q=(\d+) T=(\d+) N=(\d+) width=(\d+)',log)[-1])
assert q==width==692
assert n*56<=112_000_000_000,('Refuse normal launch: insufficient runner memory margin',n)
assert n<2**31,('Refuse normal launch: next Vec capacity exceeds runner limit',n)
available=int(next(x.split()[1]for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))*1024
assert available>=190_000_000_000,('Refuse launch until sufficient server memory is free',available)
m=json.loads((r/'package-v6-evidence/package-manifest.json').read_text(encoding='utf8'))
assert subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip()==m['base_revision']
for name,h in m['source_sha256'].items():assert hashlib.sha256((p/name).read_bytes()).hexdigest()==h,name
for e in m['protected_files']:assert hashlib.sha256((p/e['path']).read_bytes()).hexdigest()==e['sha256'],e['path']
receipt=dict(source='pristine promoted-base patch replay',base_revision=m['base_revision'],patch_sha256=m['patch_sha256'],tree_sha=m['tree_sha'],normal_stream_env_unset=True,expected_physical_ops=n,diagnostic_emitted_toffoli=t,expected_qubits=q,op_vector_bytes=n*56,max_virtual_bytes=128_000_000_000,server_available_bytes=available,scope='launch authorization receipt; no score or correctness claim')
(r/'normal-benchmark-v6-launch.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8');print(json.dumps(receipt,indent=2))
PY
# Hard bound applies to compiler, builder and evaluator; it cannot consume the
# large server's extra memory to conceal a runner-incompatible candidate.
ulimit -v 125000000
cd "$PACKAGE"
/usr/bin/time -v ./benchmark.sh --note "Q692 exact predicate factoring; pristine current-base replay; normal build; unchanged benchmark" > "$ROOT/normal-benchmark-v6-official.log" 2>&1
sha256sum ops.bin score.json > "$ROOT/normal-benchmark-v6-artifacts.sha256"
cp score.json "$ROOT/normal-benchmark-v6-score.json"
date -u
