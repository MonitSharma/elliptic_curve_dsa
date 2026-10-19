"""Prepare a queue-only finalizer before retiring any preceding search."""
import hashlib,json,shutil,subprocess
from pathlib import Path
ws=Path(__file__).resolve().parent.parent
old=ws/'classical9-final-v3-20261020';r=ws/'classical12-final-20261020'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
assert not r.exists();r.mkdir()
bound=json.loads((old/'WATCH_SOURCE.json').read_text())
assert all(sha(old/p)==h for p,h in bound.items())
mapping={
 'product-classical-nine-20261019':'product-classical-twelve-native-20261019',
 'product-classical-nine-operational-20261019':'product-classical-twelve-operational-20261019',
 'classical9-final-v3-20261020':'classical12-final-20261020',
 '2932b6cf662e2d6be05679b0d5e34a9149ccbceaca57f8ce92cfccd13b8c8f6e':'4b7c6d3bcfc1ee1540d57c2a3e991281408ed90d09c192c5ce60e0fa15ce3d17',
 '76271c7d66785b62ec4077ec241e80d3645841ba898cf8b633c377099da687c1':'17c767f514ca98ad02d4da9e5b1dbedf67189e5c70b7b15916adc0f0c2f0a7f7',
 '17_889_627':'17_889_635','17889627':'17889635','len(manifest)==175':'len(manifest)==180',
 '0bf11d329455b2ec2582085435853454b220540d67c2c76b80da56eca44645f4':'5c25049df477ecd3bfa82e6059866dfda211af5085d1944e01ffabd48b93d5ff',
 'e6971995f1d56d1bb3011eee74efed437ad01f4540d8acaebc066da5f7b34d9d':'16939cd728cd31e60901aa04faffe2abbeb6bfab0105b0f031820282a02934ea',
 'classical9':'classical12','CLASSICAL9':'CLASSICAL12'}
for name in ['audit-terminal.py','finalize.py','watch.py','test_paths.py','test_audit.py','launch_watch.py','run-final.sh']:
 s=(old/name).read_text()
 for a,b in mapping.items():s=s.replace(a,b)
 if name=='run-final.sh':
  s=s.replace('cd "$r/candidate"','(\ncd "$r/candidate"')+'\n)\n'
  s=s.replace('classical_xor_control; do','classical_xor_control classical_wide; do')
 (r/name).write_text(s,newline='\n')
binding={'status':'RUNTIME_PINNED_AFTER_OWN_PREFIX_CONTROL','acceptance_sha256':mapping['0bf11d329455b2ec2582085435853454b220540d67c2c76b80da56eca44645f4'],
 'binary_sha256':mapping['e6971995f1d56d1bb3011eee74efed437ad01f4540d8acaebc066da5f7b34d9d'],
 'auditor_sha256':sha(r/'audit-terminal.py'),'complete_path_audit_required_before_watch':True}
(r/'RUNTIME-BINDING.json').write_text(json.dumps(binding,indent=2)+'\n')
for args,log in [(['python3',str(r/'test_audit.py')],'auditor-tests.log'),(['python3',str(r/'test_paths.py'),'--complete'],'complete-path-tests.log')]:
 with (r/log).open('xb') as f:subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,check=True)
subprocess.run(['bash','-n',str(r/'run-final.sh')],check=True)
(r/'READY.json').write_text(json.dumps({'status':'SOURCE12_ALL_NATIVE_RUNTIME_GATE_PATHS_AND_AUDITOR_CONTROLS_PASS',
 'source_files':{p.name:sha(p) for p in r.iterdir() if p.suffix in ['.py','.sh']},'binding':binding,
 'changes_from_reviewed_source9':'Only source-specific constants/paths/labels and classical_wide native tests; final shell stays root via candidate subshell.',
 'selection':'Ascending from1, lowest complete protected pass, no T selection; queue only.'},indent=2)+'\n')
print((r/'READY.json').read_text())
