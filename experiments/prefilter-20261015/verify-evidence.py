from pathlib import Path,PurePosixPath
import tarfile,hashlib,json,re,datetime,sys
r=Path(__file__).parent.resolve();p=r/(sys.argv[1] if len(sys.argv)>1 else 'evidence-local.tar.gz');sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==(r/(p.name+'.sha256')).read_text().split()[0]
redirected=[]
with tarfile.open(p) as t:
 manifest=json.loads(t.extractfile('evidence/local-archive-manifest.json').read())
 members={m.name:m for m in t if m.isfile()};assert len(members)==len(manifest['files'])+1
 for name,record in manifest['files'].items():
  data=t.extractfile(members[name]).read();assert len(data)==record['bytes'];assert hashlib.sha256(data).hexdigest()==record['sha256'],name
 for name,member in members.items():
  parts=PurePosixPath(name).parts;assert not PurePosixPath(name).is_absolute() and '..' not in parts
  if re.search(r'[<>:"|?*\x00-\x1f]',name):
   safe=re.sub(r'[^a-zA-Z0-9._-]','_',PurePosixPath(name).name)
   target=r/'evidence/nonportable'/('name-'+hashlib.sha256(name.encode()).hexdigest()[:16]+'-'+safe)
   redirected.append(dict(original_archive_name=name,local_path=str(target.relative_to(r))))
  else:target=r.joinpath(*parts)
  assert target.resolve().is_relative_to(r);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(t.extractfile(member).read())
(r/'evidence/nonportable-names.json').write_text(json.dumps(redirected,indent=2)+'\n')
report=dict(archive_sha256=sha,verified_files=len(manifest['files']),all_archived_manifest_hashes_match=True,terminal_checkpoint=manifest['terminal_checkpoint'],excluded_active_files=manifest['excluded_active_files'],verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(r/('evidence/'+sys.argv[2] if len(sys.argv)>2 else 'evidence/accelerator-supplement-checkpoint-verification.json' if len(sys.argv)>1 else 'evidence/local-checkpoint-verification.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
