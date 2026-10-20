"""Prepare new controllers; never mutate prior receipts or launch a gate."""
from pathlib import Path
import ast
ws=Path(__file__).resolve().parents[2]
ex=ws/'experiments'
n=ex/'breakthrough-public322-square-nonce-20261020';n.mkdir(exist_ok=True)
f=ex/'breakthrough-public322-square-final-20261020';f.mkdir(exist_ok=True)
s=(ex/'breakthrough-public8b-repeat-nonce-20261020/run.py').read_text()
s=s.replace('breakthrough-public8b-repeat-nonce-20261020','breakthrough-public322-square-nonce-20261020').replace('breakthrough-public8b-repeat-generic-20261020','breakthrough-public322-square-finished-20261020').replace('breakthrough-public8b-repeat-final-gate-20261020','breakthrough-public322-square-final-gate-20261020').replace('public8b-repeat-generic-final-20261020-v1','public322-square1408-final-20261020-v1').replace('SOURCE-FREEZE-v2.json','SOURCE-FREEZE.json')
s=s.replace("=='4fb7a65acb7027fe9fa519b0db781f830c5cf1e1e5573afa102247401b3b6a01'", "==json.loads((candidate/'FINISHED-RESULT.json').read_text())['native_stream_sha256']")
ast.parse(s);(n/'run.py').write_text(s)
s=(ex/'breakthrough-public8b-repeat-final-20261020/finalize.py').read_text()
s=s.replace('breakthrough-public8b-repeat-nonce-20261020','breakthrough-public322-square-nonce-20261020').replace('breakthrough-public8b-repeat-generic-20261020','breakthrough-public322-square-finished-20261020').replace('breakthrough-public8b-repeat-final-gate-20261020','breakthrough-public322-square-final-gate-20261020').replace('breakthrough-public8b-repeat-final-20261020','breakthrough-public322-square-final-20261020').replace('SOURCE-FREEZE-v2.json','SOURCE-FREEZE.json').replace('finished_pipeline.rs','finished_square_pipeline.rs')
s=s.replace("sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()", "sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()\nfinished=json.loads((old/'FINISHED-RESULT.json').read_text());operation_count=finished['operations']")
s=s.replace('10553247','operation_count')
s=s.replace("=='a680f4d979df3ebdc5601616569705df1f115ebfcc059945d6c2cb3a183c53ab'", "==json.loads((gate/'GATE-RESULT.json').read_text())['candidate_source_freeze_sha256']")
s=s.replace("=='4fb7a65acb7027fe9fa519b0db781f830c5cf1e1e5573afa102247401b3b6a01'", "==finished['native_stream_sha256']")
s=s.replace("assert q==1464 and score['score']==q*tof", "assert q==finished['qubits'] and score['score']==q*tof")
ast.parse(s);(f/'finalize.py').write_text(s)
for p in[n,f]:
 (p/'.gitattributes').write_text('* -text\n');(p/'.gitignore').write_text('candidate/\ntool/\n*resource-preflight*\npublic-before-upload.json\n')
print('Prepared nonce and final rebuild controllers; neither launched.')
