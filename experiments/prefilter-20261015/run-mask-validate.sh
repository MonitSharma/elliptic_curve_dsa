#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/mask-validate.pid
trap 'echo $? > evidence/mask-validate.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/mask-validate.resources
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin mask_validate -- --nocapture > evidence/mask-validate.tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin mask_validate > evidence/mask-validate.build.log 2>&1 || exit $?
while ! test -f evidence/global-anf-mask-export.exit; do sleep 5; done
if test "$(cat evidence/global-anf-mask-export.exit)" != 0; then echo Source_export_not_validated; exit 3; fi
sha256sum tool/target/release/mask_validate tool/src/mask_program.rs tool/src/mask_validate_body.rs mask-reference.py evidence/mr-mask-tip-v1.bin evidence/mr-mask-tip-v1.json ../product-exact-20261015/tip/ops.bin > evidence/mask-validate-before.sha256
python3 mask-reference.py evidence/mr-mask-tip-v1.bin evidence/mr-mask-tip-v1.audit-input-u64le.bin --expected evidence/mr-mask-tip-v1.audit-known-u64le.bin > evidence/mask-reference-audit.json || exit $?
for fixture in audit all-failing-tip sensitivity-structured sensitivity-arbitrary; do
prlimit --as=8589934592 -- tool/target/release/mask_validate ../product-exact-20261015/tip/ops.bin evidence/mr-mask-tip-v1.bin packets/$fixture.tsv > evidence/mask-validate-$fixture.json 2> evidence/mask-validate-$fixture.log || exit $?
done
sha256sum tool/target/release/mask_validate tool/src/mask_program.rs tool/src/mask_validate_body.rs mask-reference.py evidence/mr-mask-tip-v1.bin evidence/mr-mask-tip-v1.json ../product-exact-20261015/tip/ops.bin > evidence/mask-validate-after.sha256
cmp evidence/mask-validate-before.sha256 evidence/mask-validate-after.sha256
