from pathlib import Path
import shutil,json,hashlib
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016');d=r/'tool';src=d/'src';(src/'bin').mkdir(parents=True,exist_ok=True)
old=r.parent/'failure-floor-20261015/payload_trace.rs';s=old.read_text()
def change(a,b,count=1):
 global s
 assert s.count(a)==count,(a[:80],s.count(a),count);s=s.replace(a,b)
change('let root="/home/hclau/ecdsa_research/failure-floor-20261015"','let root="/home/hclau/ecdsa_research/current-value-attribution-20261016"')
change('for family in ["floor31","independent"]{','for family in ["tip431"]{')
change('let mut total_bad=0;let mut total_event=0;','''
 let ids:Vec<usize>=txt.lines().filter(|l|!l.trim().is_empty()).map(|l|l.split_whitespace().next().unwrap().parse().unwrap()).collect();
 let keys:Vec<Vec<String>>=std::fs::read_to_string(format!("{root}/packets/tip431-keys.tsv")).unwrap().lines().map(|l|l.split_whitespace().map(str::to_string).collect()).collect();
 let expected:Vec<serde_json::Value>=std::fs::read_to_string(format!("{root}/packets/expected-census.jsonl")).unwrap().lines().map(|l|serde_json::from_str(l).unwrap()).collect();
 let mut total_bad=0;let mut total_event=0;''')
oldrng='''for(batch,rows)in rows.chunks(64).enumerate(){
 let mut h=Shake256::default();h.update(b"failure-floor-20261015");h.update(family.as_bytes());h.update(&(batch as u64).to_le_bytes());let mut rng=h.finalize_xof();let mut rr=rng.clone();'''
newrng='''for(context,rows)in rows.chunks(64).enumerate(){
 let batch=ids[context*64]/64;assert_eq!(rows.len(),64);assert_eq!(expected[context]["batch"].as_u64().unwrap(),batch as u64);
 let selected:Vec<bool>=(0..64).map(|lane|{let k=&keys[context*64+lane];assert_eq!(k[0].parse::<usize>().unwrap(),batch);assert_eq!(k[1].parse::<usize>().unwrap(),lane);k[4]=="1"}).collect();
 let tracked:Vec<usize>=(0..64).filter(|lane|selected[*lane]).collect();
 let label=b"tip-4b2ec52f";let mut h=Shake256::default();h.update(b"ecdsa-research-failure-census-v1");h.update(&(label.len()as u64).to_le_bytes());h.update(label);h.update(&(batch as u64).to_le_bytes());let mut rng=h.finalize_xof();
 for lane in 0..64{for which in 0..2{let mut rb=[0u8;32];sha3::digest::XofReader::read(&mut rng,&mut rb);let wanted=U256::from_str_radix(keys[context*64+lane][which+2].trim_start_matches("0x"),16).unwrap();assert_eq!(U256::from_le_bytes(rb),wanted,"exact original input draw/MR continuation");}}
 let mut rr=rng.clone();'''
change(oldrng,newrng)
change('for lane in 0..rows.len(){','for &lane in &tracked{',s.count('for lane in 0..rows.len(){'))
change('map(|lane|[word(&m.pay[0],&s.qubits,lane),word(&m.pay[1],&s.qubits,lane)])','map(|lane|if selected[lane]{[word(&m.pay[0],&s.qubits,lane),word(&m.pay[1],&s.qubits,lane)]}else{[U256::ZERO;2]})')
change('map(|lane|(unsigned(&m.out,&s.qubits,lane),unsigned(&m.value,&s.qubits,lane),m.cin.map_or(0,|q|s.qubits[q.0 as usize]>>lane&1)))','map(|lane|if selected[lane]{(unsigned(&m.out,&s.qubits,lane),unsigned(&m.value,&s.qubits,lane),m.cin.map_or(0,|q|s.qubits[q.0 as usize]>>lane&1))}else{(U256::ZERO,U256::ZERO,0)})')
change('map(|lane|{let l=small','map(|lane|{if !selected[lane]{return(0,0,0,0,0,0,0);}let l=small')
change('rows.iter().map(|r|sub(r[1],r[3],p).mul_mod(pow(sub(r[0],r[2],p),p-U256::from(2),p),p))','rows.iter().enumerate().map(|(lane,r)|if selected[lane]{sub(r[1],r[3],p).mul_mod(pow(sub(r[0],r[2],p),p-U256::from(2),p),p)}else{U256::ZERO})')
change('assert_eq!(got,want,"fold low-window observer mismatch");','''if got!=want{eprintln!("FOLD_LOW_MISMATCH family={family} shot={} phase={} tick={} rev={} window={w} at={} low_L={l} E={e} Nm={nm} shift={sh} m={m} C={cst} got={got} want={want}",batch*64+lane,f.phase,f.t,f.rev,f.at);}''')
change('for(lane,row)in rows.iter().enumerate(){let bad=','''let expected_batch=&expected[context];let mut value_mask=0u64;
 for(lane,row)in rows.iter().enumerate(){if sim.get_register(&regs[0],lane)!=row[4]||sim.get_register(&regs[1],lane)!=row[5]{value_mask|=1u64<<lane;}}
 let mut desired=[0u64;3];for f in expected_batch["failures"].as_array().unwrap(){let lane=f["lane"].as_u64().unwrap();for(i,k)in ["value","phase","dirty"].iter().enumerate(){desired[i]|=f[*k].as_u64().unwrap()<<lane;}}
 let dirty=sim.qubits.iter().skip(512).fold(0u64,|v,q|v|q);assert_eq!([value_mask,sim.phase,dirty],desired,"exact actual-final census failure masks");assert_eq!(sim.stats.toffoli_gates,expected_batch["toffoli"].as_u64().unwrap());
 eprintln!("ATTR_BATCH batch={batch} tracked={} full64q_b_phase_T_equal=true original_census_flags_reproduced=true",tracked.len());
 for &lane in &tracked{let row=&rows[lane];let bad=''')
