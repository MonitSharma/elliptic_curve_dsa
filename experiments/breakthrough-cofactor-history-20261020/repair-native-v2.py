"""Preserve the initial test-harness compile failure, then fix its generic type."""
import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive'
assert (r/'native.exit').read_text().strip()=='101'
old=r/'failed-native-compile-v1';old.mkdir(exist_ok=False)
for name in ['native-tests.log','native.exit','native-source.patch','NATIVE-SOURCE-FREEZE.json','cofactor_history.rs']:
 shutil.copyfile(r/name,old/name)
source=(r/'cofactor_history-v2.rs').read_bytes()
assert b"Simulator<'_,R>"in source
(t/'src/point_add/cofactor_history.rs').write_bytes(source)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=json.loads((r/'NATIVE-SOURCE-FREEZE.json').read_text())
assert all(sha(t/name)==h for name,h in freeze['protected_files'].items())
freeze['source_files']={p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()}
freeze['repair']='Test helper supplies the protected Simulator XOF-reader generic; no primitive gate changed.'
(r/'NATIVE-SOURCE-FREEZE-v2.json').write_text(json.dumps(freeze,indent=2)+'\n')
(r/'native-source-v2.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
with(r/'native-tests-v2.log').open('xb')as log:
 result=subprocess.run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','cofactor_history::tests','--','--nocapture'],cwd=t,stdout=log,stderr=subprocess.STDOUT)
(r/'native-v2.exit').write_text(str(result.returncode)+'\n')
assert result.returncode==0
assert all(sha(t/name)==h for name,h in{**freeze['source_files'],**freeze['protected_files']}.items())
(r/'NATIVE-RESULT.json').write_text(json.dumps({'status':'NATIVE_REVERSIBLE_HISTORY_CODEC_PRIMITIVE_CONTROLS_PASS','tests':3,'data_lookup_cases':128,'signed_cofactor_residue_cases':3072,'toffolis_per_erase':14,'clean_scratch_peak':3,'measurement_and_phase_gates':0,'first_step_tail_and_full_point_add_not_implemented':True,'source_freeze_sha256':sha(r/'NATIVE-SOURCE-FREEZE-v2.json'),'test_log_sha256':sha(r/'native-tests-v2.log'),'protected_files_unchanged':True},indent=2)+'\n')
