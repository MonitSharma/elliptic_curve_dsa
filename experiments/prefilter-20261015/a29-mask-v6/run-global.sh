#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-mask-v6/global.pid
trap 'echo $? > a29-mask-v6/global.exit' EXIT
ulimit -c 0
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > a29-mask-v6/global.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -30 >> a29-mask-v6/global.resources
available=$(awk '/MemAvailable:/{print $2}' /proc/meminfo)
if test "$available" -lt 130023424; then echo Insufficient_memory_reserve; exit 2; fi
printf '%s  %s\n' 1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522 ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin | sha256sum --check || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin a29_rng_mask_v6 > a29-mask-v6/global.build.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin a29_rng_mask_v6 -- --nocapture > a29-mask-v6/global.tests.log 2>&1 || exit $?
files='tool/target/release/a29_rng_mask_v6 tool/src/bin/a29_rng_mask_v6.rs tool/src/a29_rng_mask_v6_body.rs tool/src/a29_mask_program_trace.rs tool/src/input_anf_dag_trace.rs tool/src/global_rng_anf_retained_masks.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/shadow_value_contract_bound.rs tool/src/shadow_apply_region_keep_actual.rs a29-mask-v6/candidates.json a29-mask-v1/reset-all-scopes.summary.json ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin'
sha256sum $files > a29-mask-v6/global-before.sha256
timeout 1200 /usr/bin/time -v prlimit --as=25769803776 -- tool/target/release/a29_rng_mask_v6 ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin packets/audit.tsv 32 a29-mask-v1/reset-all-scopes.summary.json > a29-mask-v6/global.json 2> a29-mask-v6/global.log || exit $?
sha256sum $files > a29-mask-v6/global-after.sha256
cmp a29-mask-v6/global-before.sha256 a29-mask-v6/global-after.sha256 || exit $?
sha256sum a29-mask-v6/mr-mask-a29.bin a29-mask-v6/mr-mask-a29.json a29-mask-v6/mr-mask-a29.audit-input-u64le.bin a29-mask-v6/mr-mask-a29.audit-known-u64le.bin > a29-mask-v6/mask.sha256
