#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/global-anf-nary-capped.pid
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/global-anf-nary-capped.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/global-anf-nary-capped.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -50 >> evidence/global-anf-nary-capped.resources
available=$(awk '/MemAvailable:/{print $2}' /proc/meminfo)
if test "$available" -lt 171966464; then echo Insufficient_memory_reserve; exit 2; fi
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin global_rng_anf_nary -- --nocapture > evidence/global-anf-nary-capped.tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin global_rng_anf_nary > evidence/global-anf-nary-capped.build.log 2>&1 || exit $?
sha256sum tool/target/release/global_rng_anf_nary tool/src/global_rng_anf_nary.rs tool/src/global_rng_anf_nary_body.rs tool/src/input_dag_nary.rs /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin /home/hclau/ecdsa_research/product-exact-20261015/chain-retained.bin > evidence/global-anf-nary-capped-before.sha256
prlimit --as=34359738368 -- tool/target/release/global_rng_anf_nary /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin packets/audit.tsv 32 > evidence/global-anf-nary-capped-tip32.json 2> evidence/global-anf-nary-capped-tip32.log || exit $?
if grep -q '"proved_value_rng_independent":true' evidence/global-anf-nary-capped-tip32.json; then
 prlimit --as=34359738368 -- tool/target/release/global_rng_anf_nary /home/hclau/ecdsa_research/product-exact-20261015/chain-retained.bin packets/audit.tsv 32 > evidence/global-anf-nary-capped-product32.json 2> evidence/global-anf-nary-capped-product32.log || exit $?
fi
sha256sum tool/target/release/global_rng_anf_nary tool/src/global_rng_anf_nary.rs tool/src/global_rng_anf_nary_body.rs tool/src/input_dag_nary.rs /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin /home/hclau/ecdsa_research/product-exact-20261015/chain-retained.bin > evidence/global-anf-nary-capped-after.sha256
cmp evidence/global-anf-nary-capped-before.sha256 evidence/global-anf-nary-capped-after.sha256 || exit $?
exit 0
