#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
test ! -f evidence/first-macro-proof.tests.log || cp evidence/first-macro-proof.tests.log evidence/first-macro-proof.attempt1.tests.log
rm -f evidence/first-macro-proof.exit
echo $$ > evidence/first-macro-proof.pid
trap 'echo $? > evidence/first-macro-proof.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/first-macro-proof.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -40 >> evidence/first-macro-proof.resources
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin macro_proof -- --nocapture > evidence/first-macro-proof.tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin macro_proof > evidence/first-macro-proof.build.log 2>&1 || exit $?
sha256sum tool/target/release/macro_proof tool/src/macro_proof_body.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_inputanf16.rs /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin > evidence/first-macro-proof-before.sha256
for start in 688341 688342; do
 if test "$start" = 688341; then end=689349; else end=689348; fi
 for mode in arbitrary zero_reset; do
  prlimit --as=17179869184 -- tool/target/release/macro_proof /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin "$start" "$end" "$mode" > "evidence/first-macro-$start-$mode.json" 2> "evidence/first-macro-$start-$mode.log" || exit $?
 done
done
sha256sum tool/target/release/macro_proof tool/src/macro_proof_body.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_inputanf16.rs /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin > evidence/first-macro-proof-after.sha256
cmp evidence/first-macro-proof-before.sha256 evidence/first-macro-proof-after.sha256 || exit $?
