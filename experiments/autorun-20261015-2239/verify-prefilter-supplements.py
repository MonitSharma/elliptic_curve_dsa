from pathlib import Path,PurePosixPath
import hashlib,json,tarfile
root=Path(__file__).resolve().parent.parent/'prefilter-20261015'
results=[]
for stem,expected in [('accelerator','5e2c52415aa007cfc9f137492ac799ce503fbd7b39c05d92cc7382bea2585e23'),('nary','e16fccd83c17592403f97d65ca8a5c676f1f4551756fa2a786213bb9e9f63dd8')]:
 path=root/f'evidence-{stem}-supplement.tar.gz';sha=hashlib.sha256(path.read_bytes()).hexdigest();assert sha==expected
 with tarfile.open(path) as data:
  names=data.getnames();assert len(names)==len(set(names));assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
  candidates=[n for n in names if n.endswith('archive-manifest.json') or n.endswith('supplement-manifest.json')];assert len(candidates)==1,candidates
  manifest=json.load(data.extractfile(candidates[0]));entries=manifest['files']
  for name,record in entries.items():
   payload=data.extractfile(name).read();assert len(payload)==record['bytes'];assert hashlib.sha256(payload).hexdigest()==record['sha256'],name
 results.append({'archive':path.name,'sha256':sha,'verified_files':len(entries),'no_extraction_or_active_file_changes':True})
(root/'root-supplement-verification.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
