"""One extensible, source-hashed job registry; retain the old watcher unchanged."""
import hashlib,json,shutil,subprocess
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;old=ws/'classical9-final-v2-20261019';r=ws/'classical9-final-v3-20261020';sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
assert not r.exists();r.mkdir();bound=json.loads((old/'WATCH_SOURCE.json').read_text());assert all(sha(old/p)==h for p,h in bound.items())
for name in ['audit-terminal.py','finalize.py','watch.py','test_paths.py','test_audit.py','launch_watch.py']:shutil.copy2(old/name,r/name)
profiles={str(ws/'autonomous-20261019'/p):sha(ws/'autonomous-20261019'/p) for p in ['preflight_v15.py','resource_registry.py']}
s=(old/'run-final.sh').read_text().replace('classical9-final-v2-20261019','classical9-final-v3-20261020').replace('preflight_v14.py','preflight_v15.py')
guard="python3 - <<'PY'\nimport hashlib\nfrom pathlib import Path\nexpected="+repr(profiles)+"\nfor name,h in expected.items():\n with Path(name).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==h,'Changed immutable resource profile'\nPY\n"
s=s.replace('python3 ../autonomous-20261019/preflight_v15.py',guard+'python3 ../autonomous-20261019/preflight_v15.py');(r/'run-final.sh').write_text(s,newline='\n')
shutil.copy2(old/'RUNTIME-BINDING.json',r/'RUNTIME-BINDING.json')
(r/'RESOURCE-PROFILE.json').write_text(json.dumps({'immutable_source_hashes':profiles,'dynamic_manifest_directory':str(ws/'resource-registry-20261020'),'schema':'reviewed kind, slots, exact source hashes, PID and actual cwd/entrypoint; unknown processes still refused','old_profiles_unchanged':True},indent=2)+'\n')
for args,log in [(['python3',str(ws/'autonomous-20261019/test_resource_registry.py')],'registry-tests.log'),(['python3',str(r/'test_audit.py')],'auditor-tests.log'),(['python3',str(r/'test_paths.py'),'--complete'],'complete-path-tests.log')]:
    with (r/log).open('xb') as f:subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,check=True)
(r/'READY.json').write_text(json.dumps({'status':'COPIED_BOUND_AUDITOR_AND_ALL_NATIVE_RUNTIME_GATE_PATHS_PASS','source_files':{p.name:sha(p) for p in r.iterdir() if p.suffix in ['.py','.sh']},'profile_sha256':profiles[str(ws/'autonomous-20261019/preflight_v15.py')],'profile_helper_sha256':profiles[str(ws/'autonomous-20261019/resource_registry.py')]},indent=2)+'\n')
(r/'STATUS.md').write_text('# Queue-only classical9 finalizer with immutable extensible registry\n\nAll scoring/auditor/native/search logic is unchanged. Only final shell root and resource checks change. Profile15 and its helper are hash-literal-bound inside the watched final shell. Reviewed future jobs register immutable source descriptors without editing any running source. Unknown jobs, source changes and over-capacity launches still fail closed.9 registry tests,6 auditor corruption tests and complete native/runtime/gate path checks pass. Prepare before intentionally retiring only the old idle watcher.\n')
print((r/'READY.json').read_text())
