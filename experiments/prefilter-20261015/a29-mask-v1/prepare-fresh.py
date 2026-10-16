from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
out=root/'a29-mask-v1'
def put(p,s): p.write_bytes(s.encode())
put(out/'run-scan.sh','''#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-mask-v1/scan.pid
trap 'echo $? > a29-mask-v1/scan.exit' EXIT
ulimit -c 0
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > a29-mask-v1/scan.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -20 >> a29-mask-v1/scan.resources
printf '%s  %s\\n' 1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522 ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin | sha256sum --check || exit $?
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/reset_projection_all_scopes_scan ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin a29-mask-v1/reset-all-scopes 100000 > a29-mask-v1/scan.stdout 2> a29-mask-v1/scan.log
''')
# Endpoint mapping is only a source of candidates. The new global replay must
# prove every actual new interval; no old theorem or mask is imported.
p=root/'tool/src/bin/a29_contract_map.rs'
s=p.read_text(encoding='utf8')
s=s.replace('len()<64','len()<512')
s=s.replace('let mapping=if pairs.len()==1', '''if pairs.len()>1{let guide:serde_json::Value=serde_json::from_str(&std::fs::read_to_string(&a[4]).unwrap()).unwrap();let nearest=guide["rows"].as_array().unwrap().iter().filter(|r|!r["mapping"].is_null()).min_by_key(|r|r["hint"]["old_start"].as_u64().unwrap().abs_diff(oldlo as u64));if let Some(g)=nearest{let offset=g["mapping"]["start"].as_i64().unwrap()-g["hint"]["old_start"].as_i64().unwrap();let predicted=(oldlo as i64+offset).max(0)as usize;let mut ranked:Vec<_>=pairs.iter().copied().collect();ranked.sort_by_key(|(lo,hi)|(lo.abs_diff(predicted),(hi-lo).abs_diff(len)));if ranked.len()==1||ranked[0].0.abs_diff(predicted)<ranked[1].0.abs_diff(predicted){pairs=std::collections::BTreeSet::from([ranked[0]]);}}}
let mapping=if pairs.len()==1''')
s=s.replace('ACTUAL_OPERATION_ANCHOR_CANDIDATES_REQUIRE_FRESH_LOCAL_PROOFS','ACTUAL_OPERATION_ANCHOR_AND_OFFSET_CANDIDATES_REQUIRE_FRESH_LOCAL_PROOFS')
put(root/'tool/src/bin/a29_contract_map_v2.rs',s)
v3=s.replace('if pairs.len()>1{let guide:', 'if pairs.len()>1{let exact:std::collections::BTreeSet<_>=pairs.iter().copied().filter(|(lo,hi)|old[oldlo..oldhi]==new[*lo..*hi]).collect();if exact.len()==1{pairs=exact;}}if pairs.len()>1{let guide:')
put(root/'tool/src/bin/a29_contract_map_v3.rs',v3)

