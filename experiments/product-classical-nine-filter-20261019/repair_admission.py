"""Preserve a failed build admission and replace only its waiting manager."""
import hashlib,json,os,shutil,signal,time
from pathlib import Path
r=Path(__file__).resolve().parent
assert str(r)=='/home/hclau/ecdsa_research/product-classical-nine-filter-20261019'
assert (r/'build.exit').read_text().strip()=='1' and not (r/'tool').exists()
assert not (r/'QUALIFICATION-START.json').exists() and not list(r.glob('*.jsonl'))
pre=json.loads((r/'build-preflight.json').read_text());pid=int((r/'watch.pid').read_text())
assert pre['total_reserved_research_slots']==64
assert pre['unknown_active_research']==[{'pid':pid,'cwd':str(r),'command':'python3'}]
assert Path(f'/proc/{pid}/cwd').resolve()==r
assert b'after_gate.py' in Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
bound=json.loads((r/'WATCH_SOURCE.json').read_text())
assert all(hashlib.sha256((r/p).read_bytes()).hexdigest()==h for p,h in bound.items())
old=int((r/'build.pid').read_text());assert not Path(f'/proc/{old}').exists()
dest=r/'failed-admission-v1';dest.mkdir(exist_ok=False)
for p in r.iterdir():
    if p.is_file() and p.suffix in ['.py','.sh','.md']:shutil.copy2(p,dest/p.name)
os.kill(pid,signal.SIGTERM)
for _ in range(30):
    p=Path(f'/proc/{pid}/status')
    if not p.exists() or '\nState:\tZ' in p.read_text():break
    time.sleep(.1)
else:raise RuntimeError('Old waiting manager did not exit')
for name in ['build.pid','watch.pid','build.exit','build-preflight.json','build-nohup.log','watch-nohup.log','WATCH_SOURCE.json']:
    shutil.move(r/name,dest/name)
receipt={'status':'BUILD_ADMISSION_FAILED_ON_UNREGISTERED_OWN_WAITING_MANAGER_BEFORE_BUILD_OR_NONCE','old_build_pid':old,'stopped_waiting_pid':pid,'source_bindings_verified_before_stop':True,'candidate_and_gate_untouched':True,'nonce_shots_executed':0,'fix':'Build uses preflight_v9, which registers this exact waiting manager at zero slots. All previous admission checks remain enabled.'}
(r/'ADMISSION-REPAIR.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
