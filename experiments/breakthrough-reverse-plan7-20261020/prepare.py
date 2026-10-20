import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-fin1-fold-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert not t.exists() and (old/'run.exit').read_text().strip()=='0';assert all(sha(old/'observer'/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items());a=json.loads((old/'ADMISSION-RESULT.json').read_text());assert a['cases'][0]['exit']==0 and a['cases'][1]['exit']==0 and a['cases'][2]['exit']==101
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in (old/'observer/src/point_add').rglob('*'):
 if p.is_file():q=t/p.relative_to(old/'observer');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes()
def change(a,b):
 global raw
 assert raw.count(a)==1,(a,raw.count(a));raw=raw.replace(a,b)
change(b'let need = if let Some(fin)=core_route{31-fin}else{fixed + min_budget - drop - 2 * usize::from(Y15_LEAN45)};',b'''let reverse7=at.0&&nbits==50&&drop>=2&&super::super::phase_fit::cap()<1233&&cells::cap()<1233;
    let need = if let Some(fin)=core_route{31-fin}else{fixed + min_budget - drop - 2 * usize::from(Y15_LEAN45)-usize::from(reverse7)};''')
a=b'    if drop > 0 && merged_plan(nbits - 1, budget).is_none() && merged_plan(nbits, budget).is_none() {'
b=a+b'\n        if what=="reverse"&&nbits==50&&budget==7&&drop>=2&&super::super::phase_fit::cap()<1233{return(Y28_PLAN7.0.to_vec(),lean45,Y28_PLAN7.1.to_vec());}\n';change(a,b)
raw+=(r/'tests.rs').read_bytes();p.write_bytes(raw);subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True);assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in (t/'src/point_add').rglob('*')if p.is_file()};f['scope']='Credit existing native-verified Y28_PLAN7 only for reverse50bit/drop>=2 under hard/walk<=1232. Existing general-capacity assertions remain, with an explicit new validated budget7 case before the old8/9 contract. Add meaningful native planner-to-adder tests for exact target cap, arbitrary affine source/shared sign, guards, inverse, independentSHAKE words and everyRNGtoggle; repeat22 existing controls, thenthreecaps. No arithmeticcut/window/iteration change or finalgate/nonce/score.';(r/'SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
