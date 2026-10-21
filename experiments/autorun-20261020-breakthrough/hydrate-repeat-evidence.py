from pathlib import Path
import hashlib,json,tarfile
a=Path(__file__).parent;ex=a.parent;r=ex/'breakthrough-de8-repeat-final-20261020';sha=lambda b:hashlib.sha256(b).hexdigest();receipt=json.loads((r/'PACKAGE-RESULT.json').read_bytes());manifest=json.loads((r/'EVIDENCE-MANIFEST.json').read_bytes());assert sha((r/'final-evidence.tar.gz').read_bytes())==receipt['archive_sha256'];assert sha((r/'EVIDENCE-MANIFEST.json').read_bytes())==receipt['manifest_sha256']
mapping={'gate':'breakthrough-de8-repeat-final-gate-20261020','search':'breakthrough-de8-repeat-nonce-20261020','finished':'breakthrough-de8-repeat-finished-20261020','proof':'breakthrough-de8-second-cache-20261020','development':'breakthrough-de8-repeat-finished-development-20261020','prototype':'breakthrough-de8-generic-repeat-v3-20261020','prototype-development':'breakthrough-de8-generic-development-20261020'};count=0
with tarfile.open(r/'final-evidence.tar.gz')as ar:
 members=ar.getmembers();assert len(members)==receipt['members']
 for m in members:
  p=Path(m.name);assert m.isfile()and not p.is_absolute()and'..'not in p.parts;data=ar.extractfile(m).read();expected=receipt['manifest_sha256']if m.name=='EVIDENCE-MANIFEST.json'else manifest['files'][m.name];assert sha(data)==expected,m.name
  if len(p.parts)<2 or p.parts[0]not in mapping:continue
  dest=ex/mapping[p.parts[0]]/Path(*p.parts[1:])
  if dest.exists():assert dest.read_bytes()==data,str(dest)
  else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
  count+=1
(r/'NESTED-HYDRATION.json').write_text(json.dumps({'status':'ALL239_ARCHIVE_MEMBERS_REVERIFIED_NESTED_EVIDENCE_MATERIALIZED','verified_members':len(members),'nested_materialized_members':count,'archive_sha256':receipt['archive_sha256'],'mapping':mapping,'scope':'Original immutable final archive remains authoritative; official receipts collected separately after upload. No new gate/nonce/benchmark.'},indent=2)+'\n');print(count,'nested files materialized;',len(members),'members verified')
