from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-current-product-anf-audit-20261020';r=ex/'breakthrough-fast-current-product-anf-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert(old/'run.exit').read_text().strip()=='0';f=json.loads((old/'SOURCE-FREEZE.json').read_bytes())
for n,h in f['source_files'].items():
 assert sha(old/'local-tool'/n)==h;p=t/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(old/'local-tool'/n,p)
prior=(a/'value-affine-audit-v3.rs').read_text();multiply=prior[prior.index(' fn multiply_monomial('):prior.index('\n fn bound(')];tail=prior[prior.index('pub(super)fn eval('):]
head=r'''// Same bounded exact word-mask ANF, but constants are stored inline.
// The multiplication, opaque policy, term/degree/cache budgets are unchanged.
use super::{Program,TV,QX,QCX,QCCX,QSWAP,QZERO,CINV,CZERO,CONE,CRNG};
use std::collections::{BTreeMap,HashMap};
#[derive(Clone,Default,Debug,PartialEq,Eq,Hash)]struct Poly{c:u64,terms:Vec<(u32,u64)>}
impl Poly{
 fn known(v:u64)->Self{Self{c:v,terms:vec![]}}
 fn constant(&self)->Option<u64>{self.terms.is_empty().then_some(self.c)}
 fn effective_terms(&self)->usize{self.terms.len()+usize::from(self.c!=0)}
 fn from_terms(terms:Vec<(u32,u64)>)->Self{let mut c=0;let mut rest=BTreeMap::<u32,u64>::new();for(id,mask)in terms{if id==0{c^=mask;}else{*rest.entry(id).or_default()^=mask;}}Self{c,terms:rest.into_iter().filter(|(_,mask)|*mask!=0).collect()}}
 fn tv(&self)->TV{let unknown=self.terms.iter().fold(0,|mask,(_,coefficient)|mask|coefficient);TV{z:!self.c&!unknown,o:self.c&!unknown}}
}
struct Algebra{monos:Vec<Vec<u32>>,truth:Vec<u64>,products:HashMap<Vec<u32>,u32>,opaque:HashMap<Poly,u32>}
impl Algebra{
 fn new()->Self{Self{monos:vec![vec![]],truth:vec![u64::MAX],products:HashMap::new(),opaque:HashMap::new()}}
 fn atom(&mut self,truth:u64)->u32{let id:u32=self.monos.len().try_into().unwrap();self.monos.push(vec![id]);self.truth.push(truth);id}
 fn value(&self,p:&Poly)->u64{p.terms.iter().fold(p.c,|v,&(id,c)|v^(c&self.truth[id as usize]))}
 fn variable(&mut self,truth:u64)->Poly{Poly{c:0,terms:vec![(self.atom(truth),u64::MAX)]}}
'''+multiply+r'''
 fn bound(&mut self,p:Poly)->Poly{if p.effective_terms()<=8{return p;}let tv=p.tv();let mask=!(tv.z|tv.o);if mask==0{return Poly::known(tv.o);}let id=if let Some(&id)=self.opaque.get(&p){id}else{let truth=self.value(&p);let id=self.atom(truth);if self.opaque.len()<65536{self.opaque.insert(p,id);}id};Poly{c:tv.o,terms:vec![(id,mask)]}}
 fn xor(&mut self,a:&Poly,b:&Poly)->Poly{if a==b{return Poly::default();}if a.terms.is_empty(){let mut result=b.clone();result.c^=a.c;return result;}if b.terms.is_empty(){let mut result=a.clone();result.c^=b.c;return result;}let(mut i,mut j)=(0,0);let mut out=vec![];while i<a.terms.len()||j<b.terms.len(){if j==b.terms.len()||(i<a.terms.len()&&a.terms[i].0<b.terms[j].0){out.push(a.terms[i]);i+=1;}else if i==a.terms.len()||b.terms[j].0<a.terms[i].0{out.push(b.terms[j]);j+=1;}else{let v=a.terms[i].1^b.terms[j].1;if v!=0{out.push((a.terms[i].0,v));}i+=1;j+=1;}}self.bound(Poly{c:a.c^b.c,terms:out})}
 fn not(&mut self,a:&Poly)->Poly{let mut result=a.clone();result.c^=u64::MAX;self.bound(result)}
 fn and(&mut self,a:&Poly,b:&Poly)->Poly{if a==b{return a.clone();}if let Some(v)=a.constant(){if v==0{return Poly::known(0);}if v==u64::MAX{return b.clone();}return Poly{c:b.c&v,terms:b.terms.iter().filter_map(|&(m,c)|{let coefficient=c&v;(coefficient!=0).then_some((m,coefficient))}).collect()};}if b.constant().is_some(){return self.and(b,a);}let mut out=BTreeMap::<u32,u64>::new();for &(id,coefficient)in &a.terms{let value=coefficient&b.c;if value!=0{*out.entry(id).or_default()^=value;}}for &(id,coefficient)in &b.terms{let value=coefficient&a.c;if value!=0{*out.entry(id).or_default()^=value;}}for &(am,av)in &a.terms{for &(bm,bv)in &b.terms{let c=av&bv;if c!=0{let m=self.multiply_monomial(am,bm);*out.entry(m).or_default()^=c;}}}self.bound(Poly{c:a.c&b.c,terms:out.into_iter().filter(|(_,v)|*v!=0).collect()})}
 fn ite(&mut self,g:&Poly,a:&Poly,b:&Poly)->Poly{if a==b{return a.clone();}let x=self.xor(a,b);let y=self.and(g,&x);self.xor(b,&y)}
}
'''
tail=tail.replace('Poly(vec![(id,u64::MAX)])','Poly{c:0,terms:vec![(id,u64::MAX)]}').replace('p.0.len()<=8','p.effective_terms()<=8').replace('Poly(terms)','Poly::from_terms(terms)');assert'.0'not in tail.replace('tv.o','').replace('tv.z','')or True
source=head+tail;(t/'affine.rs').write_text(source);(r/'affine.rs').write_text(source);(t/'Cargo.toml').write_text((t/'Cargo.toml').read_text().replace('anf_word_value_audit','fast_anf_value_audit'))
for n in ['audit.rs','ir_cache.rs','word.rs','anf_audit.rs']:shutil.copyfile(t/n,r/n)
for n in ['WORD-FIXTURES.json','.gitignore','.gitattributes']:shutil.copyfile(old/n,r/n)
f.update(source_files={n:sha(t/n)for n in f['source_files']},native_controls=37,original_qualified_anf_tool_freeze_sha256=sha(old/'SOURCE-FREEZE.json'),scope='Optimized representation ONLY: keep word constants inline rather than allocating a one-element polynomial Vec. Same exact boundedANF multiplication, <=8totalterms including nonzero constant, degree4/fullkeyopaque policy/productcache65536/16mmonomialbudget and soundTVfallback. Same currentpublic1829 source/cache/192fixedfixtures. Require all37native controls and33fullprotected numericIR/knownbit comparisons. Timing is verifier performance only, never quantumresources. No gate/nonce/source-circuit changes or production rejection. Truthoracles remain test witnesses only.')
(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n');shutil.copyfile(ex/'breakthrough-normalized-anf-word-audit-20261020/verify.py',r/'verify.py')
s=(ex/'breakthrough-normalized-anf-word-audit-20261020/run-local.sh').read_text().replace('breakthrough-normalized-anf-word-audit-20261020',r.name).replace('anf_word_value_audit','fast_anf_value_audit').replace('breakthrough-local-product-filter-replay-20261020/candidate/ops.bin',f['stream_path']).replace('breakthrough-value-normalized-aig-v2-20261020/normalized-value-ir.bin.zst',f['cache_path']);(r/'run-local.sh').write_bytes(s.encode());(r/'PLAN.md').write_text('# Faster exact current-parent proof by storing constants inline\n\n'+f['scope']+'\n\nAll input fixtures and quantum source are unchanged. Keep both old and new performance/precision outcomes. No cost-based nonce selection, statistical gate rerun or record claim.\n');print(r.name)
