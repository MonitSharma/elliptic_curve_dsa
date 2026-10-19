import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'product-anf256-20261019'
s=(old/'anf.rs').read_text();s=s.replace('fn scan(v:&[Op],alg:&mut Algebra)->(Vec<Op>,Vec<serde_json::Value>){','include!("witness.rs");\nfn scan(v:&[Op],alg:&mut Algebra)->(Vec<Op>,Vec<serde_json::Value>){scan_with_witness(v,alg,std::env::var("ANF_WITNESSES").unwrap_or_else(|_|"1".into())=="1")}\nfn scan_with_witness(v:&[Op],alg:&mut Algebra,use_witnesses:bool)->(Vec<Op>,Vec<serde_json::Value>){')
needle=' let mut base=one();let mut stack=vec![];let mut out=vec![];let mut sites=vec![];';assert s.count(needle)==1
s=s.replace(needle,' let mut witnesses=Witnesses::default();if use_witnesses{for (slot,value)in q.iter().enumerate(){witnesses.insert(slot,value);}}\n'+needle)
s=s.replace('let mut replacement=Some(*o);let mut increment=None;','let mut replacement=Some(*o);let mut increment=None;let mut prefix=None;')
assert s.count('let ab=alg.and(&q[a],&q[b]);let ab=alg.and(&eff,&ab);')==1
s=s.replace('let ab=alg.and(&q[a],&q[b]);let ab=alg.and(&eff,&ab);','let raw_product=alg.and(&q[a],&q[b]);let ab=alg.and(&eff,&raw_product);')
needle='   }increment=Some(ab);';assert s.count(needle)==1
extra='''
   if use_witnesses&&!eff.is_empty()&&replacement.as_ref().is_some_and(|x|x.kind==K::CCX){
    if let Some((w,complement))=witnesses.find(&raw_product,a,b,t,alg.cap){
     let mut x=*o;x.kind=K::CX;x.q_control2=QubitId(NO);x.q_control1=QubitId(w as u64);x.validate();replacement=Some(x);
     if complement{let mut z=*o;z.kind=K::X;z.q_control1=QubitId(NO);z.q_control2=QubitId(NO);z.validate();prefix=Some(z);}
     sites.push(serde_json::json!({"op":i,"kind":"exact_current_wire_product","witness":w,"complement":complement,"guard":eff,"product":raw_product,"witness_value":q[w]}));
    }
   }
'''
s=s.replace(needle,'   }'+extra+'increment=Some(ab);')
s=s.replace('  if let Some(o)=replacement{out.push(o);}','  if let Some(x)=prefix{out.push(x);}\n  if let Some(o)=replacement{out.push(o);}')
needle='  match o.kind{';assert s.count(needle)==1
s=s.replace(needle,'  let mut changed=if use_witnesses{match o.kind{K::Swap=>vec![a,t],K::X|K::CX|K::CCX|K::R|K::Hmr=>vec![t],_=>vec![]}}else{vec![]};changed.sort_unstable();changed.dedup();for &slot in &changed{witnesses.remove(slot,&q[slot]);}\n'+needle)
needle='  if i%1_000_000==0';assert s.count(needle)==1;s=s.replace(needle,'  for &slot in &changed{witnesses.insert(slot,&q[slot]);}\n'+needle)
s+='\n#[cfg(test)] #[path="tests_witness.rs"] mod witness_tests;\n';(r/'anf.rs').write_text(s,newline='\n')
for name in ['io.rs','factor_trace.rs','tests_large.rs']:shutil.copy2(old/name,r/name)
(r/'PREPARATION.json').write_text(json.dumps({'status':'SOURCE_ONLY_CURRENT_WIRE_ANF_WITNESS_PREPARED','parent_anf_source_sha256':hashlib.sha256((old/'anf.rs').read_bytes()).hexdigest(),'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in r.glob('*.rs')},'source_frozen_input':'17c767f514ca98ad02d4da9e5b1dbedf67189e5c70b7b15916adc0f0c2f0a7f7','gate_or_nonce_started':False},indent=2)+'\n')
