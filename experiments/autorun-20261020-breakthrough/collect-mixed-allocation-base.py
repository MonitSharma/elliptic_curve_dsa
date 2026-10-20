"""Verify every native evidence byte and retain a compact source/test bundle."""
import gzip,hashlib,io,json,subprocess,sys,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
allowed=['breakthrough-prefix-tick-mixed-20261020','breakthrough-prefix-tick-alloc-20261020','breakthrough-prefix27-global-reuse-20261020','breakthrough-prefix27-production-20261020','breakthrough-public140-cache-20261020', 'breakthrough-public140-cone-cache-20261020', 'breakthrough-prefix-dag-20261020', 'breakthrough-prefix27-native-20261020', 'breakthrough-prefix27-fold-native-20261020', 'breakthrough-public140-exact154-20261020', 'breakthrough-public140-exact154-final-gate-20261020']
for name in sys.argv[1:]:
 assert name in allowed;r=root/'experiments'/name;r.mkdir(exist_ok=True)
 subprocess.run(['scp']+[f'smu_server:/home/hclau/ecdsa_research/{name}/{file}'for file in['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']]+[str(r)],check=True)
 receipt=json.loads((r/'PACKAGE-RESULT.json').read_bytes());manifest=json.loads((r/'EVIDENCE-MANIFEST.json').read_bytes());sha=lambda b:hashlib.sha256(b).hexdigest()
 assert sha((r/'evidence.tar.gz').read_bytes())==receipt['archive_sha256']
 retained={}
 with tarfile.open(r/'evidence.tar.gz')as archive:
  members=archive.getmembers();assert len(members)==receipt['members'];assert{m.name for m in members}==set(manifest['files'])|{'EVIDENCE-MANIFEST.json'}
  for path,expected in manifest['files'].items():assert sha(archive.extractfile(path).read())==expected,path
  assert sha(archive.extractfile('EVIDENCE-MANIFEST.json').read())==receipt['manifest_sha256']
  for m in members:
   p=Path(m.name);data=archive.extractfile(m).read();retained[m.name]=data
   if '/'not in m.name and(m.name.endswith('.json')or m.name.endswith('.rs'))and m.name!='EVIDENCE-MANIFEST.json':(r/m.name).write_bytes(data)
   if m.name=='EVIDENCE-MANIFEST.json'or m.name.startswith(('added-source/','tool/src/','tool-v2/src/'))or p.suffix in['.patch','.rs','.exit']or p.name.startswith(('SOURCE_FREEZE','TOOL-SOURCE-FREEZE'))or p.name.startswith('tests')and p.suffix=='.log'or p.name in['Cargo.toml','Cargo.lock','build.rs','simd8count.c','simd8wide.h']:
    retained[m.name]=data
 buffer=io.BytesIO()
 with gzip.GzipFile(fileobj=buffer,mode='wb',mtime=0)as compressed:
  with tarfile.open(fileobj=compressed,mode='w')as archive:
   for path,data in sorted(retained.items()):
    info=tarfile.TarInfo(path);info.size=len(data);info.mode=0o644;info.mtime=0;archive.addfile(info,io.BytesIO(data))
 bundle=r/'native-source-and-tests.tar.gz';bundle.write_bytes(buffer.getvalue())
 (r/'SOURCE-AND-TESTS-MANIFEST.json').write_text(json.dumps({'origin_archive_sha256':receipt['archive_sha256'],'bundle_sha256':sha(bundle.read_bytes()),'members':{p:sha(b)for p,b in retained.items()},'scope':'Exact native source patch, added source and test logs preserved without line-ending conversion. Full native archive also verifies locally and remains retained on server.'},indent=2)+'\n')
 (r/'LOCAL-VERIFICATION.json').write_text(json.dumps({'status':'EVERY_ARCHIVE_MEMBER_VERIFIED_LOCALLY','archive_sha256':receipt['archive_sha256'],'members':len(members),'native_source_test_bundle_sha256':sha(bundle.read_bytes())},indent=2)+'\n')
 print(name,len(members),'native members verified;',len(retained),'source/test members retained',flush=True)
