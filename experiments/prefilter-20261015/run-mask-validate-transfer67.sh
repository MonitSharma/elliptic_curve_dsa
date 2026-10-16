#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/mask-validate-transfer67.pid
trap 'echo $? > evidence/mask-validate-transfer67.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/mask-validate-transfer67.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -30 >> evidence/mask-validate-transfer67.resources
available=$(awk '/MemAvailable:/{print $2}' /proc/meminfo)
if test "$available" -lt 120000000; then exit 2; fi
printf '%s  %s\n' 268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d ../product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin 2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e ../product-exact-20261015/tip/ops.bin 560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d evidence/mr-mask-tip-v3.bin | sha256sum --check || exit $?
test "$(cat evidence/candidate67-static-abi.exit)" = 0 || exit 3
printf '%s  %s\n' 9b83de8ea7812eea80b19bd02f624053c9fcf0e57816e3258f64f9130538537e tool/target/release/mask_validate_transfer 303a75ec86a4da8c3a4008646e1b8257768fa40e198f0b7172eeafd19408c7c6 ../product-exact-20261015/cache-certificate67-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json d774c492b94f1c6ca458cc42de82d6dbee90a316f7d80c9dc6ee32eb1fe5201f ../product-exact-20261015/cache-certificate67-20261016/PER_INPUT_MASK_TRANSFER.json | sha256sum --check || exit $?
sha256sum tool/target/release/mask_validate_transfer tool/src/mask_validate_transfer_body.rs tool/src/bin/mask_validate_transfer.rs evidence/mr-mask-tip-v3.bin ../product-exact-20261015/tip/ops.bin ../product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin ../product-exact-20261015/cache-certificate67-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json ../product-exact-20261015/cache-certificate67-20261016/PER_INPUT_MASK_TRANSFER.json > evidence/mask-validate-transfer67-before.sha256
for fixture in audit all-failing-tip sensitivity-structured sensitivity-arbitrary; do
prlimit --as=8589934592 -- tool/target/release/mask_validate_transfer ../product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin evidence/mr-mask-tip-v3.bin packets/$fixture.tsv ../product-exact-20261015/tip/ops.bin > evidence/mask-validate-transfer67-$fixture.json 2> evidence/mask-validate-transfer67-$fixture.log || exit $?
done
sha256sum tool/target/release/mask_validate_transfer tool/src/mask_validate_transfer_body.rs tool/src/bin/mask_validate_transfer.rs evidence/mr-mask-tip-v3.bin ../product-exact-20261015/tip/ops.bin ../product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin ../product-exact-20261015/cache-certificate67-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json ../product-exact-20261015/cache-certificate67-20261016/PER_INPUT_MASK_TRANSFER.json > evidence/mask-validate-transfer67-after.sha256
cmp evidence/mask-validate-transfer67-before.sha256 evidence/mask-validate-transfer67-after.sha256
