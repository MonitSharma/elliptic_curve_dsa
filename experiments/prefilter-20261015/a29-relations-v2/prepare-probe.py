from pathlib import Path
import json
r=Path(__file__).resolve().parents[1];out=r/'a29-fold-family-v1';out.mkdir(exist_ok=True)
def put(p,s):p.write_bytes(s.encode())
s=(r/'tool/src/bin/a29_rng_mask_v2.rs').read_text(encoding='utf8')
s=s[:s.index('include!("../a29_rng_mask_v2_body.rs");')]+'''fn main(){let args:Vec<_>=std::env::args().collect();let ops=load_ops(&args[1]).unwrap();let prefix:serde_json::Value=serde_json::from_str(&std::fs::read_to_string(&args[2]).unwrap()).unwrap();assert_eq!(prefix["source_stream_sha256"],"1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522");let row=&prefix["local_results"][0];let start=row["start"].as_u64().unwrap()as usize;let end=row["end_exclusive"].as_u64().unwrap()as usize;let zeros:std::collections::BTreeSet<_>=row["required_proved_zero_entry_wires"].as_array().unwrap().iter().map(|x|x.as_u64().unwrap()).collect();let r=shadow_value_contract_with_zeros(&ops[start..end],500000,5000,&zeros);let digest=r.operation_digest.iter().map(|b|format!("{b:02x}")).collect::<String>();assert_eq!(digest,row["source_region_digest"].as_str().unwrap());println!("{}",serde_json::json!({"status":"EXISTING_GENERIC_SHADOW_CONTRACT_CHECK_WITH_EXTERNALLY_PROVED_ZERO_PRECONDITIONS","source_stream_sha256":prefix["source_stream_sha256"],"start":start,"end_exclusive":end,"proved":r.proved,"local_status":r.status,"choices":r.choices,"q_outputs":r.quantum_ids.len(),"local_nodes":r.nodes,"local_caps":r.caps,"digest":digest,"required_prefix_zero_qids":zeros,"prefix_receipt":args[2]}));}
'''
put(r/'tool/src/bin/a29_whole_zero_probe.rs',s)
family=json.loads((r.parent/'precision-family-20261016/FAMILY-A.json').read_text())
hints=dict(status='SOURCE_FAMILY_BOUNDARIES_ARE_CANDIDATES_ONLY_REQUIRE_FRESH_ACTUAL_GATE_PROOF',source_family='every structurally unchanged late-forward fold in FAMILY-A; no packet selection',hints=[dict(kind='shadow',old_start=x['final_begin'],old_end_exclusive=x['final_end'],tick=x['tick'])for x in family['records']])
put(out/'hints.json',json.dumps(hints,indent=2)+'\n')
put(out/'run-probe-map.sh','''#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-fold-family-v1/run.pid
trap 'echo $? > a29-fold-family-v1/run.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > a29-fold-family-v1/run.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -25 >> a29-fold-family-v1/run.resources
printf '%s  %s\\n' 1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522 ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin | sha256sum --check || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin a29_whole_zero_probe > a29-fold-family-v1/build.log 2>&1 || exit $?
timeout 60 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/a29_whole_zero_probe ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin a29-relations-v2/report.json > a29-fold-family-v1/probe.json 2> a29-fold-family-v1/probe.log || exit $?
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/a29_contract_map_v3 ../product-exact-20261015/tip/ops.bin ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin a29-fold-family-v1/hints.json a29-mask-v2/candidates-v3.json > a29-fold-family-v1/candidates.json 2> a29-fold-family-v1/map.log
''')
