import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-core-loan-fold-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert not t.exists() and (old/'run.exit').read_text().strip()=='0';assert all(sha(old/'observer'/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items());assert json.loads((old/'ADMISSION-RESULT.json').read_text())['cases'][1]['raw_sha256']=='6b375c3a6e3e08cd3d67f7113d443e32976eeedb9c0e4a326019759da6ea77ec'
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in (old/'observer/src/point_add').rglob('*'):
 if p.is_file():q=t/p.relative_to(old/'observer');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
p=t/'src/point_add/core_loan_runtime.rs';raw=p.read_bytes()
def change(a,b):
 global raw
 assert raw.count(a)==1,(a,raw.count(a));raw=raw.replace(a,b)
change(b' for &(index,terms)in CORE_LOAN_ERASE{',b''' let target=super::super::super::phase_fit::cap().min(cells::cap());
 let loan_count=10usize.saturating_sub(target.saturating_sub(c.active_qubits()as usize)).clamp(1,11);
 for &(index,terms)in &CORE_LOAN_ERASE[..loan_count]{''')
change(b'let active=c.active_qubits();let target=super::super::super::phase_fit::cap().min(cells::cap());',b'let active=c.active_qubits();')
change(b'for &(index,linear,products)in CORE_LOAN_REBUILD{let q=held[index];',b'for &(index,linear,products)in CORE_LOAN_REBUILD{if !CORE_LOAN_ERASE[..loan_count].iter().any(|&(i,_)|i==index){continue;}let q=held[index];')
change(b'{active}\\t{target}\\t{plan:?}',b'{active}\\t{target}\\t{loan_count}\\t{plan:?}')
p.write_bytes(raw);subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in (t/'src/point_add').rglob('*')if p.is_file()};f['scope']='Only borrow the smallest prefix of the independently verified erasure order needed to leave10 clean ladder carries at the independent hard cap. Rebuild only selected helpers. All certificate identities retain their available operands under subsequences; skipped helper forms stay live. No arithmetic cuts, inputs, windows or iteration changes. Repeat same complete full-fold native controls and raw source generation. No finalgate/nonce/score.';(r/'SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
