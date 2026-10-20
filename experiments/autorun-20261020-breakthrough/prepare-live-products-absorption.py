from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-live-products-v2-20261020';r=root/'experiments/breakthrough-live-products-absorption-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore','PLAN.md']:shutil.copyfile(old/p,r/p)
s=(old/'main.rs').read_text();needle='Algebra{next:1,products:HashMap::new(),cap:96,truncations:0}';assert s.count(needle)==1;s=s.replace(needle,'Algebra{next:1,products:HashMap::new(),witness:HashMap::new(),cap:512,truncations:0}')
at=s.rfind('\n}');assert at>0
s=s[:at]+r'''
fn eval(e:&E,a:&Algebra,row:u64)->bool{e.iter().fold(false,|v,&x|v^if x==0{true}else if x<=8{row>>(x-1)&1!=0}else{let t=a.witness.get(&x).expect("Every test product atom is bound");eval(&t[0],a,row)&&eval(&t[1],a,row)})}
#[test]fn product_implication_absorption_complements_and_xor_are_exhaustive_boolean_identities(){let mut a=Algebra{next:9,products:HashMap::new(),witness:HashMap::new(),cap:512,truncations:0};let x=vec![1,2];let y=vec![2,3,4];let p=a.and(&x,&y);let triple=Algebra::triple(&x,&y);let s=a.and(&p,&vec![5]);let mut cases=vec![];for f in triple{let complement=Algebra::xor_raw(&vec![0],&f);let diff=Algebra::xor_raw(&p,&f);cases.push((p.clone(),f.clone()));cases.push((p.clone(),complement));cases.push((p.clone(),diff));cases.push((s.clone(),f));}cases.push((s.clone(),Algebra::xor_raw(&p,&vec![5])));cases.push((s.clone(),vec![5,6,7]));for(left,right)in cases{let out=a.and(&left,&right);for row in 0..256{assert_eq!(eval(&out,&a,row),eval(&left,&a,row)&&eval(&right,&a,row));}}assert_eq!(a.truncations,0);assert_eq!(a.and(&p,&x),p);assert!(a.and(&p,&Algebra::xor_raw(&vec![0],&x)).is_empty());}
'''+s[at:];(r/'main.rs').write_text(s)
(r/'patch-algebra.py').write_text(r'''from pathlib import Path
p=Path(__file__).resolve().parent/'tool/algebra.rs';s=p.read_text();needle='products:HashMap<Triple,u32>, cap:';assert s.count(needle)==1;s=s.replace(needle,'products:HashMap<Triple,u32>, witness:HashMap<u32,Triple>, cap:')
needle=' fn and(&mut self,a:&E,b:&E)->E {';assert s.count(needle)==1
helpers=r'''+ '"""'+''' fn implied(&self,r:u32,e:&E,depth:usize)->Option<bool>{if e.is_empty(){return Some(false);}if e==&vec![0]||e==&vec![r]{return Some(true);}if e==&Self::xor_raw(&vec![0],&vec![r]){return Some(false);}if depth==0{return None;}if let Some(t)=self.witness.get(&r){for f in t{if e==f{return Some(true);}if e==&Self::xor_raw(&vec![0],f){return Some(false);}}for f in t{if f.len()==1&&f[0]!=0{if let Some(v)=self.implied(f[0],e,depth-1){return Some(v);}}}}None}
 fn absorb(&mut self,p:&E,e:&E)->Option<E>{if p.len()!=1||p[0]==0{return None;}let r=p[0];if let Some(v)=self.implied(r,e,32){return Some(if v{p.clone()}else{vec![]});}let mut rest=vec![];let mut one=false;let mut changed=false;for &x in e{if let Some(v)=self.implied(r,&vec![x],32){one^=v;changed=true;}else{rest.push(x);}}if changed{let z=self.and(p,&rest);return Some(if one{self.xor(&z,p)}else{z});}None}
'''+ '"""'+'''
s=s.replace(needle,helpers+needle)
needle='  let t=Self::triple(a,b);';assert s.count(needle)==1;s=s.replace(needle,'  if let Some(v)=self.absorb(a,b){return v;}if let Some(v)=self.absorb(b,a){return v;}\n'+needle)
needle='self.products.insert(t,v);vec![v]';assert s.count(needle)==1;s=s.replace(needle,'self.products.insert(t.clone(),v);self.witness.insert(v,t);vec![v]');p.write_text(s)
''')
s=(old/'run.py').read_text();needle="(t/'algebra.rs').write_text(algebra);";assert s.count(needle)==1;s=s.replace(needle,needle+"subprocess.run(['python3',str(r/'patch-algebra.py')],check=True);")
needle="inputs={'publice3':";assert s.count(needle)==1;s=s.replace(needle,"inputs={'cache53':(ws/'breakthrough-public-e3-cache-finished-v2-20261020/candidate/ops.bin','93c7830ef7d19f63d342a9eabef1ec61abf50d12c4189751d09c063a5e4be176'),'publice3':")
(r/'run.py').write_text(s)
with(r/'PLAN.md').open('a')as out:out.write('''
New fixed512-term proof algebra adds sound product implications: an AND product
implies each of its three exact SymTriple factors, and annihilates their Boolean
complements. Product-parent implications compose to depth32; known singleton
terms distribute through an XOR with strictly fewer unknown terms. Unsupported
facts remain unknown, overflow still creates fresh whole-function atoms. Six
native controls include exhaustive256 Boolean assignments for all three factors,
complements, correlated XOR and nested products. Add the separately finished
cache53/93c783 stream as a fourth fixed input. No finalgate has been declared for
this publice3 family; candidate assembly will use fixed proof results, no packet
or failure-label optimization. Prior96-term/component results remain intact.
''')
print(r)
