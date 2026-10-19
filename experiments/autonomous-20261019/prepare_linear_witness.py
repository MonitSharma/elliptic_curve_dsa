"""Prepare bounded exact linear spans of current wires, never value sampling."""
from pathlib import Path
import hashlib,json,shutil
ws=Path(__file__).resolve().parent.parent;old=ws/'product-pair-witness-20261020';r=ws/'product-linear-witness-20261020'
assert not r.exists();r.mkdir()
for p in old.glob('*.rs'):shutil.copy2(p,r/p.name)
(r/'linear.rs').write_text('''// Every row is an exact current-wire identity. Dropping rows only loses opportunities.
#[derive(Clone,Debug)]struct LinearRow{p:P,wires:BTreeSet<usize>,constant:bool}
struct LinearWitnesses{rows:std::collections::BTreeMap<M,LinearRow>,reverse:std::collections::HashMap<usize,BTreeSet<M>>,term_limit:usize,wire_limit:usize}
impl Default for LinearWitnesses{fn default()->Self{Self{rows:Default::default(),reverse:Default::default(),term_limit:1024,wire_limit:32}}}
fn xor_support(a:&BTreeSet<usize>,b:&BTreeSet<usize>)->BTreeSet<usize>{a.symmetric_difference(b).copied().collect()}
fn nonconstant(p:&P)->(P,bool){let mut out=p.clone();let c=out.first().is_some_and(|m|m.is_empty());if c{out.remove(0);}(out,c)}
impl LinearWitnesses{
 fn reduce(&self,mut row:LinearRow)->Option<LinearRow>{
  while let Some(pivot)=row.p.last(){let Some(other)=self.rows.get(pivot)else{break};
   row.p=exact_xor(&row.p,&other.p);row.wires=xor_support(&row.wires,&other.wires);row.constant^=other.constant;
   if row.p.len()>self.term_limit||row.wires.len()>self.wire_limit{return None;}
  }Some(row)
 }
 fn insert(&mut self,q:usize,value:&P){
  let(p,constant)=nonconstant(value);if p.is_empty()||p.len()>self.term_limit{return;}
  let Some(row)=self.reduce(LinearRow{p,wires:BTreeSet::from([q]),constant})else{return;};
  let Some(pivot)=row.p.last().cloned()else{return;};assert!(!self.rows.contains_key(&pivot));
  for &wire in &row.wires{assert!(self.reverse.entry(wire).or_default().insert(pivot.clone()));}
  self.rows.insert(pivot,row);
 }
 fn invalidate(&mut self,q:usize){
  let pivots=self.reverse.remove(&q).unwrap_or_default();
  for pivot in pivots{let row=self.rows.remove(&pivot).expect("registered pivot");
   for wire in row.wires{if wire==q{continue;}let members=self.reverse.get_mut(&wire).expect("registered support");assert!(members.remove(&pivot));if members.is_empty(){self.reverse.remove(&wire);}}
  }
 }
 fn find(&self,p:&P,a:usize,b:usize,t:usize)->Option<(Vec<usize>,bool)>{
  let(p,constant)=nonconstant(p);if p.is_empty()||p.len()>self.term_limit{return None;}
  let row=self.reduce(LinearRow{p,wires:BTreeSet::new(),constant})?;
  if !row.p.is_empty()||row.wires.is_empty()||[a,b,t].iter().any(|w|row.wires.contains(w)){return None;}
  Some((row.wires.into_iter().collect(),row.constant))
 }
}
''',newline='\n')
p=r/'anf.rs';s=p.read_text();s=s.replace('include!("witness.rs");','include!("witness.rs");\ninclude!("linear.rs");')
needle='fn scan_with_modes(v:&[Op],alg:&mut Algebra,use_witnesses:bool,use_pairs:bool)->(Vec<Op>,Vec<serde_json::Value>){';assert s.count(needle)==1
s=s.replace(needle,needle+'scan_with_linear(v,alg,use_witnesses,use_pairs,std::env::var("ANF_LINEAR_WITNESSES").unwrap_or_else(|_|"0".into())=="1")}\nfn scan_with_linear(v:&[Op],alg:&mut Algebra,use_witnesses:bool,use_pairs:bool,use_linear:bool)->(Vec<Op>,Vec<serde_json::Value>){')
needle='let mut base=one();';assert s.count(needle)==1;s=s.replace(needle,'let mut linear=LinearWitnesses::default();if use_witnesses&&use_linear{for (slot,value)in q.iter().enumerate(){linear.insert(slot,value);}}\n '+needle)
needle='increment=Some(ab);';assert s.count(needle)==1
s=s.replace(needle,'''if use_witnesses&&use_linear&&!eff.is_empty()&&replacement.as_ref().is_some_and(|x|x.kind==K::CCX){
    if let Some((controls,complement))=linear.find(&raw_product,a,b,t){
     let mut gates=vec![];for &w in &controls{let mut x=*o;x.kind=K::CX;x.q_control2=QubitId(NO);x.q_control1=QubitId(w as u64);x.validate();gates.push(x);}
     replacement=gates.pop();pair_prefix.extend(gates);
     if complement{let mut z=*o;z.kind=K::X;z.q_control1=QubitId(NO);z.q_control2=QubitId(NO);z.validate();prefix=Some(z);}
     sites.push(serde_json::json!({"op":i,"kind":"exact_current_wire_linear_product","witnesses":controls,"complement":complement,"product":raw_product,"witness_values":controls.iter().map(|&w|q[w].clone()).collect::<Vec<_>>(),"guard":eff}));
    }
   }
increment=Some(ab);''')
needle='for &slot in &changed{witnesses.remove(slot,&q[slot]);}';assert s.count(needle)==1;s=s.replace(needle,needle+'if use_witnesses&&use_linear{for &slot in &changed{linear.invalidate(slot);}}')
needle='for &slot in &changed{witnesses.insert(slot,&q[slot]);}';assert s.count(needle)==1;s=s.replace(needle,needle+'if use_witnesses&&use_linear{for &slot in &changed{linear.insert(slot,&q[slot]);}}')
s+='\n#[cfg(test)] #[path="tests_linear.rs"] mod linear_tests;\n';p.write_text(s,newline='\n')
(r/'tests_linear.rs').write_text('''use super::*;
use quantum_ecc::sim::Simulator;
struct Fixed(u8);impl sha3::digest::XofReader for Fixed{fn read(&mut self,o:&mut[u8]){o.fill(self.0);}}
fn algebra()->Algebra{Algebra{next:1,cap:256,degree:12,cuts:0}}
fn gate(k:K,a:u64,b:u64,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(a);o.q_control2=QubitId(b);o.q_target=QubitId(t);o}
fn fixture()->Vec<Op>{(0..4).map(|t|{let mut o=gate(K::AppendToRegister,NO,NO,t);o.r_target.0=0;o}).collect()}
fn run(v:&[Op])->(Vec<Op>,Vec<serde_json::Value>){scan_with_linear(v,&mut algebra(),true,true,true)}
fn n(s:&[serde_json::Value])->usize{s.iter().filter(|x|x["kind"]=="exact_current_wire_linear_product").count()}
fn paired(v:&[Op],out:&[Op]){for byte in [0,255,0xa5,0x5a]{for input in 0..32{let mut ra=Fixed(byte);let mut rb=Fixed(byte);let mut a=Simulator::new(10,2,&mut ra);let mut b=Simulator::new(10,2,&mut rb);for q in 0..4{a.qubits[q]=input>>q&1;}a.bits[0]=input>>4&1;a.phase=0xa55a;b.qubits.clone_from(&a.qubits);b.bits.clone_from(&a.bits);b.phase=a.phase;a.apply_iter(v.iter());b.apply_iter(out.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.bits,b.bits);assert_eq!(a.phase,b.phase);}}}
fn held()->Vec<Op>{let mut v=fixture();v.extend([gate(K::CCX,0,1,4),gate(K::CX,2,NO,4),gate(K::CX,3,NO,4)]);v}
#[test]fn three_wire_product_and_complement_preserve_every_input(){for complement in [false,true]{let mut v=held();if complement{v.push(gate(K::X,NO,NO,4));}v.push(gate(K::CCX,0,1,5));let(out,s)=run(&v);assert_eq!(n(&s),1);assert_eq!(s.last().unwrap()["witnesses"].as_array().unwrap().len(),3);assert_eq!(s.last().unwrap()["complement"],complement);paired(&v,&out);let(disabled,_)=scan_with_linear(&v,&mut algebra(),true,true,false);assert_eq!(disabled,v);}}
#[test]fn guarded_linear_replacement_retains_condition(){let mut v=held();let mut c=Op::empty();c.kind=K::AppendToRegister;c.c_target.0=0;c.r_target.0=1;v.push(c);let mut g=gate(K::CCX,0,1,5);g.c_condition.0=0;v.push(g);let(out,s)=run(&v);assert_eq!(n(&s),1);paired(&v,&out);}
#[test]fn target_is_excluded_from_its_own_linear_product(){let mut v=held();v.push(gate(K::CCX,0,1,4));let(out,s)=run(&v);assert_eq!(n(&s),0);paired(&v,&out);}
#[test]fn reset_and_measurement_invalidate_old_support(){for kind in [K::R,K::Hmr]{let mut v=held();let mut g=gate(kind,NO,NO,4);if kind==K::Hmr{g.c_target.0=0;}v.extend([g,gate(K::CCX,0,1,5)]);let(out,s)=run(&v);assert_eq!(n(&s),0);paired(&v,&out);}}
#[test]fn swap_tracks_current_wire_provenance(){let mut v=held();v.extend([gate(K::Swap,4,NO,6),gate(K::CCX,0,1,5)]);let(out,s)=run(&v);assert_eq!(n(&s),1);assert!(s.last().unwrap()["witnesses"].as_array().unwrap().contains(&serde_json::json!(6)));paired(&v,&out);}
fn p(mask:usize)->P{(0..6).filter(|i|mask>>(i)&1!=0).map(|i|if i==0{vec![]}else{vec![i as u32]}).collect()}
fn check_rows(index:&LinearWitnesses,values:&[P]){for row in index.rows.values(){let mut actual=vec![];for &w in &row.wires{actual=exact_xor(&actual,&values[w]);}if row.constant{actual=exact_xor(&actual,&one());}assert_eq!(actual,row.p);}for query in 1..64{let target=p(query);if let Some((w,c))=index.find(&target,99,98,97){let mut actual=vec![];for q in w{actual=exact_xor(&actual,&values[q]);}if c{actual=exact_xor(&actual,&one());}assert_eq!(actual,target);}}}
#[test]fn exhaustive_small_linear_values_and_mutations_never_use_stale_rows(){for seed in 0..64{let mut values=vec![p(seed),p(seed^7),p(seed^19),p(seed^41)];let mut index=LinearWitnesses::default();for(i,v)in values.iter().enumerate(){index.insert(i,v);}check_rows(&index,&values);for w in 0..4{index.invalidate(w);values[w]=p((seed*3+w*7)%64);index.insert(w,&values[w]);check_rows(&index,&values);}}}
#[test]fn bounded_queries_drop_opportunities_without_atoms_or_assumptions(){let mut index=LinearWitnesses::default();index.wire_limit=1;let values=vec![p(2),p(4),p(8)];for(i,v)in values.iter().enumerate(){index.insert(i,v);}assert!(index.find(&p(14),99,98,97).is_none());check_rows(&index,&values);index.term_limit=1;index.insert(7,&p(62));assert!(index.rows.values().all(|r|!r.wires.contains(&7)));}
#[test]fn invalidating_one_wire_removes_all_and_only_dependent_rows(){let mut index=LinearWitnesses::default();let values=vec![p(6),p(10),p(18),p(34)];for(i,v)in values.iter().enumerate(){index.insert(i,v);}let surviving=index.rows.iter().filter(|(_,r)|!r.wires.contains(&1)).map(|(k,r)|(k.clone(),r.p.clone())).collect::<Vec<_>>();index.invalidate(1);assert!(index.rows.values().all(|r|!r.wires.contains(&1)));for(k,p)in surviving{assert_eq!(index.rows[&k].p,p);}check_rows(&index,&values);}
''',newline='\n')
(r/'.gitignore').write_text('/*.bin\n')
(r/'STATUS.md').write_text('''# Exact sparse linear witnesses over current qubit values

Prepared source method, not a gate/nonce/benchmark result. Generalize exact
one/two-wire products to a bounded sparse linear span of current ANF values.
Every row has explicit physical-wire provenance and a constant. On a wire
write, remove ALL rows depending on it before inserting its new value.
Never infer a zero from a missing pivot, size limit or dropped row. Limits:
1024 terms/32 wires per row/query, fixed before whole-source observation.
No allocated abstract atoms/cuts in row reductions or queries. A successful
query emits CNOTs and optional X under each original classical condition;
exclude target and original control wires. Original abstract execution stays
unchanged, so future Boolean/phase operations retain the same values.
No new width, reset or measurement. Existing22 and8 new independent tests;
complete disabled-mode report/hash control and512 protected transcript shots
on changed source. Universal source-bound proofs/native reproduction/own gate
remain required for any positive result. One local CPU/12GiB, serial jobs.
''')
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
(r/'PREPARATION.json').write_text(json.dumps({'source_files':{p.name:sha(p) for p in r.glob('*.rs')},'parent_source':'product-pair-witness-20261020','term_limit':1024,'wire_limit':32,'input_raw_sha3_256':'d343ca717c726c9136505edb1ba3602a58f7bfe063151d8a9e82b4f39d71a6a5','no_gate_or_nonce':True},indent=2)+'\n')
print('Prepared bounded exact sparse linear witness source and eight controls; not built or launched')
