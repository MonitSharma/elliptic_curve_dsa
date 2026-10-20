import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'breakthrough-generic-lease-prover-20261020';t=r/'tool';f=json.loads((old/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert not t.exists();assert all(sha(old/'tool'/p)==h for p,h in f['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items());t.mkdir()
for p in(old/'tool').iterdir():
 if p.is_file():shutil.copyfile(p,t/p.name)
s=(t/'discover.rs').read_text().replace('\r','')
def change(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
change('let f=ops[first];let expected=alg.and(&q[f.q_control1.0 as usize],&q[f.q_control2.0 as usize]);','let f=ops[first];let product=alg.and(&q[f.q_control1.0 as usize],&q[f.q_control2.0 as usize]);let expected=if f.c_condition.0==no{product}else{alg.and(&product,&c[f.c_condition.0 as usize])};')
change('let o=ops[last];stack.is_empty()&&base==vec![0]&&alg.and(&q[o.q_control1.0 as usize],&q[o.q_control2.0 as usize])==expected','let o=ops[last];let product=alg.and(&q[o.q_control1.0 as usize],&q[o.q_control2.0 as usize]);let actual=if o.c_condition.0==no{product}else{alg.and(&product,&c[o.c_condition.0 as usize])};stack.is_empty()&&base==vec![0]&&actual==expected')
change('let mut base=1;let mut stack=vec![];let mut cb=1i8;let mut cs=vec![];','let mut base=1;let mut stack=vec![];let mut cb=1i8;let mut cs=vec![];let mut scope=Vec::<usize>::new();let mut lease_scopes=Vec::<Vec<usize>>::new();let mut saved_proxy=0f64;')
change('uses:HashMap<[H;3],(usize,Op)>','uses:HashMap<(Vec<usize>,H),(usize,Op)>')
change('if o.kind==K::PushCondition{stack.push(base);','if o.kind==K::PushCondition{scope.push(i);stack.push(base);')
change('if o.kind==K::PopCondition{base=stack.pop().unwrap();','if o.kind==K::PopCondition{scope.pop().unwrap();base=stack.pop().unwrap();')
change('if o.kind==K::CCX&&stack.is_empty()&&o.c_condition.0==no{','if o.kind==K::CCX&&ce!=0{')
change('let mut key=[q[a],q[b],1^q[a]^q[b]];key.sort();','let product=f.and(q[a],q[b]);let key=(scope.clone(),f.and(eff,product));')
change(']);busy[d]=Some(i);endpoints.insert(first);',']);lease_scopes.push(scope.clone());saved_proxy+=2f64.powi(-(scope.len()as i32)-i32::from(o.c_condition.0!=no));busy[d]=Some(i);endpoints.insert(first);')
change('"leases":leases,"zero_products":[]','"leases":leases,"lease_scopes":lease_scopes,"depth_weight_saving_diagnostic":saved_proxy,"zero_products":[]')
change('Each product equality proved with full expressions, arbitrary cut inputs and arbitrary measurement outcomes. Clean donors proved by exact constant guards and no intervening possible touches. Fingerprints only nominate pairs.','Within the same lexical outer scope, cofactor the common outer guard true; false skips both endpoints with donor zero. Effective per-op products proved with full expressions and arbitrary cut data/classical values/measurement outcomes. Clean donors and no touches/overlap proved conservatively. Fingerprints only nominate. Depth weights diagnostic only.')
a=s.index(' let starts:HashMap<_,_>=leases.iter()');b=s.index('\n#[cfg(test)]mod tests',a);s=s[:a]+' let rewritten=rewrite_ops(ops,&leases,nb);io::save_ops(&format!("{out}.ops.bin"),&rewritten);\n}\n'+(r/'rewrite.rs').read_text()+s[b:]+(r/'tests.rs').read_text();(t/'discover.rs').write_bytes(s.encode());subprocess.run(['cp','-a','--reflink=auto',str(old/'tool/target'),str(t/'target')],check=True)
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'tool_source_files':{p.name:sha(p)for p in t.iterdir()if p.is_file()},'protected_dependency_files':f['protected_dependency_files'],'inputs':f['inputs'],'scope':'Exact guarded leases in identical lexical scopes. Outer guard cofactored true, per-op guards proved in full expressions. Native guarded value/phase/Toffoli and negative/fault controls precede scans; no quantum scratch, samples, nonce or finalgate.'},indent=2)+'\n')