s=(root/'tool/src/bin/global_rng_anf_mask_trace.rs').read_text(encoding='utf8')
s=s.replace('../mask_program_trace.rs','../a29_mask_program_trace.rs').replace('../global_rng_anf_mask_trace_body.rs','../a29_rng_mask_body.rs')
put(root/'tool/src/bin/a29_rng_mask.rs','#![recursion_limit = "256"]\n'+s)
s=(root/'tool/src/mask_program_trace.rs').read_text(encoding='utf8')
s=s.replace('"source_commit":"4b2ec52fc55da796aa8f5ef851290297e8706424","original_stream_sha256":"2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e"','"source_variant":"frozen_A29_precision_repair","source_stream_sha256":"1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522","ancestor_commit":"4b2ec52fc55da796aa8f5ef851290297e8706424","old_mask_transfer_used":false')
put(root/'tool/src/a29_mask_program_trace.rs',s)
s=(root/'tool/src/global_rng_anf_mask_trace_body.rs').read_text(encoding='utf8')
s=s.replace('let(nq,nb,_,regs)=analyze_ops(ops.iter());','assert_eq!(ops.len(),11636536);let(nq,nb,_,regs)=analyze_ops(ops.iter());')
s=s.replace('end-start<10000','end-start<100000')
marker='ranges.sort_unstable_by_key'
at=s.index(marker)
s=s[:at]+'''let mapped:serde_json::Value=serde_json::from_str(&std::fs::read_to_string("a29-mask-v1/candidates-v2.json").unwrap()).unwrap();assert_eq!(mapped["full_operation_count"].as_u64().unwrap(),ops.len()as u64);for r in mapped["candidate_reset_regions"].as_array().unwrap(){ranges.push((r[0].as_u64().unwrap()as usize,r[1].as_u64().unwrap()as usize));}
let mut freshly_proved=Vec::new();let mut failed_reset_candidates=Vec::new();ranges.sort_unstable();ranges.dedup();for(start,end)in ranges{let span=&ops[start..=end];if coeff_projection::prove(span)||symbol_projection::prove(span){freshly_proved.push((start,end));}else{failed_reset_candidates.push((start,end));}}let mut ranges=freshly_proved;
'''+s[at:]
start=s.index(' let prior:serde_json::Value=')
end=s.index(' for ends in shadow_candidates.values_mut()',start)
s=s[:start]+''' for r in mapped["candidate_shadow_regions"].as_array().unwrap(){let lo=r[0].as_u64().unwrap()as usize;let hi=r[1].as_u64().unwrap()as usize;assert!(lo<hi&&hi<=ops.len());let compatible=selected.iter().all(|(s,e)|hi<=*s||lo>*e||(lo<=*s&&hi>*e));if compatible{shadow_candidates.entry(lo).or_default().push(hi);}}
'''+s[end:]
s=s.replace('evidence/mr-mask-tip-v3','a29-mask-v1/mr-mask-a29')
s=s.replace('"stream_path":args[1],','"stream_path":args[1],"source_stream_sha256":"1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522","old_mask_transfer_used":false,"failed_reset_candidates":failed_reset_candidates,')
put(root/'tool/src/a29_rng_mask_body.rs',s)
put(out/'run-map-v2.sh','''#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-mask-v1/map-v2.pid
trap 'echo $? > a29-mask-v1/map-v2.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin a29_contract_map_v2 --bin a29_rng_mask > a29-mask-v1/build-v2.log 2>&1 || exit $?
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/a29_contract_map_v2 ../product-exact-20261015/tip/ops.bin ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin a29-mask-v1/old-boundary-hints.json a29-mask-v1/candidates.json > a29-mask-v1/candidates-v2.json 2> a29-mask-v1/map-v2.log
''')
put(out/'run-global.sh','''#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-mask-v1/global.pid
trap 'echo $? > a29-mask-v1/global.exit' EXIT
ulimit -c 0
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > a29-mask-v1/global.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -30 >> a29-mask-v1/global.resources
available=$(awk '/MemAvailable:/{print $2}' /proc/meminfo)
if test "$available" -lt 130023424; then echo Insufficient_memory_reserve; exit 2; fi
printf '%s  %s\\n' 1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522 ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin | sha256sum --check || exit $?
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin a29_rng_mask -- --nocapture > a29-mask-v1/global.tests.log 2>&1 || exit $?
files='tool/target/release/a29_rng_mask tool/src/bin/a29_rng_mask.rs tool/src/a29_rng_mask_body.rs tool/src/a29_mask_program_trace.rs tool/src/input_anf_dag_trace.rs tool/src/global_rng_anf_retained_masks.rs tool/src/reset_projection.rs tool/src/reset_projection_symbols.rs tool/src/shadow_value_contract_bound.rs tool/src/shadow_apply_region_bound.rs a29-mask-v1/candidates-v2.json a29-mask-v1/reset-all-scopes.summary.json ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin'
sha256sum $files > a29-mask-v1/global-before.sha256
timeout 1200 /usr/bin/time -v prlimit --as=25769803776 -- tool/target/release/a29_rng_mask ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin packets/audit.tsv 32 a29-mask-v1/reset-all-scopes.summary.json > a29-mask-v1/global.json 2> a29-mask-v1/global.log || exit $?
sha256sum $files > a29-mask-v1/global-after.sha256
cmp a29-mask-v1/global-before.sha256 a29-mask-v1/global-after.sha256 || exit $?
sha256sum a29-mask-v1/mr-mask-a29.bin a29-mask-v1/mr-mask-a29.json a29-mask-v1/mr-mask-a29.audit-input-u64le.bin a29-mask-v1/mr-mask-a29.audit-known-u64le.bin > a29-mask-v1/mask.sha256
''')
