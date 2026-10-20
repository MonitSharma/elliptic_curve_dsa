import hashlib,json,shutil,subprocess
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research');r=ws/'breakthrough-cross-scope-leases-20261020';old=ws/'breakthrough-guarded-lease-prover-20261020';t=r/'tool';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert not t.exists();f=json.loads((old/'SOURCE_FREEZE.json').read_text());assert all(sha(old/'tool'/p)==h for p,h in f['tool_source_files'].items());t.mkdir()
for p in(old/'tool').iterdir():
 if p.is_file():shutil.copyfile(p,t/p.name)
s=(t/'discover.rs').read_text();a=s.index('fn local_proof(');b=s.index('\nfn tri_and(',a);proof=s[a:b]
proof=proof.replace('fn local_proof(ops:&[Op],first:usize,last:usize,nq:usize,nb:usize)->bool{','fn cross_scope_proof(ops:&[Op],first:usize,last:usize,fs:&[usize],ls:&[usize],nq:usize,nb:usize)->bool{')
oldstart='let f=ops[first];let product=alg.and(&q[f.q_control1.0 as usize],&q[f.q_control2.0 as usize]);let expected=if f.c_condition.0==no{product}else{alg.and(&product,&c[f.c_condition.0 as usize])};'
assert proof.count(oldstart)==1;proof=proof.replace(oldstart,'let common=fs.iter().zip(ls).take_while(|(a,b)|a==b).count();let start=if common<fs.len(){fs[common]}else{first};if last-start>200000{return false;}let mut expected=None;')
proof=proof.replace('for o in &ops[first..last]{','for(index,o)in ops[start..last].iter().enumerate(){let index=index+start;')
anchor='let eff=if o.c_condition.0==no{base.clone()}else{alg.and(&base,&c[o.c_condition.0 as usize])};if eff.is_empty(){continue;}'
assert proof.count(anchor)==1;proof=proof.replace(anchor,'let eff=if o.c_condition.0==no{base.clone()}else{alg.and(&base,&c[o.c_condition.0 as usize])};if index==first{let p=alg.and(&q[a],&q[b]);expected=Some(alg.and(&p,&eff));}if eff.is_empty(){continue;}')
anchor='let actual=if o.c_condition.0==no{product}else{alg.and(&product,&c[o.c_condition.0 as usize])};stack.is_empty()&&base==vec![0]&&actual==expected'
assert proof.count(anchor)==1;proof=proof.replace(anchor,'let eff=if o.c_condition.0==no{base}else{alg.and(&base,&c[o.c_condition.0 as usize])};let actual=alg.and(&product,&eff);expected==Some(actual)')
s=s.replace('let product=f.and(q[a],q[b]);let key=(scope.clone(),f.and(eff,product));','scope_history.insert(i,scope.clone());let product=f.and(q[a],q[b]);let key=(Vec::new(),f.and(eff,product));')
s=s.replace('let mut uses:HashMap<(Vec<usize>,H),(usize,Op)>=HashMap::new();','let mut scope_history=HashMap::<usize,Vec<usize>>::new();let mut uses:HashMap<(Vec<usize>,H),(usize,Op)>=HashMap::new();')
s=s.replace('if local_proof(&ops,first,i,nq,nb){','if cross_scope_proof(&ops,first,i,&scope_history[&first],&scope,nq,nb){')
s+='\n'+proof+'\n'+(r/'cross_tests.rs').read_text();(t/'discover.rs').write_bytes(s.encode());subprocess.run(['cp','-a','--reflink=auto',str(old/'tool/target'),str(t/'target')],check=True)
f['tool_source_files']={p.name:sha(p)for p in t.iterdir()if p.is_file()};f['inputs']={'generic1234':f['inputs']['generic1234'],'certified1234':{'path':str(ws/'breakthrough-certified-prefix-20261020/certified/ops.bin'),'sha256':'85958b9f90cc93c7bba94d158cba2b4dde890bf9f4231cd70dc5b4fd9f1218b2'}};f['scope']='Cross-lexical-scope nomination uses global effective product fingerprints only to propose. Full exact arbitrary-cut algebra begins at first unmatched PushCondition under common ancestor snapshot, includes all nested/per-op guards and accepts equality of complete effective products. Requires globally zero donor, no intervening touches/overlap. Existing rewrite retained. Cut span limit200000 operations. Component only; no finalgate/nonce/score.';(r/'SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
