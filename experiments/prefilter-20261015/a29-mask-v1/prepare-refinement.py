from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'a29-mask-v2'
out.mkdir(exist_ok=True)
def put(p,s): p.write_bytes(s.encode())
s=(root/'tool/src/bin/a29_rng_mask.rs').read_text(encoding='utf8').replace('../a29_rng_mask_body.rs','../a29_rng_mask_v2_body.rs')
put(root/'tool/src/bin/a29_rng_mask_v2.rs',s)
s=(root/'tool/src/a29_rng_mask_body.rs').read_text(encoding='utf8').replace('a29-mask-v1/candidates-v2.json','a29-mask-v2/candidates-v3.json').replace('a29-mask-v1/mr-mask-a29','a29-mask-v2/mr-mask-a29')
put(root/'tool/src/a29_rng_mask_v2_body.rs',s)
put(out/'run-map.sh','''#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-mask-v2/map.pid
trap 'echo $? > a29-mask-v2/map.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin a29_contract_map_v3 --bin a29_rng_mask_v2 > a29-mask-v2/build.log 2>&1 || exit $?
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/a29_contract_map_v3 ../product-exact-20261015/tip/ops.bin ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin a29-mask-v1/old-boundary-hints.json a29-mask-v1/candidates.json > a29-mask-v2/candidates-v3.json 2> a29-mask-v2/map.log
''')
s=(root/'a29-mask-v1/run-global.sh').read_text(encoding='utf8')
s=s.replace('a29-mask-v1/global','a29-mask-v2/global').replace('a29-mask-v1/mask.sha256','a29-mask-v2/mask.sha256').replace('a29-mask-v1/mr-mask-a29','a29-mask-v2/mr-mask-a29').replace('a29-mask-v1/candidates-v2.json','a29-mask-v2/candidates-v3.json').replace('tool/target/release/a29_rng_mask','tool/target/release/a29_rng_mask_v2').replace('--bin a29_rng_mask','--bin a29_rng_mask_v2').replace('tool/src/bin/a29_rng_mask.rs','tool/src/bin/a29_rng_mask_v2.rs').replace('tool/src/a29_rng_mask_body.rs','tool/src/a29_rng_mask_v2_body.rs')
put(out/'run-global.sh',s)
