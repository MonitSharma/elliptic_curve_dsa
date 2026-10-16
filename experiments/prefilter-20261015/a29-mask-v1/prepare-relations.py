from pathlib import Path
r=Path(__file__).resolve().parents[1]
out=r/'a29-relations-v1';out.mkdir(exist_ok=True)
def put(p,s):p.write_bytes(s.encode())
src=(r/'tool/src/shadow_value_contract_bound.rs').read_text(encoding='utf8')
start=src.index('fn shadow_value_contract_with_zeros(')
end=src.index('#[cfg(test)]',start)
s=src[start:end]
s=s.replace('fn shadow_value_contract_with_zeros(', 'fn relation_obligations(').replace('-> ShadowCertificate {','-> RelationObligations {',1)
s=s.replace('let b:Vec<_>=','let input_nodes:Vec<_>=q.iter().map(|p|p.0.first().map(|(_,c)|*c).unwrap_or(0)).collect();\n    let b:Vec<_>=',1)
begin=s.index('    ShadowCertificate{operation_digest:')
s=s[:begin]+'''    let differences=actual.q.iter().zip(&zero.q).zip(&reset).map(|((actual,zero),reset)|[a.xor(actual,zero),a.xor(actual,reset)]).collect();
    RelationObligations{operation_digest:shadow_region_digest(ops),quantum_ids:qs.into_iter().collect(),input_nodes,differences,complete:status=="EXACT_PROOF"||status=="UNKNOWN_DIFFERENCE_NOT_PROVED_ZERO",status,dag:a.dag,caps:a.capped}
}
'''
header='''struct RelationObligations{operation_digest:[u8;32],quantum_ids:Vec<u64>,input_nodes:Vec<u32>,differences:Vec<[GlobalPoly;2]>,complete:bool,status:&'static str,dag:Dag,caps:usize}
// Substitute exact declared quantum-entry functions. Classical entry bits and
// all fresh/capped MR symbols remain arbitrary outer variables; requiring every
// substituted coefficient to be zero is sufficient, never a sampled criterion.
fn relation_substitute(local:&RelationObligations,global:&mut Dag,entry:&[u32])->Vec<u32>{
 assert!(local.complete);assert_eq!(entry.len(),local.input_nodes.len());
 let ports:std::collections::HashMap<_,_>=local.input_nodes.iter().zip(entry).filter(|(p,_)|**p>1).map(|(p,r)|(*p,*r)).collect();
 let d=&local.dag;let mut map=vec![u32::MAX;d.nodes.len()];map[0]=0;map[1]=1;
 for i in 2..d.nodes.len(){let id=d.find(i as u32);if id!=i as u32{map[i]=map[id as usize];continue;}let n=d.nodes[i];assert!(!n.random);let raw=match n.kind{
  2=>*ports.get(&(i as u32)).expect("undeclared opaque local input"),
  3|4=>{let a=map[d.find(n.a)as usize];let b=map[d.find(n.b)as usize];assert_ne!(a,u32::MAX);assert_ne!(b,u32::MAX);if n.kind==3{global.xor(a,b)}else{global.and(a,b)}},
  7=>{let t=d.construction[i];let a=map[d.find(t.a)as usize];let b=map[d.find(t.b)as usize];assert_ne!(a,u32::MAX);assert_ne!(b,u32::MAX);let v=match t.kind{3=>global.xor(a,b),4=>global.and(a,b),_=>panic!("missing exact definition")};if t.invert{global.not(v)}else{v}},
  8=>{let mut product=1;for m in[n.a,n.b]{for j in d.monomials[m as usize].iter(){let v=map[d.find(*j)as usize];assert_ne!(v,u32::MAX);product=global.and(product,v);}}product},_=>panic!("missing exact coefficient definition")};map[i]=raw;
 }map
}
fn relation_options(local:&RelationObligations,global:&Dag,map:&[u32])->Vec<[Vec<u32>;2]>{local.differences.iter().map(|pair|std::array::from_fn(|which|{let mut roots:Vec<_>=pair[which].0.iter().map(|(_,c)|global.find(map[local.dag.find(*c)as usize])).filter(|c|*c!=0).collect();roots.sort_unstable();roots.dedup();roots})).collect()}
'''
tests='''
#[cfg(test)]mod relation_tests{use super::*;
 fn op(k:OperationType,a:u64,t:u64,bt:u64,c:u64)->Op{Op{kind:k,q_control1:QubitId(a),q_control2:QubitId(u64::MAX),q_target:QubitId(t),c_target:BitId(bt),c_condition:BitId(c),r_target:RegisterId(u64::MAX)}}
 #[test]fn exact_entry_alias_cancels_but_wrong_relation_stays_unknown(){let n=u64::MAX;let ops=[op(OperationType::Hmr,n,3,0,n),op(OperationType::CX,1,0,n,0),op(OperationType::CX,2,0,n,0)];let local=relation_obligations(&ops,10000,1000,&Default::default());assert!(local.complete);let mut g=Dag::new();let x=g.variable(false);let y=g.variable(false);let mut entry=vec![x;local.quantum_ids.len()];let m=relation_substitute(&local,&mut g,&entry);assert!(relation_options(&local,&g,&m).iter().all(|options|options[0].is_empty()));entry[local.quantum_ids.iter().position(|q|*q==2).unwrap()]=y;let m=relation_substitute(&local,&mut g,&entry);assert!(relation_options(&local,&g,&m).iter().any(|options|!options[0].is_empty()&&!options[1].is_empty()));}
 #[test]fn complemented_entry_relation_is_proved_exactly(){let n=u64::MAX;let ops=[op(OperationType::Hmr,n,3,0,n),op(OperationType::X,n,0,n,0),op(OperationType::CX,1,0,n,0),op(OperationType::CX,2,0,n,0)];let local=relation_obligations(&ops,10000,1000,&Default::default());let mut g=Dag::new();let x=g.variable(false);let nx=g.not(x);let mut entry=vec![x;local.quantum_ids.len()];entry[local.quantum_ids.iter().position(|q|*q==2).unwrap()]=nx;let m=relation_substitute(&local,&mut g,&entry);assert!(relation_options(&local,&g,&m).iter().all(|options|options[0].is_empty()));}
}
'''
put(r/'tool/src/a29_relation_obligations.rs',header+s+tests)
s=(r/'tool/src/bin/a29_rng_mask_v2.rs').read_text(encoding='utf8').replace('include!("../a29_rng_mask_v2_body.rs");','include!("../a29_relation_obligations.rs");\ninclude!("../a29_relation_prefix_body.rs");')
put(r/'tool/src/bin/a29_relation_prefix.rs',s)
s=(r/'tool/src/a29_rng_mask_v2_body.rs').read_text(encoding='utf8')
needle='for(i,o)in ops.iter().enumerate(){if i<shadow_resume{continue;}'
assert s.count(needle)==1
handler='''
 if i==3991190 {
 let mut receipts=Vec::new();let before=alg.dag.nodes.len();
 for end in[3991588usize,3991609]{let local=relation_obligations(&ops[i..end],500000,5000,&Default::default());assert_eq!(local.operation_digest,shadow_region_digest(&ops[i..end]));let mut entry=Vec::new();let mut rng_inputs=Vec::new();for id in &local.quantum_ids{let p=&q[*id as usize];if p.0.iter().any(|(k,c)|!k.is_empty()&&alg.dag.find(*c)!=0){rng_inputs.push(*id);}entry.push(p.0.iter().find(|(k,_)|k.is_empty()).map(|(_,c)|alg.dag.find(*c)).unwrap_or(0));}
 if !local.complete||!rng_inputs.is_empty(){receipts.push(serde_json::json!({"start":i,"end_exclusive":end,"status":"UNKNOWN_LOCAL_OR_ENTRY_RNG","local_status":local.status,"rng_inputs":rng_inputs}));continue;}
 let map=relation_substitute(&local,&mut alg.dag,&entry);let options=relation_options(&local,&alg.dag,&map);let choices:Vec<_>=options.iter().map(|pair|if pair[0].is_empty(){0}else if pair[1].is_empty(){1}else{2}).collect();
 receipts.push(serde_json::json!({"start":i,"end_exclusive":end,"status":"EXACT_PREFIX_SUBSTITUTED_LOCAL_COEFFICIENT_OBLIGATIONS","source_region_digest":local.operation_digest.iter().map(|b|format!("{b:02x}")).collect::<String>(),"all_outputs_covered":choices.iter().all(|c|*c!=2),"quantum_ids":local.quantum_ids,"entry_exact_input_roots":entry,"choices":choices,"nonzero_substituted_coefficient_roots":options,"local_nodes":local.dag.nodes.len(),"local_caps":local.caps}));
 }
 let mut values=vec![0u64;alg.dag.nodes.len()];values[1]=u64::MAX;for(id,wire)in&input_nodes{values[*id as usize]=match wire{QubitOrBit::Qubit(id)=>initialq[id.0 as usize],QubitOrBit::Bit(id)=>initialb[id.0 as usize]};}for(j,n)in alg.dag.nodes.iter().enumerate().skip(2){assert!(!n.random);values[j]=match n.kind{2=>values[j],3=>values[n.a as usize]^values[n.b as usize],4=>values[n.a as usize]&values[n.b as usize],7=>alg.dag.large_defs[n.a as usize].iter().fold(0,|x,m|x^alg.dag.monomials[*m as usize].iter().fold(u64::MAX,|x,k|x&values[*k as usize])),8=>[n.a,n.b].iter().fold(u64::MAX,|x,m|x&alg.dag.monomials[*m as usize].iter().fold(u64::MAX,|x,k|x&values[*k as usize])),_=>panic!()};}
 let concrete=|p:&GlobalPoly|{let(mut c,mut d)=(0,0);for(k,v)in&p.0{if k.is_empty(){c^=values[*v as usize]}else{d|=values[*v as usize]}}(c,!d)};
 for seed in 0..4{let mut random=seeded(seed);let mut sim=Simulator::new(nq as usize,nb as usize,&mut random);sim.qubits.copy_from_slice(&initialq);sim.bits.copy_from_slice(&initialb);sim.apply_iter(ops[..i].iter());for(j,p)in q.iter().enumerate(){let(c,k)=concrete(p);assert_eq!((sim.qubits[j]^c)&k,0,"prefix q{j} seed{seed}");}for(j,p)in b.iter().enumerate(){let(c,k)=concrete(p);assert_eq!((sim.bits[j]^c)&k,0,"prefix b{j} seed{seed}");}}
 println!("{}",serde_json::json!({"status":"SOURCE_EXACT_PREFIX_RELATION_DIAGNOSTIC_NO_REWRITE_APPLIED","source_stream_sha256":"1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522","prefix_end_exclusive":i,"local_results":receipts,"prefix_input_dag_nodes":before,"dag_nodes_after_substitution":alg.dag.nodes.len(),"protected_prefix_fullstate_streams":4,"seconds":start.elapsed().as_secs_f64()}));return;
 }
'''
s=s.replace(needle,needle+handler)
put(r/'tool/src/a29_relation_prefix_body.rs',s)
put(out/'run.sh','''#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-relations-v1/run.pid
trap 'echo $? > a29-relations-v1/run.exit' EXIT
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > a29-relations-v1/run.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -25 >> a29-relations-v1/run.resources
printf '%s  %s\\n' 1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522 ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin | sha256sum --check || exit $?
/home/hclau/.cargo/bin/cargo test --manifest-path tool/Cargo.toml --release --bin a29_relation_prefix -- --nocapture > a29-relations-v1/tests.log 2>&1 || exit $?
/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin a29_relation_prefix > a29-relations-v1/build.log 2>&1 || exit $?
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/a29_relation_prefix ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin packets/audit.tsv 32 a29-mask-v1/reset-all-scopes.summary.json > a29-relations-v1/report.json 2> a29-relations-v1/run.log
''')
