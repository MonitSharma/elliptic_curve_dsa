#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
candidate="$root/product-b3-baseline"
evidence="$root/coordinator-b3-reference-eval"
binary="$root/coordinator-b3-classical-evidence/target/release/eval_circuit"
mkdir -p "$evidence/run"
trap 'code=$?; printf "%s\n" "$code" > "$evidence/run.exit"; python3 "$root/research-receipt.py" "$candidate" "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit" --stream "$evidence/run/ops.bin" --score "$evidence/run/score.json" --full-benchmark' EXIT
ulimit -v 16777216
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py
python3 - "$root" "$candidate" <<'PY'
import hashlib,json,subprocess,sys
from pathlib import Path
root,base=map(Path,sys.argv[1:])
assert subprocess.check_output(['git','-C',str(base),'rev-parse','HEAD'],text=True).strip()=='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
assert not subprocess.check_output(['git','-C',str(base),'status','--porcelain'],text=True).strip()
binding=json.loads((root/'coordinator-b3-classical-evidence/source-binding.json').read_text())
for name,digest in binding['protected_sha256'].items():
 assert hashlib.sha256((base/name).read_bytes()).hexdigest()==digest,name
 assert (base/name).read_bytes()==subprocess.check_output(['git','-C',str(base),'show','HEAD:'+name]),name
stream=root/'product-evidence/b3-baseline/run/ops.bin'
assert hashlib.sha256(stream.read_bytes()).hexdigest()=='0f10de57f45349c89163faf6e5ab0694aec3d3bfa720f10ee8b185a9fb2914ce'
PY
sha256sum "$binary" "$root/server-b3-reference-eval.sh" > "$evidence/evaluator-launcher.sha256"
cd "$evidence/run"
test ! -e ops.bin && test ! -e results.tsv && test ! -e score.json
ln -s "$root/product-evidence/b3-baseline/run/ops.bin" ops.bin
/usr/bin/time -v "$binary" --note 'Clean unchanged B3 public baseline reproduction; sourcehash0f10de57; no candidate modifications'
date -u
