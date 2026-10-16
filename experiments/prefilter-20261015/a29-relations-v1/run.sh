#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-relations-v1/run.pid
trap 'echo $? > a29-relations-v1/run.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > a29-relations-v1/run.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -25 >> a29-relations-v1/run.resources
printf '%s  %s\n' 1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522 ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin | sha256sum --check || exit $?
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin a29_relation_prefix -- --nocapture > a29-relations-v1/tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin a29_relation_prefix > a29-relations-v1/build.log 2>&1 || exit $?
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/a29_relation_prefix ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin packets/audit.tsv 32 a29-mask-v1/reset-all-scopes.summary.json > a29-relations-v1/report.json 2> a29-relations-v1/run.log
