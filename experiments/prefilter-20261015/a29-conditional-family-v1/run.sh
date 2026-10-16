#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-conditional-family-v1/run.pid
trap 'echo $? > a29-conditional-family-v1/run.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > a29-conditional-family-v1/resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -25 >> a29-conditional-family-v1/resources
timeout 90 prlimit --as=8589934592 -- python3 a29-conditional-family-v1/prepare-actual-frames.py > a29-conditional-family-v1/binding.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin a29_pair_fold_family -- --nocapture > a29-conditional-family-v1/tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin a29_pair_fold_family > a29-conditional-family-v1/build.log 2>&1 || exit $?
sha256sum tool/src/bin/a29_pair_fold_family.rs tool/src/input_anf_dag_trace.rs tool/src/global_rng_anf_retained_masks.rs tool/src/shadow_value_contract_bound.rs tool/src/shadow_apply_region_bound.rs a29-conditional-family-v1/*.prefix.json a29-conditional-family-v1/*.old.bin a29-conditional-family-v1/*.new.bin > a29-conditional-family-v1/before.sha256
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- python3 a29-conditional-family-v1/run-family.py > a29-conditional-family-v1/family.log 2> a29-conditional-family-v1/family.stderr || exit $?
sha256sum tool/src/bin/a29_pair_fold_family.rs tool/src/input_anf_dag_trace.rs tool/src/global_rng_anf_retained_masks.rs tool/src/shadow_value_contract_bound.rs tool/src/shadow_apply_region_bound.rs a29-conditional-family-v1/*.prefix.json a29-conditional-family-v1/*.old.bin a29-conditional-family-v1/*.new.bin > a29-conditional-family-v1/after.sha256
cmp a29-conditional-family-v1/before.sha256 a29-conditional-family-v1/after.sha256
