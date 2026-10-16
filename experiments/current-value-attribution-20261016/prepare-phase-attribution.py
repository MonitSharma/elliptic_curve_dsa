from pathlib import Path
import json,hashlib,datetime
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016')
assert(r/'actual-replay.exit').read_text().strip()=='0';assert(r/'attribution-checkpoint-v1-receipt.json').exists()
s=(r/'tool/src/payload_runtime.rs').read_text()
decl='''
#[derive(Clone)]struct Park{at:usize,phase:String,r0:Vec<QubitId>,r1:Vec<QubitId>}
static PARKS:Mutex<Vec<Park>>=Mutex::new(Vec::new());
'''
s=s.replace('pub fn run(ops:&[Op]){',decl+'\npub fn run(ops:&[Op]){\nlet parks=PARKS.lock().unwrap().clone();')
needle='let mut entries=HashMap::<usize,Vec<[U256;2]>>::new();';assert s.count(needle)==1;s=s.replace(needle,'let mut phase_first=HashMap::<&\'static str,Vec<bool>>::new();let mut park_cursor=0;\n'+needle)
needle='sim.apply_observed(ops.iter(),|idx,s,_,_|{';assert s.count(needle)==1
hook='''
while park_cursor<parks.len()&&parks[park_cursor].at==idx{let m=&parks[park_cursor];park_cursor+=1;for &lane in &tracked{let signed=|q:&[QubitId]|{assert_eq!(q.len(),5);let v=1+2*small(q,&s.qubits,lane);if v&32!=0{v-64}else{v}};let r0=signed(&m.r0);let r1=signed(&m.r1);eprintln!("PARKED_RAILS shot={} phase={} at={} r0={r0} r1={r1} clean0={} clean1={}",batch*64+lane,m.phase,m.at,r0.abs()==1,r1.abs()==1);}}
'''
s=s.replace(needle,needle+hook)
needle='if first[lane]{continue;}';assert s.count(needle)==1;s=s.replace(needle,'if phase_first.entry(m.phase).or_insert_with(||vec![false;64])[lane]{continue;}')
needle='first[lane]=true;total_event+=1;';assert s.count(needle)==1;s=s.replace(needle,'phase_first.get_mut(m.phase).unwrap()[lane]=true;'+needle)
needle='assert_eq!(cursor,marks.len());';assert s.count(needle)==1;s=s.replace(needle,'assert_eq!(park_cursor,parks.len());'+needle)
needle='}}run(ops);';assert s.count(needle)==1
loader='''}}
let extra:serde_json::Value=serde_json::from_str(&std::fs::read_to_string("/home/hclau/ecdsa_research/current-value-attribution-20261016/actual-loan-markers.json").unwrap()).unwrap();for m in extra["markers"].as_array().unwrap(){if m["label"]=="out-before"{PARKS.lock().unwrap().push(Park{at:m["at"].as_u64().unwrap()as usize,phase:m["phase"].as_str().unwrap().to_string(),r0:ids(m,"rail0"),r1:ids(m,"rail1")});}}run(ops);'''
s=s.replace(needle,loader);(r/'tool/src/phase_payload_runtime.rs').write_text(s)
s=(r/'tool/src/bin/current_payload.rs').read_text().replace('../payload_runtime.rs','../phase_payload_runtime.rs');(r/'tool/src/bin/current_phase_payload.rs').write_text(s)
(r/'PHASE-REPLAY-DECLARATION.json').write_text(json.dumps(dict(status='FIXED SAME ALL431/413CONTEXT REPLAY BEFORE OBSERVATION',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),same_original_declaration_sha256=hashlib.sha256((r/'REPLAY-PREDECLARATION.json').read_bytes()).hexdigest(),same_original_batch_contexts_and_MR=True,no_new_sampling=True,no_candidate_or_repair_selection=True,change='first PAY interface mismatch PER actualsourcephase instead of wholecircuit; add exact parked6bit rail snapshots at all2 already bound source loan-out sites',historical_limit='wholecircuit latch checkpoint preserves first local violation even when a later global stage cancels it; it can hide later otherphase violations',files={str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest()for p in[r/'tool/src/phase_payload_runtime.rs',r/'tool/src/bin/current_phase_payload.rs']}),indent=2)+'\n')
