"""Prepare an exact two-wire XOR witness screen, independent of test packets."""
from pathlib import Path
import json,hashlib,shutil
ws=Path(__file__).resolve().parent.parent;old=ws/'product-anf-witness-20261019';r=ws/'product-pair-witness-20261020'
assert not r.exists();r.mkdir()
for p in old.glob('*.rs'):shutil.copy2(p,r/p.name)
s=(r/'witness.rs').read_text().replace('struct Witnesses(std::collections::HashMap<P,BTreeSet<usize>>);','struct Witnesses(std::collections::HashMap<P,BTreeSet<usize>>,std::collections::HashMap<M,BTreeSet<usize>>);')
a='fn insert(&mut self,q:usize,value:&P){if !value.is_empty()&&value!=&one(){self.0.entry(value.clone()).or_default().insert(q);}}'
b='fn insert(&mut self,q:usize,value:&P){if !value.is_empty()&&value!=&one(){self.0.entry(value.clone()).or_default().insert(q);for m in value.iter().filter(|m|!m.is_empty()){self.1.entry(m.clone()).or_default().insert(q);}}}'
assert a in s;s=s.replace(a,b)
a='fn remove(&mut self,q:usize,value:&P){if let Some(s)=self.0.get_mut(value){assert!(s.remove(&q));if s.is_empty(){self.0.remove(value);}}}'
b='fn remove(&mut self,q:usize,value:&P){if let Some(s)=self.0.get_mut(value){assert!(s.remove(&q));if s.is_empty(){self.0.remove(value);}}for m in value.iter().filter(|m|!m.is_empty()){let s=self.1.get_mut(m).expect("current monomial index");assert!(s.remove(&q));if s.is_empty(){self.1.remove(m);}}}'
assert a in s;s=s.replace(a,b)
s+='''
// Pure symmetric difference: queries never allocate abstract atoms or lose terms.
fn exact_xor(a:&P,b:&P)->P{let(mut i,mut j)=(0,0);let mut out=vec![];while i<a.len()||j<b.len(){if j==b.len()||(i<a.len()&&a[i]<b[j]){out.push(a[i].clone());i+=1;}else if i==a.len()||b[j]<a[i]{out.push(b[j].clone());j+=1;}else{i+=1;j+=1;}}out}
impl Witnesses{
 fn find_pair(&self,p:&P,values:&[P],a:usize,b:usize,t:usize)->Option<(usize,usize,bool)>{
  // Any nonconstant term in p occurs in exactly one member of an XOR pair.
  // Enumerating all live wires containing its rarest term is therefore complete.
  let m=p.iter().filter(|m|!m.is_empty()).min_by_key(|m|self.1.get(*m).map_or(0,|s|s.len()))?;
  let permitted=|q:usize|q!=a&&q!=b&&q!=t;
  for &u in self.1.get(m)?{if !permitted(u){continue;}let wanted=exact_xor(p,&values[u]);
   for complement in [false,true]{let mut key=wanted.clone();if complement{if key.first().is_some_and(|m|m.is_empty()){key.remove(0);}else{key.insert(0,vec![]);}}
    if let Some(&v)=self.0.get(&key).and_then(|s|s.iter().find(|&&v|v!=u&&permitted(v))){return Some((u.min(v),u.max(v),complement));}
   }
  }None
 }
}
'''
(r/'witness.rs').write_text(s,newline='\n')
p=r/'anf.rs';s=p.read_text();needle='fn scan_with_witness(v:&[Op],alg:&mut Algebra,use_witnesses:bool)->(Vec<Op>,Vec<serde_json::Value>){';assert s.count(needle)==1
s=s.replace(needle,needle+'scan_with_modes(v,alg,use_witnesses,std::env::var("ANF_PAIR_WITNESSES").unwrap_or_else(|_|"0".into())=="1")}\nfn scan_with_modes(v:&[Op],alg:&mut Algebra,use_witnesses:bool,use_pairs:bool)->(Vec<Op>,Vec<serde_json::Value>){')
s=s.replace('let mut prefix=None;','let mut prefix=None;let mut pair_prefix=vec![];')
needle='increment=Some(ab);';assert s.count(needle)==1
s=s.replace(needle,'''if use_witnesses&&use_pairs&&!eff.is_empty()&&replacement.as_ref().is_some_and(|x|x.kind==K::CCX){
    if let Some((u,w,complement))=witnesses.find_pair(&raw_product,&q,a,b,t){
     let mut x=*o;x.kind=K::CX;x.q_control2=QubitId(NO);x.q_control1=QubitId(u as u64);x.validate();pair_prefix.push(x);x.q_control1=QubitId(w as u64);x.validate();replacement=Some(x);
     if complement{let mut z=*o;z.kind=K::X;z.q_control1=QubitId(NO);z.q_control2=QubitId(NO);z.validate();prefix=Some(z);}
     sites.push(serde_json::json!({"op":i,"kind":"exact_two_wire_xor_product","witness1":u,"witness2":w,"complement":complement,"product":raw_product,"value1":q[u],"value2":q[w],"guard":eff}));
    }
   }
increment=Some(ab);''')
s=s.replace('if let Some(x)=prefix{out.push(x);}','out.extend(pair_prefix);if let Some(x)=prefix{out.push(x);}')
s+='\n#[cfg(test)] #[path="tests_pair.rs"] mod pair_tests;\n';p.write_text(s,newline='\n')
(r/'tests_pair.rs').write_text('''use super::*;
use quantum_ecc::sim::Simulator;
struct Fixed(u8);impl sha3::digest::XofReader for Fixed{fn read(&mut self,o:&mut[u8]){o.fill(self.0);}}
fn algebra()->Algebra{Algebra{next:1,cap:256,degree:12,cuts:0}}
fn gate(k:K,a:u64,b:u64,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(a);o.q_control2=QubitId(b);o.q_target=QubitId(t);o}
fn fixture()->Vec<Op>{(0..3).map(|t|{let mut o=gate(K::AppendToRegister,NO,NO,t);o.r_target.0=0;o}).collect()}
fn run(v:&[Op])->(Vec<Op>,Vec<serde_json::Value>){scan_with_modes(v,&mut algebra(),true,true)}
fn n(s:&[serde_json::Value])->usize{s.iter().filter(|x|x["kind"]=="exact_two_wire_xor_product").count()}
fn paired(v:&[Op],out:&[Op]){for byte in [0,255,0xa5,0x5a]{for input in 0..16{let mut ra=Fixed(byte);let mut rb=Fixed(byte);let mut a=Simulator::new(8,2,&mut ra);let mut b=Simulator::new(8,2,&mut rb);a.qubits[0]=input&1;a.qubits[1]=input>>1&1;a.qubits[2]=input>>2&1;a.bits[0]=input>>3&1;a.phase=0xa55a;b.qubits.clone_from(&a.qubits);b.bits.clone_from(&a.bits);b.phase=a.phase;a.apply_iter(v.iter());b.apply_iter(out.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.bits,b.bits);assert_eq!(a.phase,b.phase);}}}
#[test]fn pair_and_complement_preserve_all_boundary_inputs(){for complement in [false,true]{let mut v=fixture();v.extend([gate(K::CCX,0,1,3),gate(K::CX,2,NO,3)]);if complement{v.push(gate(K::X,NO,NO,3));}v.push(gate(K::CCX,0,1,4));let(out,s)=run(&v);assert_eq!(n(&s),1);assert_eq!(s.last().unwrap()["complement"],complement);assert_eq!(out.iter().filter(|x|x.kind==K::CCX).count(),1);paired(&v,&out);let(disabled,_)=scan_with_modes(&v,&mut algebra(),true,false);assert_eq!(disabled,v);}}
#[test]fn guarded_pair_keeps_classical_condition(){let mut v=fixture();let mut c=Op::empty();c.kind=K::AppendToRegister;c.c_target.0=0;c.r_target.0=1;v.push(c);v.extend([gate(K::CCX,0,1,3),gate(K::CX,2,NO,3)]);let mut last=gate(K::CCX,0,1,4);last.c_condition.0=0;v.push(last);let(out,s)=run(&v);assert_eq!(n(&s),1);paired(&v,&out);}
#[test]fn target_cannot_be_a_pair_member(){let mut v=fixture();v.extend([gate(K::CCX,0,1,3),gate(K::CX,2,NO,3),gate(K::CCX,0,1,3)]);let(out,s)=run(&v);assert_eq!(n(&s),0);paired(&v,&out);}
#[test]fn mutation_reset_and_measurement_invalidate_index(){for k in [K::X,K::R,K::Hmr]{let mut v=fixture();v.extend([gate(K::CCX,0,1,3),gate(K::CX,2,NO,3)]);let mut reset=gate(k,NO,NO,3);if k==K::Hmr{reset.c_target.0=0;}v.push(reset);v.push(gate(K::CCX,0,1,4));let(out,s)=run(&v);if k==K::X{assert_eq!(n(&s),1);}else{assert_eq!(n(&s),0);}paired(&v,&out);}}
#[test]fn swap_updates_both_pair_indices(){let mut v=fixture();v.extend([gate(K::CCX,0,1,3),gate(K::CX,2,NO,3),gate(K::Swap,3,NO,5),gate(K::CCX,0,1,4)]);let(out,s)=run(&v);assert_eq!(n(&s),1);assert_eq!(s.last().unwrap()["witness2"],5);paired(&v,&out);}
#[test]fn pure_query_matches_brute_force_and_does_not_cut(){let values=vec![vec![vec![1]],vec![vec![2]],vec![vec![1,2],vec![3]],vec![vec![3]],vec![vec![],vec![1,2],vec![3]]];let mut w=Witnesses::default();for(i,p)in values.iter().enumerate(){w.insert(i,p);}for p in [vec![vec![1,2]],vec![vec![1],vec![2]],vec![vec![9]]]{let actual=w.find_pair(&p,&values,99,98,97);let mut expected=false;for u in 0..values.len(){for v in u+1..values.len(){let mut x=exact_xor(&values[u],&values[v]);if x.first().is_some_and(|m|m.is_empty()){x.remove(0);}let mut target=p.clone();if target.first().is_some_and(|m|m.is_empty()){target.remove(0);}expected|=x==target;}}assert_eq!(actual.is_some(),expected);if let Some((u,v,c))=actual{let mut x=exact_xor(&values[u],&values[v]);if c{x=exact_xor(&x,&one());}assert_eq!(x,p);}}}
''',newline='\n')
(r/'.gitignore').write_text('/*.bin\n')
(r/'STATUS.md').write_text('''# Exact two-wire XOR product witnesses

Fixed new source method on the frozen copy-cache circuit. A live monomial
inverse index enumerates all wires containing the rarest nonconstant term in
the product. If P=X XOR Y (optionally complemented), that term must occur in
exactly one member; pure exact symmetric difference plus the current-value
index proves the other member. No atom/cut allocation in queries. Distinct
non-target/non-control witnesses only, original classical conditions retained.
Replace one CCX with two CX and optional X, original abstract state unchanged.
No new quantum width/reset/measurement. All prior16 controls plus6 new
exhaustive/corruption/index controls, full baseline report/stream reproduction
and512 raw full-state/phase/physical-RNG integration controls on changes.
No source/packet/cut tuning, census, nonce or score. One local CPU/12GiB.
Wait for the existing local new-input screen to finish before launching.
''')
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
(r/'PREPARATION.json').write_text(json.dumps({'new_method':'two-wire XOR current products; pure complete rare-monomial enumeration','input_raw_sha3_256':'d343ca717c726c9136505edb1ba3602a58f7bfe063151d8a9e82b4f39d71a6a5','source_files':{p.name:sha(p) for p in r.glob('*.rs')},'no_nonce_or_gate':True},indent=2)+'\n')
print('Prepared exact two-wire XOR witness source and six controls; not built/launched')
