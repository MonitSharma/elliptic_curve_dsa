"""Prepare a new immutable coordinator; never edit the running old watcher."""
import hashlib,json,shutil,subprocess
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;old=ws/'classical9-final-20261019';r=ws/'classical9-final-v2-20261019'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
assert not r.exists();r.mkdir()
bound=json.loads((old/'WATCH_SOURCE.json').read_text());assert all(sha(old/p)==h for p,h in bound.items())
assert sha(old/'audit-terminal.py')=='47e8c89c308a15026a4da85310829f8a35188149716fcc6fb349adcac5d27ba1'
names=['audit-terminal.py','finalize.py','watch.py','test_paths.py','test_audit.py','launch_watch.py']
for name in names:shutil.copy2(old/name,r/name)
s=(old/'run-final.sh').read_text();assert s.count('r=/home/hclau/ecdsa_research/classical9-final-20261019')==1
s=s.replace('r=/home/hclau/ecdsa_research/classical9-final-20261019','r=/home/hclau/ecdsa_research/classical9-final-v2-20261019').replace('preflight_v13.py','preflight_v14.py')
(r/'run-final.sh').write_text(s,newline='\n');shutil.copy2(old/'RUNTIME-BINDING.json',r/'RUNTIME-BINDING.json')
(r/'PREPARATION.json').write_text(json.dumps({'status':'NEW_COORDINATOR_PREPARED_OLD_WATCHER_UNCHANGED','identical_old_files':{p:sha(old/p) for p in names},'run_final_changes':['own root directory only','new explicit preflight_v14 registry'], 'old_watched_files':bound,'source9_stream_unchanged':True,'search_or_nonce_algorithm_changed':False,'new_nonce_screening':False},indent=2)+'\n')
(r/'STATUS.md').write_text('# Queue-only classical9 finalizer, explicit next-job registry\n\nCopies the current bound auditor/native preparation and six corruption controls unchanged. Only the final shell root and read-only resource-profile version change. New profile registers forthcoming classical12 runtime jobs. Prepare and test before intentionally retiring the idle old watcher. No circuit, search order, nonce, score or benchmark changes. Never modify a running watched source.\n')
for args,log in [(['python3',str(r/'test_audit.py')],'auditor-tests.log'),(['python3',str(r/'test_paths.py'),'--complete'],'complete-path-tests.log')]:
    with (r/log).open('xb') as f:subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,check=True)
(r/'READY.json').write_text(json.dumps({'status':'COPIED_BOUND_AUDITOR_AND_ALL_NATIVE_RUNTIME_GATE_PATHS_PASS','source_files':{p.name:sha(p) for p in r.iterdir() if p.suffix in ['.py','.sh']},'profile_sha256':sha(ws/'autonomous-20261019/preflight_v14.py')},indent=2)+'\n')
print((r/'READY.json').read_text())
