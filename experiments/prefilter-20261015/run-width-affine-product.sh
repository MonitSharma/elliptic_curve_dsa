#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/width-affine-product.pid
trap 'echo $? > evidence/width-affine-product.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > evidence/width-affine-product.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -25 >> evidence/width-affine-product.resources
printf '%s  %s\n' 2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e ../product-exact-20261015/tip/ops.bin | sha256sum --check || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin width_affine_product_audit > evidence/width-affine-product.build.log 2>&1 || exit $?
sha256sum tool/src/bin/width_affine_product_audit.rs tool/src/width_interned_witness.rs tool/target/release/width_affine_product_audit ../product-exact-20261015/tip/ops.bin > evidence/width-affine-product-before.sha256
prlimit --as=8589934592 -- tool/target/release/width_affine_product_audit ../product-exact-20261015/tip/ops.bin > evidence/width-affine-product-tip.json 2> evidence/width-affine-product-tip.log || exit $?
sha256sum tool/src/bin/width_affine_product_audit.rs tool/src/width_interned_witness.rs tool/target/release/width_affine_product_audit ../product-exact-20261015/tip/ops.bin > evidence/width-affine-product-after.sha256
cmp evidence/width-affine-product-before.sha256 evidence/width-affine-product-after.sha256
