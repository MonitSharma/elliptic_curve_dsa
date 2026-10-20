import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-t0-shared-product-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text());native=ws/'breakthrough-fin1-loan-native-20261020';nf=json.loads((native/'SOURCE_FREEZE.json').read_text())
assert not t.exists() and (old/'run.exit').read_text().strip()=='0' and (native/'run.exit').read_text().strip()=='0';assert all(sha(old/'observer'/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items());assert all(sha(native/'primitive'/p)==h for p,h in {**nf['source_files'],**nf['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in (old/'observer/src/point_add').rglob('*'):
 if p.is_file():q=t/p.relative_to(old/'observer');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
p=t/'src/point_add/mod.rs';raw=p.read_bytes();a=b'["1234","1233"].contains(&hard.as_str())';assert raw.count(a)==1;raw=raw.replace(a,b'["1234","1233","1232"].contains(&hard.as_str())');p.write_bytes(raw)
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes()
def change(a,b):
 global raw
 assert raw.count(a)==1,(a,raw.count(a));raw=raw.replace(a,b)
change(b'drop: usize, core_route: bool) ->',b'drop: usize, core_route: Option<usize>) ->')
change(b'let need = if core_route{31}else{fixed + min_budget - drop - 2 * usize::from(Y15_LEAN45)};',b'let need = if let Some(fin)=core_route{31-fin}else{fixed + min_budget - drop - 2 * usize::from(Y15_LEAN45)};')
change(b'    (block, tops, c3m, gsh, fin)\n}',b'    (block, tops, c3m, gsh, core_route.unwrap_or(fin))\n}')
a=b'let core_route=!rev&&!close&&!deep&&!swap01&&Y18_FIN_MIN==0&&fold_window(t,false)==56&&super::super::phase_fit::cap()<1234&&cells::cap()<1234&&room_now+(N-4).saturating_sub(sp2)+tops_max>=31;'
b=b'let core_room=room_now+(N-4).saturating_sub(sp2)+tops_max;let core_route=if !rev&&!close&&!deep&&!swap01&&Y18_FIN_MIN==0&&fold_window(t,false)==56&&super::super::phase_fit::cap()<1234&&cells::cap()<1234{if core_room>=31{Some(0)}else if core_room>=30{Some(1)}else{None}}else{None};';change(a,b)
a=b'    if core_loans::selected(c,mw,fin,ttm,loan,esh.is_none())';b=b'    if core_loans_fin1::selected(mw,fin,ttm,esh.is_none()){LOAN_ACTIVE.with(|x|x.set(false));return core_loans_fin1::fold(c,acc,e,nm,k1,k2,[c1,c3,c4,c5,c6],recs,&a4,&a5,drop);}\n'+a;change(a,b)
raw+=b'\nmod core_loans_fin1{include!("fin1_fold_runtime.rs");}\n';raw+=(r/'tests.rs').read_bytes();p.write_bytes(raw)
for a,b in [('certificate.rs','fin1_fold_certificate.rs'),('runtime.rs','fin1_fold_runtime.rs')]: (t/'src/point_add'/b).write_bytes((r/a).read_bytes())
subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True);assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in (t/'src/point_add').rglob('*')if p.is_file()};f['caps']=[1234,1233,1232];f['scope']='Integrate independently native-verified fin1 prefix30 ->retained20. Source preflight selects fin0 when31fit or fin1 when30fit, ordinary no deep/close/swap56bit contexts only; original m0 erase budget and capacity assertions remain. Missingc2 conditional phase repair/reconstruction validated before fullfold all14inputs, upperwords, guards andRNG controls. Attempt rawcaps1234,1233,1232. No arithmetic cut/window/iteration change, no finalgate/nonce/score.';(r/'SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
