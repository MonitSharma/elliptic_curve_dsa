#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/width-terminal-recheck.pid
trap 'echo $? > evidence/width-terminal-recheck.exit' EXIT
export OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1
sha256sum ../product-exact-20261015/tip/ops.bin tool/target/release/width_contract_audit tool/target/release/width_affine_audit > evidence/width-terminal-recheck-before.sha256
prlimit --as=8589934592 -- tool/target/release/width_contract_audit ../product-exact-20261015/tip/ops.bin > evidence/width-contract-recheck.json || exit $?
cmp evidence/width-contract-tip.json evidence/width-contract-recheck.json || exit $?
prlimit --as=8589934592 -- tool/target/release/width_affine_audit ../product-exact-20261015/tip/ops.bin > evidence/width-affine-recheck.json 2> evidence/width-affine-recheck.log || exit $?
cmp evidence/width-affine-tip.json evidence/width-affine-recheck.json || exit $?
sha256sum ../product-exact-20261015/tip/ops.bin tool/target/release/width_contract_audit tool/target/release/width_affine_audit > evidence/width-terminal-recheck-after.sha256
cmp evidence/width-terminal-recheck-before.sha256 evidence/width-terminal-recheck-after.sha256
