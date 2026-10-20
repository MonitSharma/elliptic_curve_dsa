"""Isolate each already specified structural prefix change; leave bound passes intact."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
r=root/'experiments/breakthrough-prefix-tick-isolated-20261020'
r.mkdir(exist_ok=False)
(r/'PLAN.md').write_text('''# Isolated structural tick experiment

Parent: exact public product source3dee0cd6, Q1234/T761052. The prior two-tick
candidate passes native arithmetic/interface controls, but stops at the unchanged
square_finish whole-stream binding. Isolate divide/fwd/payload ticks129 and130,
each with the previously specified mask0/room30 prefix and exact zero-gate
allocator restoration. No other arithmetic, precision, table, guard or cut changes.
Predicted raw savings0.75 and7 respectively; full-pipeline effects unknown.
Run all13 native controls then both complete constructions. Each must pass every
inherited binding unchanged to proceed. Preserve failures independently and do
not stop the second case if the first fails. No statistical gate or nonce screen
is authorized by this research plan; any promising finished source needs its own
new frozen source, fresh exact public comparison and declared final gate.
''')
(r/'.gitattributes').write_text('* -text\n')
(r/'.gitignore').write_text('observer/\ntarget/\n__pycache__/\n*resource-preflight*\nevidence.tar.gz\n')
(r/'prepare.py').write_text('''import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'breakthrough-prefix-tick-canonical-20261020';t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((old/'SOURCE-FREEZE.json').read_text());assert not t.exists()and(old/'run.exit').read_text().strip()=='1';assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in f['source_files']:dest=t/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(old/'observer'/p,dest)
p=t/'src/point_add/mod.rs';raw=p.read_bytes();a=b'assert!(["control","mixed"].contains(&mixed_mode.as_str()));let mixed=mixed_mode=="mixed";';assert raw.count(a)==1;raw=raw.replace(a,b'assert!(["tick129","tick130"].contains(&mixed_mode.as_str()));let mixed=true;let selected_tick=if mixed_mode=="tick129"{"129"}else{"130"};');a=b'eprintln!("BOUND_TICK_MIXED {}",mixed);';assert raw.count(a)==1;raw=raw.replace(a,b'std::env::set_var("RESEARCH_TICK_ONLY",selected_tick);eprintln!("BOUND_TICK_MIXED {} selected={}",mixed,selected_tick);');p.write_bytes(raw)
p=t/'src/point_add/leapfrog.rs';raw=p.read_bytes();a=b'&&(t==129||t==130);if selected';assert raw.count(a)==1;raw=raw.replace(a,b'&&std::env::var("RESEARCH_TICK_ONLY").is_ok_and(|v|v.parse::<usize>().ok()==Some(t));if selected');p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());assert all(sha(t/'src/point_add'/n)==sha(old/'observer/src/point_add'/n)for n in['square_finish.rs','square_finish.bin','y42_bound_pass.rs','linear_restore.rs','census_anchored.rs','and_cache.rs','product_copy.rs']);subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True);subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True);(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']));(r/'SOURCE-FREEZE.json').write_text(json.dumps({'base':f['base'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'protected_files':f['protected_files'],'prior_freeze_sha256':sha(old/'SOURCE-FREEZE.json'),'choices':['tick129','tick130'],'scope':'Each structural choice independently; every inherited bound pass/assertion/table unchanged; research construction only, no gate/nonce/score.'},indent=2)+'\\n')
''')
run=(root/'experiments/breakthrough-prefix-tick-canonical-20261020/run.py').read_text()
run=run.replace("for mode in ['control','mixed']:","for mode in ['tick129','tick130']:")
a="dest.mkdir();start=time.time();run(['timeout','1800',str(t/'target/release/build_circuit')],'generate-'+mode,dest,dict(os.environ,BREAK_TICK_MODE=mode));assert"
b="dest.mkdir();start=time.time();\n  try:run(['timeout','1800',str(t/'target/release/build_circuit')],'generate-'+mode,dest,dict(os.environ,BREAK_TICK_MODE=mode))\n  except AssertionError:\n   rows.append({'mode':mode,'status':'CONSTRUCTION_FAILED_UNCHANGED_BINDINGS','exit':(r/('generate-'+mode+'.exit')).read_text().strip(),'seconds':time.time()-start});(r/'PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\\n');continue\n  assert"
assert run.count(a)==1
run=run.replace(a,b).replace("'FULL_PUBLIC_PIPELINE_STRICT_BINDINGS_PASS_NOT_GATED_OR_SCORED'","'ISOLATED_TICK_CONSTRUCTIONS_TERMINAL_NOT_GATED_OR_SCORED'")
(r/'run.py').write_text(run)
print(r)
