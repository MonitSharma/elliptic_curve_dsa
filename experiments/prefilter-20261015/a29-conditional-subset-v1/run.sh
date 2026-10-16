#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-conditional-subset-v1/run.pid
trap 'echo $? > a29-conditional-subset-v1/run.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > a29-conditional-subset-v1/resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -25 >> a29-conditional-subset-v1/resources
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin a29_retained_subset > a29-conditional-subset-v1/build.log 2>&1 || exit $?
files='tool/src/bin/a29_retained_subset.rs tool/src/a29_retained_subset_body.rs ../product-exact-20261015/tip/ops.bin evidence/mr-mask-tip-v3.bin a29-conditional-prefix-v1/public-discrepancy-guard.bin a29-conditional-coverage-v1/fixed445-inputs.tsv'
sha256sum $files > a29-conditional-subset-v1/before.sha256
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/a29_retained_subset ../product-exact-20261015/tip/ops.bin evidence/mr-mask-tip-v3.bin a29-conditional-prefix-v1/public-discrepancy-guard.bin a29-conditional-coverage-v1/fixed445-inputs.tsv > a29-conditional-subset-v1/result.json 2> a29-conditional-subset-v1/result.log || exit $?
sha256sum $files > a29-conditional-subset-v1/after.sha256
cmp a29-conditional-subset-v1/before.sha256 a29-conditional-subset-v1/after.sha256
