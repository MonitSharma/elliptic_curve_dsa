#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/mask-validate-transfer.pid
trap 'echo $? > evidence/mask-validate-transfer.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/mask-validate-transfer.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -30 >> evidence/mask-validate-transfer.resources
available=$(awk '/MemAvailable:/{print $2}' /proc/meminfo)
if test "$available" -lt 120000000; then exit 2; fi
printf '%s  %s\n' 180af069679ffa33b099b200d3337d6fc6c20a451a72508a40dea6617150dc64 ../product-exact-20261015/candidate-product-final25/ops.bin 2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e ../product-exact-20261015/tip/ops.bin 560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d evidence/mr-mask-tip-v3.bin | sha256sum --check || exit $?
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin mask_validate_transfer > evidence/mask-validate-transfer.tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin mask_validate_transfer > evidence/mask-validate-transfer.build.log 2>&1 || exit $?
sha256sum tool/target/release/mask_validate_transfer tool/src/mask_validate_transfer_body.rs tool/src/bin/mask_validate_transfer.rs evidence/mr-mask-tip-v3.bin ../product-exact-20261015/tip/ops.bin ../product-exact-20261015/candidate-product-final25/ops.bin > evidence/mask-validate-transfer-before.sha256
for fixture in audit all-failing-tip sensitivity-structured sensitivity-arbitrary; do
prlimit --as=8589934592 -- tool/target/release/mask_validate_transfer ../product-exact-20261015/candidate-product-final25/ops.bin evidence/mr-mask-tip-v3.bin packets/$fixture.tsv ../product-exact-20261015/tip/ops.bin > evidence/mask-validate-transfer-$fixture.json 2> evidence/mask-validate-transfer-$fixture.log || exit $?
done
sha256sum tool/target/release/mask_validate_transfer tool/src/mask_validate_transfer_body.rs tool/src/bin/mask_validate_transfer.rs evidence/mr-mask-tip-v3.bin ../product-exact-20261015/tip/ops.bin ../product-exact-20261015/candidate-product-final25/ops.bin > evidence/mask-validate-transfer-after.sha256
cmp evidence/mask-validate-transfer-before.sha256 evidence/mask-validate-transfer-after.sha256
