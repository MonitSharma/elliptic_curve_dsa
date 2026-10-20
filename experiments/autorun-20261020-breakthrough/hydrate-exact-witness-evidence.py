"""Materialize independently checked nested evidence without changing archives."""
import hashlib,json,tarfile
from pathlib import Path

root=Path(__file__).resolve().parents[2];ex=root/'experiments';r=ex/'breakthrough-exact-witness-final-20261020'
sha=lambda data:hashlib.sha256(data).hexdigest()
receipt=json.loads((r/'PACKAGE-RESULT.json').read_bytes())
assert sha((r/'final-evidence.tar.gz').read_bytes())==receipt['archive_sha256']
assert sha((r/'EVIDENCE-MANIFEST.json').read_bytes())==receipt['manifest_sha256']
manifest=json.loads((r/'EVIDENCE-MANIFEST.json').read_bytes())
mapping={'gate':'breakthrough-exact-witness-final-gate-20261020','search':'breakthrough-exact-witness-nonce-20261020','finished':'breakthrough-exact-witness-finished-20261020','proof':'breakthrough-exact-witness-context-20261020','development':'breakthrough-exact-witness-finished-development-20261020','grid':'breakthrough-exact-witness-ripple-v3-20261020','grid-development':'breakthrough-exact-witness-development-20261020','proof-tool':'breakthrough-exact-witness-context-20261020/tool-source'}
count=0
with tarfile.open(r/'final-evidence.tar.gz') as archive:
 members=archive.getmembers();assert len(members)==receipt['members']
 for m in members:
  assert m.isfile();path=Path(m.name);assert not path.is_absolute()and'..'not in path.parts
  data=archive.extractfile(m).read();expected=receipt['manifest_sha256']if m.name=='EVIDENCE-MANIFEST.json'else manifest['files'][m.name];assert sha(data)==expected,m.name
  if len(path.parts)<2 or path.parts[0] not in mapping:continue
  dest=ex/mapping[path.parts[0]]/Path(*path.parts[1:])
  if dest.exists():assert dest.read_bytes()==data,str(dest)
  else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
  count+=1
(r/'NESTED-HYDRATION.json').write_text(json.dumps({'status':'ALL_ARCHIVE_MEMBERS_REVERIFIED_NESTED_EVIDENCE_MATERIALIZED','archive_sha256':receipt['archive_sha256'],'verified_members':len(members),'nested_materialized_members':count,'mapping':mapping,'separately_preserved_failures':'setup-v1/native-v2 retained in original separately verified archives; immutable final archive authoritative'},indent=2)+'\n')
print(count,'nested evidence files materialized; all',len(members),'archive members verified')
