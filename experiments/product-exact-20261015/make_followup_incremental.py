"""Store only changes after the verified3703 logical base (85MiB+36MiB chain)."""
import hashlib,json,shutil,sys,tarfile
from pathlib import Path,PurePosixPath
r=Path(__file__).resolve().parent;stem=sys.argv[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=r/'evidence-through-repair53-qualification-20261016.tar.gz'
previous=r/'supplement-repaired67-qualified-20261016.tar.gz'
assert sha(base)=='aa137f820aad142765c2d56ef0aa582cdc451fc5ea0cb3a7d564f4a8c6ebcf96'
assert sha(previous)=='9ec9889206393fd00ee7188c969c5fcdeffe6b23e34673acb9ba93dec047561e'
with tarfile.open(previous,'r:gz') as old:
 prior_manifest=json.load(old.extractfile('increment/manifest.json'));prior_bytes=old.extractfile('increment/current-receipt.json').read()
assert hashlib.sha256(prior_bytes).hexdigest()==prior_manifest['current_receipt_sha256'] and prior_manifest['base_archive_sha256']==sha(base)
prior=json.loads(prior_bytes);assert len(prior['files'])==3703
current_bytes=(r/'receipt.json').read_bytes();current=json.loads(current_bytes);snapshot=r/current['snapshot_directory']
assert not current['protected_dependency_mismatches'] and all(not x['protected_mismatches'] for x in current['all_candidates'].values())
dest=r/(stem+'-payload');archive=r/(stem+'.tar.gz');assert not dest.exists() and not archive.exists();dest.mkdir()
old_by_hash={h:p for p,h in prior['files'].items()};stored=[];aliases={};same=0
for rel,h in current['files'].items():
 safe=PurePosixPath(rel);assert not safe.is_absolute() and '..' not in safe.parts
 if prior['files'].get(rel)==h:same+=1;continue
 if h in old_by_hash:aliases[rel]=old_by_hash[h];continue
 source=snapshot/rel;assert sha(source)==h;target=dest/'artifacts'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);assert sha(target)==h;stored.append(rel)
manifest=dict(schema='composed-followup-incremental-v1',root_base_archive=base.name,root_base_archive_sha256=sha(base),previous_supplement_archive=previous.name,previous_supplement_archive_sha256=sha(previous),logical_base_receipt_sha256=hashlib.sha256(prior_bytes).hexdigest(),logical_base_artifacts=len(prior['files']),current_receipt_sha256=hashlib.sha256(current_bytes).hexdigest(),current_canonical_archive_sha256=sha(r/'evidence.tar.gz'),target_artifacts=len(current['files']),stored_new_or_changed_paths=stored,copy_from_verified_logical_base_path=aliases,unchanged_same_path=same,historical_paths_absent_from_current=sorted(set(prior['files'])-set(current['files'])),previous_verifier_sha256=sha(r/'verify_incremental.py'),pending_warning=current['pending_evidence_warning'],scope='First verify every3703 logical-base file with the immutable root base plus previous supplement and verify_incremental.py. Then every target file is newly stored and hashed, an explicit same-hash logical-base alias, or the unchanged same path/hash from that fully verified logical base. No historical archive or source is deleted. Reconstructed tar container byte identity is not claimed.')
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(dest/'logical-base-receipt.json').write_bytes(prior_bytes);(dest/'current-receipt.json').write_bytes(current_bytes)
(dest/'RESTORE.md').write_text('Keep the immutable root base and previous supplement named and hashed in manifest.json. They reconstruct the3703-file logical base using the previous supplement RESTORE.md. For each current-receipt target path, use artifacts/ when stored; use the explicitly named logical-base path for an alias; otherwise use the unchanged same logical-base path. Validate every target SHA256. verify_followup_incremental.py first revalidates all3703 old files, then independently checks every target content or exact verified-hash inheritance. Historical evidence remains in the two prior archives. Canonical tar container byte identity is not claimed.\n')
with tarfile.open(archive,'w:gz') as out:out.add(dest,arcname='followup')
delivery=dict(schema='composed-followup-delivery-v1',archive=archive.name,archive_bytes=archive.stat().st_size,archive_sha256=sha(archive),root_base_archive_sha256=sha(base),previous_supplement_archive_sha256=sha(previous),target_artifacts=len(current['files']),stored_artifacts=len(stored),logical_base_aliases=len(aliases),parts=[])
if archive.stat().st_size>40*1024**2:
 with archive.open('rb') as source:
  i=0
  while chunk:=source.read(32*1024**2):
   i+=1;part=r/f'{stem}.part{i:03d}';part.write_bytes(chunk);delivery['parts'].append(dict(path=part.name,bytes=len(chunk),sha256=sha(part)))
(r/(stem+'.delivery.json')).write_text(json.dumps(delivery,indent=2)+'\n');print(json.dumps(delivery),flush=True)
