#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/mask-validate-v3.pid
trap 'echo $? > evidence/mask-validate-v3.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/mask-validate-v3.resources
while ! test -f evidence/global-anf-mask-trace.exit; do sleep 5; done
if test "$(cat evidence/global-anf-mask-trace.exit)" != 0; then echo Source_export_not_validated; exit 3; fi
sha256sum tool/target/release/mask_validate tool/src/mask_program.rs tool/src/mask_validate_body.rs mask-reference.py evidence/mr-mask-tip-v3.bin evidence/mr-mask-tip-v3.json ../product-exact-20261015/tip/ops.bin > evidence/mask-validate-v3-before.sha256
python3 mask-reference.py evidence/mr-mask-tip-v3.bin evidence/mr-mask-tip-v3.audit-input-u64le.bin --expected evidence/mr-mask-tip-v3.audit-known-u64le.bin > evidence/mask-reference-audit.json || exit $?
for fixture in audit all-failing-tip sensitivity-structured sensitivity-arbitrary; do
prlimit --as=8589934592 -- tool/target/release/mask_validate ../product-exact-20261015/tip/ops.bin evidence/mr-mask-tip-v3.bin packets/$fixture.tsv > evidence/mask-validate-v3-$fixture.json 2> evidence/mask-validate-v3-$fixture.log || exit $?
done
sha256sum tool/target/release/mask_validate tool/src/mask_program.rs tool/src/mask_validate_body.rs mask-reference.py evidence/mr-mask-tip-v3.bin evidence/mr-mask-tip-v3.json ../product-exact-20261015/tip/ops.bin > evidence/mask-validate-v3-after.sha256
cmp evidence/mask-validate-v3-before.sha256 evidence/mask-validate-v3-after.sha256
