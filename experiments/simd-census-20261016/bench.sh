#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/simd-census-20261016
echo $$ > bench.pid
trap 'rc=$?; echo "$rc" > bench.exit' EXIT
test "$(cat run.exit)" = 0
python3 /home/hclau/ecdsa_research/server-preflight.py > bench-preflight.json
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 33554432
exe=tool/target/release/product_paired_diagnostic
parent=/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin
"$exe" "$parent" simd-census-validation-20261016 17 11 3 partial.jsonl 11 > partial.out 2> partial.err
/home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census "$parent" simd-census-validation-20261016 17 11 3 partial-reference.jsonl > partial-reference.out 2> partial-reference.err
cmp partial.jsonl partial-reference.jsonl
"$exe" "$parent" simd-census-validation-20261016 0 4096 4 bench4096.jsonl 0 > bench4096.out 2> bench4096.err
python3 - <<'PY'
from pathlib import Path
import json
root=Path.cwd()
rows=[json.loads(x) for x in (root/'bench4096.jsonl').read_text().splitlines()]
assert [r['batch'] for r in rows]==list(range(4096))
reference=[json.loads(x) for x in (root/'tip-reference.jsonl').read_text().splitlines()]
assert rows[:128]==reference
out={'status':'exact_research_census_validation_only_not_a_score','batches':4096,'shots':262144,'same_first128_reference_rows':True,'all_full_state_and_T_verified_batches_across_sources':128,'partial_first17_count11_workers3_reference_match':True,'failed_batches':sum(bool(r['failures']) for r in rows),'dirty_shots':sum(r['dirty_shots'] for r in rows),'mean_executed_Toffoli':sum(r['toffoli'] for r in rows)/262144}
(root/'validation-summary.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
PY
