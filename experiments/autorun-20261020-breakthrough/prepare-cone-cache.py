import hashlib,json,shutil,subprocess
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research');r=ws/'breakthrough-public140-cone-cache-20261020';old=ws/'breakthrough-public140-cache-20261020';t=r/'tool';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text());assert not t.exists();assert all(sha(old/'tool'/p)==h for p,h in f['tool_source_files'].items());t.mkdir()
for p in(old/'tool').iterdir():
 if p.is_file():shutil.copyfile(p,t/p.name)
s=(t/'discover.rs').read_text();a='if local_proof(&ops,first,i,nq,nb){';assert s.count(a)==1;s=s.replace(a,'if cone_local_proof(&ops,first,i,nq,nb){');s+='\n'+(r/'cone-proof.rs').read_text();(t/'discover.rs').write_bytes(s.encode());subprocess.run(['cp','-a','--reflink=auto',str(old/'tool/target'),str(t/'target')],check=True)
f['tool_source_files']={p.name:sha(p)for p in t.iterdir()if p.is_file()};f['scope']+=' Proof experiment prunes only backwards-irrelevant writes and unused lexical guard blocks; guard snapshots and all value/classical dependencies retained. Exact arbitrary-cut algebra unchanged; native agreement/fault controls precede scans.';(r/'SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
