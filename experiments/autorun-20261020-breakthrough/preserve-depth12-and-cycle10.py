import ast,gzip,hashlib,json,tarfile
from pathlib import Path
a=Path(__file__).parent;ex=a.parent;r=ex/'breakthrough-depth12-final-20261020';sha=lambda b:hashlib.sha256(b).hexdigest()
receipt=json.loads((r/'PACKAGE-RESULT.json').read_text());manifest=json.loads((r/'EVIDENCE-MANIFEST.json').read_text());assert sha((r/'final-evidence.tar.gz').read_bytes())==receipt['archive_sha256'];assert sha((r/'EVIDENCE-MANIFEST.json').read_bytes())==receipt['manifest_sha256']
mapping={'gate':'breakthrough-depth12-final-gate-20261020','search':'breakthrough-depth12-nonce-20261020','finished':'breakthrough-depth12-finished-20261020','proof':'breakthrough-depth12-context-20261020','development':'breakthrough-depth12-development-20261020','grid':'breakthrough-grouped-exact-resource-grid-v2-20261020','grid-development':'breakthrough-grouped-resource-development-20261020','proof-tool':'breakthrough-depth12-context-20261020/tool-source'};counts={k:0 for k in mapping}
with tarfile.open(r/'final-evidence.tar.gz')as archive:
 for m in archive:
  p=Path(m.name);assert not p.is_absolute() and '..'not in p.parts and m.isfile();data=archive.extractfile(m).read();assert sha(data)==(receipt['manifest_sha256']if m.name=='EVIDENCE-MANIFEST.json'else manifest['files'][m.name])
  if len(p.parts)<2 or p.parts[0]not in mapping:continue
  dest=ex/mapping[p.parts[0]]/Path(*p.parts[1:]);assert 'resource-preflight'not in m.name;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():assert dest.read_bytes()==data,m.name
  else:dest.write_bytes(data)
  counts[p.parts[0]]+=1
for key,n in counts.items():
 d=ex/mapping[key];(d/'SUBMISSION-EVIDENCE-LINK.json').write_text(json.dumps({'archive':r.name+'/final-evidence.tar.gz','archive_sha256':receipt['archive_sha256'],'namespace':key,'hydrated_members':n,'status':'EVERY_HYDRATED_MEMBER_MATCHES_IMMUTABLE_SUBMISSION_MANIFEST'},indent=2)+'\n')
print('Depth12 evidence hydration',counts)
p=ex/'breakthrough-assessment-20261020/snapshots/20261020T192716Z';raw=(p/'public-submissions.json').read_bytes();json.loads(raw);(p/'public-submissions.json.gz').write_bytes(gzip.compress(raw,mtime=0));files=['leader-product.json','leader-qubits.json','leader-toffoli.json','PUBLIC-RECORDS.json','public-submissions.json.gz'];(p/'SNAPSHOT-MANIFEST.json').write_text(json.dumps({'raw_api_sha256':sha(raw),'files':{n:sha((p/n).read_bytes())for n in files},'scope':'Fresh public records confirm official independentT747218; globalproduct933231010 unchanged.'},indent=2)+'\n');(p/'.gitattributes').write_text('* -text\n')
names=['breakthrough-public-drop-tradeoffs-v2-20261020','breakthrough-public-best-drop-context-20261020','breakthrough-public-best-drop-finished-20261020','breakthrough-public-best-drop-development-20261020','breakthrough-public-best-drop-final-gate-20261020','breakthrough-public-best-drop-nonce-20261020','breakthrough-value-ir-audit-20261020']
for src,dest,terminator in [('seal-research-cycle9.py','seal-research-cycle10.py','\nws='),('collect-research-cycle9.py','collect-research-cycle10.py','\nsha=')]:
 s=(a/src).read_text();start=s.index('names=[');end=s.index(terminator,start);s=s[:start]+'names='+repr(names)+s[end:];ast.parse(s);(a/dest).write_text(s)
print('Seven completed fronts selected; active nonce v2 and audit v2 excluded.')
