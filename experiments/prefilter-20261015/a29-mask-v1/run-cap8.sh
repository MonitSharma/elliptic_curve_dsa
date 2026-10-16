#!/bin/bash
set -u
base=/home/hclau/ecdsa_research/prefilter-20261015
out=$base/a29-mask-cap8
mkdir -p "$out/a29-mask-v2"
cd "$out"
echo $$ > run.pid
trap 'echo $? > run.exit' EXIT
ulimit -c 0
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > run.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -25 >> run.resources
available=$(awk '/MemAvailable:/{print $2}' /proc/meminfo)
if test "$available" -lt 130023424; then exit 2; fi
ln -s "$base/a29-mask-v2/candidates-v3.json" a29-mask-v2/candidates-v3.json || exit $?
printf '%s  %s\n' 1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522 /home/hclau/ecdsa_research/product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin | sha256sum --check || exit $?
files="$base/tool/target/release/a29_rng_mask_v2 $base/tool/src/bin/a29_rng_mask_v2.rs $base/tool/src/a29_rng_mask_v2_body.rs $base/tool/src/a29_mask_program_trace.rs $base/tool/src/input_anf_dag_trace.rs $base/tool/src/global_rng_anf_retained_masks.rs $base/tool/src/reset_projection.rs $base/tool/src/reset_projection_symbols.rs $base/tool/src/shadow_value_contract_bound.rs $base/tool/src/shadow_apply_region_bound.rs $base/a29-mask-v2/candidates-v3.json $base/a29-mask-v1/reset-all-scopes.summary.json /home/hclau/ecdsa_research/product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin"
sha256sum $files > before.sha256
timeout 600 /usr/bin/time -v prlimit --as=25769803776 -- "$base/tool/target/release/a29_rng_mask_v2" /home/hclau/ecdsa_research/product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin "$base/packets/audit.tsv" 8 "$base/a29-mask-v1/reset-all-scopes.summary.json" > report.json 2> run.log || exit $?
sha256sum $files > after.sha256
cmp before.sha256 after.sha256 || exit $?
sha256sum a29-mask-v2/mr-mask-a29.bin a29-mask-v2/mr-mask-a29.json a29-mask-v2/mr-mask-a29.audit-input-u64le.bin a29-mask-v2/mr-mask-a29.audit-known-u64le.bin > mask.sha256
