#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/width-primitives.pid
trap 'echo $? > evidence/width-primitives.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > evidence/width-primitives.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -25 >> evidence/width-primitives.resources
printf '%s  %s\n' 2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e ../product-exact-20261015/tip/ops.bin | sha256sum --check || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin width_primitive_check > evidence/width-primitives.build.log 2>&1 || exit $?
sha256sum tool/src/bin/width_primitive_check.rs tool/target/release/width_primitive_check ../product-exact-20261015/tip/ops.bin > evidence/width-primitives-before.sha256
prlimit --as=8589934592 -- tool/target/release/width_primitive_check > evidence/width-primitives-tip.json 2> evidence/width-primitives-tip.log || exit $?
sha256sum tool/src/bin/width_primitive_check.rs tool/target/release/width_primitive_check ../product-exact-20261015/tip/ops.bin > evidence/width-primitives-after.sha256
cmp evidence/width-primitives-before.sha256 evidence/width-primitives-after.sha256
