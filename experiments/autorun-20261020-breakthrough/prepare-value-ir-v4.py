from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-value-ir-audit-v3-20261020';r=a.parent/'breakthrough-value-ir-audit-v4-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
s=(old/'audit.rs').read_text();p=s.index('fn compile(')
s=s[:p]+'''#[derive(Default)]struct Expr{next:u32,and:HashMap<(u32,u32),u32>,xor:HashMap<(u32,u32),u32>}
impl Expr{
 fn atom(&mut self)->u32{self.next+=2;self.next}
 fn and(&mut self,mut a:u32,mut b:u32)->u32{if a==0||b==0{return 0;}if a==1{return b;}if b==1||a==b{return a;}if a==b^1{return 0;}if a>b{std::mem::swap(&mut a,&mut b);}if let Some(&v)=self.and.get(&(a,b)){return v;}let v=self.atom();self.and.insert((a,b),v);v}
 fn or(&mut self,a:u32,b:u32)->u32{self.and(a^1,b^1)^1}
 fn xor(&mut self,mut a:u32,mut b:u32)->u32{if a==0{return b;}if b==0{return a;}if a==1{return b^1;}if b==1{return a^1;}if a==b{return 0;}if a==b^1{return 1;}let neg=(a^b)&1;a&=!1;b&=!1;if a>b{std::mem::swap(&mut a,&mut b);}if let Some(&v)=self.xor.get(&(a,b)){return v^neg;}let v=self.atom();self.xor.insert((a,b),v);v^neg}
 fn ite(&mut self,g:u32,new:u32,old:u32)->u32{if g==0||new==old{return old;}if g==1{return new;}if old==0{return self.and(g,new);}if new==0{return self.and(g^1,old);}if old==1{return self.or(g^1,new);}if new==1{return self.or(g,old);}if new==old^1{return self.xor(g,old);}let a=self.and(g,new);let b=self.and(g^1,old);self.or(a,b)}
}
''' +s[p:]
needle='let mut versions=nb;';replacement='let mut expressions=Expr::default();let mut symbols:Vec<u32>=constants.iter().map(|&v|if v==0{0}else{expressions.atom()}).collect();let mut representatives:HashMap<u32,u32>=HashMap::new();for(i,&symbol)in symbols.iter().enumerate(){representatives.entry(symbol).or_insert(i.try_into().unwrap());}let mut guard_symbols:HashMap<u32,u32>=HashMap::from([(1,0)]);let mut versions=nb;'
assert s.count(needle)==1;s=s.replace(needle,replacement)
needle='let g=if false_guard{NO}else{intern(merge(&guards[base as usize],&own),&mut guards,&mut index)};'
replacement='''let mut gsymbol=if false_guard{0}else{1};if !false_guard{for &v in guards[base as usize].iter().chain(own.iter()){gsymbol=expressions.and(gsymbol,symbols[v as usize]);}}let g=if gsymbol==0{NO}else if let Some(&id)=guard_symbols.get(&gsymbol){id}else{let id=intern(merge(&guards[base as usize],&own),&mut guards,&mut index);guard_symbols.insert(gsymbol,id);id};'''
assert s.count(needle)==1;s=s.replace(needle,replacement)
start=s.index('let old_constant=constants[old as usize];');end=s.index('nodes.push(Node{k,a:old',start)
s=s[:start]+'''let prior=symbols[old as usize];let symbol=match k{CZERO=>expressions.and(prior,gsymbol^1),CONE=>expressions.or(prior,gsymbol),CINV=>expressions.xor(prior,gsymbol),CRNG=>{let random=expressions.atom();expressions.ite(gsymbol,random,prior)},_=>unreachable!()};symbols.push(symbol);constants.push(if symbol<=1{symbol as i8}else{-1});current[bit]=*representatives.entry(symbol).or_insert(new);''' +s[end:]
pos=s.rfind('\n}')
s=s[:pos]+'''
 #[test]fn double_classical_inversion_reuses_immutable_guard_version(){let n=u64::MAX;let ops=vec![op(K::X,n,n,2,n,0),op(K::BitInvert,n,n,n,0,n),op(K::BitInvert,n,n,n,0,n),op(K::X,n,n,2,n,0)];let p=checked(&ops,&[0,1,2],&[0,1,2]);assert_eq!(p.nodes.iter().filter(|n|n.k==QX).count(),0);}
 #[test]fn boolean_store_alias_and_captured_complement_are_exact(){let n=u64::MAX;let ops=vec![op(K::BitStore0,n,n,n,1,n),op(K::BitStore1,n,n,n,1,0),op(K::X,n,n,2,n,1),op(K::X,n,n,2,n,0),op(K::PushCondition,n,n,n,n,0),op(K::BitInvert,n,n,n,0,n),op(K::X,n,n,2,n,0),op(K::PopCondition,n,n,n,n,n)];let p=checked(&ops,&[0,1,2],&[0,1,2]);assert_eq!(p.nodes.iter().filter(|n|n.k==QX).count(),0);}
''' +s[pos:]
(r/'audit.rs').write_text(s)
s=(old/'run.py').read_text().replace('10 passed; 0 failed;','12 passed; 0 failed;').replace("'native_controls':10","'native_controls':12").replace('Ten protected native','Twelve protected native').replace('with SSA constant propagation','with SSA constant propagation and exact structurally interned Boolean aliases/complement edges')
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text((old/'PLAN.md').read_text()+'''\nV4 exact classical Boolean interning: immutableinitialinput and HMRrandom atoms,\nconstant0/1, complement edges, commutative AND/XOR and exact ITE expansion.\nClassical SSA expressions may alias an EARLIER available identical expression;\nits old SSA value is immutable even after physical-bit mutation. Guards with\nidentical expression use the earlier captured conjunction. False complementary\nclauses removed only by exact algebraic identities. No probabilistic Boolean\nidentity tests, packet/census inputs or approximate model. Extra2 protected\nsmallbasis controls cover doubleinvert aliases, conditionalstores and captured\ncomplements.128round value-only audit, no nonce/circuit changes or score.\n''');print(r)
