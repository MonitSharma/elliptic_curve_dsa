#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-conditional-validation-v1/run.pid
trap 'echo $? > a29-conditional-validation-v1/run.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > a29-conditional-validation-v1/resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -25 >> a29-conditional-validation-v1/resources
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin a29_pair_fold_validate -- --nocapture > a29-conditional-validation-v1/tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin a29_pair_fold_validate > a29-conditional-validation-v1/build.log 2>&1 || exit $?
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- python3 a29-conditional-validation-v1/run-validation.py > a29-conditional-validation-v1/validation.log 2> a29-conditional-validation-v1/validation.stderr
