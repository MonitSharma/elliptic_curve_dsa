#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/reset-projection-symbols-scan.pid
trap 'echo $? > evidence/reset-projection-symbols-scan.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
free -m > evidence/reset-projection-symbols-scan.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -40 >> evidence/reset-projection-symbols-scan.resources
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin reset_projection_symbols_scan -- --nocapture > evidence/reset-projection-symbols-scan.tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin reset_projection_symbols_scan > evidence/reset-projection-symbols-scan.build.log 2>&1 || exit $?
sha256sum tool/target/release/reset_projection_symbols_scan tool/src/reset_projection_symbols.rs tool/src/reset_projection_symbols_scan_body.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_inputanf16.rs /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin > evidence/reset-projection-symbols-scan-before.sha256
prlimit --as=17179869184 -- tool/target/release/reset_projection_symbols_scan /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin evidence/reset-projection-symbols-tip 10000 > evidence/reset-projection-symbols-scan.report.log 2> evidence/reset-projection-symbols-scan.progress.log || exit $?
sha256sum tool/target/release/reset_projection_symbols_scan tool/src/reset_projection_symbols.rs tool/src/reset_projection_symbols_scan_body.rs tool/src/input_anf_dag16.rs tool/src/global_rng_anf_inputanf16.rs /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin > evidence/reset-projection-symbols-scan-after.sha256
cmp evidence/reset-projection-symbols-scan-before.sha256 evidence/reset-projection-symbols-scan-after.sha256 || exit $?
