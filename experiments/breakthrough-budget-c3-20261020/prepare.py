import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-direct-transport-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE-v2.json').read_text())
assert not t.exists()and(old/'run-v3.exit').read_text().strip()=='0';assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
ad=json.loads((old/'ADMISSION-RESULT.json').read_text());assert ad['cases'][1]['raw_sha256']=='99b8d8260804bb8c183748c0977f01e670139ddcb1ee8505be99a3262ebc2848'
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'observer/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'observer');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();needle=b'    let loan=PAYLOAD_AT.with(|x|x.get().is_some_and(|(rev,t)|carry_loan_selected(rev,t)));';assert raw.count(needle)==1;raw=raw.replace(needle,needle.replace(b'let loan=',b'let mut loan='))
needle=b'    let mut add = if Y16_CORE { addend_prog(c, &mut recs, &k, &Y16_FWD_GATES, &Y16_FWD_OUT, mw) } else { addend_from_k(c, &mut recs, &k, mw) };';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'''
    let after_tt=(c.active_qubits()as usize).saturating_sub(usize::from(fin>=3||ttm));
    let core_room=cells::cap().saturating_sub(after_tt);
    let mut extra_c3=!loan&&super::super::phase_fit::cap()<1234&&mw==56&&drop>0&&(6..=7).contains(&core_room);
    #[cfg(test)] if let Some(value)=budget_c3_tests::override_value(){extra_c3=value;}
    if extra_c3&&!loan{loan=true;LOAN_ACTIVE.with(|x|x.set(true));eprintln!("BUDGET_C3_LOAN\\t{}\\t{}\\t{}\\t{core_room}\\t{fin}\\t{ttm}\\t{drop}",c.current_phase(),c.op_count(),c.active_qubits());}
''')
raw+=(r/'tests.rs').read_bytes();p.write_bytes(raw)
assert not(t/'target').exists();subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'caps':[1234,1233],'scope':'Reuse shipped forward C3 loan only for hard1233/mw56/drop>0 and static after-TT room6/7. Original loan selection/caller shed budgets/eligibility/windows/iterations unchanged; caller remains conservative. Native full-forward fin0..3, TT modes and bothlow budgets on all16384smallsource inputs plus fixedrandomupper words, exactold/new data/phase/cleanup, before retained controls and fullsource generation. No finalgate/nonce/record.'},indent=2)+'\n')
