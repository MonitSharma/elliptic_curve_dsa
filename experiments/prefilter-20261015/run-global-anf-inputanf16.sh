#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
test ! -f evidence/global-anf-inputanf16.tests.log || cp evidence/global-anf-inputanf16.tests.log evidence/global-anf-inputanf16.attempt1.tests.log
rm -f evidence/global-anf-inputanf16.exit
echo $$ > evidence/global-anf-inputanf16.pid
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/global-anf-inputanf16.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/global-anf-inputanf16.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -50 >> evidence/global-anf-inputanf16.resources
available=$(awk '/MemAvailable:/{print $2}' /proc/meminfo)
if test "$available" -lt 171966464; then echo Insufficient_memory_reserve; exit 2; fi
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin global_rng_anf_inputanf16 -- --nocapture > evidence/global-anf-inputanf16.tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin global_rng_anf_inputanf16 > evidence/global-anf-inputanf16.build.log 2>&1 || exit $?
sha256sum tool/target/release/global_rng_anf_inputanf16 tool/src/global_rng_anf_inputanf16.rs tool/src/global_rng_anf_inputanf16_body.rs tool/src/input_anf_dag16.rs /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin /home/hclau/ecdsa_research/product-exact-20261015/chain-retained.bin > evidence/global-anf-inputanf16-before.sha256
prlimit --as=34359738368 -- tool/target/release/global_rng_anf_inputanf16 /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin packets/audit.tsv 32 > evidence/global-anf-inputanf16-tip32.json 2> evidence/global-anf-inputanf16-tip32.log || exit $?
if grep -q '"proved_value_rng_independent":true' evidence/global-anf-inputanf16-tip32.json; then
 prlimit --as=34359738368 -- tool/target/release/global_rng_anf_inputanf16 /home/hclau/ecdsa_research/product-exact-20261015/chain-retained.bin packets/audit.tsv 32 > evidence/global-anf-inputanf16-product32.json 2> evidence/global-anf-inputanf16-product32.log || exit $?
fi
sha256sum tool/target/release/global_rng_anf_inputanf16 tool/src/global_rng_anf_inputanf16.rs tool/src/global_rng_anf_inputanf16_body.rs tool/src/input_anf_dag16.rs /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin /home/hclau/ecdsa_research/product-exact-20261015/chain-retained.bin > evidence/global-anf-inputanf16-after.sha256
cmp evidence/global-anf-inputanf16-before.sha256 evidence/global-anf-inputanf16-after.sha256 || exit $?
exit 0
