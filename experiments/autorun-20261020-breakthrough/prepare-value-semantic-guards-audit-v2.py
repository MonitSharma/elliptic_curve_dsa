from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-value-semantic-guards-audit-20261020';r=ex/'breakthrough-value-semantic-guards-audit-v2-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
for n in ['.gitattributes','.gitignore','verify-input.py']:shutil.copyfile(old/n,r/n)
for n in ['Cargo.lock','io.rs']:shutil.copyfile(old/'local-tool'/n,t/n)
s=(old/'audit.rs').read_text();s=s.replace('struct Expr{truths:','struct Expr{restricting:bool,truths:')
needle='if let Some(&v)=self.and.get(&(a,b)){return v;}';assert s.count(needle)==1
s=s.replace(needle,needle+'''if !self.restricting{self.restricting=true;let mut result=None;if let Some(v)=self.cofactor(b,a,6){if v!=b{result=Some(self.and(a,v));}}if result.is_none(){if let Some(v)=self.cofactor(a,b,6){if v!=a{result=Some(self.and(b,v));}}}self.restricting=false;if let Some(v)=result{self.and.insert((a,b),v);return v;}}''')
pos=s.index('fn compile(')
s=s[:pos]+'''impl Expr{fn cofactor(&mut self,expression:u32,assumed:u32,depth:usize)->Option<u32>{if expression==assumed{return Some(1);}if expression==assumed^1{return Some(0);}if expression<=1||depth==0{return None;}let(k,a,b)=self.nodes[(expression/2-1)as usize];if k==0{return None;}let left=self.cofactor(a,assumed,depth-1);let right=self.cofactor(b,assumed,depth-1);if left.is_none()&&right.is_none(){return None;}let a=left.unwrap_or(a);let b=right.unwrap_or(b);let value=if k==1{self.and(a,b)}else{self.xor(a,b)};Some(value^(expression&1))}}
''' +s[pos:]
pos=s.rfind('\n}');s=s[:pos]+'''
 #[test]fn context_cofactoring_removes_masked_random_alias_even_above_truth_support_limit(){let mut e=Expr::default();let mut g=1;for _ in 0..8{let a=e.atom();g=e.and(g,a);}let mut old=1;for _ in 0..8{let a=e.atom();old=e.and(old,a);}let random=e.atom();let masked=e.ite(g,random,old);let under=e.and(g,masked);let expected=e.and(g,random);assert_eq!(under,expected);let outside=e.and(g^1,masked);let expected=e.and(g^1,old);assert_eq!(outside,expected);}
''' +s[pos:];(r/'audit.rs').write_text(s);(t/'audit.rs').write_text(s)
(t/'Cargo.toml').write_text((old/'local-tool/Cargo.toml').read_text().replace('value_semantic_guards_audit','value_semantic_guards_v2_audit'))
f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());f.update(source_files={n:sha((t/n).read_bytes())for n in ['Cargo.toml','Cargo.lock','io.rs','audit.rs']},native_controls=25,scope=f['scope']+' Add exact bounded Shannon cofactoring a&b = a&b[a:=1], depth6; only rebuild if literal assumption occurs. Disable nested cofactoring during rebuild, no sampled identity. Large-support masked HMR aliases tested directly.');(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
for n in ['run-local.sh','launch-local.sh']:(r/n).write_bytes((old/n).read_text().replace(old.name,r.name).replace('value_semantic_guards_audit','value_semantic_guards_v2_audit').replace('24 passed; 0 failed;','25 passed; 0 failed;').encode())
(r/'PLAN.md').write_text((old/'PLAN.md').read_text()+'''\nV2 adds exact bounded Shannon cofactoring to AND construction: a&b equals
a&b[a:=1], also symmetric. Restrict only actual matching literal occurrences,
six raw DAG levels, no guessing. This handles a&(a?random:old)=a&random even
when a/old have more than6underlying atoms. Rebuild with cofactoring disabled
to bound recursion; preserve exact old hashed expressions and all prior tests.
25native includes direct large-support inside/outside masked-alias regression.
Same frozen source and verifier fixtures, no gate/circuit/nonce change.
''');print(r.name)
