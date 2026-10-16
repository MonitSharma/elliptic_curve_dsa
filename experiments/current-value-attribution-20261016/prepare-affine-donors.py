from pathlib import Path
import json,hashlib
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016');d=r/'tool/src/bin'
source=r.parent/'value-carry-contracts-20261016/support-original.rs';s=source.read_text();(r/'donor-support-original.rs').write_text(s)
s+='''
impl Support {
pub(super) fn stable_relations(&self,eligible:&[usize])->Vec<(usize,bool,Vec<usize>,Vec<usize>)>{
use std::collections::HashMap;
fn sx(a:&[u64],b:&[u64])->Vec<u64>{let mut out=Vec::new();let(mut i,mut j)=(0,0);while i<a.len()||j<b.len(){if j==b.len()||(i<a.len()&&a[i]<b[j]){out.push(a[i]);i+=1;}else if i==a.len()||b[j]<a[i]{out.push(b[j]);j+=1;}else{i+=1;j+=1;}}out}
type Row=(Vec<u64>,bool,Vec<u64>);let mut basis:HashMap<u64,Row>=HashMap::new();let mut out=Vec::new();let nb=self.bits.len()as u64;
for (domain,id) in (0..self.bits.len()).map(|b|(false,b)).chain(eligible.iter().copied().map(|q|(true,q))){
let value=if domain{&self.qubits[id]}else{&self.bits[id]};let mut atoms=value.atoms.clone();let mut constant=value.constant;let mut rhs=if domain{vec![]}else{vec![id as u64]};
while let Some(&pivot)=atoms.last(){if let Some((row,c,ids))=basis.get(&pivot){atoms=sx(&atoms,row);constant^=*c;rhs=sx(&rhs,ids);}else{break}}
if atoms.is_empty(){if domain{out.push((id,constant,rhs.iter().filter(|x|**x>=nb).map(|x|(*x-nb)as usize).collect(),rhs.iter().filter(|x|**x<nb).map(|x|*x as usize).collect()));}}
else{if domain{rhs=sx(&rhs,&[nb+id as u64]);}basis.insert(*atoms.last().unwrap(),(atoms,constant,rhs));}
}out
}}
'''
(d/'donor_support.rs').write_text(s)
main=(r.parent/'value-carry-contracts-20261016/support_donors.rs').read_text().split('fn main(){')[0].replace('mod support;','#[path="donor_support.rs"]mod support;')
main+='''fn main(){let root="/home/hclau/ecdsa_research/current-value-attribution-20261016";let ops=load("/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin");let v:serde_json::Value=serde_json::from_slice(&std::fs::read(format!("{root}/n2-loan-family.json")).unwrap()).unwrap();let mut queries=std::collections::BTreeMap::new();for f in v["families"].as_array().unwrap(){let start=f["whole_borrow_interval"][0].as_u64().unwrap()as usize;let end=f["whole_borrow_interval"][1].as_u64().unwrap()as usize;let mut touched=std::collections::BTreeSet::new();for o in &ops[start..end]{for q in [o.q_control1,o.q_control2,o.q_target]{if q.0!=u64::MAX{touched.insert(q.0 as usize);}}}let eligible:Vec<_>=(0..1234).filter(|q|!touched.contains(q)).collect();queries.insert(start,(f["phase"].as_str().unwrap().to_string(),end,eligible));}let mut support=support::Support::new(&ops);let start=std::time::Instant::now();for(at,o)in ops.iter().enumerate(){if let Some((phase,end,eligible))=queries.remove(&at){let relations=support.stable_relations(&eligible);println!("{}",serde_json::json!({"at":at,"end":end,"phase":phase,"eligible_quantum_untouched_full_window":eligible,"exact_relations":relations,"seconds":start.elapsed().as_secs_f64(),"no_rewrites_applied":true}));if queries.is_empty(){break}}let _=support.step(o);}assert!(queries.is_empty());}
'''
(d/'affine_loan_donors.rs').write_text(main)
(r/'affine-donor-source.json').write_text(json.dumps(dict(immutable_source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),query='Gaussian span of CURRENT classical bits plus stable untouched quantum wires; dependent quantum wire is never inserted into RHS basis; constants allowed; all original ops replayed, rewrites ignored',files={str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest()for p in[d/'donor_support.rs',d/'affine_loan_donors.rs']}),indent=2)+'\n')
