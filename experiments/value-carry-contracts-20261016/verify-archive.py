from pathlib import Path
import tarfile,json,hashlib
r=Path(__file__).resolve().parent;a=r/'evidence.tar.gz';h=hashlib.sha256(a.read_bytes()).hexdigest();assert h==(r/'evidence.sha256').read_text().split()[0]
with tarfile.open(a)as t:
 m=json.load(t.extractfile('manifest.json'))
 for n,v in m['files'].items():
  content=t.extractfile(n).read();assert len(content)==v['bytes']and hashlib.sha256(content).hexdigest()==v['sha256'],n
(r/'verified-manifest.json').write_text(json.dumps(dict(archive_sha256=h,verified_files=len(m['files']),external_preserved_only=len(m['external'])),indent=2)+'\n');print(h,len(m['files']),len(m['external']))
