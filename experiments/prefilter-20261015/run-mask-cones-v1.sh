#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/mask-cones-v1.pid
trap 'echo $? > evidence/mask-cones-v1.exit' EXIT
export CARGO_BUILD_JOBS=1 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1
free -m > evidence/mask-cones-v1.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -20 >> evidence/mask-cones-v1.resources
printf '%s  %s\n' 560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d evidence/mr-mask-tip-v3.bin | sha256sum --check || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin mask_cone_census > evidence/mask-cones-v1.build.log 2>&1 || exit $?
sha256sum evidence/mr-mask-tip-v3.bin tool/src/bin/mask_cone_census.rs tool/target/release/mask_cone_census > evidence/mask-cones-v1-before.sha256
timeout 600 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/mask_cone_census evidence/mr-mask-tip-v3.bin > evidence/mask-cones-v1.json 2> evidence/mask-cones-v1.log || exit $?
sha256sum evidence/mr-mask-tip-v3.bin tool/src/bin/mask_cone_census.rs tool/target/release/mask_cone_census > evidence/mask-cones-v1-after.sha256
cmp evidence/mask-cones-v1-before.sha256 evidence/mask-cones-v1-after.sha256
