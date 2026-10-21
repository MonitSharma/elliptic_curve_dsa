"""Prepare a research-only universal proof for reusing the original value mask.

This never edits the frozen candidate or enables nonce rejection. It verifies
the public parent's 27 retained products and zero row, then reproduces our
769 copy removals and four retained products with the already tested kernels.
"""
import hashlib, json, re, subprocess
from pathlib import Path
root = Path(__file__).resolve().parent
out = root / 'parent4-transfer'
out.mkdir(exist_ok=False)
scan = (root / 'scan.rs').read_text()
prefix = scan[:scan.index('fn main(){')]
semantics = scan[scan.index('  match o.kind {'):scan.index('  if i%1000000==0')]
body = r'''
fn audit(ops:&[Op],leases:&[[u64;9]],zeros:&[usize],cap:usize){
 let no=u64::MAX;
 let nq=ops.iter().flat_map(|o|[o.q_target.0,o.q_control1.0,o.q_control2.0]).filter(|x|*x!=no).max().unwrap()as usize+1;
 let nb=ops.iter().flat_map(|o|[o.c_target.0,o.c_condition.0]).filter(|x|*x!=no).max().unwrap()as usize+1;
 let mut alg=Algebra{next:1,products:HashMap::new(),cap,truncations:0};
 let(mut q,mut c)=initial_inputs(ops,nq,nb,&mut alg);let mut base=vec![0];let mut stack=vec![];
 let starts:HashMap<_,_>=leases.iter().map(|s|(s[0]as usize,s)).collect();
 let ends:HashMap<_,_>=leases.iter().map(|s|(s[1]as usize,s)).collect();
 assert_eq!(starts.len(),leases.len());assert_eq!(ends.len(),leases.len());
 assert!(starts.keys().all(|i|!ends.contains_key(i)));
 let mut expected:HashMap<usize,E>=HashMap::new();let mut active:HashMap<u64,usize>=HashMap::new();
 let zeros:HashSet<_>=zeros.iter().copied().collect();let mut checked_zero=0;let mut checked_end=0;
 for(i,o)in ops.iter().enumerate(){
  if o.kind==K::AppendToRegister||o.kind==K::Register{continue;}
  if o.kind==K::PushCondition{stack.push(base.clone());base=alg.and(&base,&c[o.c_condition.0 as usize]);continue;}
  if o.kind==K::PopCondition{base=stack.pop().unwrap();continue;}
  let eff=if o.c_condition.0==no{base.clone()}else{alg.and(&base,&c[o.c_condition.0 as usize])};
  let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let b=o.q_control2.0 as usize;let ct=o.c_target.0 as usize;
  let product=if o.kind==K::CCX{Some(alg.and(&q[a],&q[b]))}else{None};
  if zeros.contains(&i){assert_eq!(o.kind,K::CCX);let v=alg.and(product.as_ref().unwrap(),&eff);assert!(v.is_empty(),"unproved zero row {i}");checked_zero+=1;}
  if let Some(s)=starts.get(&i){
   assert_eq!(eff,vec![0],"unknown start guard {i}");assert_eq!(o.kind,K::CCX);
   assert_eq!([o.q_control2.0,o.q_control1.0,o.q_target.0],[s[3],s[4],s[5]]);
   assert!(q[s[2]as usize].is_empty(),"unclean donor at {i}");
   assert!(!active.contains_key(&s[2]));assert!(s[0]<s[1]);
   active.insert(s[2],i);expected.insert(i,product.clone().unwrap());
  }
  if let Some(s)=ends.get(&i){
   assert_eq!(eff,vec![0],"unknown end guard {i}");assert_eq!(o.kind,K::CCX);
   assert_eq!([o.q_control2.0,o.q_control1.0,o.q_target.0],[s[6],s[7],s[8]]);
   assert_eq!(product.as_ref().unwrap(),&expected[&(s[0]as usize)],"unequal product at {i}");
   assert_eq!(active.get(&s[2]),Some(&(s[0]as usize)));checked_end+=1;
  }
  if !eff.is_empty(){for w in [o.q_control2.0,o.q_control1.0,o.q_target.0]{assert!(!active.contains_key(&w),"donor touched at {i}");}}
  if let Some(s)=ends.get(&i){active.remove(&s[2]);}
  __SEMANTICS__
  if i%2000000==0{eprintln!("audited {i} end_proofs={checked_end} zero_proofs={checked_zero}");}
 }
 assert!(stack.is_empty()&&active.is_empty());assert_eq!(checked_end,leases.len());assert_eq!(checked_zero,zeros.len());
}
fn main(){
 let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),5,"baseline public_parent leases_json receipt");
 let base=io::load_ops(&args[1]);let parent=io::load_ops(&args[2]);
 assert_eq!(base.len(),17891821);assert_eq!(parent.len(),17891901);
 assert_eq!(hash(&base[..base.len()-96]),"c143e90580bb0c6f6a12996a50147c179c4fdfe3a50d8af85350bf9e6d755e04");
 assert_eq!(hash(&parent),"429af1c31b54064e17e7602be516b519c066c241e218d56f002287ea02b16842");
 let leases:Vec<[u64;9]>=serde_json::from_str(&std::fs::read_to_string(&args[3]).unwrap()).unwrap();assert_eq!(leases.len(),27);
 audit(&base,&leases,&[],8192);
 let no=u64::MAX;let nb=base.iter().flat_map(|o|[o.c_target.0,o.c_condition.0]).filter(|x|*x!=no).max().unwrap()+1;assert_eq!(nb,54995);
 let starts:HashMap<_,_>=leases.iter().map(|s|(s[0]as usize,s)).collect();let ends:HashMap<_,_>=leases.iter().map(|s|(s[1]as usize,s)).collect();
 let mut generated=Vec::with_capacity(parent.len()+1);
 for(i,o)in base[..base.len()-96].iter().enumerate(){
  if let Some(s)=starts.get(&i){let mut fill=*o;fill.q_target=QubitId(s[2]);generated.push(fill);generated.push(make(K::CX,no,s[2],s[5],no,no));}
  else if let Some(s)=ends.get(&i){generated.push(make(K::CX,no,s[2],s[8],no,no));generated.push(make(K::Hmr,no,no,s[2],nb,no));generated.push(make(K::CZ,no,s[6],s[7],no,nb));}
  else{generated.push(*o);}
 }
 assert_eq!(hash(&generated),"468e86dd1628976643d42b4bb50bdb8c43211f4d29bfbc3df60b11f7342ac619");
 generated.extend_from_slice(&parent[parent.len()-96..]);
 audit(&generated,&[],&[17876252],8192);
 generated.remove(17876252);assert_eq!(generated,parent);
 for s in [&base[base.len()-96..],&parent[parent.len()-96..]]{for pair in s.chunks_exact(2){assert_eq!(pair[0],pair[1]);assert_eq!(pair[0].kind,K::X);assert!(pair[0].q_target.0<=1);}}
 let result=serde_json::json!({"status":"PUBLIC_PARENT_EXTENSION_UNIVERSAL_AUDIT_PASS","base_pre_tail_sha3_256":hash(&base[..base.len()-96]),"parent_sha3_256":hash(&parent),"retained_products":leases.len(),"zero_rows":1,"no_sampled_inputs":true,"statement":"The 27 unconditional products have exact equal Boolean expressions, clean untouched donors and fresh private measurement/phase correction. The removed CCX has zero effective product for every input and measurement assignment. Reconstructed output equals the exact public parent bytes."});
 std::fs::write(&args[4],serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("PUBLIC_PARENT_EXTENSION_UNIVERSAL_AUDIT_PASS");
}
'''.replace('__SEMANTICS__', semantics)
(out / 'verify.rs').write_text(prefix + body)
(out / 'io.rs').write_text((root / 'io.rs').read_text())
cargo = (root / 'Cargo.toml').read_text().split('[[bin]]')[0]
cargo = cargo.replace('product_pareto_exact', 'parent4_transfer_proof')
(out / 'Cargo.toml').write_text(cargo + '\n[[bin]]\nname="verify_parent_extension"\npath="verify.rs"\n\n[profile.release]\nopt-level=3\n')
text = (root / 'parent/src/point_add/retained_products.rs').read_text()
rows = json.loads(text.split('=&', 1)[1].split(';', 1)[0])
assert len(rows) == 27 and all(len(r) == 10 for r in rows)
(out / 'leases.json').write_text(json.dumps([r[:9] for r in rows], indent=2) + '\n')
manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
(out / 'PROOF-SOURCE.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('Research verifier prepared; no nonce rejection enabled.', flush=True)
