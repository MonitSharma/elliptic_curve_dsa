from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).resolve().parent;ex=a.parent;old=ex/'breakthrough-compact-context-alias-20261021';r=ex/'breakthrough-associative-prefix-20261021';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());assert all(sha(old/'local-tool'/p)==h for p,h in f['tool_source_files'].items())
for n in ['Cargo.toml','Cargo.lock','io.rs']:shutil.copyfile(old/'local-tool'/n,t/n)
p=t/'Cargo.toml';p.write_text(p.read_text().replace('name = "compact_context_alias"','name = "associative_prefix"'))
s=(old/'local-tool/discover.rs').read_text();s=s.replace('struct Expr{restricting:bool,','struct Expr{and_sums:HashMap<Vec<u32>,u32>,xor_sums:HashMap<Vec<u32>,u32>,restricting:bool,')
assert s.count('fn xor(&mut self,mut a:u32,mut b:u32)')==1 and s.count('fn and(&mut self,mut a:u32,mut b:u32)')==1
s=s.replace('fn xor(&mut self,mut a:u32,mut b:u32)','fn xor_pair(&mut self,mut a:u32,mut b:u32)').replace('fn and(&mut self,mut a:u32,mut b:u32)','fn and_pair(&mut self,mut a:u32,mut b:u32)')
new='''
impl Expr{
 // Full immutable expression keys only. Bounded expansion misses proofs; it
 // never replaces an unsupported expression by a correlated approximation.
 fn xor_leaves(&self,v:u32,terms:&mut BTreeSet<u32>,neg:&mut bool,budget:&mut usize)->bool{
  if *budget==0{return false;}*budget-=1;*neg^=v&1!=0;let v=v&!1;if v==0{return true;}
  let(k,a,b)=self.nodes[(v/2-1)as usize];if k==2{if !self.xor_leaves(a,terms,neg,budget)||!self.xor_leaves(b,terms,neg,budget){return false;}}else if !terms.insert(v){terms.remove(&v);}terms.len()<=8
 }
 fn xor(&mut self,a:u32,b:u32)->u32{
  let(mut terms,mut neg,mut budget)=(BTreeSet::new(),false,64);
  if !self.xor_leaves(a,&mut terms,&mut neg,&mut budget)||!self.xor_leaves(b,&mut terms,&mut neg,&mut budget){return self.xor_pair(a,b);}
  if terms.is_empty(){return neg as u32;}let key:Vec<_>=terms.into_iter().collect();if key.len()==1{return key[0]^(neg as u32);}
  if let Some(&v)=self.xor_sums.get(&key){return v^(neg as u32);}
  let mut value=0;for &v in &key{value=self.xor_pair(value,v);}if self.xor_sums.len()>=500000{self.xor_sums.clear();}self.xor_sums.insert(key,value);value^(neg as u32)
 }
 fn and_leaves(&self,v:u32,terms:&mut BTreeSet<u32>,budget:&mut usize)->bool{
  if *budget==0{return false;}*budget-=1;if v==1{return true;}if v>1&&v&1==0{let(k,a,b)=self.nodes[(v/2-1)as usize];if k==1{return self.and_leaves(a,terms,budget)&&self.and_leaves(b,terms,budget);}}terms.insert(v);terms.len()<=8
 }
 fn and(&mut self,a:u32,b:u32)->u32{
  let(mut terms,mut budget)=(BTreeSet::new(),64);
  if !self.and_leaves(a,&mut terms,&mut budget)||!self.and_leaves(b,&mut terms,&mut budget){return self.and_pair(a,b);}
  if terms.contains(&0)||terms.iter().any(|v|terms.contains(&(v^1))){return 0;}if terms.is_empty(){return 1;}let key:Vec<_>=terms.into_iter().collect();if key.len()==1{return key[0];}
  if let Some(&v)=self.and_sums.get(&key){return v;}let mut value=1;for &v in &key{value=self.and_pair(value,v);}if self.and_sums.len()>=500000{self.and_sums.clear();}self.and_sums.insert(key,value);value
 }
}
#[cfg(test)]mod associative_controls{
 use super::*;
 fn eval(e:&Expr,v:u32,inputs:&[u32],row:usize)->bool{if v<=1{return v==1;}let id=v&!1;let(k,a,b)=e.nodes[(id/2-1)as usize];let value=if k==0{row>>inputs.iter().position(|&x|x==id).unwrap()&1!=0}else if k==1{eval(e,a,inputs,row)&&eval(e,b,inputs,row)}else{eval(e,a,inputs,row)^eval(e,b,inputs,row)};value^(v&1!=0)}
 #[test]fn eight_atom_xor_reassociation_and_complement_are_exact(){let mut e=Expr::default();let x:Vec<_>=(0..8).map(|_|e.atom()).collect();let(mut a,mut b)=(0,0);for &v in &x{a=e.xor(a,v);}for &v in x.iter().rev(){b=e.xor(v,b);}assert_eq!(a,b);let one=e.xor(a,b^1);assert_eq!(one,1);for row in 0..256{assert_eq!(eval(&e,a,&x,row),row.count_ones()%2==1);}}
 #[test]fn eight_atom_and_reassociation_absorption_and_contradiction_are_exact(){let mut e=Expr::default();let x:Vec<_>=(0..8).map(|_|e.atom()).collect();let(mut a,mut b)=(1,1);for &v in &x{a=e.and(a,v);}for &v in x.iter().rev(){b=e.and(v,b);}assert_eq!(a,b);assert_eq!(e.and(a,x[3]),a);assert_eq!(e.and(a,x[3]^1),0);for row in 0..256{assert_eq!(eval(&e,a,&x,row),row==255);}}
 #[test]fn mixed_complemented_products_match_all_ten_atom_inputs(){let mut e=Expr::default();let x:Vec<_>=(0..10).map(|_|e.atom()).collect();let mut a=1;for &v in &x[..8]{a=e.and(a,v);}let b=e.xor(x[8],x[9]^1);let c=e.and(a,b);let d=e.xor(c,a^1);for row in 0..1024{let aa=row&255==255;let bb=(row>>8&1!=0)^(row>>9&1==0);assert_eq!(eval(&e,d,&x,row),(aa&&bb)^!aa);}}
 #[test]fn expansion_and_cache_limits_only_miss_proofs(){let mut e=Expr::default();let x:Vec<_>=(0..12).map(|_|e.atom()).collect();let(mut a,mut b)=(0,1);for &v in &x{a=e.xor(a,v);b=e.and(b,v);}e.xor_sums.clear();e.and_sums.clear();for row in 0usize..4096{assert_eq!(eval(&e,a,&x,row),row.count_ones()%2==1);assert_eq!(eval(&e,b,&x,row),row==4095);}}
}
'''
s+=new;(t/'discover.rs').write_text(s);(r/'discover.rs').write_text(s)
paths={'compact1233':ex/'breakthrough-compact-generic-repeat-20261021/compact1233.ops.bin','compact1234':ex/'breakthrough-compact-generic-repeat-20261021/compact1234.ops.bin','public1829':ex/'breakthrough-public1829-width-port-local-v4-20261020/public/ops.bin','official_ffe20':ex/'breakthrough-global-quantum-alias-v3-20261021/official-ffe20.ops.bin'}
f.update(tool_source_files={n:sha(t/n)for n in ['Cargo.toml','Cargo.lock','io.rs','discover.rs']},input_streams={n:sha(p)for n,p in paths.items()},native_controls=19,scope='Fresh exact associativity/commutativity/cancellation normalization over at most eight immutable XOR terms or AND literals,64expansion visits,500000full-key cache flush. Full-prefix old semantic/cofactor proofs retained. Overflow falls back to original exact pair expression; no dropped terms, sampling or arithmetic cut. Four exhaustive8/10/12-atom controls plus fifteen inherited controls,24complete protected arbitrary input/absolute phase/classical/RNG comparisons per whole source. Diagnostic component only; own final source/gate/nonce/benchmark required for any future record.')
(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n');(r/'PLAN.md').write_text(f['scope']+'\n');(r/'.gitignore').write_text('local-tool/\n*.ops.bin\n__pycache__/\n');(r/'.gitattributes').write_text('* -text\n')
s=(old/'run.py').read_text().replace(old.name,r.name).replace("target/release/compact_context_alias'","target/release/associative_prefix'")
start=s.index('for name,path in [');end=s.index(']:',start)+2
ws=lambda p:'/mnt/c/'+str(p.resolve())[3:].replace('\\','/')
s=s[:start]+'for name,path in [(n,Path(p))for n,p in '+repr({n:ws(p)for n,p in paths.items()})+'.items()]:'+s[end:]
s=s.replace("'native_controls':15","'native_controls':19");(r/'run.py').write_text(s)
s=(old/'run-local.sh').read_text().replace(old.name,r.name).replace('--bin compact_context_alias','--bin associative_prefix').replace('15 passed;','19 passed;');(r/'run-local.sh').write_bytes(s.encode());print(r.name)
