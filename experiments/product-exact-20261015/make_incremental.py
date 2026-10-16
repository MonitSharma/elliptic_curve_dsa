"""Preserve terminal snapshot changes without repacking committed history for Git."""
import hashlib,json,shutil,sys,tarfile
from pathlib import Path,PurePosixPath
r=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base_path=r/'receipt-through-repair53-qualification-20261016.json';base_archive=r/'evidence-through-repair53-qualification-20261016.tar.gz'
assert sha(base_archive)=='aa137f820aad142765c2d56ef0aa582cdc451fc5ea0cb3a7d564f4a8c6ebcf96'
base=json.loads(base_path.read_text());current_path=r/'receipt.json';current=json.loads(current_path.read_text());snapshot=r/current['snapshot_directory'];assert snapshot.is_dir()
stem=sys.argv[1];assert stem and '/' not in stem and '\\' not in stem
dest=r/(stem+'-payload');assert not dest.exists();dest.mkdir();aliases={};gzip_headers={};stored=[]
base_by_hash={h:p for p,h in base['files'].items()}
gzip_by_body={}
with tarfile.open(base_archive,'r:gz') as old:
    for rel in base['files']:
        if not rel.endswith('.gz'):continue
        data=old.extractfile('evidence/'+rel).read()
        if data[:3]==b'\x1f\x8b\x08':gzip_by_body[hashlib.sha256(data[:4]+data[8:]).hexdigest()]=rel
for rel,h in current['files'].items():
    safe=PurePosixPath(rel);assert not safe.is_absolute() and '..' not in safe.parts
    if base['files'].get(rel)==h:continue
    if h in base_by_hash:aliases[rel]=base_by_hash[h];continue
    source=snapshot/rel;assert sha(source)==h
    if rel.endswith('.gz'):
        data=source.read_bytes()
        if data[:3]==b'\x1f\x8b\x08':
            match=gzip_by_body.get(hashlib.sha256(data[:4]+data[8:]).hexdigest())
            if match is not None:gzip_headers[rel]={'base_path':match,'mtime_bytes_hex':data[4:8].hex()};continue
    target=dest/'artifacts'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);stored.append(rel)
manifest={'schema':'immutable-terminal-supplement-v1','base_archive':base_archive.name,'base_archive_sha256':sha(base_archive),'base_receipt_sha256':sha(base_path),'current_receipt_sha256':sha(current_path),'current_full_canonical_archive_sha256':sha(r/'evidence.tar.gz'),'current_snapshot':current['snapshot_directory'],'current_artifacts':len(current['files']),'stored_new_or_changed_paths':stored,'copy_from_base_artifact_path':aliases,'unchanged_at_same_path':sum(base['files'].get(p)==h for p,h in current['files'].items()),'historical_base_paths_absent_from_current_snapshot':sorted(set(base['files'])-set(current['files'])),'scope':'No historical source/evidence removed. The complete immutable base remains authoritative for unchanged/history artifacts. Reconstruct the current snapshot by selecting every current-receipt path from artifacts/ when stored, the named base alias when specified, then any exact gzip timestamp-byte patch, otherwise the same base path. Validate every reconstructed file against current-receipt.json. Canonical tar.gz byte identity is not claimed for a reconstructed tar container.'}
manifest['exact_gzip_mtime_byte_patches']=gzip_headers
manifest['gzip_patch_scope']='Only replace bytes4..7 of a base gzip member when every other byte is identical. These compression-header timestamps are not evidence changes. Full reconstructed file SHA256 remains mandatory.'
manifest['pending_evidence_warning']=current['pending_evidence_warning']
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');shutil.copy2(current_path,dest/'current-receipt.json');shutil.copy2(base_path,dest/'base-receipt.json')
(dest/'RESTORE.md').write_text('Keep the immutable base archive named in manifest.json. Read current-receipt.json as the complete target file list. For each path use the stored artifacts entry, then any explicit base alias, then any exact gzip timestamp-byte patch specified in the manifest, otherwise the same path from the base. A gzip patch replaces only bytes4..7 with the four specified bytes; every other byte remains identical. Verify every file SHA256. Historical artifacts remain in the base and are not deleted. verify_incremental.py validates all target files without extraction. If delivery parts exist, concatenate them in delivery order and verify the full supplement SHA256 before opening.\n')
archive=r/(stem+'.tar.gz')
with tarfile.open(archive,'w:gz') as out:out.add(dest,arcname='increment')
delivery={'schema':'immutable-supplement-delivery-v1','archive':archive.name,'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'base_archive':base_archive.name,'base_archive_sha256':manifest['base_archive_sha256'],'target_artifacts':len(current['files']),'stored_artifacts':len(stored),'base_alias_artifacts':len(aliases),'parts':[]}
delivery['gzip_mtime_patched_artifacts']=len(gzip_headers)
if archive.stat().st_size>40*1024**2:
    with archive.open('rb') as source:
        i=0
        while chunk:=source.read(32*1024**2):
            i+=1;part=r/f'{stem}.part{i:03d}';part.write_bytes(chunk);delivery['parts'].append({'path':part.name,'bytes':len(chunk),'sha256':sha(part)})
(r/(stem+'.delivery.json')).write_text(json.dumps(delivery,indent=2)+'\n');print(json.dumps(delivery),flush=True)
