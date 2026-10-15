"""Verify all old content, then every new/unchanged target by hash composition."""
import hashlib,json,subprocess,sys,tarfile
from pathlib import Path,PurePosixPath
base,previous,followup=map(Path,sys.argv[1:4]);r=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with tarfile.open(followup,'r:gz') as delta:
 m=json.load(delta.extractfile('followup/manifest.json'));assert m['schema']=='composed-followup-incremental-v1'
 assert sha(base)==m['root_base_archive_sha256'] and sha(previous)==m['previous_supplement_archive_sha256']
 verifier=r/'verify_incremental.py';assert sha(verifier)==m['previous_verifier_sha256']=='7fd75a88ce20b54827dd9ed4df87342c416147d03103a6e9412e1928513e07b8'
 # This full revalidation establishes every old content hash, including all
 # stored native blobs, aliases and exact gzip-header patches. It is not a
 # trust assumption about a previous success marker.
 subprocess.run([sys.executable,str(verifier),str(base),str(previous)],check=True)
 prior_bytes=delta.extractfile('followup/logical-base-receipt.json').read();assert hashlib.sha256(prior_bytes).hexdigest()==m['logical_base_receipt_sha256'];prior=json.loads(prior_bytes)
 with tarfile.open(previous,'r:gz') as old:assert old.extractfile('increment/current-receipt.json').read()==prior_bytes
 current_bytes=delta.extractfile('followup/current-receipt.json').read();assert hashlib.sha256(current_bytes).hexdigest()==m['current_receipt_sha256'];current=json.loads(current_bytes)
 assert len(prior['files'])==m['logical_base_artifacts']==3703
 stored=set(m['stored_new_or_changed_paths']);aliases=m['copy_from_verified_logical_base_path'];assert not stored.intersection(aliases)
 assert stored.issubset(current['files']) and set(aliases).issubset(current['files'])
 for rel,h in current['files'].items():
  safe=PurePosixPath(rel);assert not safe.is_absolute() and '..' not in safe.parts
  if rel in stored:assert hashlib.sha256(delta.extractfile('followup/artifacts/'+rel).read()).hexdigest()==h,rel
  elif rel in aliases:assert prior['files'][aliases[rel]]==h,rel
  else:assert prior['files'][rel]==h,rel
 assert len(current['files'])==m['target_artifacts']
print(json.dumps(dict(status='ALL_ROOT_BASE_PLUS_PREVIOUS_PLUS_FOLLOWUP_TARGET_HASHES_VERIFIED',target_artifacts=len(current['files']),root_base_archive_sha256=sha(base),previous_supplement_archive_sha256=sha(previous),followup_sha256=sha(followup))),flush=True)
