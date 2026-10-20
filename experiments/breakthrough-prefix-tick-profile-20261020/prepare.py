import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'breakthrough-prefix-retained-cleanup-20261020';t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((old/'SOURCE-FREEZE.json').read_text());prior=json.loads((old/'RESULT.json').read_text());assert(old/'run.exit').read_text().strip()=='0'and not t.exists();assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p,h in f['source_files'].items():dest=t/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(old/'observer'/p,dest)
p=t/'src/point_add/leapfrog.rs';raw=p.read_bytes()
for direction in ['fwd','rev']:
 signature=f'fn {direction}_tick_fast(c: &mut Builder, wk: &mut Walk, t: usize, mut pay: Option<&mut [Vec<QubitId>; 2]>) {{'.encode();assert raw.count(signature)==1
 wrapper=f'''fn {direction}_tick_fast(c: &mut Builder, wk: &mut Walk, t: usize, pay: Option<&mut [Vec<QubitId>; 2]>) {{
 let phase=c.current_phase();let payload=pay.is_some();let live_before=c.active_qubits();let op0=c.op_count();let before=c.report_totals().unwrap_or((0,0.));
 {direction}_tick_fast_profile_body(c,wk,t,pay);
 let after=c.report_totals().unwrap_or((0,0.));eprintln!("RETAIN_TICK phase={{phase}} direction={direction} t={{t}} payload={{payload}} live_before={{live_before}} live_after={{}} op0={{op0}} op1={{}} native={{}} cost={{:.6}}",c.active_qubits(),c.op_count(),after.0 as i64-before.0 as i64,after.1-before.1);
}}
fn {direction}_tick_fast_profile_body(c: &mut Builder, wk: &mut Walk, t: usize, mut pay: Option<&mut [Vec<QubitId>; 2]>) {{'''.encode();raw=raw.replace(signature,wrapper)
p.write_bytes(raw);subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True);subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True);(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']));assert all(sha(t/p)==h for p,h in f['protected_files'].items())
cases=[{'label':'baseline','keep':0,'mask':0,'room':30,'mode':'control','expected_raw_sha256':'13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'}]
for row in prior['cases']:
 if row['exit']==0:cases.append({'label':'prior'+str(row['index']),'keep':row['keep'],'mask':row['mask'],'room':row['room'],'mode':'enabled','expected_raw_sha256':row['raw_sha256']})
assert len(cases)==22
(r/'SOURCE-FREEZE.json').write_text(json.dumps({'base':f['base'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'protected_files':f['protected_files'],'prior_source_freeze_sha256':sha(old/'SOURCE-FREEZE.json'),'prior_native_controls':prior['native_test_counts'],'prior_native_logs':{f'tests-{i}.log':sha(old/f'tests-{i}.log')for i in range(10)},'cases':cases,'scope':'Read-only counters wrap entire forward/reverse ticks, including surrounding preflight and arithmetic. Original function bodies/arguments unchanged; all22 raw streams must byte-match frozen original/control or previous passing retention cases. Reuse prior13 native controls with explicit log hashes; no new control claim. Failed keep11 cases preserved and not rerun. Fixed structural costs only, no packet/census/nonce. Determine which tick-specific choices merit a new full build; no scored result.'},indent=2)+'\n')
