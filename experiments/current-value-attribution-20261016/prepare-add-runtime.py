from pathlib import Path
import json,hashlib
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016')
assert (r/'add-markers.exit').read_text().strip()=='0'
assert (r/'raw-add-builder.sha256').read_text().split()[0]=='ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69'
s=(r/'map-final-markers.py').read_text().replace("'raw-markers.jsonl'","'raw-add-markers.jsonl'").replace("'actual-markers.json'","'actual-add-markers.json'")
(r/'map-add-markers.py').write_text(s)
s=(r/'tool/src/payload_runtime.rs').read_text()
top='''
#[derive(Clone)]
struct Add {at:usize,id:usize,before:bool,phase:String,tick:usize,rev:bool,b:Vec<QubitId>,acc:Vec<QubitId>,carry:Option<QubitId>}
static ADDS:Mutex<Vec<Add>>=Mutex::new(Vec::new());
'''
s=s.replace('pub fn run(ops:&[Op]){',top+'\npub fn run(ops:&[Op]){\nlet adds=ADDS.lock().unwrap().clone();')
needle='let selected:Vec<bool>=(0..64).map(|lane|';assert s.count(needle)==1
targets=[8409,23131,41019,49035,68031,90346,105657,112095,123940,126544,178414,218737,235473,246936]
s=s.replace(needle,f'let selected_shots:[usize;14]={targets};if !selected_shots.iter().any(|shot|shot/64==batch){{continue;}}\n'+needle)
s=s.replace('k[4]=="1"','selected_shots.contains(&(batch*64+lane))')
needle='sim.apply_observed(ops.iter(),|idx,s,_,_|{';assert s.count(needle)==1
hook='''
while add_cursor<adds.len()&&adds[add_cursor].at==idx{let m=&adds[add_cursor];add_cursor+=1;
if m.before{add_entries.insert(m.id,(0..64).map(|lane|if selected[lane]{(unsigned(&m.b,&s.qubits,lane),unsigned(&m.acc,&s.qubits,lane))}else{(U256::ZERO,U256::ZERO)}).collect::<Vec<_>>());}
else{let values=add_entries.remove(&m.id).unwrap();for &lane in &tracked{let(b,a)=values[lane];let width=m.acc.len();let(sum,overflow)=a.overflowing_add(b);let carry=if width==256{u64::from(overflow)}else{u64::from(sum.bit(width))};let want=if width==256{sum}else{sum&((U256::from(1)<<width)-U256::from(1))};let got=unsigned(&m.acc,&s.qubits,lane);let got_b=unsigned(&m.b,&s.qubits,lane);let got_carry=s.qubits[m.carry.unwrap().0 as usize]>>lane&1;
if got!=want||got_b!=b||got_carry!=carry{eprintln!("ADD_EVENT shot={} phase={} tick={} rev={} at={} id={} width={} a={a:#x} b={b:#x} got={got:#x} want={want:#x} got_b={got_b:#x} carry={carry} got_carry={got_carry} delta={:#x}",batch*64+lane,m.phase,m.tick,m.rev,m.at,m.id,width,got.wrapping_sub(want));}
}}}
'''
s=s.replace(needle,'let mut add_cursor=0;let mut add_entries=HashMap::new();\n'+needle+hook)
s=s.replace('assert_eq!(cursor,marks.len());','assert_eq!(add_cursor,adds.len());assert!(add_entries.is_empty());assert_eq!(cursor,marks.len());')
s=s.replace("let(l,e,nm,sh,m,cst,c)=vs[lane];let got=", "let(l,e,nm,sh,m,cst,c)=vs[lane];if f.phase==\"divide\"&&(130..=132).contains(&f.t){eprintln!(\"FOLD_INPUT shot={} tick={} at={} width={w} L={l} E={e} Nm={nm} shift={sh} m={m} C={cst} c={c}\",batch*64+lane,f.t,f.at);}let got=")
needle='}}run(ops);';assert s.count(needle)==1
loader='''}}
let extra:serde_json::Value=serde_json::from_str(&std::fs::read_to_string("/home/hclau/ecdsa_research/current-value-attribution-20261016/actual-add-markers.json").unwrap()).unwrap();
for m in extra["markers"].as_array().unwrap(){ADDS.lock().unwrap().push(Add{at:m["at"].as_u64().unwrap()as usize,id:m["id"].as_u64().unwrap()as usize,before:m["before"].as_bool().unwrap(),phase:m["phase"].as_str().unwrap().to_string(),tick:m["tick"].as_u64().unwrap()as usize,rev:m["rev"].as_bool().unwrap(),b:ids(m,"b"),acc:ids(m,"acc"),carry:m["carry"].as_u64().map(QubitId)});}run(ops);'''
s=s.replace(needle,loader);(r/'tool/src/add_runtime.rs').write_text(s)
s=(r/'tool/src/bin/current_payload.rs').read_text().replace('../payload_runtime.rs','../add_runtime.rs');(r/'tool/src/bin/current_adds.rs').write_text(s)
(r/'ADD-REPLAY-DECLARATION.json').write_text(json.dumps(dict(status='FIXED DIAGNOSTIC BEFORE ADD OBSERVATION',target_shots=targets,selection='all14 previously observed current-source tick131 cases; original full64-lane batch contexts and original MR streams retained',source_family='ALL low_keep_add calls; entire raw stream must remain hash-identical; exact centered unique mapping only; UNKNOWN retained',no_candidate=True,no_new_sampling=True,no_repair_or_source_selection=True),indent=2)+'\n')
print('Prepared all-source-add observations and fixed14-case exact-original-context replay.')
