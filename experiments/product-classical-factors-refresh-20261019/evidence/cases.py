import json
from pathlib import Path
r=Path(__file__).resolve().parent;e=r.parent;g=e/'product-guard-schedule-20261019'
assert json.loads((g/'CONTROL.json').read_text())['status']=='PROTECTED_SIMULATOR_MATERIALIZED_GUARD_PHYSICAL_TRANSCRIPT_CONTROL_PASS'
report=json.loads((g/'scheduled.json').read_text())
cases=[{'name':'public','input':str(e/'product-pareto-20261019/parent/ops.bin'),'input_sha3_256':'429af1c31b54064e17e7602be516b519c066c241e218d56f002287ea02b16842'},
       {'name':'parent4','input':str(e/'product-pareto-20261019/candidate-parent4/ops.bin'),'compressed_sha256':'9f50f06098026882a57f5f6c436abaaf68be79be2fc7c6e33b8e884065195a3a'},
       {'name':'guard','input':str(g/'scheduled.ordered.ops.bin'),'input_sha3_256':report['output_full_sha3_256']}]
# The independently frozen gate/search receipt binds the parent4 raw stream.
import hashlib,ctypes,struct
p=Path(cases[1]['input']);assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==cases[1]['compressed_sha256']
receipt=json.loads((e/'parent4-operational-sat-20261019/ACCEPTANCE.json').read_text())
# Read only known metadata; use the already preserved gate stream raw digest.
matches=[]
for q in [e/'product-pareto-20261019/evidence/parent4-qualification.json',e/'product-pareto-20261019/parent4-qualification.json']:
    if q.exists():matches.append(str(q))
(r/'PARENT4-RECEIPT-LOOKUP.json').write_text(json.dumps({'acceptance_fields':list(receipt),'possible_qualification_files':matches},indent=2)+'\n')
# A one-off streaming decompression computes its raw operation hash, independent
# of packet inputs. No private nonce log or circuit content is modified.
import subprocess
sha=subprocess.check_output([str(r/'hash_ops'),str(p)],text=True).strip()
assert len(sha)==64;cases[1]['input_sha3_256']=sha
(r/'DECLARED-CASES.json').write_text(json.dumps(cases,indent=2)+'\n')
for x in cases:print('\t'.join(x[k] for k in ['name','input','input_sha3_256']))
