import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'product-anf256-20261019'
s=(old/'anf.rs').read_text();begin=s.index('fn scan(v:');end=s.index('\nfn hash(',begin)
core=s[begin:end].replace('fn scan(v:&[Op],alg:&mut Algebra)->(Vec<Op>,Vec<serde_json::Value>){','fn scan_core(v:&[Op],alg:&mut Algebra,cache_enabled:bool)->(Vec<Op>,Vec<serde_json::Value>,CopyCache){')
needle=' let mut base=one();';assert core.count(needle)==1;core=core.replace(needle,' let mut cache=CopyCache::new(v,nq);\n'+needle)
core=core.replace(' for(i,o)in v.iter().enumerate(){',' for(i,o)in v.iter().enumerate(){\n  if cache_enabled{cache.touch(i,o);}')
needle='let ab=alg.and(&q[a],&q[b]);let ab=alg.and(&eff,&ab);';assert core.count(needle)==1
core=core.replace(needle,'let raw_product=alg.and(&q[a],&q[b]);let ab=alg.and(&eff,&raw_product);\n   if cache_enabled&&stack.is_empty()&&o.c_condition.0==NO{assert_eq!(eff,one());cache.observe(i,o,&raw_product,&q);}')
needle='(out,sites)\n}';assert core.count(needle)==1;core=core.replace(needle,'(out,sites,cache)\n}')
wrappers='''include!("cache.rs");
fn scan(v:&[Op],alg:&mut Algebra)->(Vec<Op>,Vec<serde_json::Value>){let(out,sites,_)=scan_core(v,alg,false);(out,sites)}
fn scan_copy(v:&[Op],alg:&mut Algebra)->(Vec<Op>,Vec<serde_json::Value>){let(_,_,cache)=scan_core(v,alg,true);let sites=cache.pairs.iter().map(|p|serde_json::json!({"first":p.first.op,"first_target":p.first.target,"last":p.last.op,"last_target":p.last.target,"storage":p.storage,"unconditional":true,"consume_target_proved_zero":true,"no_original_quantum_touch_in_closed_interval":true,"cleanup":"CX from consuming clean target; no new measurement"})).collect();eprintln!("copy_cache_pairs={} missed_no_idle={} product_keys={}",cache.pairs.len(),cache.missed_no_idle,cache.last.len());(apply_pairs(v,&cache.pairs),sites)}
'''
s=s[:begin]+wrappers+core+s[end:]
needle='let(out,sites)=scan(&v,&mut alg);';assert s.count(needle)==1;s=s.replace(needle,'let(out,sites)=if std::env::var("COPY_CACHE").unwrap_or_else(|_|"1".into())=="1"{scan_copy(&v,&mut alg)}else{scan(&v,&mut alg)};')
s+='\n#[cfg(test)] #[path="tests_cache.rs"] mod copy_cache_tests;\n';(r/'anf.rs').write_text(s,newline='\n')
for name in ['io.rs','factor_trace.rs','tests_large.rs']:shutil.copy2(old/name,r/name)
(r/'PREPARATION.json').write_text(json.dumps({'status':'SOURCE_ONLY_REVERSIBLE_COPY_CACHE_PREPARED','source_parent':hashlib.sha256((old/'anf.rs').read_bytes()).hexdigest(),'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in r.glob('*.rs')},'no_new_native_candidate_gate_nonce_or_score':True},indent=2)+'\n')
