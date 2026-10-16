from pathlib import Path
import json,hashlib
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016')
s=(r/'map-final-markers.py').read_text().replace("r/'raw-builder.bin'","r/'raw-seed-builder.bin'").replace("r/'raw-markers.jsonl'","r/'raw-seed-markers.jsonl'").replace("r/'actual-markers.json'","r/'actual-seed-markers.json'")
exec(compile(s,'map-seed-boundaries','exec'))
s=(r/'tool/src/payload_runtime.rs').read_text()
s=s.replace('pub fn run(ops:&[Op]){','''#[derive(Clone)]struct Seed{at:usize,id:usize,before:bool,target:Vec<QubitId>}
static SEEDS:Mutex<Vec<Seed>>=Mutex::new(Vec::new());
pub fn run(ops:&[Op]){
let seeds=SEEDS.lock().unwrap().clone();''')
needle='let mut entries=HashMap::<usize,Vec<[U256;2]>>::new();';assert s.count(needle)==1;s=s.replace(needle,'let mut seed_cursor=0;let mut seed_values=HashMap::<usize,Vec<U256>>::new();'+needle)
needle='sim.apply_observed(ops.iter(),|idx,s,_,_|{';assert s.count(needle)==1
s=s.replace(needle,needle+'''
while seed_cursor<seeds.len()&&seeds[seed_cursor].at==idx{let m=&seeds[seed_cursor];seed_cursor+=1;
if m.before{seed_values.insert(m.id,(0..64).map(|lane|word(&m.target,&s.qubits,lane)).collect());}else{
let vs=seed_values.remove(&m.id).unwrap();let mask:U256=(U256::from(1)<<53usize)-U256::from(1);let ff=U256::from(0x1000003d1u64);
for &lane in &tracked{let a=vs[lane];let adj=if a.bit(0){a.wrapping_sub(ff)}else{a};let v=(a&!mask)|(adj&mask);let want=(v>>1)|if a.bit(0){U256::from(1)<<255}else{U256::ZERO};let got=word(&m.target,&s.qubits,lane);if got!=want||batch*64+lane==131050{eprintln!("SEED_EVENT shot={} id={} at={} a={a:#x} got={got:#x} want={want:#x} delta={:#x} matches={}",batch*64+lane,m.id,m.at,got.wrapping_sub(want),got==want);}}
}}
''')
needle='assert_eq!(cursor,marks.len());';assert s.count(needle)==1;s=s.replace(needle,'assert_eq!(seed_cursor,seeds.len());'+needle)
needle='}}run(ops);';assert s.count(needle)==1
s=s.replace(needle,'''} }
let extra:serde_json::Value=serde_json::from_str(&std::fs::read_to_string("/home/hclau/ecdsa_research/current-value-attribution-20261016/actual-seed-markers.json").unwrap()).unwrap();for m in extra["markers"].as_array().unwrap(){SEEDS.lock().unwrap().push(Seed{at:m["at"].as_u64().unwrap()as usize,id:m["id"].as_u64().unwrap()as usize,before:m["before"].as_bool().unwrap(),target:ids(m,"target")});}run(ops);''')
(r/'tool/src/seed_payload_runtime.rs').write_text(s)
s=(r/'tool/src/bin/current_payload.rs').read_text().replace('../payload_runtime.rs','../seed_payload_runtime.rs');(r/'tool/src/bin/current_seed_payload.rs').write_text(s)
(r/'SEED-REPLAY-DECLARATION.json').write_text(json.dumps(dict(status='FIXED ALL431/413CONTEXT REPLAY BEFORE OBSERVATION',same_original_declaration_sha256=hashlib.sha256((r/'REPLAY-PREDECLARATION.json').read_bytes()).hexdigest(),same_original_batch_contexts_and_MR=True,no_new_sampling=True,no_candidate=True,observation='ALL source-defined mod_halve_pm instances with unique centered literal-final paired boundaries; compare actual ENTRY to exact finite53bit seed formula; UNKNOWN retained'),indent=2)+'\n')
