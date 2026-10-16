from pathlib import Path
import json,hashlib,tarfile,shutil
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016');name='phase-attribution-addendum-v2';d=r/name;assert not d.exists();d.mkdir()
assert(r/'phase-attribution.exit').read_text().strip()=='0';out=json.loads((r/'PHASE-ATTRIBUTION.json').read_text());assert out['by_observed_mechanism']['exact_fold_boundary_loss_at_first_bad_global_stage']==34
files=['PHASE-ATTRIBUTION.json','PHASE-REPLAY-DECLARATION.json','phase-attribution.log','phase-attribution.exit','phase-attribution-build.log','phase-attribution-build.exit','phase-attribution-prepare.log','phase-attribution-prepare.exit','phase-attribution-preflight.log','phase-attribution-stream-before.sha256','phase-attribution-stream-after.sha256','prepare-phase-attribution.py','run-phase-attribution.sh','analyze-phase-attribution.py','tool/src/phase_payload_runtime.rs','tool/src/bin/current_phase_payload.rs']
for namefile in files:
 p=r/namefile;q=d/namefile;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pin=dict(base_checkpoint='attribution-checkpoint-v1.tar.gz',base_sha256=sha(r/'attribution-checkpoint-v1.tar.gz'),base_manifest_members=326,base_contains='source/protected code, exact413original batch packets, originalwholecircuit-latch report and literal final2a marker bindings',all_inputs_MR_and_simulator_unchanged=True,limitation='v1 first local interface mismatch can cancel before correct global stage and hide a later phase mismatch; v2 preserves it and adds phase-specific first events',no_candidate_or_failure_rate_change=True)
(d/'BASE-CHECKPOINT-PIN.json').write_text(json.dumps(pin,indent=2)+'\n')
manifest={str(p.relative_to(d)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in d.rglob('*')if p.is_file()}
(d/'MANIFEST.json').write_text(json.dumps(dict(files=manifest,depends_on=pin),indent=2)+'\n')
archive=r/(name+'.tar.gz')
with tarfile.open(archive,'w:gz',compresslevel=6)as tf:tf.add(d,arcname=name)
with tarfile.open(archive)as tf:
 for f,h in manifest.items():assert hashlib.sha256(tf.extractfile(name+'/'+f).read()).hexdigest()==h['sha256']
receipt=dict(status='PASS',archive=str(archive),bytes=archive.stat().st_size,sha256=sha(archive),verified_members=len(manifest),base_checkpoint_sha256=pin['base_sha256'])
(r/(name+'-receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
