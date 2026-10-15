from pathlib import Path
import json,hashlib,tarfile
r=Path(__file__).resolve().parent;name='attribution-checkpoint-v1';p=r/(name+'.tar.gz');receipt=json.loads((r/(name+'-receipt.json')).read_text())
digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest==receipt['sha256']
with tarfile.open(p)as tf:
 manifest=json.load(tf.extractfile(name+'/MANIFEST.json'))
 for file,info in manifest['files'].items():
  data=tf.extractfile(name+'/'+file).read();assert len(data)==info['bytes']and hashlib.sha256(data).hexdigest()==info['sha256'],file
 diagnosis=json.load(tf.extractfile(name+'/N2-DIAGNOSIS.json'));assert diagnosis['target_current_value_witnesses']==431 and diagnosis['original_batch_contexts']==413
 assert len(diagnosis['cases'])==14
out=dict(status='PASS',archive=str(p.resolve()),sha256=digest,all_manifest_archive_members_verified=len(manifest['files']),server_only_external_streams=len(manifest['external']),external_streams_not_claimed_locally_verified=True,terminal431_context_replay_and14_N2_diagnosis=True)
(r/(name+'-local-verification.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
