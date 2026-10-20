import hashlib,json,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];ex=root/'experiments'
jobs=[('breakthrough-native-context-final-20261020',{'gate':'breakthrough-native-context-final-gate-20261020','search':'breakthrough-native-context-nonce-20261020','finished':'breakthrough-native-context-finished-v3-20261020','proof':'breakthrough-native-both-context16-20261020','development':'breakthrough-native-context-development-20261020','assembly-v1':'breakthrough-native-context-finished-20261020','assembly-v2':'breakthrough-native-context-finished-v2-20261020'}),('breakthrough-groups-safe-final-20261020',{'gate':'breakthrough-groups-safe-final-gate-20261020','search':'breakthrough-groups-safe-nonce-20261020','finished':'breakthrough-groups-safe-finished-20261020','development':'breakthrough-groups-safe-development-20261020','prototype':'breakthrough-grouped-square-ports-20261020'})]
jobs.append(('breakthrough-groups-context-final-20261020',{'gate':'breakthrough-groups-context-final-gate-20261020','search':'breakthrough-groups-context-nonce-20261020','finished':'breakthrough-groups-context-finished-20261020','proof16':'breakthrough-groups-safe-context16-20261020','proof0':'breakthrough-groups-safe-context0-20261020','development':'breakthrough-groups-context-development-20261020'}))
for name,mapping in jobs:
 r=ex/name;manifest=json.loads((r/'EVIDENCE-MANIFEST.json').read_text());receipt=json.loads((r/'PACKAGE-RESULT.json').read_text());counts={k:0 for k in mapping}
 with tarfile.open(r/'final-evidence.tar.gz') as archive:
  for member in archive:
   parts=Path(member.name).parts
   if len(parts)!=2 or parts[0] not in mapping:continue
   data=archive.extractfile(member).read();assert hashlib.sha256(data).hexdigest()==manifest['files'][member.name]
   dest=ex/mapping[parts[0]]/parts[1];assert 'resource-preflight' not in member.name;dest.parent.mkdir(exist_ok=True)
   if dest.exists():assert dest.read_bytes()==data,member.name
   else:dest.write_bytes(data)
   counts[parts[0]]+=1
 for namespace,n in counts.items():
  directory=ex/mapping[namespace];(directory/'SUBMISSION-EVIDENCE-LINK.json').write_text(json.dumps({'archive':name+'/final-evidence.tar.gz','archive_sha256':receipt['archive_sha256'],'namespace':namespace,'hydrated_members':n,'status':'EVERY_HYDRATED_MEMBER_MATCHES_SUBMISSION_MANIFEST','scope':'Original immutable submission archive remains authoritative; candidate/tool/large streams retained on server.'},indent=2)+'\n')
 print(name,counts)
