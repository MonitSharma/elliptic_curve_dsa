import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-core-loan-select-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert not t.exists() and (old/'run.exit').read_text().strip()=='0';assert all(sha(old/'observer'/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in (old/'observer/src/point_add').rglob('*'):
 if p.is_file():q=t/p.relative_to(old/'observer');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
p=t/'src/point_add/mod.rs';raw=p.read_bytes();a=b'std::env::set_var("HEO_PIN_PP_WALK_MAX_QUBITS", &break_cap);';assert raw.count(a)==1;raw=raw.replace(a,b'std::env::set_var("HEO_PIN_PP_WALK_MAX_QUBITS", &hard);');p.write_bytes(raw)
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes()
def change(a,b):
 global raw
 assert raw.count(a)==1,(a,raw.count(a));raw=raw.replace(a,b)
change(b'at: (bool, usize), drop: usize) -> (usize, usize, usize, usize, usize)',b'at: (bool, usize), drop: usize, core_route: bool) -> (usize, usize, usize, usize, usize)')
change(b'let need = fixed + min_budget - drop - 2 * usize::from(Y15_LEAN45);',b'let need = if core_route{31}else{fixed + min_budget - drop - 2 * usize::from(Y15_LEAN45)};')
change(b'    let shed_for = |fixed: usize, fmax: usize| {',b'''    let core_route=!rev&&!close&&!deep&&!swap01&&Y18_FIN_MIN==0&&fold_window(t,false)==56&&super::super::phase_fit::cap()<1234&&cells::cap()<1234&&room_now+(N-4).saturating_sub(sp2)+tops_max>=31;
    let shed_for = |fixed: usize, fmax: usize| {''')
change(b'            drop_n,\n        )',b'            drop_n,\n            core_route,\n        )')
change(b'if core_loans::selected(c,mw,fin,ttm,loan,esh.is_none()){return core_loans::fold',b'if core_loans::selected(c,mw,fin,ttm,loan,esh.is_none()){LOAN_ACTIVE.with(|x|x.set(false));return core_loans::fold')
change(b'let(_,peak)=super::super::super::pingpong::with_phase_cap(Some(1234),||c.r3_peak',b'let reference_cap=if !new&&budget<6{1250}else{1234};let(_,peak)=super::super::super::pingpong::with_phase_cap(Some(reference_cap),||c.r3_peak')
change(b'peak<=if new{1233}else{1234}',b'peak<=if new{1233}else{reference_cap}')
change(b'  for budget in 6..=10{for ttm',b'  for budget in 1..=5{for guard in[0,0xA55A_DD33_FF00_1701,u64::MAX]{fixture(budget,false,guard,None);}}\n  for budget in 6..=10{for ttm')
p.write_bytes(raw)
p=t/'src/point_add/core_loan_runtime.rs';raw=p.read_bytes();a=b' if fin!=0||loan||!no_esh||mw!=56{return false;}';b=b' if fin!=0||!no_esh||mw!=56{return false;}\n let global_route=super::super::super::phase_fit::cap()<1234&&cells::cap()<1234;\n if loan&&!global_route{return false;}';assert raw.count(a)==1;raw=raw.replace(a,b);p.write_bytes(raw)
subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True);assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in (t/'src/point_add').rglob('*')if p.is_file()};f['scope']='Global walk budget1233 with source-derived core-loan-aware forward preflight: peak=max31 prefix helpers, retained helper count plus10 ladder carries. Only fin0,56bit,no close/deep/swap, enough ordinary shed pool for31; before any old C3 basis changes prefer exact full-core route. Original m0 erase budget, arithmetic, cuts, windows, iterations unchanged. Extend complete-fold native controls to before-ladder room0..4 against an unconstrained1250cap reference; same all16384inputs, upper words, guards and allRNGcontrols. Full control must stay13f6. No finalgate/nonce/score.';(r/'SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