load='''
pub fn load_and_run(ops:&[Op]){
let raw=std::fs::read_to_string("/home/hclau/ecdsa_research/current-value-attribution-20261016/actual-markers.json").unwrap();let root:serde_json::Value=serde_json::from_str(&raw).unwrap();
let ids=|m:&serde_json::Value,key:&str|m[key].as_array().unwrap().iter().map(|x|QubitId(x.as_u64().unwrap())).collect::<Vec<_>>();
let text=|m:&serde_json::Value,key:&str|->&'static str{Box::leak(m[key].as_str().unwrap().to_string().into_boxed_str())};
for m in root["markers"].as_array().unwrap(){let at=m["at"].as_u64().unwrap()as usize;let id=m["id"].as_u64().unwrap()as usize;
 match m["family"].as_str().unwrap(){
 "payload"=>MARKS.lock().unwrap().push(Mark{at,id,before:m["before"].as_bool().unwrap(),phase:text(m,"phase"),t:m["tick"].as_u64().unwrap()as usize,rev:m["rev"].as_bool().unwrap(),skip:m["skip"].as_bool().unwrap(),pay:[ids(m,"pay0"),ids(m,"pay1")],letter:ids(m,"letter")}),
 "fold"=>FOLDS.lock().unwrap().push(Fold{at,id,before:m["before"].as_bool().unwrap(),phase:text(m,"phase"),t:m["tick"].as_u64().unwrap()as usize,rev:m["rev"].as_bool().unwrap(),acc:ids(m,"acc"),e:ids(m,"e").try_into().unwrap(),nm:ids(m,"nm").try_into().unwrap(),shift:ids(m,"shift").try_into().unwrap(),src:ids(m,"src")}),
 "stage"=>STAGES.lock().unwrap().push(Stage{at,label:text(m,"label"),x:ids(m,"x"),y:ids(m,"y"),offset:U256::from_str_radix(m["offset"].as_str().unwrap().trim_start_matches("0x"),16).unwrap()}),
 "window"=>WINDOWS.lock().unwrap().push(Window{at,id,before:m["before"].as_bool().unwrap(),inv:m["inv"].as_bool().unwrap(),shift:m["shift"].as_u64().unwrap()as usize,value:ids(m,"value"),out:ids(m,"out"),cin:m["cin"].as_u64().map(QubitId)}),
 _=>panic!("unknown marker family"),
 }}run(ops);
}
'''
(src/'payload_runtime.rs').write_text(s+load)
observed=r.parent/'prefilter-20261015/observer-tip/src/point_add/observed_sim.rs';shutil.copy2(observed,src/'observed_sim.rs')
oldtool=r.parent/'value-carry-contracts-20261016/tool'
manifest=(oldtool/'Cargo.toml').read_text().replace('sha3="0.10"','sha3="0.10"\nruint="1.12"');(d/'Cargo.toml').write_text(manifest);shutil.copy2(oldtool/'Cargo.lock',d/'Cargo.lock')
loader=(r.parent/'value-carry-contracts-20261016/support_donors.rs').read_text();a=loader.index('fn load(');b=loader.index('\nfn main()',a);loader=loader[a:b]
main='''pub use quantum_ecc::{circuit,sim};
use circuit::{Op,OperationType as K,QubitId,BitId,RegisterId};
use std::io::Read;
pub const SECP256K1_P:alloy_primitives::U256=alloy_primitives::U256::from_limbs([0xfffffffefffffc2f,0xffffffffffffffff,0xffffffffffffffff,0xffffffffffffffff]);
#[path="../observed_sim.rs"]mod observed_sim;
#[path="../payload_runtime.rs"]mod payload_runtime;
'''+loader+'''
fn main(){let ops=load("/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin");assert_eq!(ops.len(),11630716);let(nq,nb,_,regs)=circuit::analyze_ops(ops.iter());assert_eq!((nq,nb),(1234,45701));for(i,reg)in regs[..2].iter().enumerate(){for(j,q)in reg.iter().enumerate(){assert_eq!(*q,circuit::QubitOrBit::Qubit(QubitId((i*256+j)as u64)));}}payload_runtime::load_and_run(&ops);}
'''
# QubitOrBit lacks PartialEq on this protected revision: pattern-match ABI.
main=main.replace('assert_eq!(*q,circuit::QubitOrBit::Qubit(QubitId((i*256+j)as u64)));','match q{circuit::QubitOrBit::Qubit(q)=>assert_eq!(q.0,(i*256+j)as u64),_=>panic!("ABI")};')
(src/'bin/current_payload.rs').write_text(main)
(r/'runtime-source.json').write_text(json.dumps(dict(authoritative_payload_decoder_path=str(old),authoritative_payload_decoder_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),observed_simulator_path=str(observed),observed_simulator_sha256=hashlib.sha256(observed.read_bytes()).hexdigest(),actual_final_ops_only=True,source_files={str(p.relative_to(d)):hashlib.sha256(p.read_bytes()).hexdigest()for p in src.rglob('*')if p.is_file()}),indent=2)+'\n')
print('Prepared actual-final full state differential, exact original per-batch MR continuation, all431selected witnesses, signed payload/stage/window arithmetic')
