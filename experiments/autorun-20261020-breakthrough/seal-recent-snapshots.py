import gzip,hashlib,json
from pathlib import Path
b=Path(__file__).resolve().parents[1]/'breakthrough-assessment-20261020';sha=lambda v:hashlib.sha256(v).hexdigest()
for name in ['20261020T064008Z','20261020T072008Z']:
 p=b/'snapshots'/name;assert p.is_dir()
 if(p/'SNAPSHOT-MANIFEST.json').exists():continue
 raw=(p/'public-submissions.json').read_bytes();json.loads(raw);(p/'public-submissions.json.gz').write_bytes(gzip.compress(raw,mtime=0));files=['leader-product.json','leader-qubits.json','leader-toffoli.json','PUBLIC-RECORDS.json','public-submissions.json.gz'];(p/'SNAPSHOT-MANIFEST.json').write_bytes((json.dumps({'raw_api_sha256':sha(raw),'files':{n:sha((p/n).read_bytes())for n in files},'scope':'Immutable fresh public snapshot; original dated records retained.'},indent=2)+'\n').encode());(p/'.gitattributes').write_bytes(b'* -text\n');print(name,'sealed')
