#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > loan-rhs-followup.pid
trap 'rc=$?; echo "$rc" > "$root/loan-rhs-followup.exit"' EXIT
ulimit -v 8388608
grep -qx 0 loan-normal-forms.exit
grep -qx 0 loan-affine-factors.exit
test -f loan-normal-forms-20261016/STRUCTURAL_RETURN_ZERO_AUDIT.json
python3 /home/hclau/ecdsa_research/server-preflight.py > loan-rhs-followup-preflight.json
python3 - <<'PY'
import hashlib,shutil
from pathlib import Path
r=Path.cwd();old=r/'evidence-through-finalproof95-endpoint-20261016.tar.gz';source=r/'evidence.tar.gz'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='18e060f60a4e0facc46fd81d847f1832bf344c2edd0801814924e640c6b4bd2b'
if not old.exists():shutil.copy2(source,old)
assert sha(old)==sha(source)
receipt=r/'receipt-through-finalproof95-endpoint-20261016.json'
if not receipt.exists():shutil.copy2(r/'receipt.json',receipt)
PY
python3 collect.py > loan-rhs-followup-collection.log 2>&1
python3 verify_archive.py > loan-rhs-followup-full-verification.log 2>&1
python3 make_followup_incremental.py supplement-loan-dirty-rhs-20261016 > loan-rhs-followup-delivery.log 2>&1
python3 verify_followup_incremental.py evidence-through-repair53-qualification-20261016.tar.gz supplement-repaired67-qualified-20261016.tar.gz supplement-loan-dirty-rhs-20261016.tar.gz > loan-rhs-followup-verification.log 2>&1
